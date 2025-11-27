from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import pandas as pd
import unicodedata
import os
import sys

# Add parent directory to path to import config
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import PACKAGE_LEADS, TARGET_REGION, SELECTED_NICHE, BUSINESS_CONTACT, REPORTS_DIR, PACKAGE_FEATURES

class LeadReportPDF:
    def __init__(self, df, package):
        self.package = package
        self.leads = df.head(PACKAGE_LEADS[package]) if package in PACKAGE_LEADS else df.head(50)
        self.features = PACKAGE_FEATURES.get(package, [])

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

        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Title Page
        title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=20, alignment=1)
        story.append(Paragraph("Lead Generation Report", title_style))
        story.append(Spacer(1, 12))

        package_style = ParagraphStyle('Package', parent=styles['Italic'], fontSize=16, alignment=1)
        story.append(Paragraph(f"Package: {self.package.capitalize()}", package_style))
        story.append(Paragraph(f"Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}", package_style))
        story.append(Spacer(1, 12))

        # Summary Page
        story.append(Paragraph("Report Summary", styles['Heading2']))
        story.append(Spacer(1, 6))
        summary_data = [
            f"Total Leads Included: {len(self.leads)}",
            f"Niche: {SELECTED_NICHE.replace('_', ' ').capitalize()}",
            f"Region: {TARGET_REGION}",
            "Source: Public Business Directories"
        ]
        for item in summary_data:
            story.append(Paragraph(item, styles['Normal']))
            story.append(Spacer(1, 6))

        # Leads Table
        story.append(Spacer(1, 12))
        story.append(Paragraph("Leads Data", styles['Heading2']))
        story.append(Spacer(1, 6))

        table_data = [['ID', 'Business Name', 'Phone', 'Address', 'Category']]
        for _, row in self.leads.iterrows():
            name = self._clean_text(row['name'])[:18]
            phone = self._clean_text(row['phone'])[:12]
            address = self._clean_text(row['address'])[:18]
            category = self._clean_text(row['category'])[:10]
            table_data.append([str(row['id']), name, phone, address, category])

        table = Table(table_data, colWidths=[0.5*inch, 1.5*inch, 1*inch, 1.5*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        story.append(table)
        story.append(Spacer(1, 12))

        # Analytics page for premium package
        if self.package == 'premium':
            story.append(Paragraph("Premium Analytics Dashboard", styles['Heading2']))
            story.append(Spacer(1, 6))
            story.append(Paragraph("Lead Quality Distribution:", styles['Heading3']))
            # Simple text analytics
            if 'score' in self.leads.columns:
                score_counts = self.leads['score'].value_counts().sort_index()
                for score, count in score_counts.items():
                    story.append(Paragraph(f"Score {score}: {count} leads", styles['Normal']))
            story.append(Spacer(1, 6))
            story.append(Paragraph("Geographic Insights:", styles['Heading3']))
            # Basic geographic analysis
            if 'address' in self.leads.columns:
                cities = self.leads['address'].str.split(',').str[0].value_counts().head(5)
                for city, count in cities.items():
                    story.append(Paragraph(f"{city}: {count} leads", styles['Normal']))
            story.append(Spacer(1, 12))

        # Footer
        footer_text = self._clean_text(f"For inquiries: {BUSINESS_CONTACT['name']} | {BUSINESS_CONTACT['phone']} | {BUSINESS_CONTACT['email']}")
        footer_style = ParagraphStyle('Footer', parent=styles['Normal'], alignment=1, fontSize=10)
        story.append(Paragraph(footer_text, footer_style))

        doc.build(story)
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
