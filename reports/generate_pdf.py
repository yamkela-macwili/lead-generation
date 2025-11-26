from fpdf import FPDF
import pandas as pd
from config import PACKAGE_LEADS, TARGET_REGION, SELECTED_NICHE, BUSINESS_CONTACT, REPORTS_DIR

class LeadReportPDF:
    def __init__(self, df, package):
        self.package = package
        self.leads = df.head(PACKAGE_LEADS[package]) if package in PACKAGE_LEADS else df.head(50)

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
            pdf.cell(10, 8, str(row['id']), 1, align='C')
            pdf.cell(50, 8, row['name'][:18] if pd.notna(row['name']) else 'N/A', 1)
            pdf.cell(30, 8, row['phone'][:12] if pd.notna(row['phone']) else 'N/A', 1)
            pdf.cell(50, 8, row['address'][:18] if pd.notna(row['address']) else 'N/A', 1)
            pdf.cell(30, 8, row['category'][:10] if pd.notna(row['category']) else 'N/A', 1)
            pdf.ln()

        # Footer on last page
        pdf.cell(200, 10, txt="", ln=True, align='C')
        pdf.cell(200, 10, txt=f"For inquiries: {BUSINESS_CONTACT['name']} | {BUSINESS_CONTACT['phone']} | {BUSINESS_CONTACT['email']}", align='C', ln=True)

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
