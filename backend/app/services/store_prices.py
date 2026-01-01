"""
Store price service for integrating pharmacy scrapers
"""
import asyncio
from typing import List, Dict, Optional
from datetime import datetime

from app.schemas.store_prices import StorePrice, StorePricesResponse


class StorePriceService:
    """Service for fetching prices from various pharmacy stores"""
    
    def __init__(self):
        # Store configurations
        self.stores = {
            "apteka911": {
                "name": "Apteka 911",
                "base_url": "https://apteka911.ua"
            },
            "anc": {
                "name": "ANC",
                "base_url": "https://anc.ua"
            },
            "tabletki": {
                "name": "Tabletki.ua", 
                "base_url": "https://tabletki.ua"
            },
            "apteka": {
                "name": "Apteka.net.ua",
                "base_url": "https://apteka.net.ua"
            }
        }
    
    async def get_apteka911_price(self, medication_name: str) -> StorePrice:
        """Get price from Apteka 911 using the scraper"""
        try:
            # Import the scraper
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
            
            # Import from the 911.py file directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("apteka911", 
                os.path.join(os.path.dirname(__file__), '..', '..', 'utils', '911.py'))
            apteka911_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(apteka911_module)
            
            parser = apteka911_module.Apteka911Parser()
            result = parser.get_price_and_link(medication_name)
            
            return StorePrice(
                store_name="Apteka 911",
                price=result.get('price'),
                currency="грн",
                link=result.get('link'),
                status="success" if result.get('price') else "not_found"
            )
        except Exception as e:
            return StorePrice(
                store_name="Apteka 911",
                price=None,
                currency="грн", 
                link=None,
                status="error"
            )
    
    async def get_anc_price(self, medication_name: str) -> StorePrice:
        """Get price from ANC using the updated scraper"""
        try:
            # Import the scraper
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
            
            # Import from the anc.py file directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("anc", 
                os.path.join(os.path.dirname(__file__), '..', '..', 'utils', 'anc.py'))
            anc_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(anc_module)
            
            parser = anc_module.AncParser()
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
                from urllib.parse import quote
                encoded_name = quote(medication_name)
                link = f"https://anc.ua/search?q={encoded_name}"
                
                # Use link from first product if available and valid
                if result.get('products') and result['products'][0].get('link'):
                    product_link = result['products'][0]['link']
                    if product_link.startswith('http'):
                        link = product_link
                    elif product_link.startswith('/'):
                        link = f"https://anc.ua{product_link}"
            
            return StorePrice(
                store_name="ANC",
                price=price,
                currency="грн",
                link=link,
                status="success" if price else "not_found"
            )
        except Exception as e:
            return StorePrice(
                store_name="ANC",
                price=None,
                currency="грн",
                link=None,
                status="error"
            )
    
    async def get_tabletki_price(self, medication_name: str) -> StorePrice:
        """Get price from Tabletki.ua using the scraper"""
        try:
            # Import the scraper
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
            
            # Import from the tabletki.py file directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("tabletki", 
                os.path.join(os.path.dirname(__file__), '..', '..', 'utils', 'tabletki.py'))
            tabletki_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(tabletki_module)
            
            parser = tabletki_module.TabletkiParser()
            price = parser.get_first_price(medication_name)
            
            # Generate link
            from urllib.parse import quote
            encoded_name = quote(medication_name)
            link = f"https://tabletki.ua/uk/search/{encoded_name}/"
            
            return StorePrice(
                store_name="Tabletki.ua",
                price=price,
                currency="грн",
                link=link,
                status="success" if price else "not_found"
            )
        except Exception as e:
            return StorePrice(
                store_name="Tabletki.ua",
                price=None,
                currency="грн",
                link=None,
                status="error"
            )
    
    async def get_apteka_price(self, medication_name: str) -> StorePrice:
        """Get price from Apteka.net.ua using the updated scraper"""
        try:
            # Import the scraper
            import sys
            import os
            sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'utils'))
            
            # Import from the apteka.py file directly
            import importlib.util
            spec = importlib.util.spec_from_file_location("apteka", 
                os.path.join(os.path.dirname(__file__), '..', '..', 'utils', 'apteka.py'))
            apteka_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(apteka_module)
            
            # Use the new AptekaScraper class
            scraper = apteka_module.AptekaScraper()
            result = scraper.scrape_medicine(medication_name)
            
            # Extract price and link from the new result structure
            price = result.get('lowest_price')
            link = result.get('search_link')
            
            # Generate specific medicine link if available
            if result.get('medicines') and result['medicines']:
                first_medicine = result['medicines'][0]
                if first_medicine.get('url'):
                    medicine_url = first_medicine['url']
                    if medicine_url.startswith('/'):
                        link = f"https://apteka.net.ua{medicine_url}"
                    elif not medicine_url.startswith('http'):
                        link = f"https://apteka.net.ua/{medicine_url}"
                    else:
                        link = medicine_url
            
            # Determine status based on whether we found a price
            status = "success" if price is not None else "not_found"
            
            # Handle error cases
            if 'error' in result:
                status = "error"
            
            return StorePrice(
                store_name="Apteka.net.ua",
                price=price,
                currency="грн",
                link=link,
                status=status
            )
        except Exception as e:
            return StorePrice(
                store_name="Apteka.net.ua",
                price=None,
                currency="грн",
                link=None,
                status="error"
            )
    
    async def get_all_store_prices(self, medication_id: int, medication_name: str) -> StorePricesResponse:
        """Get prices from all stores concurrently"""
        
        # Run all scrapers concurrently for better performance
        tasks = [
            self.get_apteka911_price(medication_name),
            self.get_anc_price(medication_name),
            self.get_tabletki_price(medication_name),
            self.get_apteka_price(medication_name)
        ]
        
        store_prices = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out exceptions and convert to StorePrice objects
        valid_prices = []
        for price in store_prices:
            if isinstance(price, StorePrice):
                valid_prices.append(price)
            else:
                # Handle exceptions by creating error entries
                valid_prices.append(StorePrice(
                    store_name="Unknown",
                    price=None,
                    currency="грн",
                    link=None,
                    status="error"
                ))
        
        return StorePricesResponse(
            medication_id=medication_id,
            medication_name=medication_name,
            stores=valid_prices,
            total_stores=len(valid_prices),
            last_updated=datetime.now().isoformat()
        )
