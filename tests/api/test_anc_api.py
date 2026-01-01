#!/usr/bin/env python3
"""
Test the complete ANC integration flow via API
"""

import requests
import json


def test_api_health():
    """Test basic API health"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        print(f"Health check: {response.status_code}")
        if response.status_code == 200:
            print(f"Health response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def test_store_prices():
    """Test store prices endpoint with ANC integration"""
    
    # Test household ID 1, medication ID 1 with атоксіл
    household_id = 1
    medication_id = 1
    medication_name = "атоксіл"
    
    url = f"http://localhost:8000/api/v1/households/{household_id}/medications/{medication_id}/store-prices"
    params = {"name": medication_name}
    
    print(f"Testing store prices for: {medication_name}")
    print(f"URL: {url}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, timeout=30)
        print(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print("Store prices response:")
            print(json.dumps(data, indent=2, ensure_ascii=False))
            
            # Check if ANC data is included
            if 'stores' in data:
                anc_store = None
                for store in data['stores']:
                    if store.get('store_name') == 'ANC':
                        anc_store = store
                        break
                
                if anc_store:
                    print(f"\n🎯 ANC Integration Test Results:")
                    print(f"Status: {anc_store.get('status')}")
                    print(f"Price: {anc_store.get('price')} {anc_store.get('currency')}")
                    print(f"Link: {anc_store.get('link')}")
                    
                    if anc_store.get('status') == 'success' and anc_store.get('price'):
                        print("✅ ANC integration working correctly!")
                        return True
                    else:
                        print("⚠️ ANC integration returned no price")
                        return False
                else:
                    print("❌ ANC store not found in response")
                    return False
            else:
                print("❌ No stores in response")
                return False
        elif response.status_code == 404:
            print("❌ Endpoint not found - may need authentication or household doesn't exist")
            return False
        elif response.status_code == 401:
            print("❌ Authentication required")
            return False
        else:
            print(f"❌ API error: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False


def main():
    print("Testing complete ANC integration...")
    print("="*50)
    
    # Test API health first
    if not test_api_health():
        print("❌ API health check failed")
        return
    
    print("\n" + "="*50)
    
    # Test store prices with ANC
    if test_store_prices():
        print("\n🎉 ANC integration test passed!")
    else:
        print("\n❌ ANC integration test failed!")


if __name__ == "__main__":
    main()
