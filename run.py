from scrapers.scraper import LeadScraper
from cleaner.cleaner import LeadCleaner
from reports.generate_pdf import LeadReportPDF
from reports.generate_excel import LeadReportExcel
from config import NICHE_OPTIONS, PACKAGE_LEADS, SELECTED_NICHE, PRICES
import os

def main():
    print("Lead Generation Automation Tool")
    print("Choose niche:")
    for key, desc in NICHE_OPTIONS.items():
        print(f"{key}: {desc}")
    niche = input("Enter niche key (default: real_estate): ").strip() or SELECTED_NICHE
    if niche not in NICHE_OPTIONS:
        print("Invalid niche, using default real_estate")
        niche = SELECTED_NICHE

    print("\nChoose package:")
    for pkg, leads in PACKAGE_LEADS.items():
        print(f"{pkg}: {leads} leads - R{PRICES[pkg]}")
    package = input("Enter package (basic/standard/premium): ").strip().lower()
    if package not in PACKAGE_LEADS:
        print("Invalid package, using basic")
        package = 'basic'

    # Scrape leads
    print(f"Scraping leads for {niche}...")
    scraper = LeadScraper()
    df = scraper.scrape_leads(niche)
    print(f"Scraped {len(df)} raw leads.")

    # Clean leads
    cleaner = LeadCleaner()
    df = cleaner.clean_leads(df)

    # Ensure directories exist
    os.makedirs('reports', exist_ok=True)
    os.makedirs('exports', exist_ok=True)

    # Generate PDF report
    print(f"Generating PDF report for {package} package...")
    pdf_gen = LeadReportPDF(df, package)
    pdf_file = pdf_gen.generate()
    print(f"PDF saved: {pdf_file}")

    # Generate Excel export
    print("Generating Excel export...")
    excel_gen = LeadReportExcel(df, package)
    excel_file = excel_gen.generate()
    print(f"Excel saved: {excel_file}")

    print("\nReport generation complete!")
    print("You can find the files in:")
    print(f"- PDF: {pdf_file}")
    print(f"- Excel: {excel_file}")
    print("\nStart selling these leads on WhatsApp and Facebook Marketplace!")

if __name__ == '__main__':
    import config as import_config  # To access PRICES
    main()
