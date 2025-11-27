import pandas as pd
import xlsxwriter
from config import EXPORTS_DIR, PACKAGE_LEADS

class LeadReportExcel:
    def __init__(self, df, package):
        self.package = package
        self.leads = df.head(PACKAGE_LEADS[package]) if package in PACKAGE_LEADS else df.head(50)

    def generate(self, filename=None):
        if filename is None:
            filename = f"{EXPORTS_DIR}{self.package}_leads_{pd.Timestamp.now().strftime('%Y%m%d')}.xlsx"

        # Create workbook with xlsxwriter
        workbook = xlsxwriter.Workbook(filename)
        worksheet = workbook.add_worksheet('Business Leads')

        # Add headers
        headers = ['ID', 'Business Name', 'Phone', 'Address', 'Category', 'Score']
        for col_num, header in enumerate(headers):
            worksheet.write(0, col_num, header)

        # Write data
        for row_num, (_, row) in enumerate(self.leads.iterrows(), 1):
            worksheet.write(row_num, 0, row.get('id', 'N/A'))
            worksheet.write(row_num, 1, row.get('name', 'N/A'))
            worksheet.write(row_num, 2, row.get('phone', 'N/A'))
            worksheet.write(row_num, 3, row.get('address', 'N/A'))
            worksheet.write(row_num, 4, row.get('category', 'N/A'))
            worksheet.write(row_num, 5, row.get('score', 0))

        # Add analytics sheet for premium
        if self.package == 'premium':
            analytics_sheet = workbook.add_worksheet('Analytics')

            # Lead quality chart
            chart = workbook.add_chart({'type': 'column'})
            chart.add_series({
                'categories': '=Business Leads!$F$2:$F$' + str(len(self.leads) + 1),
                'values': '=Business Leads!$G$2:$G$' + str(len(self.leads) + 1),
                'name': 'Lead Scores'
            })
            chart.set_title({'name': 'Lead Quality Distribution'})
            analytics_sheet.insert_chart('A1', chart)

            # Geographic data
            analytics_sheet.write(0, 5, 'City')
            analytics_sheet.write(0, 6, 'Count')
            cities = self.leads['address'].str.split(',').str[0].value_counts().head(5)
            for i, (city, count) in enumerate(cities.items(), 1):
                analytics_sheet.write(i, 5, city)
                analytics_sheet.write(i, 6, count)

        workbook.close()
        return filename

if __name__ == '__main__':
    # Test with sample data
    sample_df = pd.DataFrame([
        {'id': 1, 'name': 'ABC Realty', 'phone': '6 12 345 678', 'address': 'Main St, Maseru', 'category': 'real_estate'},
        {'id': 2, 'name': 'DEF Agents', 'phone': '6 23 498 765', 'address': 'Highway Rd, Qoaling', 'category': 'real_estate'},
    ])
    generator = LeadReportExcel(sample_df, 'basic')
    excel_file = generator.generate('test_leads.xlsx')
    print(f"Excel generated: {excel_file}")
