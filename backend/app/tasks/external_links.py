"""
Tasks for resolving external medication links from DRLZ and Tabletki.
"""

import httpx
from celery import shared_task
from typing import Optional, Dict, Any, List
from urllib.parse import quote
import logging
import hashlib
from datetime import datetime
import sys
import os

# Add the backend directory to the path so we can import drlz
sys.path.append('/app')

from app.core.config import settings

logger = logging.getLogger(__name__)


def normalize_search_query(query: str) -> str:
    """Normalize search query for consistent caching"""
    return query.strip().upper()


def get_cache_key(source: str, query: str) -> str:
    """Generate cache key for external link resolution"""
    normalized = normalize_search_query(query)
    query_hash = hashlib.md5(normalized.encode()).hexdigest()
    return f"ext_link:{source}:{query_hash}"


@shared_task(bind=True, max_retries=3)
def search_drlz_medication(self, query: str) -> Dict[str, Any]:
    """
    Search for medication in DRLZ CSV registry.
    
    Args:
        query: The medication name to search for
        
    Returns:
        Dictionary with medication details from DRLZ CSV
    """
    try:
        # Import DRLZ CSV service
        try:
            from app.services.drlz_csv import drlz_service
        except ImportError:
            logger.error("DRLZ CSV service not found")
            raise
        
        # Get medication details with instructions
        medications = drlz_service.get_medication_with_instructions(query, limit=5)
        
        result = {
            'source': 'DRLZ',
            'query': query,
            'status': 'SUCCESS',
            'medications': medications,
            'fetched_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Found {len(medications)} medications in DRLZ CSV for: {query}")
        return result
        
    except Exception as e:
        logger.error(f"Error searching DRLZ CSV for {query}: {e}")
        result = {
            'source': 'DRLZ',
            'query': query,
            'status': 'ERROR',
            'error': str(e),
            'medications': [],
            'fetched_at': datetime.utcnow().isoformat()
        }
        
        return result


@shared_task(bind=True, max_retries=3)
def search_tabletki_medication(self, query: str) -> Dict[str, Any]:
    """
    Create search URL for medication on Tabletki.ua.
    
    Args:
        query: The medication name to search for
        
    Returns:
        Dictionary with search URL
    """
    try:
        # Create search URL - always valid, no need to actually fetch
        search_url = f"https://tabletki.ua/uk/search/{quote(query)}"
        
        result = {
            'source': 'TABLETKI',
            'query': query,
            'search_url': search_url,
            'status': 'SUCCESS',
            'fetched_at': datetime.utcnow().isoformat()
        }
        
        logger.info(f"Generated Tabletki search URL for: {query}")
        return result
        
    except Exception as e:
        logger.error(f"Error generating Tabletki search URL for {query}: {e}")
        result = {
            'source': 'TABLETKI',
            'query': query,
            'search_url': f"https://tabletki.ua/uk/search/{quote(query)}",
            'status': 'ERROR',
            'error': str(e),
            'fetched_at': datetime.utcnow().isoformat()
        }
        return result


@shared_task
def resolve_medication_links(medication_id: int, query: str) -> None:
    """
    Resolve external links for a medication and store results in database.
    
    Args:
        medication_id: ID of the medication to resolve links for
        query: Normalized medication name to search for
    """
    logger.info(f"Starting link resolution for medication {medication_id} with query: {query}")
    
    # Search DRLZ and Tabletki concurrently
    drlz_result = search_drlz_medication.delay(query)
    tabletki_result = search_tabletki_medication.delay(query)
    
    # Wait for results
    try:
        drlz_data = drlz_result.get(timeout=60)
        tabletki_data = tabletki_result.get(timeout=30)
    except Exception as e:
        logger.error(f"Error getting search results for medication {medication_id}: {e}")
        return
    
    # Store results in database using sync session
    try:
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from app.core.config import settings
        from app.models.medication import Medication
        from app.models.audit import ExternalResolution
        
        # Create sync engine for the task
        sync_db_url = str(settings.DATABASE_URL).replace("postgresql+asyncpg://", "postgresql://")
        engine = create_engine(sync_db_url)
        SessionLocal = sessionmaker(bind=engine)
        
        with SessionLocal() as db:
            # Update medication with external links
            medication = db.get(Medication, medication_id)
            if medication:
                # Update DRLZ data
                if drlz_data.get('status') == 'SUCCESS' and drlz_data.get('medications'):
                    # Take the first medication result
                    first_med = drlz_data['medications'][0]
                    if first_med.get('medication_link'):
                        medication.drlz_link = first_med['medication_link']
                    if first_med.get('instruction_link'):
                        medication.drlz_instruction_link = first_med['instruction_link']
                    if first_med.get('main_name'):
                        # Use DRLZ main name as description if we don't have one
                        if not medication.description:
                            medication.description = f"{first_med['main_name']} - {first_med.get('form', '')}"
                
                # Update Tabletki data
                if tabletki_data.get('status') == 'SUCCESS':
                    medication.tabletki_link = tabletki_data['search_url']
                
                # Store resolution records
                for data, source in [(drlz_data, 'DRLZ'), (tabletki_data, 'TABLETKI')]:
                    resolution = ExternalResolution(
                        medication_id=medication_id,
                        source=data['source'],
                        query=data['query'],
                        page_url=data.get('search_url') or (data.get('medications', [{}])[0].get('medication_link') if data.get('medications') else None),
                        status=data['status'],
                        hash=get_cache_key(data['source'], data['query'])
                    )
                    db.add(resolution)
                
                db.commit()
                logger.info(f"Updated external links for medication {medication_id}")
            else:
                logger.error(f"Medication {medication_id} not found")
                
    except Exception as e:
        logger.error(f"Error storing resolution results for medication {medication_id}: {e}")


@shared_task(bind=True, max_retries=3)
def resolve_tabletki_link(self, url: str) -> Optional[Dict[str, Any]]:
    """
    Resolve a Tabletki.ua medication link and extract medication information.
    
    Args:
        url: The Tabletki.ua medication page URL
        
    Returns:
        Dictionary with medication info or None if failed
    """
    try:
        with httpx.Client(timeout=30.0) as client:
            response = client.get(url)
            response.raise_for_status()
            
            result = {
                'source': 'tabletki',
                'url': url,
                'status': 'SUCCESS',
                'extracted_at': datetime.utcnow().isoformat(),
            }
            
            logger.info(f"Successfully resolved Tabletki link: {url}")
            return result
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error resolving Tabletki link {url}: {e}")
        raise self.retry(countdown=60, exc=e)
    except Exception as e:
        logger.error(f"Error resolving Tabletki link {url}: {e}")
        raise self.retry(countdown=60, exc=e)


@shared_task
def resolve_external_link(url: str) -> Optional[Dict[str, Any]]:
    """
    Dispatch task to resolve external medication links based on domain.
    
    Args:
        url: The medication page URL
        
    Returns:
        Dictionary with medication info or None if failed
    """
    if 'tabletki.ua' in url:
        return resolve_tabletki_link.delay(url)
    elif 'drlz.com.ua' in url:
        # For DRLZ links, we can try to extract instruction
        return None  # Not implemented yet
    else:
        logger.warning(f"Unknown external URL domain: {url}")
        return None
