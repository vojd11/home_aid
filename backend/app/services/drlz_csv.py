"""
DRLZ CSV Service - Ukraine State Register of Medicines CSV Parser
Provides medication search functionality using the official CSV registry
"""

import csv
import os
import re
from typing import List, Dict, Optional, Tuple
from difflib import SequenceMatcher
import logging

logger = logging.getLogger(__name__)


class DRLZCSVService:
    """Service for searching medications in the Ukrainian DRLZ registry CSV"""
    
    def __init__(self, csv_path: str = "/app/data/reestr.csv"):
        self.csv_path = csv_path
        self._medications = None
        self._load_medications()
    
    def _load_medications(self) -> None:
        """Load medications from CSV file"""
        if not os.path.exists(self.csv_path):
            logger.error(f"DRLZ CSV file not found at {self.csv_path}")
            self._medications = []
            return
            
        try:
            medications = []
            
            # Try different encodings
            encodings = ['utf-8', 'windows-1251', 'cp1251', 'iso-8859-1', 'latin-1']
            file_content = None
            
            for encoding in encodings:
                try:
                    with open(self.csv_path, 'r', encoding=encoding) as file:
                        file_content = file.read()
                        logger.info(f"Successfully opened CSV with encoding: {encoding}")
                        break
                except UnicodeDecodeError:
                    logger.debug(f"Failed to open with encoding: {encoding}")
                    continue
            
            if not file_content:
                logger.error("Could not decode CSV file with any supported encoding")
                self._medications = []
                return
            
            # Parse the CSV content
            lines = file_content.strip().split('\n')
            if not lines:
                logger.error("CSV file is empty")
                self._medications = []
                return
            
            # Skip header row
            headers = lines[0]
            logger.info(f"CSV headers: {headers[:100]}...")
            
            for row_num, line in enumerate(lines[1:], start=2):
                if not line.strip():
                    continue
                    
                # Split by semicolon and handle quoted fields
                row = []
                in_quotes = False
                current_field = ""
                
                i = 0
                while i < len(line):
                    char = line[i]
                    if char == '"':
                        in_quotes = not in_quotes
                    elif char == ';' and not in_quotes:
                        row.append(current_field.strip('"'))
                        current_field = ""
                        i += 1
                        continue
                    else:
                        current_field += char
                    i += 1
                
                # Add the last field
                if current_field:
                    row.append(current_field.strip('"'))
                
                if len(row) >= 42:  # Ensure we have enough columns
                    try:
                        medication = {
                            'id': row[0] if len(row) > 0 else "",
                            'commercial_name': row[1] if len(row) > 1 else "",
                            'international_name': row[2] if len(row) > 2 else "",
                            'release_form': row[3] if len(row) > 3 else "",
                            'composition': row[5] if len(row) > 5 else "",
                            'registration_number': row[32] if len(row) > 32 else "",
                            'applicant_name': row[10] if len(row) > 10 else "",
                            'applicant_city': row[11] if len(row) > 11 else "",
                            'applicant_country': row[12] if len(row) > 12 else "",
                            'manufacturer_name': row[14] if len(row) > 14 else "",
                            'manufacturer_city': row[15] if len(row) > 15 else "",
                            'manufacturer_country': row[16] if len(row) > 16 else "",
                            'instruction_url': row[41] if len(row) > 41 else "",
                            'validity_period': row[42] if len(row) > 42 else ""
                        }
                        
                        # Only include if we have commercial name
                        if medication['commercial_name']:
                            medications.append(medication)
                            
                    except (IndexError, AttributeError) as e:
                        logger.warning(f"Error parsing row {row_num}: {e}")
                        continue
                            
            self._medications = medications
            logger.info(f"Loaded {len(medications)} medications from DRLZ CSV")
            
        except Exception as e:
            logger.error(f"Error loading DRLZ CSV: {e}")
            self._medications = []
    
    def _normalize_text(self, text: str) -> str:
        """Normalize text for search comparison"""
        if not text:
            return ""
        # Convert to lowercase and remove extra spaces
        normalized = re.sub(r'\s+', ' ', text.lower().strip())
        # Remove quotes and special characters
        normalized = re.sub(r'["""\'`]', '', normalized)
        return normalized
    
    def _calculate_similarity(self, search_term: str, medication_name: str) -> float:
        """Calculate similarity between search term and medication name"""
        search_norm = self._normalize_text(search_term)
        med_norm = self._normalize_text(medication_name)
        
        if not search_norm or not med_norm:
            return 0.0
        
        # Exact match gets highest score
        if search_norm == med_norm:
            return 1.0
            
        # Check if search term is contained in medication name
        if search_norm in med_norm:
            return 0.9
            
        # Check if medication name starts with search term
        if med_norm.startswith(search_norm):
            return 0.8
            
        # Use sequence matcher for fuzzy matching
        return SequenceMatcher(None, search_norm, med_norm).ratio()
    
    def search_medications(self, query: str, limit: int = 50) -> List[Dict]:
        """
        Search for medications by name
        
        Args:
            query: Search query (medication name)
            limit: Maximum number of results to return
            
        Returns:
            List of medication dictionaries sorted by relevance
        """
        if not self._medications:
            return []
            
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        results = []
        
        for medication in self._medications:
            # Calculate similarity for both commercial and international names
            commercial_similarity = self._calculate_similarity(query, medication['commercial_name'])
            international_similarity = self._calculate_similarity(query, medication['international_name'])
            
            # Take the higher similarity score
            max_similarity = max(commercial_similarity, international_similarity)
            
            # Include if similarity is above threshold
            if max_similarity >= 0.3:
                result = medication.copy()
                result['similarity_score'] = max_similarity
                result['main_name'] = medication['commercial_name']
                result['form'] = medication['release_form']
                result['medication_link'] = None  # We don't have individual medication page URLs
                result['instruction_link'] = medication['instruction_url'] if medication['instruction_url'] else None
                
                results.append(result)
        
        # Sort by similarity score (descending)
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        
        return results[:limit]
    
    def get_medication_names(self, query: str, limit: int = 20) -> List[str]:
        """
        Get just the medication names from search results
        
        Args:
            query: Search query
            limit: Maximum number of names to return
            
        Returns:
            List of unique medication names
        """
        medications = self.search_medications(query, limit)
        names = []
        seen_names = set()
        
        for med in medications:
            name = med.get('main_name', '').strip()
            if name and name not in seen_names:
                names.append(name)
                seen_names.add(name)
        
        return names
    
    def get_medication_details(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Get medication details including main name, form, and links
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of medication details with main_name, form, and instruction_link
        """
        medications = self.search_medications(query, limit)
        details = []
        
        for med in medications:
            if med.get('main_name'):
                detail = {
                    'main_name': med.get('main_name', ''),
                    'form': med.get('form', ''),
                    'instruction_link': med.get('instruction_link'),
                    'registration_number': med.get('registration_number', ''),
                    'manufacturer': f"{med.get('manufacturer_name', '')} ({med.get('manufacturer_country', '')})".strip(' ()')
                }
                details.append(detail)
        
        return details
    
    def get_medication_with_instructions(self, query: str, limit: int = 20) -> List[Dict]:
        """
        Get medication details including instructions (same as get_medication_details for CSV)
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of medication details with instruction links
        """
        return self.get_medication_details(query, limit)
    
    def search_by_international_name(self, international_name: str, limit: int = 20) -> List[Dict]:
        """
        Search medications by international (INN) name
        
        Args:
            international_name: International name to search for
            limit: Maximum number of results to return
            
        Returns:
            List of medication details
        """
        if not self._medications:
            return []
            
        results = []
        normalized_query = self._normalize_text(international_name)
        
        for medication in self._medications:
            normalized_inn = self._normalize_text(medication['international_name'])
            
            if normalized_query in normalized_inn or normalized_inn in normalized_query:
                similarity = self._calculate_similarity(international_name, medication['international_name'])
                if similarity >= 0.5:
                    result = medication.copy()
                    result['similarity_score'] = similarity
                    result['main_name'] = medication['commercial_name']
                    result['form'] = medication['release_form']
                    result['instruction_link'] = medication['instruction_url'] if medication['instruction_url'] else None
                    results.append(result)
        
        # Sort by similarity score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)
        return results[:limit]
    
    def get_statistics(self) -> Dict:
        """Get statistics about the loaded medication database"""
        if not self._medications:
            return {
                'total_medications': 0,
                'with_instruction_urls': 0,
                'unique_manufacturers': 0,
                'unique_international_names': 0
            }
        
        instruction_count = sum(1 for med in self._medications if med.get('instruction_url'))
        unique_manufacturers = len(set(med['manufacturer_name'] for med in self._medications if med.get('manufacturer_name')))
        unique_international_names = len(set(med['international_name'] for med in self._medications if med.get('international_name')))
        
        return {
            'total_medications': len(self._medications),
            'with_instruction_urls': instruction_count,
            'unique_manufacturers': unique_manufacturers,
            'unique_international_names': unique_international_names
        }


# Global instance for easy access
drlz_service = DRLZCSVService()
