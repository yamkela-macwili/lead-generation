import schedule
import time
from scrapers.scraper import LeadScraper
from cleaner.cleaner import LeadCleaner
from reports.generate_pdf import LeadReportPDF
from reports.generate_excel import LeadReportExcel
from config import NICHE_OPTIONS, PACKAGE_LEADS, SELECTED_NICHE, PRICES
import os

def generate_lead_package(niche, package):
    """Generate a lead package for given niche and package type."""
    print(f"Generating {package} package for {niche}...")

    # Scrape leads
    scraper = LeadScraper()
    df = scraper.scrape_leads(niche)
    print(f"Scraped {len(df)} raw leads.")

    # Clean leads
    cleaner = LeadCleaner()
    df = cleaner.clean_leads(df)
    print(f"Cleaned to {len(df)} leads.")

    # Ensure directories exist
    os.makedirs('reports', exist_ok=True)
    os.makedirs('exports', exist_ok=True)

    files_generated = []

    # Generate reports based on package
    if package in ['basic', 'standard', 'premium']:
        # All packages get PDF
        pdf_gen = LeadReportPDF(df, package)
        pdf_file = pdf_gen.generate()
        files_generated.append(f"PDF: {pdf_file}")

    if package in ['standard', 'premium']:
        # Standard and premium get Excel
        excel_gen = LeadReportExcel(df, package)
        excel_file = excel_gen.generate()
        files_generated.append(f"Excel: {excel_file}")

    print(f"\n{package.capitalize()} package generated!")
    print("Files:")
    for file in files_generated:
        print(f"- {file}")
    print(f"\nReady to sell for R{PRICES[package]}!")

    return files_generated

def automated_daily_update():
    """Automated daily lead refresh for all niches."""
    print("Running automated daily lead update...")
    for niche in NICHE_OPTIONS.keys():
        print(f"Updating leads for {niche}...")
        scraper = LeadScraper()
        df = scraper.scrape_leads(niche, max_pages=2)  # Limited pages for daily update
        cleaner = LeadCleaner()
        df = cleaner.clean_leads(df)
        # Save to cache or database (for now, just print)
        print(f"Updated {len(df)} leads for {niche}")
    print("Daily update complete.")

def main():
    print("Lead Generation Automation Tool")
    print("Choose mode:")
    print("1. Generate single package")
    print("2. Start automated daily updates")
    mode = input("Enter mode (1 or 2, default 1): ").strip() or '1'

    if mode == '2':
        # Automated mode
        print("Starting automated daily updates...")
        schedule.every().day.at("06:00").do(automated_daily_update)
        print("Scheduled daily updates at 06:00. Press Ctrl+C to stop.")
        while True:
            schedule.run_pending()
            time.sleep(60)
    else:
        # Single package mode
        print("Choose niche:")
        for key, desc in NICHE_OPTIONS.items():
            print(f"{key}: {desc}")
        niche = input(f"Enter niche key (default: {SELECTED_NICHE}): ").strip() or SELECTED_NICHE
        if niche not in NICHE_OPTIONS:
            print(f"Invalid niche, using default {SELECTED_NICHE}")
            niche = SELECTED_NICHE

        print("\nChoose package:")
        for pkg, leads in PACKAGE_LEADS.items():
            print(f"{pkg}: {leads} leads - R{PRICES[pkg]}")
        package = input("Enter package (basic/standard/premium): ").strip().lower()
        if package not in PACKAGE_LEADS:
            print("Invalid package, using basic")
            package = 'basic'

        generate_lead_package(niche, package)
        

if __name__ == '__main__':
    main()
