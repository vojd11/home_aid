#!/usr/bin/env python3
"""
Test script for store prices functionality
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append('/home/vojd/projects/home_aid_sonnet/backend')

async def test_store_prices():
    """Test the store price service"""
    from app.services.store_prices import StorePriceService
    
    service = StorePriceService()
    
    # Test with a medication name
    medication_name = "ібупрофен"
    medication_id = 1
    
    print(f"Testing store prices for: {medication_name}")
    print("-" * 50)
    
    try:
        result = await service.get_all_store_prices(medication_id, medication_name)
        
        print(f"Medication ID: {result.medication_id}")
        print(f"Medication Name: {result.medication_name}")
        print(f"Total Stores: {result.total_stores}")
        print(f"Last Updated: {result.last_updated}")
        print("\nStore Prices:")
        
        for store in result.stores:
            print(f"  {store.store_name}:")
            print(f"    Price: {store.price} {store.currency}" if store.price else "    Price: Not found")
            print(f"    Link: {store.link}" if store.link else "    Link: None")
            print(f"    Status: {store.status}")
            print()
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_store_prices())
