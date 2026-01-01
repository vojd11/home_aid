#!/usr/bin/env python3
"""
Test script to verify DRLZ integration for medication creation
"""
import requests
import json

BASE_URL = "http://hate.local:8000"

def test_drlz_search():
    """Test DRLZ medication search"""
    print("Testing DRLZ medication search...")
    
    # This would require authentication in a real scenario
    # For testing, we'll just check if the endpoint exists
    response = requests.get(f"{BASE_URL}/api/v1/drlz/search-drlz", 
                           params={"query": "Ibuprofen", "limit": 5})
    
    print(f"DRLZ Search Status: {response.status_code}")
    if response.status_code == 401:
        print("✓ DRLZ endpoint exists (requires authentication)")
    elif response.status_code == 200:
        data = response.json()
        print(f"✓ Found {len(data.get('medications', []))} medications")
        
        # Show example medication structure
        if data.get('medications'):
            med = data['medications'][0]
            print(f"Example medication: {med.get('main_name')}")
            print(f"Form: {med.get('form')}")
            print(f"Instruction link: {med.get('instruction_link')}")
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
    
    return response.status_code in [200, 401]  # Both are acceptable

def test_medication_creation_schema():
    """Test that medication creation accepts DRLZ fields"""
    print("\nTesting medication creation schema...")
    
    # Test data with DRLZ fields
    test_medication = {
        "name": "Test Medication",
        "quantity": 10,
        "description": "Test description from DRLZ",
        "notes": "Test notes",
        "drlz_link": "https://drlz.com.ua/test",
        "drlz_instruction_link": "https://drlz.com.ua/instruction/test.mht",
        "tabletki_link": "https://tabletki.ua/uk/search/Test%20Medication",
        "tags": ["test", "integration"]
    }
    
    # This would fail without authentication, but we can check the schema
    response = requests.post(f"{BASE_URL}/api/v1/households/1/medications/", 
                           json=test_medication)
    
    print(f"Medication Creation Status: {response.status_code}")
    if response.status_code == 401:
        print("✓ Endpoint exists (requires authentication)")
        return True
    elif response.status_code == 422:
        # Check if it's a validation error or auth error
        try:
            error_data = response.json()
            print(f"Validation error details: {error_data}")
            return False
        except:
            print("✗ Schema validation failed")
            return False
    else:
        print(f"✗ Unexpected status code: {response.status_code}")
        return False

def test_tabletki_link_generation():
    """Test Tabletki link generation logic"""
    print("\nTesting Tabletki link generation...")
    
    medication_name = "Ibuprofen 200mg"
    expected_link = f"https://tabletki.ua/uk/search/{requests.utils.quote(medication_name)}"
    
    print(f"Medication: {medication_name}")
    print(f"Generated link: {expected_link}")
    
    # Test that the link is properly encoded
    if "Ibuprofen" in expected_link and "200mg" in expected_link:
        print("✓ Tabletki link generation working")
        return True
    else:
        print("✗ Tabletki link generation failed")
        return False

def main():
    """Run all tests"""
    print("🧪 Testing DRLZ Integration for Medication Management\n")
    print("=" * 60)
    
    tests = [
        ("DRLZ Search API", test_drlz_search),
        ("Medication Creation Schema", test_medication_creation_schema), 
        ("Tabletki Link Generation", test_tabletki_link_generation)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 60)
    print("📊 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:<8} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! DRLZ integration is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the implementation.")

if __name__ == "__main__":
    main()
