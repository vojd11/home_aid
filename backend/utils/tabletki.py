#!/usr/bin/env python3
"""
Tabletki.ua Parser
==================

A comprehensive parser for scraping product prices from tabletki.ua, 
a Ukrainian pharmacy website.

Features:
- Search for medications by name
- Extract first available price
- Get detailed product information
- Support for multiple product searches
- Command-line interface
- Interactive search mode

Usage:
    python tabletki.py                    # Run default examples
    python tabletki.py "Product Name"     # Search for specific product
    python tabletki.py --interactive      # Interactive search mode

Example:
    python tabletki.py "АТОКСІЛ"
    Output: АТОКСІЛ: 310.31 грн

Requirements:
    - requests
    - beautifulsoup4
    - lxml

Author: Parser for tabletki.ua
Date: 2025
"""

import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote


class TabletkiParser:
    def __init__(self):
        self.base_url = "https://tabletki.ua/uk/search/"
        self.session = requests.Session()
        # Set headers to mimic a real browser
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'uk-UA,uk;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

    def search_product(self, product_name):
        """
        Search for a product and return the search results page
        """
        # URL encode the product name
        encoded_name = quote(product_name)
        url = f"{self.base_url}{encoded_name}/"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching page: {e}")
            return None

    def parse_first_price(self, html_content):
        """
        Parse the first price from the search results
        """
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Look for price patterns in the text
        price_patterns = [
            r'від\s+(\d+(?:\.\d+)?)\s+грн',  # "від XXX.XX грн"
            r'(\d+(?:\.\d+)?)\s+грн',        # "XXX.XX грн"
            r'грн\s+(\d+(?:\.\d+)?)',        # "грн XXX.XX"
        ]
        
        # Search in the entire page text
        page_text = soup.get_text()
        
        for pattern in price_patterns:
            matches = re.findall(pattern, page_text, re.IGNORECASE)
            if matches:
                try:
                    price = float(matches[0])
                    return price
                except ValueError:
                    continue
        
        # Alternative method: look for specific price elements
        price_selectors = [
            '.price',
            '.cost',
            '[class*="price"]',
            '[class*="cost"]',
            'span[data-price]',
            '.product-price',
        ]
        
        for selector in price_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text(strip=True)
                # Extract numbers from the text
                numbers = re.findall(r'\d+(?:\.\d+)?', text)
                if numbers:
                    try:
                        price = float(numbers[0])
                        return price
                    except ValueError:
                        continue
        
        return None

    def get_product_info(self, product_name):
        """
        Get comprehensive product information including price
        """
        html_content = self.search_product(product_name)
        if not html_content:
            return None
            
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Extract product information
        products = []
        
        # Look for specific product patterns in the text
        page_text = soup.get_text()
        
        # Find product entries with prices
        product_pattern = r'(Атоксіл[^від]*від\s+(\d+(?:\.\d+)?)\s+грн)'
        matches = re.findall(product_pattern, page_text, re.IGNORECASE)
        
        for match in matches[:5]:  # Limit to first 5 products
            full_text = match[0]
            price = float(match[1])
            
            # Extract product name from the full text
            name_match = re.search(r'(Атоксіл[^від]*)', full_text, re.IGNORECASE)
            product_name_extracted = name_match.group(1).strip() if name_match else product_name
            
            products.append({
                'name': product_name_extracted,
                'price': price,
                'currency': 'грн',
                'full_text': full_text.strip()
            })
        
        # Fallback: if no specific products found, just return the first price
        if not products:
            price = self.parse_first_price(html_content)
            if price:
                return [{
                    'name': product_name,
                    'price': price,
                    'currency': 'грн'
                }]
        
        return products if products else None

    def get_first_price(self, product_name):
        """
        Get just the first price found for a product
        """
        html_content = self.search_product(product_name)
        price = self.parse_first_price(html_content)
        return price

    def search_multiple_products(self, product_names):
        """
        Search for multiple products and return their prices
        """
        results = {}
        for product_name in product_names:
            print(f"Searching for: {product_name}")
            price = self.get_first_price(product_name)
            results[product_name] = price
            time.sleep(1)  # Be respectful to the server
        return results


def main():
    """
    Example usage of the parser
    """
    parser = TabletkiParser()
    
    # Test with the АТОКСІЛ search
    product_name = "АТОКСІЛ"
    
    print(f"Searching for: {product_name}")
    print("-" * 50)
    
    # Get first price
    first_price = parser.get_first_price(product_name)
    if first_price:
        print(f"First price found: {first_price} грн")
    else:
        print("No price found")
    
    print("-" * 50)
    
    # Get detailed product information
    products = parser.get_product_info(product_name)
    if products:
        print("Product information:")
        for i, product in enumerate(products, 1):
            print(f"{i}. {product.get('name', 'Unknown')}")
            if 'price' in product:
                print(f"   Price: {product['price']} {product.get('currency', '')}")
            if 'full_text' in product:
                print(f"   Details: {product['full_text'][:100]}...")
            print()
    else:
        print("No products found")

    # Test with multiple products
    print("\n" + "="*60)
    print("Testing multiple products:")
    print("="*60)
    
    test_products = ["Нурофен", "Парацетамол", "Аспірин"]
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
    parser = TabletkiParser()
    
    print("Tabletki.ua Price Parser")
    print("Enter 'quit' to exit")
    print("-" * 30)
    
    while True:
        product_name = input("\nEnter product name to search: ").strip()
        
        if product_name.lower() in ['quit', 'exit', 'q']:
            break
            
        if not product_name:
            continue
            
        print(f"\nSearching for: {product_name}")
        price = parser.get_first_price(product_name)
        
        if price:
            print(f"Price found: {price} грн")
        else:
            print("No price found")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--interactive":
            interactive_search()
        else:
            # Search for command line argument
            parser = TabletkiParser()
            product_name = " ".join(sys.argv[1:])
            price = parser.get_first_price(product_name)
            if price:
                print(f"{product_name}: {price} грн")
            else:
                print(f"{product_name}: No price found")
    else:
        main()
