"""
Apteka.net.ua Scraper

This scraper extracts medicine information and prices from apteka.net.ua

Features:
- Search for medicines by name
- Extract medicine IDs, names, producers, and URLs
- Get current prices from multiple pharmacies
- Find the lowest available price
- Generate search result links
- Handle discounts and stock information

Usage:
    from apteka import scrape_medicine_price, AptekaScraper
    
    # Simple usage
    result = scrape_medicine_price("атоксіл")
    print(f"Lowest price: {result['lowest_price']} {result['currency']}")
    print(f"Search link: {result['search_link']}")
    
    # Advanced usage
    scraper = AptekaScraper()
    detailed_result = scraper.scrape_medicine("атоксіл")
    # Access detailed price information, all medicines, etc.

API Endpoints used:
- Search: https://apteka.net.ua/sr-search
- Prices: https://apteka.net.ua/api/rest_ws_price
"""

import requests
import json
import urllib.parse
from typing import Dict, List, Optional, Tuple


class AptekaScraper:
    def __init__(self):
        self.base_url = "https://apteka.net.ua"
        self.search_url = f"{self.base_url}/sr-search"
        self.price_api_url = f"{self.base_url}/api/rest_ws_price"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def search_medicine_ids(self, medicine_name: str, city_id: str = "46") -> List[Dict]:
        """
        Search for medicine and extract IDs from the response
        
        Args:
            medicine_name: Name of the medicine to search for
            city_id: City ID (default is 46)
            
        Returns:
            List of medicine data with IDs
        """
        params = {
            'l': 'uk',
            't': 'goods',
            'q': medicine_name,
            'cid': city_id,
            'dq': '',
            'fid': ''
        }
        
        try:
            response = self.session.get(self.search_url, params=params)
            response.raise_for_status()
            
            # Try to parse JSON response
            data = response.json()
            
            # Extract medicine data from response
            medicines = []
            if 'response' in data and 'docs' in data['response']:
                for doc in data['response']['docs']:
                    medicine_info = {
                        'id': doc.get('id_goods') or doc.get('id'),
                        'name': doc.get('name', ''),
                        'producer': doc.get('producer', ''),
                        'url': ''
                    }
                    
                    # Extract URL if available
                    if 'url' in doc and isinstance(doc['url'], dict):
                        if 'docs' in doc['url'] and doc['url']['docs']:
                            medicine_info['url'] = doc['url']['docs'][0].get('url', '')
                    
                    medicines.append(medicine_info)
            
            return medicines
            
        except requests.RequestException as e:
            print(f"Error searching for medicine: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"Error parsing search response: {e}")
            return []

    def get_prices(self, medicine_ids: List[str], city_id: str = "46") -> Dict[str, Dict]:
        """
        Get prices for medicine IDs using the API
        
        Args:
            medicine_ids: List of medicine IDs
            city_id: City ID (default is 46)
            
        Returns:
            Dictionary with medicine ID as key and price info as value
        """
        # Prepare the request body
        ids_dict = {}
        for med_id in medicine_ids:
            ids_dict[str(med_id)] = {
                "id": str(med_id),
                "ph": 0
            }
        
        request_body = {
            "ln": "uk",
            "COOKIE": {
                "my_city": "22605",
                "my_city_id": city_id
            },
            "ids": ids_dict,
            "type": "info",
            "spl_full": True,
            "uid": 0
        }
        
        try:
            response = self.session.post(
                self.price_api_url,
                json=request_body,
                headers={'Content-Type': 'application/json'}
            )
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.RequestException as e:
            print(f"Error getting prices: {e}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing price response: {e}")
            return {}

    def get_search_link(self, medicine_name: str) -> str:
        """
        Generate search result link for the medicine
        
        Args:
            medicine_name: Name of the medicine
            
        Returns:
            Search result URL
        """
        encoded_name = urllib.parse.quote(medicine_name)
        return f"{self.base_url}/search/result?search={encoded_name}"

    def find_lowest_price(self, price_data: Dict) -> Tuple[Optional[float], Optional[str], List[Dict]]:
        """
        Find the lowest price from price data
        
        Args:
            price_data: Price data from API response
            
        Returns:
            Tuple of (lowest_price, medicine_id, all_price_info)
        """
        lowest_price = None
        lowest_price_id = None
        all_prices = []
        
        # The price data is in 'resInfo' array
        if 'resInfo' in price_data and isinstance(price_data['resInfo'], list):
            for item in price_data['resInfo']:
                if isinstance(item, dict) and 'price' in item and 'id' in item:
                    price = item['price']
                    med_id = str(item['id'])
                    
                    if isinstance(price, (int, float)) and price > 0:
                        price_info = {
                            'id': med_id,
                            'price': price,
                            'old_price': item.get('priceOld', 0),
                            'discount': item.get('discount'),
                            'currency': price_data.get('currency', '₴'),
                            'bonus': item.get('bonus', 0),
                            'in_stock': item.get('in_stosk', {}).get('on', False),
                            'quantity': item.get('in_stosk', {}).get('qty', 0)
                        }
                        all_prices.append(price_info)
                        
                        if lowest_price is None or price < lowest_price:
                            lowest_price = price
                            lowest_price_id = med_id
        
        return lowest_price, lowest_price_id, all_prices

    def scrape_medicine(self, medicine_name: str, city_id: str = "46") -> Dict:
        """
        Complete scraping process for a medicine
        
        Args:
            medicine_name: Name of the medicine to search for
            city_id: City ID (default is 46)
            
        Returns:
            Dictionary with search results, prices, and lowest price info
        """
        print(f"Searching for: {medicine_name}")
        
        # Step 1: Get medicine IDs
        medicines = self.search_medicine_ids(medicine_name, city_id)
        if not medicines:
            print("No medicines found")
            return {
                'medicine_name': medicine_name,
                'search_link': self.get_search_link(medicine_name),
                'medicines': [],
                'lowest_price': None,
                'error': 'No medicines found'
            }
        
        print(f"Found {len(medicines)} medicines")
        
        # Step 2: Get prices
        medicine_ids = [str(med['id']) for med in medicines if med['id']]
        if not medicine_ids:
            print("No valid medicine IDs found")
            return {
                'medicine_name': medicine_name,
                'search_link': self.get_search_link(medicine_name),
                'medicines': medicines,
                'lowest_price': None,
                'error': 'No valid medicine IDs found'
            }
        
        print(f"Getting prices for {len(medicine_ids)} medicines")
        price_data = self.get_prices(medicine_ids, city_id)
        
        # Step 3: Find lowest price
        lowest_price, lowest_price_id, all_prices = self.find_lowest_price(price_data)
        
        # Step 4: Generate search link
        search_link = self.get_search_link(medicine_name)
        
        result = {
            'medicine_name': medicine_name,
            'search_link': search_link,
            'medicines': medicines,
            'all_prices': all_prices,
            'lowest_price': lowest_price,
            'lowest_price_medicine_id': lowest_price_id,
            'currency': price_data.get('currency', '₴')
        }
        
        return result


def scrape_medicine_price(medicine_name: str, city_id: str = "46") -> Dict:
    """
    Simple function to scrape medicine price
    
    Args:
        medicine_name: Name of the medicine to search for
        city_id: City ID (default is 46 for Kyiv)
        
    Returns:
        Dictionary with medicine name, search link, and lowest price
    """
    scraper = AptekaScraper()
    result = scraper.scrape_medicine(medicine_name, city_id)
    
    return {
        'medicine_name': result['medicine_name'],
        'search_link': result['search_link'],
        'lowest_price': result.get('lowest_price'),
        'currency': result.get('currency', '₴'),
        'medicines_count': len(result.get('medicines', [])),
        'success': result.get('lowest_price') is not None
    }


def main():
    scraper = AptekaScraper()
    
    # Test with the provided example
    test_medicines = ["атоксіл", "ВІПРАТОКС"]
    
    for medicine in test_medicines:
        print(f"\n{'='*50}")
        print(f"Scraping: {medicine}")
        print(f"{'='*50}")
        
        result = scraper.scrape_medicine(medicine)
        
        print(f"Search link: {result['search_link']}")
        print(f"Found medicines: {len(result.get('medicines', []))}")
        
        if result.get('lowest_price'):
            currency = result.get('currency', '₴')
            print(f"Lowest price: {result['lowest_price']} {currency}")
            print(f"Medicine ID with lowest price: {result['lowest_price_medicine_id']}")
            
            # Show all prices
            print(f"\nAll prices:")
            for price_info in result.get('all_prices', []):
                price_text = f"{price_info['price']} {currency}"
                if price_info.get('old_price') and price_info['old_price'] > 0:
                    price_text += f" (was {price_info['old_price']} {currency}"
                    if price_info.get('discount'):
                        price_text += f", -{price_info['discount']}%"
                    price_text += ")"
                
                stock_status = "✓ In stock" if price_info.get('in_stock') else "✗ Out of stock"
                print(f"   ID {price_info['id']}: {price_text} - {stock_status}")
                if price_info.get('quantity'):
                    print(f"      Available: {price_info['quantity']} units")
        else:
            print("No price information available")
            if 'error' in result:
                print(f"Error: {result['error']}")
        
        # Print medicine details
        for i, med in enumerate(result.get('medicines', [])[:3], 1):  # Show first 3
            print(f"\n{i}. {med['name']}")
            print(f"   ID: {med['id']}")
            print(f"   Producer: {med['producer']}")
            if med['url']:
                print(f"   URL: https://apteka.net.ua{med['url']}")


if __name__ == "__main__":
    main()
