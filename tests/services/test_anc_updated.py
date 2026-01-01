#!/usr/bin/env python3
"""
Test script for updated ANC integration
"""

import sys
import os
import asyncio

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from app.services.store_prices import StorePriceService


async def test_anc_integration():
    """Test the updated ANC integration"""
    print("Testing updated ANC integration...")
    
    service = StorePriceService()
    
    # Test with various medications
    test_medicines = [
        "атоксіл",
        "парацетамол", 
        "аспірин",
        "но-шпа"
    ]
    
    for medicine in test_medicines:
        print(f"\n{'='*50}")
        print(f"Testing: {medicine}")
        print('='*50)
        
        try:
            result = await service.get_anc_price(medicine)
            
            print(f"Store: {result.store_name}")
            print(f"Status: {result.status}")
            print(f"Price: {result.price} {result.currency}" if result.price else "Price: Not found")
            print(f"Link: {result.link}" if result.link else "Link: Not available")
            
        except Exception as e:
            print(f"Error testing {medicine}: {e}")
    
    print(f"\n{'='*50}")
    print("Testing complete store price fetch...")
    print('='*50)
    
    try:
        # Test getting all store prices
        all_prices = await service.get_all_store_prices(1, "атоксіл")
        
        print(f"Medication: {all_prices.medication_name}")
        print(f"Total stores: {all_prices.total_stores}")
        print(f"Last updated: {all_prices.last_updated}")
        
        for store in all_prices.stores:
            print(f"\n{store.store_name}:")
            print(f"  Status: {store.status}")
            print(f"  Price: {store.price} {store.currency}" if store.price else "  Price: Not found")
            print(f"  Link: {store.link}" if store.link else "  Link: Not available")
            
    except Exception as e:
        print(f"Error testing all store prices: {e}")


if __name__ == "__main__":
    asyncio.run(test_anc_integration())
