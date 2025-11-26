from fpdf import FPDF
import pandas as pd
from config import PACKAGE_LEADS, TARGET_REGION, SELECTED_NICHE, BUSINESS_CONTACT, REPORTS_DIR
import unicodedata

class LeadReportPDF:
    def __init__(self, df, package):
        self.package = package
        self.leads = df.head(PACKAGE_LEADS[package]) if package in PACKAGE_LEADS else df.head(50)

    def _clean_text(self, text):
        """Clean text to handle Unicode characters for PDF generation."""
        if not text or pd.isna(text):
            return 'N/A'

        # Convert to string if not already
        text = str(text)

        # Normalize Unicode characters
        text = unicodedata.normalize('NFKD', text)

        # Remove or replace problematic characters
        # Replace common Unicode punctuation with ASCII equivalents
        replacements = {
            '\u2013': '-',  # en dash
            '\u2014': '-',  # em dash
            '\u2018': "'",  # left single quotation mark
            '\u2019': "'",  # right single quotation mark
            '\u201c': '"',  # left double quotation mark
            '\u201d': '"',  # right double quotation mark
            '\u2026': '...',  # horizontal ellipsis
        }

        for unicode_char, ascii_char in replacements.items():
            text = text.replace(unicode_char, ascii_char)

        # Remove any remaining non-ASCII characters
        text = ''.join(char for char in text if ord(char) < 128)

        return text.strip()

    def generate(self, filename=None):
        if filename is None:
            filename = f"{REPORTS_DIR}{self.package}_{pd.Timestamp.now().strftime('%Y%m%d')}.pdf"

        pdf = FPDF()
        pdf.add_page()

        # Title Page
        pdf.set_font('Arial', 'B', 20)
        pdf.cell(200, 20, txt="Lead Generation Report", ln=True, align='C')
        pdf.set_font('Arial', 'I', 16)
        pdf.cell(200, 10, txt=f"Package: {self.package.capitalize()}", ln=True, align='C')
        pdf.cell(200, 10, txt=f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='C')

        # Summary Page
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(200, 10, txt="Report Summary", ln=True)
        pdf.set_font('Arial', size=12)
        pdf.cell(200, 10, txt=f"Total Leads Included: {len(self.leads)}", ln=True)
        pdf.cell(200, 10, txt=f"Niche: {SELECTED_NICHE.replace('_', ' ').capitalize()}", ln=True)
        pdf.cell(200, 10, txt=f"Region: {TARGET_REGION}", ln=True)
        pdf.cell(200, 10, txt=f"Source: Public Business Directories", ln=True)

        # Leads Table
        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(10, 10, "ID", 1, align='C')
        pdf.cell(50, 10, "Business Name", 1, align='C')
        pdf.cell(30, 10, "Phone", 1, align='C')
        pdf.cell(50, 10, "Address", 1, align='C')
        pdf.cell(30, 10, "Category", 1, align='C')
        pdf.ln()

        pdf.set_font('Arial', size=10)
        for _, row in self.leads.iterrows():
            # Clean all text fields to handle Unicode
            name = self._clean_text(row['name'])[:18]
            phone = self._clean_text(row['phone'])[:12]
            address = self._clean_text(row['address'])[:18]
            category = self._clean_text(row['category'])[:10]

            pdf.cell(10, 8, str(row['id']), 1, align='C')
            pdf.cell(50, 8, name, 1)
            pdf.cell(30, 8, phone, 1)
            pdf.cell(50, 8, address, 1)
            pdf.cell(30, 8, category, 1)
            pdf.ln()

        # Footer on last page
        pdf.cell(200, 10, txt="", ln=True, align='C')
        footer_text = self._clean_text(f"For inquiries: {BUSINESS_CONTACT['name']} | {BUSINESS_CONTACT['phone']} | {BUSINESS_CONTACT['email']}")
        pdf.cell(200, 10, txt=footer_text, align='C', ln=True)

        pdf.output(filename)
        return filename

if __name__ == '__main__':
    # Test with sample data
    sample_df = pd.DataFrame([
        {'id': 1, 'name': 'ABC Realty', 'phone': '6 12 345 678', 'address': 'Main St, Maseru', 'category': 'real_estate'},
        {'id': 2, 'name': 'DEF Agents', 'phone': '6 23 498 765', 'address': 'Highway Rd, Qoaling', 'category': 'real_estate'},
    ])
    generator = LeadReportPDF(sample_df, 'basic')
    generator.generate('test_report.pdf')
    generator = LeadReportPDF(sample_df, 'basic')
    generator.generate('test_report.pdf')
    print("PDF generated: test_report.pdf")
