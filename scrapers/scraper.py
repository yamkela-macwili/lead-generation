import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
from config import *
import time

class LeadScraper:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def scrape_leads(self, niche, max_pages=5):
        """
        Scrape leads for a given niche from multiple sources.
        """
        leads = []
        query = niche.replace('_', '+')

        for source in SCRAPER_SOURCES:
            print(f"\nTrying source: {source['name']}")
            source_leads = []

            # Construct search URL for this source
            if 'category' in source['search_path']:
                # Category-based search (like Yep)
                category = CATEGORY_MAPPINGS.get(niche, '81517')  # Default to real estate
                search_path = source['search_path'].format(category=category, region=TARGET_REGION.replace(' ', '+'))
            else:
                # Query-based search
                search_path = source['search_path'].format(query=query, region=TARGET_REGION.replace(' ', '+'))

            base_url = f"{source['url']}{search_path}"
            print(f"Scraping URL: {base_url}")

            for page in range(1, max_pages + 1):
                if 'category' in source['search_path']:
                    # For category-based, pages might be &page= or ?page=
                    page_url = f"{base_url}&page={page}" if page > 1 else base_url
                else:
                    page_url = f"{base_url}&page={page}" if page > 1 else base_url

                print(f"Fetching page {page}: {page_url}")

                try:
                    response = requests.get(page_url, headers=self.headers, timeout=10)
                    print(f"Response status: {response.status_code}")

                    if response.status_code != 200:
                        print(f"Failed to fetch page {page} from {source['name']}, trying next page.")
                        continue

                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Try different selectors for business listings
                    business_listings = (
                        soup.find_all('div', class_='listing-item') or
                        soup.find_all('div', class_='business-listing') or
                        soup.find_all('article', class_='listing') or
                        soup.find_all('div', class_=re.compile(r'listing|business')) or
                        soup.find_all('tr', class_=re.compile(r'listing|business')) or
                        soup.find_all('li', class_=re.compile(r'listing|business')) or
                        # For Yep specifically
                        soup.find_all('div', class_=re.compile(r'item|card|result')) or
                        soup.find_all('a', href=re.compile(r'/business/'))
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

                    time.sleep(2)  # Rate limiting between pages

                    if len(leads) >= 500:
                        break

                except Exception as e:
                    print(f"Error scraping {source['name']} page {page}: {e}")
                    continue

            print(f"Leads from {source['name']}: {len(source_leads)}")

            # If we got enough leads from this source, we can stop or continue for more variety
            if len(source_leads) >= MIN_LEADS_PER_SOURCE:
                print(f"Got {len(source_leads)} leads from {source['name']}, continuing to next source for more variety...")
            else:
                print(f"Only {len(source_leads)} leads from {source['name']}, trying next source...")

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
