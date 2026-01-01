"""
API endpoints for MHT instruction viewer.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.core.deps import get_current_active_user
from app.models.user import User
from app.services.mht_parser import mht_parser
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/parse-instruction")
async def parse_mht_instruction(
    url: str = Query(..., description="URL to the MHT instruction file"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Download and parse an MHT instruction file from the Ukrainian medicine registry.
    
    This endpoint acts as a proxy to download MHT files and parse them to avoid CORS issues
    when accessing instruction files directly from the frontend.
    
    Args:
        url: URL to the MHT file (usually from DRLZ registry)
        current_user: Authenticated user
        
    Returns:
        Parsed instruction content with title, HTML, and plain text
    """
    try:
        # Validate that URL is from a trusted source
        trusted_domains = [
            'drlz.com.ua',
            'www.drlz.com.ua',
            'tabletki.ua',
            'www.tabletki.ua'
        ]
        
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        
        if not any(domain in parsed_url.netloc.lower() for domain in trusted_domains):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL must be from a trusted medicine registry domain"
            )
        
        # Download and parse the MHT file
        logger.info(f"User {current_user.email} requesting MHT parsing for: {url}")
        
        result = await mht_parser.download_and_parse_mht(url)
        
        if not result["success"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to parse MHT file: {result.get('error', 'Unknown error')}"
            )
        
        # Return the parsed content
        response = {
            "success": True,
            "url": url,
            "title": result.get("title", "Medicine Instruction"),
            "html_content": result.get("html_content", ""),
            "text_content": result.get("text_content", ""),
            "content_length": result.get("content_length", 0),
            "encoding": result.get("encoding", "utf-8")
        }
        
        logger.info(f"Successfully parsed MHT file for user {current_user.email}: {len(response['text_content'])} characters")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in parse_mht_instruction: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/instruction-preview")
async def get_instruction_preview(
    url: str = Query(..., description="URL to the MHT instruction file"),
    current_user: User = Depends(get_current_active_user),
):
    """
    Get a preview of an MHT instruction file (title and first few lines).
    
    This is a lighter endpoint that only extracts basic information about
    the instruction file without parsing the full content.
    
    Args:
        url: URL to the MHT file
        current_user: Authenticated user
        
    Returns:
        Preview information including title and snippet
    """
    try:
        # Use the same validation as the main endpoint
        from urllib.parse import urlparse
        parsed_url = urlparse(url)
        
        trusted_domains = [
            'drlz.com.ua',
            'www.drlz.com.ua', 
            'tabletki.ua',
            'www.tabletki.ua'
        ]
        
        if not any(domain in parsed_url.netloc.lower() for domain in trusted_domains):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="URL must be from a trusted medicine registry domain"
            )
        
        # Parse the full content (we can optimize this later if needed)
        result = await mht_parser.download_and_parse_mht(url)
        
        if not result["success"]:
            return {
                "success": False,
                "url": url,
                "error": result.get("error", "Unknown error"),
                "available": False
            }
        
        # Create a preview from the text content
        text_content = result.get("text_content", "")
        preview_text = text_content[:300] + "..." if len(text_content) > 300 else text_content
        
        return {
            "success": True,
            "url": url,
            "title": result.get("title", "Medicine Instruction"),
            "preview": preview_text,
            "content_length": result.get("content_length", 0),
            "available": True
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in get_instruction_preview: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
