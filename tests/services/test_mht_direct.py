#!/usr/bin/env python3
"""
Direct test of the MHT parser service without API authentication.
"""

import asyncio
import sys
import os

# Add the backend path to Python path
sys.path.insert(0, '/home/vojd/projects/home_aid_sonnet/backend')

from app.services.mht_parser import mht_parser

async def test_mht_parser_direct():
    """Test the MHT parser directly."""
    
    test_url = "http://www.drlz.com.ua/ibp/lz_www.nsf/id/8B1973D53B54886842258BE0004A6892/$file/UA178230101_D929.mht"
    
    print("Testing MHT Parser Service Directly")
    print("=" * 50)
    print(f"URL: {test_url}")
    print()
    
    try:
        result = await mht_parser.download_and_parse_mht(test_url)
        
        print("Parser Result:")
        print(f"  Success: {result['success']}")
        
        if result['success']:
            print(f"  Title: {result.get('title', 'N/A')}")
            print(f"  Content Length: {result.get('content_length', 0)} characters")
            print(f"  Encoding: {result.get('encoding', 'N/A')}")
            
            # Show text content snippet
            text_content = result.get('text_content', '')
            if text_content:
                snippet = text_content[:500].strip()
                print(f"\n  Text Content (first 500 chars):")
                print(f"  {'-' * 40}")
                print(f"  {snippet}")
                print(f"  {'-' * 40}")
            
            # Show HTML content info
            html_content = result.get('html_content', '')
            if html_content:
                print(f"\n  HTML Content Available: {len(html_content)} characters")
                # Show first HTML tag
                import re
                first_tag = re.search(r'<[^>]+>', html_content)
                if first_tag:
                    print(f"  First HTML tag: {first_tag.group()}")
        else:
            print(f"  Error: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"Exception during parsing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_mht_parser_direct())
