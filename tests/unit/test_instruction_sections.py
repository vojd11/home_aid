#!/usr/bin/env python3
"""
Test script specifically for testing instruction section parsing.
"""

import requests
import json

# API base URL
BASE_URL = "http://hate.local:8000/api/v1"

def test_instruction_sections():
    """Test the MHT instruction section parsing."""
    
    # Test MHT URL from the registry
    test_url = "http://www.drlz.com.ua/ibp/lz_www.nsf/id/8B1973D53B54886842258BE0004A6892/$file/UA178230101_D929.mht"
    
    print("Testing MHT Instruction Section Parsing")
    print("=" * 50)
    
    # Step 1: Register a new test user
    print("1. Registering test user...")
    register_data = {
        "email": "sections_test@example.com",
        "password": "testpass123",
        "full_name": "Sections Test User"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=register_data)
        if response.status_code == 200:
            print("✓ Registration successful")
        elif response.status_code == 400 and "already registered" in response.text:
            print("✓ User already exists, proceeding with login")
        else:
            print(f"Registration failed: {response.status_code} - {response.text}")
            return
    except Exception as e:
        print(f"Registration error: {e}")
        return
    
    # Step 2: Login and get token
    print("\n2. Logging in...")
    login_data = {
        "email": "sections_test@example.com",
        "password": "testpass123"
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
    
    # Step 3: Test instruction parsing
    print("\n3. Testing instruction parsing...")
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
            
            # Check if HTML content is available
            html_content = parse_data.get('html_content', '')
            if html_content:
                print(f"  HTML content available: {len(html_content)} characters")
                
                # Save the HTML content to a file for inspection
                with open('/tmp/instruction_content.html', 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print("  HTML content saved to /tmp/instruction_content.html")
                
                # Show a snippet of the HTML
                if len(html_content) > 500:
                    snippet = html_content[:500] + "..."
                else:
                    snippet = html_content
                print(f"  HTML snippet: {snippet}")
            else:
                print("  No HTML content available")
                
        else:
            print(f"Parse failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"Parse error: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_instruction_sections()
