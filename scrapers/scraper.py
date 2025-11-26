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
        name = listing.find('h2')
        if name:
            name = name.text.strip()
        else:
            # Try other selectors
            name = listing.find('h3')
            if name:
                name = name.text.strip()
            else:
                # Try getting text directly
                name = listing.get_text().split('\n')[0].strip() if listing.get_text() else None

        address = listing.find('span', class_='address')
        address = address.text.strip() if address else None

        phone = listing.find('span', class_='phone')
        if phone:
            phone = phone.text.strip()
        else:
            # Use regex to find phone numbers in text
            text = listing.get_text()
            phones = re.findall(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', text)  # US style, adjust for local
            phone = phones[0] if phones else None

        # Add more fields as available
        category = listing.get('data-category', 'unknown')

        return {
            'name': name,
            'phone': phone,
            'address': address,
            'category': category,
            'niche': niche
        } if name else None

if __name__ == '__main__':
    scraper = LeadScraper()
    df = scraper.scrape_leads('real_estate')
    print(f"Scraped {len(df)} leads")
