import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from config import *
import time
import os
from urllib.robotparser import RobotFileParser
import json

class LeadScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': DESCRIPTIVE_USER_AGENT
        }
        self.cache = {} if CACHE_ENABLED else None
        self.cache_file = 'scraper_cache.json'
        self.load_cache()

    def load_cache(self):
        if CACHE_ENABLED and os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as f:
                self.cache = json.load(f)

    def save_cache(self):
        if CACHE_ENABLED:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f)

    def check_robots_txt(self, url):
        if not RESPECT_ROBOTS_TXT:
            return True
        try:
            rp = RobotFileParser()
            rp.set_url(url + '/robots.txt')
            rp.read()
            return rp.can_fetch(self.headers['User-Agent'], url)
        except:
            return True  # If can't read robots.txt, assume allowed

    def cached_request(self, url):
        if CACHE_ENABLED and url in self.cache:
            # Return cached text as response-like object
            class MockResponse:
                def __init__(self, text):
                    self.text = text
                    self.status_code = 200
            return MockResponse(self.cache[url])
        if not self.check_robots_txt(url):
            print(f"Blocked by robots.txt: {url}")
            return None
        response = requests.get(url, headers=self.headers, timeout=10)
        if response.status_code != 200:
            return response  # Return even failed for status check
        if CACHE_ENABLED:
            self.cache[url] = response.text
            self.save_cache()
        time.sleep(RATE_LIMIT_SECONDS)
        return response

    def scrape_leads(self, niche, max_pages=5):
        """
        Scrape leads for a given niche from niche-specific sources.
        """
        leads = []
        if niche not in NICHE_SOURCES:
            print(f"No sources defined for niche: {niche}")
            return pd.DataFrame()

        sources = NICHE_SOURCES[niche]

        for source in sources:
            print(f"\nTrying source: {source['name']}")
            source_leads = []

            # Construct search URL for this source
            region_formatted = TARGET_REGION.replace(' ', '+')
            if '{query}' in source['search_path']:
                query = niche.replace('_', '+')
                search_path = source['search_path'].format(query=query, region=region_formatted)
            else:
                search_path = source['search_path'].format(region=region_formatted)

            base_url = f"{source['url']}{search_path}"
            print(f"Scraping URL: {base_url}")

            for page in range(1, max_pages + 1):
                page_url = f"{base_url}&page={page}" if page > 1 else base_url
                print(f"Fetching page {page}: {page_url}")

                try:
                    response_text = self.cached_request(page_url)
                    if response_text is None:
                        continue
                    if hasattr(response_text, 'status_code') and response_text.status_code != 200:
                        print(f"Failed to fetch page {page} from {source['name']}, status: {response_text.status_code}")
                        continue
                    elif hasattr(response_text, 'status_code'):
                        soup = BeautifulSoup(response_text.text, 'html.parser')
                    else:
                        soup = BeautifulSoup(response_text, 'html.parser')

                    # Try different selectors for business listings
                    business_listings = (
                        soup.find_all('div', class_=re.compile(r'listing|business|agent|doctor|tutor')) or
                        soup.find_all('article', class_=re.compile(r'listing|business')) or
                        soup.find_all('li', class_=re.compile(r'listing|business')) or
                        soup.find_all('a', href=re.compile(r'/agent/|/doctor/|/tutor/|/business/'))
                    )

                    print(f"Found {len(business_listings)} potential listings on page {page}")

                    for listing in business_listings:
                        lead = self.extract_lead(listing, niche)
                        if lead:
                            source_leads.append(lead)
                            leads.append(lead)
                            print(f"Extracted lead: {lead['name']}")
                        if len(leads) >= 500:  # Global limit
                            break

                    if len(leads) >= 500:
                        break

                except Exception as e:
                    print(f"Error scraping {source['name']} page {page}: {e}")
                    continue

            print(f"Leads from {source['name']}: {len(source_leads)}")

            if len(leads) >= 500:  # Global limit
                break

        print(f"\nTotal leads scraped from all sources: {len(leads)}")
        return pd.DataFrame(leads)

    def extract_lead(self, listing, niche):
        """
        Extract information from a single listing.
        """
        # Get all text content
        full_text = listing.get_text(separator=' ', strip=True)

        # Skip if this looks like footer/navigation content
        skip_keywords = ['premium user', 'view details', 'operating:', 'open now', 'closed now',
                        'previous next', 'the new yep!', '© yep!', 'waterproofing professionals',
                        'home services', 'building contractors']
        if any(keyword.lower() in full_text.lower() for keyword in skip_keywords):
            return None

        # Try to extract structured data first
        name = None
        address = None
        phone = None

        # Look for common patterns in the text
        # Pattern 1: Name followed by address
        lines = full_text.split(',')
        if len(lines) >= 2:
            # First part might be name
            potential_name = lines[0].strip()
            if len(potential_name) > 3 and not potential_name.isdigit():
                name = potential_name

            # Look for address pattern (street, city, postal code)
            for line in lines:
                line = line.strip()
                # Check if it looks like an address (contains street numbers, city names, postal codes)
                if (re.search(r'\d+', line) and  # Has numbers
                    any(city in line.lower() for city in ['cape town', 'johannesburg', 'durban', 'pretoria', 'port elizabeth', 'bloemfontein', 'east london', 'kimberley']) or
                    re.search(r'\d{4}', line)):  # Has postal code
                    address = line
                    break

        # If no structured extraction, try to parse the full text
        if not name:
            # Remove common prefixes and try to extract business name
            text = re.sub(r'^(premium user|[A-Z])', '', full_text).strip()
            # Take first meaningful part as name
            parts = text.split()
            if parts:
                # Find a sequence that looks like a business name
                name_parts = []
                for part in parts[:5]:  # Check first 5 words
                    if len(part) > 2 and not part.isdigit():
                        name_parts.append(part)
                    else:
                        break
                name = ' '.join(name_parts) if name_parts else None

        # Extract phone number using more comprehensive regex
        phone_patterns = [
            r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',  # 123-456-7890
            r'\b\d{10}\b',                        # 1234567890
            r'\+\d{2}[-.\s]\d{1}[-.\s]\d{3}[-.\s]\d{3}[-.\s]\d{3}\b',  # +27 1 234 567 890
            r'\d{2}[-.\s]\d{3}[-.\s]\d{4}',      # 27 123 4567 (South African)
        ]

        for pattern in phone_patterns:
            phones = re.findall(pattern, full_text)
            if phones:
                phone = phones[0]
                break

        # Clean up the extracted data
        if name:
            # Remove extra whitespace and clean up
            name = re.sub(r'\s+', ' ', name).strip()
            # Remove if it's too short or looks like garbage
            if len(name) < 3 or name.isdigit():
                name = None

        if address:
            address = re.sub(r'\s+', ' ', address).strip()

        # Only return if we have at least a name
        if name:
            return {
                'name': name,
                'phone': phone or 'N/A',
                'address': address or 'N/A',
                'category': niche,
                'niche': niche
            }

        return None

if __name__ == '__main__':
    scraper = LeadScraper()
    df = scraper.scrape_leads('real_estate')
    print(f"Scraped {len(df)} leads")
