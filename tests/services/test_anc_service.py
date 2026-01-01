#!/usr/bin/env python3
"""
Direct test for ANC integration with store price service simulation
"""

import sys
import os
from urllib.parse import quote

# Add backend utils to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'utils'))

# Simulate StorePrice response
class StorePrice:
    def __init__(self, store_name, price, currency, link, status):
        self.store_name = store_name
        self.price = price
        self.currency = currency
        self.link = link
        self.status = status

def get_anc_price(medication_name: str) -> StorePrice:
    """Get price from ANC using the updated scraper"""
    try:
        import anc
        
        parser = anc.AncParser()
        result = parser.parse_medicine(medication_name, debug=False)
        
        price = None
        link = None
        
        if result['status'] == 'success':
            # Extract lowest price from all categories
            all_prices = []
            for price_category in ['current_prices', 'pharmacy_prices', 'old_prices']:
                for price_str in result['prices'][price_category]:
                    try:
                        price_val = float(price_str.split()[0])
                        all_prices.append(price_val)
                    except (ValueError, IndexError):
                        continue
            
            if all_prices:
                price = min(all_prices)
            
            # Generate search link since scraper will handle search dynamically
            encoded_name = quote(medication_name)
            link = f"https://anc.ua/search?q={encoded_name}"
            
            # Use link from first product if available and valid
            if result.get('products') and result['products'][0].get('link'):
                product_link = result['products'][0]['link']
                if product_link.startswith('http'):
                    link = product_link
                elif product_link.startswith('/'):
                    link = f"https://anc.ua{product_link}"
                else:
                    # Relative product link
                    link = f"https://anc.ua/product/{product_link}"
        
        return StorePrice(
            store_name="ANC",
            price=price,
            currency="грн",
            link=link,
            status="success" if price else "not_found"
        )
    except Exception as e:
        print(f"Error: {e}")
        return StorePrice(
            store_name="ANC",
            price=None,
            currency="грн",
            link=None,
            status="error"
        )


def test_anc_integration():
    """Test the updated ANC integration"""
    print("Testing updated ANC integration with store price service simulation...")
    
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
        
        result = get_anc_price(medicine)
        
        print(f"Store: {result.store_name}")
        print(f"Status: {result.status}")
        print(f"Price: {result.price} {result.currency}" if result.price else "Price: Not found")
        print(f"Link: {result.link}" if result.link else "Link: Not available")


if __name__ == "__main__":
    test_anc_integration()
