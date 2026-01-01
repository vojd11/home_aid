#!/usr/bin/env python3
"""
Verification script for Apteka.net.ua integration with Home Aid Kit Manager
"""
import asyncio
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

async def test_apteka_integration():
    """Test the Apteka.net.ua integration in the store prices service"""
    print("🧪 Testing Apteka.net.ua Integration")
    print("=" * 50)
    
    from app.services.store_prices import StorePriceService
    
    service = StorePriceService()
    
    # Test medications
    test_medications = ["парацетамол", "ібупрофен", "атоксіл"]
    
    for medication_name in test_medications:
        print(f"\n📋 Testing: {medication_name}")
        print("-" * 30)
        
        try:
            # Test individual Apteka.net.ua price
            apteka_result = await service.get_apteka_price(medication_name)
            print(f"🏪 Apteka.net.ua Results:")
            print(f"   Status: {apteka_result.status}")
            print(f"   Price: {apteka_result.price} {apteka_result.currency}" if apteka_result.price else "   Price: Not found")
            print(f"   Link: {apteka_result.link}")
            
            # Test all stores together
            all_stores_result = await service.get_all_store_prices(1, medication_name)
            print(f"\n🏬 All Stores Summary:")
            print(f"   Total stores: {all_stores_result.total_stores}")
            
            apteka_store = None
            for store in all_stores_result.stores:
                if store.store_name == "Apteka.net.ua":
                    apteka_store = store
                    break
            
            if apteka_store:
                print(f"   ✅ Apteka.net.ua included: {apteka_store.status}")
            else:
                print(f"   ❌ Apteka.net.ua NOT found in results")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📊 Store Configuration:")
    print(f"   Configured stores: {len(service.stores)}")
    for key, config in service.stores.items():
        print(f"   - {config['name']}: {config['base_url']}")
    
    print("\n✅ Integration test complete!")


if __name__ == "__main__":
    asyncio.run(test_apteka_integration())
