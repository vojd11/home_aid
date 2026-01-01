#!/usr/bin/env python3
"""
911.ua Pharmacy Parser
=====================

A comprehensive parser for scraping product prices from 911.ua (apteka911.ua), 
a Ukrainian pharmacy website.

Features:
- Search for medications by name using API endpoint
- Extract lowest prices when multiple prices available
- Get link from first matching item (where analizeStr matches requested name)
- Support for multiple product searches
- Command-line interface
- Interactive search mode

Usage:
    python 911.py                         # Run default examples
    python 911.py "Product Name"          # Search for specific product
    python 911.py --interactive           # Interactive search mode

Example:
    python 911.py "АТОКСІЛ"
    Output: 
    АТОКСІЛ: 99.60 грн
    Link: https://apteka911.ua/drugs/atoksil-d323/atoksil_tn2005

API Endpoint:
    POST https://apteka911.ua/ua/shop/search
    Body: {
        "q": "атоксіл",
        "limit": 9,
        "timestamp": 1756638648901,
        "hint": 1,
        "indexes": 1,
        "products": 1
    }

Requirements:
    - requests

Author: Parser for 911.ua
Date: 2025
"""

import requests
import json
import time
import urllib.parse
from typing import Dict, List, Optional, Union


class Apteka911Parser:
    def __init__(self):
        self.base_url = "https://apteka911.ua"
        self.search_api_url = "https://apteka911.ua/ua/shop/search"
        self.session = requests.Session()
        
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'uk-UA,uk;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Origin': 'https://apteka911.ua',
            'Referer': 'https://apteka911.ua/',
            'X-Requested-With': 'XMLHttpRequest',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        })

    def search_product_api(self, product_name: str, limit: int = 9, debug: bool = False) -> Dict:
        """
        Search for products using the API endpoint
        
        Args:
            product_name: Name of the product to search for
            limit: Maximum number of results to return (default: 9)
            debug: Enable debug output
            
        Returns:
            Dictionary containing search results and prices
        """
        try:
            # Generate timestamp (current time in milliseconds)
            timestamp = int(time.time() * 1000)
            
            # Prepare form data as per the API specification
            form_data = {
                'q': product_name,
                'limit': str(limit),
                'timestamp': str(timestamp),
                'hint': '1',
                'indexes': '1',
                'products': '1'
            }
            
            if debug:
                print(f"API URL: {self.search_api_url}")
                print(f"Form data: {form_data}")
            
            print(f"Searching via API for: {product_name}")
            
            # Make POST request with form data
            response = self.session.post(
                self.search_api_url, 
                data=form_data,
                timeout=10
            )
            response.raise_for_status()
            
            if debug:
                print(f"Response status: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Response content type: {response.headers.get('content-type', 'unknown')}")
            
            # Parse JSON response
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                if debug:
                    print(f"JSON decode error: {e}")
                    print(f"Response text (first 500 chars): {response.text[:500]}")
                return {
                    'product_name': product_name,
                    'products': [],
                    'prices': {'current_prices': [], 'old_prices': [], 'pharmacy_prices': []},
                    'status': 'json_error',
                    'error': str(e)
                }
            
            result = {
                'product_name': product_name,
                'api_url': self.search_api_url,
                'products': [],
                'prices': {'current_prices': [], 'old_prices': [], 'pharmacy_prices': []},
                'status': 'failed',
                'raw_data': data  # Always store raw data to access analizeStr
            }
            
            if debug:
                print(f"API Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                if isinstance(data, dict):
                    print(f"Response structure: {json.dumps(data, indent=2, ensure_ascii=False)[:1000]}...")
            
            # Parse API response structure specific to 911.ua
            if isinstance(data, dict) and data.get('result') == 'success':
                # 911.ua API structure: data.data.results contains the products
                products_data = []
                
                if 'data' in data and isinstance(data['data'], dict):
                    if 'results' in data['data'] and isinstance(data['data']['results'], list):
                        products_data = data['data']['results']
                        if debug:
                            print(f"Found products in 'data.results': {len(products_data)} items")
                
                # Fallback: try other common patterns
                if not products_data:
                    possible_product_keys = ['products', 'items', 'results', 'medicines', 'goods']
                    
                    for key in possible_product_keys:
                        if key in data:
                            if isinstance(data[key], list):
                                products_data = data[key]
                                if debug:
                                    print(f"Found products in '{key}': {len(products_data)} items")
                                break
                            elif isinstance(data[key], dict):
                                # Check for nested structure
                                for sub_key in ['items', 'list', 'data', 'results']:
                                    if sub_key in data[key] and isinstance(data[key][sub_key], list):
                                        products_data = data[key][sub_key]
                                        if debug:
                                            print(f"Found products in '{key}.{sub_key}': {len(products_data)} items")
                                        break
                                if products_data:
                                    break
                
                if products_data:
                    for product in products_data:
                        if isinstance(product, dict):
                            # Extract price and product information from 911.ua API format
                            product_info = {
                                'id': product.get('productID'),
                                'name': product.get('name', ''),
                                'brand': product.get('brand', ''),
                                'link': product.get('alias', ''),
                                'prices': [],
                                'raw_product': product if debug else None
                            }
                            
                            # Make full URL from alias
                            if product_info['link'] and not product_info['link'].startswith('http'):
                                if product_info['link'].startswith('/'):
                                    product_info['link'] = self.base_url + product_info['link']
                                else:
                                    product_info['link'] = self.base_url + '/' + product_info['link']
                            
                            # Extract price from 911.ua specific fields
                            found_prices = []
                            
                            # Main price field in 911.ua API
                            if 'productPrice' in product and product['productPrice'] is not None:
                                try:
                                    price_val = float(product['productPrice'])
                                    if 1 <= price_val <= 50000:  # Reasonable price range
                                        price_str = f"{price_val:.2f} грн"
                                        found_prices.append(price_str)
                                        product_info['prices'].append(f"{price_str} (Current Price)")
                                        result['prices']['current_prices'].append(price_str)
                                        
                                        if debug:
                                            print(f"  Found productPrice: {price_str}")
                                except (ValueError, TypeError):
                                    pass
                            
                            # Check for other potential price fields
                            other_price_fields = [
                                ('price', 'Price'),
                                ('cost', 'Cost'),
                                ('min_price', 'Min Price'),
                                ('max_price', 'Max Price'),
                                ('productMinPrice', 'Min Price'),
                                ('productMaxPrice', 'Max Price'),
                                ('productOldPrice', 'Old Price'),
                                ('discountPrice', 'Discount Price')
                            ]
                            
                            for field, description in other_price_fields:
                                if field in product and product[field] is not None:
                                    try:
                                        price_val = float(product[field])
                                        if 1 <= price_val <= 50000:  # Reasonable price range
                                            price_str = f"{price_val:.2f} грн"
                                            if price_str not in found_prices:  # Avoid duplicates
                                                found_prices.append(price_str)
                                                product_info['prices'].append(f"{price_str} ({description})")
                                                
                                                # Categorize prices
                                                if 'old' in field.lower() or 'discount' in field.lower():
                                                    result['prices']['old_prices'].append(price_str)
                                                elif 'min' in field.lower() or 'max' in field.lower():
                                                    result['prices']['pharmacy_prices'].append(price_str)
                                                else:
                                                    result['prices']['current_prices'].append(price_str)
                                                    
                                                if debug:
                                                    print(f"  Found {description}: {price_str}")
                                    except (ValueError, TypeError):
                                        pass
                            
                            # Store product if it has a name or prices
                            if product_info['name'] or found_prices:
                                result['products'].append(product_info)
                                if debug:
                                    print(f"Added product: {product_info['name'][:50]}... with {len(found_prices)} prices")
                
                # Deduplicate and sort prices
                for price_type in result['prices']:
                    result['prices'][price_type] = list(set(result['prices'][price_type]))
                    # Sort prices numerically
                    try:
                        result['prices'][price_type].sort(key=lambda x: float(x.split()[0]))
                    except:
                        pass
                
                if result['products'] or any(result['prices'].values()):
                    result['status'] = 'success'
                    total_prices = sum(len(prices) for prices in result['prices'].values())
                    print(f"✅ API search successful: found {len(result['products'])} products with {total_prices} total prices")
                else:
                    result['status'] = 'not_found'
                    print(f"⚠️  API search returned no results for: {product_name}")
            else:
                result['status'] = 'invalid_response'
                print(f"❌ API returned invalid response format")
            
            return result
            
        except requests.RequestException as e:
            print(f"API request error: {e}")
            return {
                'product_name': product_name,
                'api_url': self.search_api_url,
                'products': [],
                'prices': {'current_prices': [], 'old_prices': [], 'pharmacy_prices': []},
                'status': 'error',
                'error': str(e)
            }
        except Exception as e:
            print(f"Unexpected API error: {e}")
            return {
                'product_name': product_name,
                'api_url': self.search_api_url,
                'products': [],
                'prices': {'current_prices': [], 'old_prices': [], 'pharmacy_prices': []},
                'status': 'error',
                'error': str(e)
            }

    def get_first_price(self, product_name: str) -> Optional[float]:
        """
        Get the lowest price found for a product
        
        Args:
            product_name: Name of the product to search for
            
        Returns:
            Lowest price found as float, or None if not found
        """
        result = self.search_product_api(product_name)
        
        if result['status'] == 'success':
            all_prices = []
            
            # Collect all prices from all categories
            for price_category in ['current_prices', 'pharmacy_prices', 'old_prices']:
                for price_str in result['prices'][price_category]:
                    try:
                        price_val = float(price_str.split()[0])
                        all_prices.append(price_val)
                    except (ValueError, IndexError):
                        continue
            
            # Return the lowest price if any prices found
            if all_prices:
                return min(all_prices)
        
        return None

    def get_price_and_link(self, product_name: str) -> Dict[str, Optional[Union[float, str]]]:
        """
        Get the lowest price and link from the first item where analizeStr matches requested name
        
        Args:
            product_name: Name of the product to search for
            
        Returns:
            Dictionary with 'price' (lowest found) and 'link' (from first matching item)
        """
        result = self.search_product_api(product_name)
        
        response = {
            'price': None,
            'link': None,
            'matching_item_name': None
        }
        
        if result['status'] == 'success':
            # First, find the link from the first item where analizeStr matches the requested name
            if 'raw_data' in result and result['raw_data'] and isinstance(result['raw_data'], dict):
                if 'data' in result['raw_data'] and 'results' in result['raw_data']['data']:
                    for item in result['raw_data']['data']['results']:
                        if isinstance(item, dict) and 'analizeStr' in item:
                            # Check if analizeStr matches the requested name (case insensitive)
                            if item['analizeStr'].lower().strip() == product_name.lower().strip():
                                response['matching_item_name'] = item['analizeStr']
                                if 'alias' in item:
                                    alias = item['alias']
                                    if alias and not alias.startswith('http'):
                                        if alias.startswith('/'):
                                            response['link'] = self.base_url + alias
                                        else:
                                            response['link'] = self.base_url + '/' + alias
                                    else:
                                        response['link'] = alias
                                break
            
            # Then, get the lowest price from all available prices
            all_prices = []
            for price_category in ['current_prices', 'pharmacy_prices', 'old_prices']:
                for price_str in result['prices'][price_category]:
                    try:
                        price_val = float(price_str.split()[0])
                        all_prices.append(price_val)
                    except (ValueError, IndexError):
                        continue
            
            if all_prices:
                response['price'] = min(all_prices)
        
        return response

    def get_product_info(self, product_name: str) -> Optional[List[Dict]]:
        """
        Get comprehensive product information including prices
        
        Args:
            product_name: Name of the product to search for
            
        Returns:
            List of product dictionaries with detailed information
        """
        result = self.search_product_api(product_name)
        
        if result['status'] == 'success' and result['products']:
            return result['products']
        
        return None

    def search_multiple_products(self, product_names: List[str]) -> Dict[str, Optional[float]]:
        """
        Search for multiple products and return their prices
        
        Args:
            product_names: List of product names to search for
            
        Returns:
            Dictionary mapping product names to their first found price
        """
        results = {}
        for product_name in product_names:
            print(f"Searching for: {product_name}")
            price = self.get_first_price(product_name)
            results[product_name] = price
            time.sleep(1)  # Be respectful to the server
        return results

    def test_api_connection(self) -> bool:
        """
        Test if the API is accessible
        
        Returns:
            True if API is accessible, False otherwise
        """
        try:
            # Test with a simple query
            result = self.search_product_api("тест", limit=1)
            return result['status'] in ['success', 'not_found']  # Both are valid responses
        except Exception as e:
            print(f"API connection test failed: {e}")
            return False


def main():
    """
    Example usage of the parser
    """
    parser = Apteka911Parser()
    
    # Test API connection first
    print("Testing API connection...")
    if parser.test_api_connection():
        print("✅ API connection successful")
    else:
        print("❌ API connection failed")
        return
    
    print("\n" + "="*60)
    
    # Test with the example from the request (атоксіл)
    product_name = "атоксіл"
    
    print(f"Searching for: {product_name}")
    print("-" * 50)
    
    # Get first price
    first_price = parser.get_first_price(product_name)
    if first_price:
        print(f"Lowest price found: {first_price} грн")
    else:
        print("No price found")
    
    # Get price and link from matching item
    price_and_link = parser.get_price_and_link(product_name)
    if price_and_link['price']:
        print(f"Lowest price: {price_and_link['price']} грн")
        if price_and_link['link']:
            print(f"Link from matching item '{price_and_link['matching_item_name']}': {price_and_link['link']}")
        else:
            print("No matching item link found")
    else:
        print("No price found")
    
    print("-" * 50)
    
    # Get detailed product information
    products = parser.get_product_info(product_name)
    if products:
        print("Product information:")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.get('name', 'Unknown')}")
            if product['prices']:
                for price in product['prices']:
                    print(f"   {price}")
            if product.get('link'):
                print(f"   Link: {product['link']}")
            print()
    else:
        print("No products found")

    # Test with multiple products
    print("\n" + "="*60)
    print("Testing multiple products:")
    print("="*60)
    
    test_products = ["ібупрофен", "парацетамол", "аспірин"]
    results = parser.search_multiple_products(test_products)
    
    for product, price in results.items():
        if price:
            print(f"{product}: {price} грн")
        else:
            print(f"{product}: No price found")


def interactive_search():
    """
    Interactive search function
    """
    parser = Apteka911Parser()
    
    print("911.ua Pharmacy Price Parser")
    print("Enter 'quit' to exit")
    print("-" * 30)
    
    while True:
        product_name = input("\nEnter product name to search: ").strip()
        
        if product_name.lower() in ['quit', 'exit', 'q']:
            break
            
        if not product_name:
            continue
            
        print(f"\nSearching for: {product_name}")
        result = parser.get_price_and_link(product_name)
        
        if result['price']:
            print(f"Lowest price: {result['price']} грн")
            if result['link']:
                print(f"Link: {result['link']}")
        else:
            print("No price found")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_search()
        else:
            # Search for command line argument
            parser = Apteka911Parser()
            product_name = " ".join(sys.argv[1:])
            
            # Use the new method to get both price and link
            result = parser.get_price_and_link(product_name)
            
            if result['price']:
                print(f"{product_name}: {result['price']} грн")
                if result['link']:
                    print(f"Link: {result['link']}")
            else:
                print(f"{product_name}: No price found")
    else:
        main()
