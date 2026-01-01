"""
Service for downloading and parsing MHT (MHTML) files.
MHT files are web archive format that contains HTML content with embedded resources.
"""

import asyncio
import email
import email.parser
import logging
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse

import httpx
from bs4 import BeautifulSoup
import chardet

logger = logging.getLogger(__name__)


class MHTParser:
    """Parser for MHT (MHTML) files from Ukrainian medicine registry."""
    
    def __init__(self):
        self.timeout = 30.0  # seconds
    
    def _decode_unicode_text(self, text: str) -> str:
        """
        Decode Unicode escape sequences and handle various encoding issues.
        
        Args:
            text: Text that may contain Unicode escapes
            
        Returns:
            Properly decoded text
        """
        if not text:
            return text
        
        # First, handle explicit Unicode escape sequences like \u0421\u043a\u043b\u0430\u0434
        # This is more aggressive than the previous version
        import re
        
        # Pattern to match Unicode escape sequences
        unicode_pattern = r'\\u([0-9a-fA-F]{4})'
        
        def decode_match(match):
            try:
                code_point = int(match.group(1), 16)
                return chr(code_point)
            except (ValueError, OverflowError):
                return match.group(0)  # Return original if can't decode
        
        # Apply Unicode escape decoding
        text = re.sub(unicode_pattern, decode_match, text)
        
        # Try multiple decoding strategies for other encoding issues
        strategies = [
            # Strategy 1: Handle JSON-style Unicode escapes that might remain
            lambda t: t.encode('utf-8').decode('unicode_escape') if '\\u' in t else t,
            # Strategy 2: Handle Latin-1 to UTF-8 conversion
            lambda t: t.encode('latin-1').decode('utf-8', errors='ignore'),
            # Strategy 3: Handle raw Unicode escape sequences
            lambda t: t.encode().decode('unicode_escape') if '\\u' in t else t,
            # Strategy 4: Direct bytes conversion
            lambda t: bytes(t, 'utf-8').decode('utf-8', errors='ignore'),
        ]
        
        for strategy in strategies:
            try:
                decoded = strategy(text)
                # Check if decoding was successful by looking for Cyrillic characters
                if any('\u0400' <= char <= '\u04FF' for char in decoded):
                    text = decoded
                    break
            except (UnicodeDecodeError, UnicodeEncodeError, AttributeError):
                continue
        
        # Final cleanup: remove any remaining escape sequences that couldn't be decoded
        text = re.sub(r'\\u[0-9a-fA-F]{4}', '', text)
        
        return text
    
    def _process_instruction_text(self, text: str) -> str:
        """
        Process instruction text by removing excessive newlines and splitting by Ukrainian pharmaceutical terms.
        
        Args:
            text: Raw instruction text
            
        Returns:
            Processed text with proper section separation
        """
        if not text:
            return text
        
        # First, remove excessive whitespace and normalize newlines
        text = re.sub(r'\n\s*\n', '\n\n', text)
        text = re.sub(r' +', ' ', text)
        
        # Define Ukrainian pharmaceutical section headers
        section_headers = [
            'Склад',  # Composition
            'Фармакотерапевтична група',  # Pharmacotherapeutic group
            'Показання',  # Indications
            'Протипоказання',  # Contraindications
            'Взаємодія з іншими лікарськими засобами та інші види взаємодій',  # Drug interactions
            'Особливості застосування',  # Special precautions
            'Застосування у період вагітності або годування груддю',  # Pregnancy and lactation
            'Здатність впливати на швидкість реакції',  # Effects on driving
            'Спосіб застосування та дозування',  # Dosage and administration
            'Передозування',  # Overdose
            'Побічні реакції',  # Adverse reactions
            'Термін придатності',  # Shelf life
            'Умови зберігання',  # Storage conditions
            'Упаковка',  # Packaging
            'Категорія відпуску',  # Prescription category
            'Виробник',  # Manufacturer
            'Заявник',  # Applicant
            'Місцезнаходження виробника',  # Manufacturer location
            'Реєстраційне посвідчення',  # Registration certificate
            'Дата останнього перегляду',  # Last review date
        ]
        
        # Create a pattern that matches section headers (case-insensitive)
        # Look for the header followed by a period, colon, or newline
        pattern_parts = []
        for header in section_headers:
            # Match header followed by optional punctuation and whitespace
            pattern_parts.append(f"({re.escape(header)})[.:\\s]*")
        
        # Combine all patterns with OR
        section_pattern = '|'.join(pattern_parts)
        
        # Split text by section headers while keeping the headers
        sections = re.split(f'({section_pattern})', text, flags=re.IGNORECASE)
        
        # Process sections to clean up and format properly
        processed_sections = []
        current_section = ""
        
        for i, section in enumerate(sections):
            if not section or not section.strip():
                continue
                
            # Check if this section is a header
            is_header = any(header.lower() in section.lower() for header in section_headers)
            
            if is_header:
                # If we have accumulated content, add it
                if current_section.strip():
                    processed_sections.append(self._clean_section_text(current_section))
                
                # Start new section with the header
                current_section = f"\n\n{section.strip()}"
            else:
                # Add content to current section
                current_section += " " + section.strip()
        
        # Add the last section
        if current_section.strip():
            processed_sections.append(self._clean_section_text(current_section))
        
        # Join all sections
        result = '\n'.join(processed_sections)
        
        # Final cleanup
        result = re.sub(r'\n{3,}', '\n\n', result)  # Max 2 consecutive newlines
        result = re.sub(r'[ \t]+', ' ', result)      # Single spaces only
        result = result.strip()
        
        return result
    
    def _clean_section_text(self, text: str) -> str:
        """
        Clean individual section text by removing excessive whitespace.
        
        Args:
            text: Section text to clean
            
        Returns:
            Cleaned section text
        """
        if not text:
            return ""
        
        # Remove excessive whitespace within the section
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        return text
        
    async def download_and_parse_mht(self, url: str) -> Dict[str, Any]:
        """
        Download and parse an MHT file from the given URL.
        
        Args:
            url: URL to the MHT file
            
        Returns:
            Dictionary containing parsed content with structure:
            {
                "success": bool,
                "title": str,
                "content": str (HTML),
                "text_content": str (plain text),
                "error": str (if success=False)
            }
        """
        try:
            # Validate URL
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                return {
                    "success": False,
                    "error": "Invalid URL format"
                }
            
            # Download the MHT file
            logger.info(f"Downloading MHT file from: {url}")
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
                
                content = response.content
                
            # Detect encoding
            detected_encoding = chardet.detect(content)
            encoding = detected_encoding.get('encoding', 'utf-8')
            
            # Parse MHT content
            parsed_data = await self._parse_mht_content(content, encoding)
            
            return {
                "success": True,
                "url": url,
                "encoding": encoding,
                **parsed_data
            }
            
        except httpx.TimeoutException:
            logger.error(f"Timeout downloading MHT file: {url}")
            return {
                "success": False,
                "error": "Request timeout - file download took too long"
            }
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error downloading MHT file: {url} - {e}")
            return {
                "success": False,
                "error": f"HTTP error: {e.response.status_code}"
            }
        except Exception as e:
            logger.error(f"Error processing MHT file: {url} - {str(e)}")
            return {
                "success": False,
                "error": f"Processing error: {str(e)}"
            }
    
    async def _parse_mht_content(self, content: bytes, encoding: str) -> Dict[str, Any]:
        """
        Parse the MHT file content using email parser.
        
        Args:
            content: Raw MHT file content
            encoding: Detected encoding
            
        Returns:
            Dictionary with parsed title, HTML content, and plain text
        """
        try:
            # Decode content
            content_str = content.decode(encoding, errors='ignore')
            
            # Parse as email message (MHT is based on MHTML/email format)
            msg = email.message_from_string(content_str)
            
            html_content = ""
            title = "Medicine Instruction"
            
            # Extract HTML content from the message
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/html':
                        charset = part.get_content_charset() or encoding
                        html_part = part.get_payload(decode=True)
                        if html_part:
                            html_content = html_part.decode(charset, errors='ignore')
                            break
            else:
                # Single part message
                if msg.get_content_type() == 'text/html':
                    charset = msg.get_content_charset() or encoding
                    payload = msg.get_payload(decode=True)
                    if payload:
                        html_content = payload.decode(charset, errors='ignore')
            
            # If no HTML found, try to extract from raw content
            if not html_content:
                html_content = await self._extract_html_from_raw(content_str)
            
            # Parse HTML and extract title and clean content
            if html_content:
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Extract title
                title_tag = soup.find('title')
                if title_tag:
                    title = title_tag.get_text(strip=True)
                    # Decode Unicode escape sequences in title
                    title = self._decode_unicode_text(title)
                
                # Clean up HTML - remove scripts, styles, etc.
                for script in soup(["script", "style", "meta", "link"]):
                    script.decompose()
                
                # Get clean HTML
                clean_html = str(soup)
                
                # Decode Unicode escape sequences in HTML content as well
                clean_html = self._decode_unicode_text(clean_html)
                
                # Get plain text content
                text_content = soup.get_text(separator='\n', strip=True)
                
                # Decode Unicode escape sequences (e.g., \u0421 -> С)
                text_content = self._decode_unicode_text(text_content)
                
                # Clean up excessive whitespace and process for Ukrainian pharma sections
                text_content = self._process_instruction_text(text_content)
                
                return {
                    "title": title,
                    "html_content": clean_html,
                    "text_content": text_content,
                    "content_length": len(text_content)
                }
            
            return {
                "title": "No content found",
                "html_content": "<p>Could not extract content from MHT file</p>",
                "text_content": "Could not extract content from MHT file",
                "content_length": 0
            }
            
        except Exception as e:
            logger.error(f"Error parsing MHT content: {str(e)}")
            raise
    
    async def _extract_html_from_raw(self, content: str) -> str:
        """
        Fallback method to extract HTML from raw MHT content.
        """
        try:
            # Look for HTML content boundaries in MHT
            html_start_patterns = [
                r'Content-Type:\s*text/html.*?\n\n(.+?)(?=\n--|\nContent-Type:|\Z)',
                r'<html.*?</html>',
                r'<HTML.*?</HTML>',
            ]
            
            for pattern in html_start_patterns:
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                if matches:
                    return matches[0]
            
            # If no HTML boundaries found, look for any HTML tags
            html_tag_match = re.search(r'<html.*?</html>', content, re.DOTALL | re.IGNORECASE)
            if html_tag_match:
                return html_tag_match.group(0)
            
            return ""
            
        except Exception as e:
            logger.error(f"Error extracting HTML from raw content: {str(e)}")
            return ""


# Global MHT parser instance
mht_parser = MHTParser()
