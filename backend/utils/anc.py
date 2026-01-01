#!/usr/bin/env python3
"""
Parser for anc.ua pharmacy website
Searches for medicine using API and extracts prices
"""

import requests
from typing import Dict


class AncParser:
    def __init__(self):
        self.base_url = "https://anc.ua"
        self.api_url = "https://anc.ua/productbrowser/v3/ua/search/query"  # API endpoint
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
            "Accept": "application/json",
            "Accept-Language": "uk,en-US;q=0.7,en;q=0.3",
            "Accept-Encoding": "gzip, deflate",  # Removed br and zstd to avoid compression issues
            "Referer": "https://anc.ua/product/atoksil",
            "Content-Type": "application/json",
            "Origin": "https://anc.ua",
            "Sec-GPC": "1",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "Priority": "u=4",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        })
        # Disable SSL verification if needed (not recommended for production)
        self.session.verify = False

    def search_medicine_api(self, medicine_name: str, city_id: int = 5, debug: bool = False, max_retries: int = 3) -> Dict:
        """
        Search for medicine using the API endpoint (better solution!)
        Returns structured data with prices directly from API
        Includes retry mechanism for handling temporary API issues
        """
        for attempt in range(max_retries):
            try:
                # Create fresh session for each retry to avoid session state issues
                if attempt > 0:
                    self.session = requests.Session()
                    self.session.headers.update({
                        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:142.0) Gecko/20100101 Firefox/142.0",
                        "Accept": "application/json",
                        "Accept-Language": "uk,en-US;q=0.7,en;q=0.3",
                        "Accept-Encoding": "gzip, deflate",  # Removed br and zstd to avoid compression issues
                        "Referer": "https://anc.ua/product/atoksil",
                        "Content-Type": "application/json",
                        "Origin": "https://anc.ua",
                        "Sec-GPC": "1",
                        "Connection": "keep-alive",
                        "Sec-Fetch-Dest": "empty",
                        "Sec-Fetch-Mode": "cors",
                        "Sec-Fetch-Site": "same-origin",
                        "Priority": "u=4",
                        "Pragma": "no-cache",
                        "Cache-Control": "no-cache"
                    })
                    self.session.verify = False
                
                payload = {
                    "city": city_id,  # 5 = Kyiv, can be changed
                    "query": medicine_name.lower(),  # API seems to expect uppercase
                    "includeCategory": False,
                    "pharmacyPrice": True,
                    "source": "webApp"
                }
                
                print(f"Searching via API for: {medicine_name}")
                if attempt > 0:
                    print(f"Retry attempt {attempt + 1}/{max_retries}")
                print(f"API URL: {self.api_url}")
                if debug:
                    print(f"Payload: {payload}")
                
                # Get base page to establish session cookies
                try:
                    self.session.get(self.base_url, timeout=10)
                except:
                    pass  # Continue even if base page fails
                
                response = self.session.post(self.api_url, json=payload, timeout=10)
                if debug:
                    print(f"Response status: {response.status_code}")
                    print(f"Response headers: {dict(response.headers)}")
                    print(f"Response content length: {len(response.content)}")
                    print(f"Response text preview: {response.text[:200]}...")
                response.raise_for_status()
                
                # Check if response is actually empty
                if not response.content or len(response.content.strip()) == 0:
                    error_msg = "Empty response from server"
                    print(f"Error: {error_msg}")
                    if attempt < max_retries - 1:
                        print(f"Retrying in 2 seconds...")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        raise ValueError(error_msg)
                
                # Better JSON parsing with error handling
                try:
                    data = response.json()
                    if debug:
                        print(data)
                except ValueError as json_error:
                    print(f"JSON parsing error: {json_error}")
                    print(f"Response status: {response.status_code}")
                    print(f"Response headers: {dict(response.headers)}")
                    print(f"Response content length: {len(response.content)}")
                    print(f"Response text (first 1000 chars): {response.text[:1000]}")
                    
                    if attempt < max_retries - 1:
                        print(f"Retrying in 2 seconds...")
                        import time
                        time.sleep(2)
                        continue
                    else:
                        raise
                
                # If we get here, the request was successful
                if debug:
                    print(f"API Response status: {response.status_code}")
                    print(f"Response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                
                # Extract products and prices from API response
                result = {
                    'medicine_name': medicine_name,
                    'api_url': self.api_url,
                    'products': [],
                    'prices': {'current_prices': [], 'old_prices': [], 'pharmacy_prices': []},
                    'status': 'failed',
                    'raw_data': data if debug else None
                }
                
                # Parse API response structure - Fixed to match actual API format
                if isinstance(data, dict):
                    # Check for brands first - but don't prioritize them over products with prices
                    brands_data = []
                    if 'brands' in data and isinstance(data['brands'], dict):
                        brands_data = data['brands'].get('items', [])
                        if debug and brands_data:
                            print(f"Found {len(brands_data)} brands")
                    
                    # Always process products first since they contain actual prices
                    products_data = []
                    if 'products' in data and isinstance(data['products'], dict):
                        products_data = data['products'].get('items', [])
                        if debug:
                            total_found = data['products'].get('total', 0)
                            print(f"API found {total_found} total products, {len(products_data)} in this page")
                    
                    if products_data:
                        if debug:
                            print("Processing products data (contains actual prices)")
                        
                        for product in products_data:
                            if isinstance(product, dict):
                                product_info = {
                                    'id': product.get('id'),
                                    'name': product.get('name', ''),
                                    'link': product.get('link', ''),
                                    'prices': []
                                }
                                
                                # Extract prices from product data - using actual API field names
                                price_fields = [
                                    ('price', 'Main Price'),
                                    ('pharmacyMinPrice', 'Min Pharmacy Price'), 
                                    ('pharmacyMaxPrice', 'Max Pharmacy Price'),
                                    ('cityPrice', 'City Price'),
                                    ('deliveryPrice', 'Delivery Price')
                                ]
                                
                                found_prices = []
                                price_values = []  # Store numeric values for comparison
                                
                                for field, description in price_fields:
                                    if field in product and product[field] is not None:
                                        try:
                                            price_val = float(product[field])
                                            if 1 <= price_val <= 50000:  # Reasonable price range
                                                price_values.append((price_val, description, field))
                                                if debug:
                                                    print(f"  Found {description}: {price_val:.2f} грн")
                                        except (ValueError, TypeError):
                                            pass
                                
                                # If we have multiple prices, select only the lowest one
                                if price_values:
                                    # Sort by price value and take the lowest
                                    lowest_price_val, lowest_description, lowest_field = min(price_values, key=lambda x: x[0])
                                    price_str = f"{lowest_price_val:.2f} грн"
                                    found_prices.append(price_str)
                                    product_info['prices'].append(f"{price_str} ({lowest_description})")
                                    
                                    # Add to appropriate category based on the lowest price type
                                    if lowest_field in ['pharmacyMinPrice', 'pharmacyMaxPrice']:
                                        result['prices']['pharmacy_prices'].append(price_str)
                                    else:
                                        result['prices']['current_prices'].append(price_str)
                                        
                                    if debug:
                                        print(f"  Selected lowest price: {price_str} ({lowest_description})")
                                
                                if product_info['name'] or found_prices:
                                    result['products'].append(product_info)
                                    if debug:
                                        print(f"Added product: {product_info['name'][:50]}... with {len(found_prices)} prices")
                    
                    # If products gave us results, use those
                    if result['products']:
                        # Deduplicate prices and keep only the lowest in each category
                        for price_type in result['prices']:
                            if result['prices'][price_type]:
                                # Remove duplicates
                                unique_prices = list(set(result['prices'][price_type]))
                                # Sort prices numerically and keep only the lowest
                                try:
                                    unique_prices.sort(key=lambda x: float(x.split()[0]))
                                    result['prices'][price_type] = [unique_prices[0]]  # Keep only the lowest
                                except:
                                    result['prices'][price_type] = unique_prices[:1]  # Keep first if sorting fails
                        
                        result['status'] = 'success'
                        total_prices = sum(len(prices) for prices in result['prices'].values())
                        print(f"✅ API search successful: found {len(result['products'])} products with {total_prices} total prices")
                        return result
                    
                    # Fallback: try brands if no products or no prices from products
                    if brands_data and not any(result['prices'].values()):
                        if debug:
                            print("Fallback: trying brands data since no prices found in products")
                        
                        for brand in brands_data:
                            if isinstance(brand, dict):
                                brand_info = {
                                    'id': brand.get('id'),
                                    'name': brand.get('name', ''),
                                    'link': brand.get('link', ''),
                                    'prices': [],
                                    'type': 'brand'
                                }
                                
                                # For brands, try different URL formats
                                if brand_info['link']:
                                    # Try multiple URL formats
                                    possible_urls = [
                                        f"{self.base_url}/brand/{brand_info['link']}",
                                        f"{self.base_url}/brands/{brand_info['link']}",
                                        f"{self.base_url}/producer/{brand_info['link']}",
                                        f"{self.base_url}/{brand_info['link']}"
                                    ]
                                    
                                    if brand_info['link'].startswith('/'):
                                        possible_urls.insert(0, self.base_url + brand_info['link'])
                                    elif brand_info['link'].startswith('http'):
                                        possible_urls.insert(0, brand_info['link'])
                                    
                                    brand_prices = []
                                    for url in possible_urls:
                                        brand_info['link'] = url
                                        brand_prices = self._fetch_brand_prices(url, debug=debug)
                                        if brand_prices:
                                            break
                                    
                                    if brand_prices:
                                        brand_info['prices'] = brand_prices
                                        # Add to result prices
                                        result['prices']['current_prices'].extend(brand_prices)
                                        if debug:
                                            print(f"Added {len(brand_prices)} prices from brand: {brand_info['name']}")
                                    
                                    result['products'].append(brand_info)
                                    if debug:
                                        print(f"Added brand: {brand_info['name']} - {brand_info['link']}")
                                else:
                                    # Even without link, add the brand for information
                                    result['products'].append(brand_info)
                                    if debug:
                                        print(f"Added brand (no link): {brand_info['name']}")
                        
                        # Deduplicate prices from brands
                        for price_type in result['prices']:
                            if result['prices'][price_type]:
                                unique_prices = list(set(result['prices'][price_type]))
                                try:
                                    unique_prices.sort(key=lambda x: float(x.split()[0]))
                                    result['prices'][price_type] = [unique_prices[0]]
                                except:
                                    result['prices'][price_type] = unique_prices[:1]
                        
                        if result['products']:
                            result['status'] = 'success'
                            total_prices = sum(len(prices) for prices in result['prices'].values())
                            print(f"✅ Brand fallback successful: found {len(result['products'])} brand(s) with {total_prices} total prices")
                            return result
                    
                    if result['products'] or any(result['prices'].values()):
                        result['status'] = 'success'
                        total_prices = sum(len(prices) for prices in result['prices'].values())
                        print(f"✅ API search successful: found {len(result['products'])} products with {total_prices} total prices")
                        return result
                    else:
                        result['status'] = 'not_found'
                        print(f"⚠️  API search returned no results for: {medicine_name}")
                        return result
                else:
                    result['status'] = 'invalid_response'
                    print(f"❌ API returned invalid response format")
                    return result
                
            except requests.RequestException as e:
                print(f"API request error: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in 2 seconds...")
                    import time
                    time.sleep(2)
                    continue
                else:
                    return {
                        'medicine_name': medicine_name,
                        'api_url': self.api_url,
                        'products': [],
                        'prices': {'current_prices': [], 'old_prices': [], 'pharmacy_prices': []},
                        'status': 'error',
                        'error': str(e)
                    }
            except Exception as e:
                print(f"Unexpected API error: {e}")
                if attempt < max_retries - 1:
                    print(f"Retrying in 2 seconds...")
                    import time
                    time.sleep(2)
                    continue
                else:
                    return {
                        'medicine_name': medicine_name,
                        'api_url': self.api_url,
                        'products': [],
                        'prices': {'current_prices': [], 'old_prices': [], 'pharmacy_prices': []},
                        'status': 'error',
                        'error': str(e)
                    }

    def _fetch_brand_prices(self, brand_url: str, debug: bool = False) -> list:
        """
        Fetch prices from a brand page by scraping the HTML content
        Returns a list of price strings found on the brand page
        """
        try:
            if debug:
                print(f"Fetching prices from brand page: {brand_url}")
            
            response = self.session.get(brand_url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML to find prices
            import re
            html_content = response.text
            
            # Look for price patterns in the HTML
            # Common patterns for Ukrainian prices: "123.45 грн", "123,45 грн", "123 грн"
            price_patterns = [
                r'(\d+(?:[,\.]\d{1,2})?\s*грн)',  # Standard price format
                r'"price"[^>]*>([^<]*\d+[^<]*грн[^<]*)<',  # Price in HTML attributes
                r'class="[^"]*price[^"]*"[^>]*>([^<]*\d+[^<]*грн[^<]*)<',  # Price in CSS classes
                r'data-price="([^"]*)"',  # Price in data attributes
                r'(\d+(?:[,\.]\d{1,2})?)(?:\s*<[^>]*>)?\s*грн',  # Price with possible HTML tags
            ]
            
            found_prices = []
            for pattern in price_patterns:
                matches = re.findall(pattern, html_content, re.IGNORECASE)
                for match in matches:
                    # Clean up the price string
                    price_str = re.sub(r'<[^>]+>', '', match).strip()  # Remove HTML tags
                    price_str = re.sub(r'\s+', ' ', price_str)  # Normalize whitespace
                    
                    # Extract numeric value for validation
                    price_match = re.search(r'(\d+(?:[,\.]\d{1,2})?)', price_str)
                    if price_match:
                        try:
                            price_val = float(price_match.group(1).replace(',', '.'))
                            if 1 <= price_val <= 50000:  # Reasonable price range
                                formatted_price = f"{price_val:.2f} грн"
                                if formatted_price not in found_prices:
                                    found_prices.append(formatted_price)
                                    if debug:
                                        print(f"Found price: {formatted_price}")
                        except ValueError:
                            continue
            
            # Also try to find JSON data embedded in the page (common for modern sites)
            json_patterns = [
                r'"price":\s*(\d+(?:\.\d{1,2})?)',
                r'"pharmacyMinPrice":\s*(\d+(?:\.\d{1,2})?)',
                r'"pharmacyMaxPrice":\s*(\d+(?:\.\d{1,2})?)',
                r'"cityPrice":\s*(\d+(?:\.\d{1,2})?)',
            ]
            
            for pattern in json_patterns:
                matches = re.findall(pattern, html_content)
                for match in matches:
                    try:
                        price_val = float(match)
                        if 1 <= price_val <= 50000:
                            formatted_price = f"{price_val:.2f} грн"
                            if formatted_price not in found_prices:
                                found_prices.append(formatted_price)
                                if debug:
                                    print(f"Found JSON price: {formatted_price}")
                    except ValueError:
                        continue
            
            # Remove duplicates and sort by price
            if found_prices:
                # Convert to set to remove duplicates, then sort
                unique_prices = list(set(found_prices))
                try:
                    unique_prices.sort(key=lambda x: float(x.split()[0]))
                except:
                    pass  # Keep original order if sorting fails
                
                if debug:
                    print(f"Extracted {len(unique_prices)} unique prices from brand page")
                
                return unique_prices
            else:
                if debug:
                    print("No prices found on brand page")
                return []
                
        except Exception as e:
            if debug:
                print(f"Error fetching brand prices: {e}")
            return []

    def parse_medicine(self, medicine_name: str, debug: bool = False) -> Dict:
        """
        Complete parsing workflow using API endpoint only
        """
        result = {
            'medicine_name': medicine_name,
            'api_url': self.api_url,
            'prices': {'current_prices': [], 'old_prices': [], 'pharmacy_prices': []},
            'status': 'failed',
            'method_used': 'api'
        }
        
        # Use API method only
        print("🚀 Using API method")
        api_result = self.search_medicine_api(medicine_name, debug=debug)
        
        if api_result['status'] == 'success':
            result.update(api_result)
            return result
        else:
            print(f"❌ API method failed for: {medicine_name}")
            result['status'] = api_result['status']
            result['error'] = api_result.get('error', 'API search failed')
            return result


def test_api_access():
    """
    Test basic access to anc.ua API
    """
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    parser = AncParser()
    
    print("Testing API access...")
    
    try:
        # Test API endpoint with a simple query
        test_payload = {
            "city": 5,
            "query": "TEST",
            "includeCategory": False,
            "pharmacyPrice": True,
            "source": "webApp"
        }
        
        response = parser.session.post(parser.api_url, json=test_payload, timeout=10)
        print(f"API status: {response.status_code}")
        print(f"Content type: {response.headers.get('content-type', 'Unknown')}")
        
        if response.status_code == 200:
            try:
                data = response.json()
                print(f"API response keys: {list(data.keys()) if isinstance(data, dict) else 'Not a dict'}")
                print("API appears to be accessible and working")
                return True
            except Exception as e:
                print(f"API response parsing error: {e}")
                return False
        else:
            print(f"API returned error status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"API access error: {e}")
        return False


def main():
    """
    Example usage of the ANC parser
    """
    import warnings
    warnings.filterwarnings('ignore', message='Unverified HTTPS request')
    
    # First test API access
    if not test_api_access():
        print("API access test failed. Check your connection...")
    
    print("\n" + "="*50)
    
    parser = AncParser()
    
    # Test with the provided example
    medicine_name = "атоксіл"
    
    print(f"Parsing medicine: {medicine_name}")
    print("=" * 50)
    
    # First run with debug to understand the site structure
    result = parser.search_medicine_api('атоксіл', debug=False)
    
    print("\nResults:")
    print(f"Medicine: {result['medicine_name']}")
    print(f"Status: {result['status']}")
    print(f"API URL: {result['api_url']}")
    
    if result.get('products'):
        print(f"\nFound {len(result['products'])} product(s):")
        for i, product in enumerate(result['products'], 1):
            print(f"  {i}. {product.get('name', 'Unknown')}")
            if product.get('link'):
                print(f"     Link: {product['link']}")
    
    if result['prices']:
        print("\nPrices found:")
        for price_type, prices in result['prices'].items():
            if prices:
                print(f"{price_type.replace('_', ' ').title()}: {', '.join(prices)}")
    
    return result


if __name__ == "__main__":
    main()
