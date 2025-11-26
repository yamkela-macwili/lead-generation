import pandas as pd
import re
from config import TARGET_REGION

class LeadCleaner:
    def __init__(self):
        pass

    def clean_leads(self, df):
        """
        Clean and filter the leads DataFrame.
        """
        if df.empty:
            return df

        # Remove duplicates based on name and phone
        df = df.drop_duplicates(subset=['name', 'phone'], keep='first')

        # Clean phone numbers
        df['phone'] = df['phone'].apply(self.clean_phone)

        # Filter by region - more inclusive for South Africa
        if TARGET_REGION.lower() == 'south africa':
            # For South Africa, check for major cities/provinces
            sa_regions = [
                'johannesburg', 'cape town', 'durban', 'pretoria', 'port elizabeth',
                'bloemfontein', 'east london', 'kimberley', 'pietermaritzburg',
                'gauteng', 'western cape', 'kwazulu-natal', 'eastern cape',
                'free state', 'north west', 'limpopo', 'mpumalanga', 'northern cape'
            ]
            region_filter = df['address'].str.contains('|'.join(sa_regions), na=False, case=False)
        else:
            # For other regions, check for exact region match
            region_filter = df['address'].str.contains(TARGET_REGION, na=False, case=False)

        df = df[region_filter | df['address'].isnull()]

        # Fill missing values
        df = df.fillna('N/A')

        # Add row numbers
        df.reset_index(drop=True, inplace=True)
        df['id'] = df.index + 1

        return df

    def clean_phone(self, phone):
        """
        Clean phone number format.
        """
        if not phone or phone == 'N/A':
            return 'N/A'
        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        # Apply local format, e.g., Lesotho: 6xx xxx xxx or +266 xxx xxx xxx
        if len(digits) == 9 and digits.startswith('6'):
            return f"6{digits[1:3]} {digits[3:6]} {digits[6:]}"
        elif len(digits) == 12 and digits.startswith('266'):
            digits = digits[3:]
            return f"+266 {digits[:3]} {digits[3:6]} {digits[6:]}"
        else:
            return phone  # Leave as is if unknown format

if __name__ == '__main__':
    # Test with sample data
    sample_data = [
        {'name': 'ABC Realty', 'phone': '61234567', 'address': 'Maseru, Lesotho'},
        {'name': 'ABC Realty', 'phone': '61234567', 'address': 'Maseru, Lesotho'},
        {'name': 'DEF Agents', 'phone': '62349875', 'address': 'Butha-Buthe, Lesotho'},
    ]
    df = pd.DataFrame(sample_data)
    cleaner = LeadCleaner()
    cleaned_df = cleaner.clean_leads(df)
    print(cleaned_df)
