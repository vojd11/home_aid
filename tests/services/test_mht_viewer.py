#!/usr/bin/env python3
"""
Test script for the MHT instruction viewer functionality.
"""

import requests
import json

# API base URL
BASE_URL = "http://hate.local:8000/api/v1"

def test_mht_viewer():
    """Test the MHT instruction viewer endpoints."""
    
    # Test MHT URL from the registry
    test_url = "http://www.drlz.com.ua/ibp/lz_www.nsf/id/8B1973D53B54886842258BE0004A6892/$file/UA178230101_D929.mht"
    
    print("Testing MHT Instruction Viewer")
    print("=" * 50)
    
    # Step 1: Skip registration, use existing user
    print("1. Using existing test user...")
    
    # Step 2: Login and get token
    print("\n2. Logging in...")
    login_data = {
        "email": "test@example.com", 
        "password": "password123"  # Try common test password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data["access_token"]
            print("✓ Login successful")
        else:
            print(f"Login failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"Login error: {e}")
        return
    
    # Headers for authenticated requests
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 3: Test instruction preview endpoint
    print("\n3. Testing instruction preview...")
    try:
        params = {"url": test_url}
        response = requests.get(f"{BASE_URL}/instructions/instruction-preview", 
                              headers=headers, params=params)
        
        if response.status_code == 200:
            preview_data = response.json()
            print("✓ Preview successful")
            print(f"  Title: {preview_data.get('title', 'N/A')}")
            print(f"  Available: {preview_data.get('available', False)}")
            print(f"  Content length: {preview_data.get('content_length', 0)}")
            if 'preview' in preview_data:
                preview_text = preview_data['preview'][:200] + "..." if len(preview_data['preview']) > 200 else preview_data['preview']
                print(f"  Preview: {preview_text}")
        else:
            print(f"Preview failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Preview error: {e}")
    
    # Step 4: Test full parse endpoint
    print("\n4. Testing full instruction parsing...")
    try:
        params = {"url": test_url}
        response = requests.get(f"{BASE_URL}/instructions/parse-instruction", 
                              headers=headers, params=params)
        
        if response.status_code == 200:
            parse_data = response.json()
            print("✓ Parse successful")
            print(f"  Title: {parse_data.get('title', 'N/A')}")
            print(f"  Content length: {parse_data.get('content_length', 0)}")
            print(f"  Encoding: {parse_data.get('encoding', 'N/A')}")
            
            # Show a snippet of the text content
            text_content = parse_data.get('text_content', '')
            if text_content:
                snippet = text_content[:300] + "..." if len(text_content) > 300 else text_content
                print(f"  Text snippet: {snippet}")
            
            # Check if HTML content is available
            html_content = parse_data.get('html_content', '')
            print(f"  HTML content available: {len(html_content) > 0}")
            if html_content:
                print(f"  HTML length: {len(html_content)} characters")
                
        else:
            print(f"Parse failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Parse error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_mht_viewer()
