import pandas as pd
import re
from config import TARGET_REGION

class LeadCleaner:
    def __init__(self):
        pass

    def clean_leads(self, df):
        """
        Clean and filter the leads DataFrame, add quality scoring.
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

        # Add quality score
        df['score'] = df.apply(self.calculate_lead_score, axis=1)

        # Sort by score descending
        df = df.sort_values('score', ascending=False)

        # Add row numbers
        df.reset_index(drop=True, inplace=True)
        df['id'] = df.index + 1

        return df

    def calculate_lead_score(self, lead):
        """
        Calculate lead quality score.
        """
        score = 0
        if lead['phone'] and lead['phone'] != 'N/A':
            score += 30
        # Assuming email not collected yet, but placeholder
        # if lead.get('email'): score += 20
        # For now, assume location match if address is not N/A
        if lead['address'] and lead['address'] != 'N/A':
            score += 25
        # Placeholder for recent activity
        # if lead.get('recent_activity'): score += 25
        return score

    def clean_phone(self, phone):
        """
        Clean phone number format.
        """
        if not phone or phone == 'N/A':
            return 'N/A'
        # Remove non-digits
        digits = re.sub(r'\D', '', phone)
        # Apply South African format
        if len(digits) == 10 and digits.startswith('0'):
            return f"0{digits[1:3]} {digits[3:6]} {digits[6:]}"
        elif len(digits) == 9:
            return f"0{digits[0:2]} {digits[2:5]} {digits[5:]}"
        elif len(digits) == 12 and digits.startswith('27'):
            digits = digits[2:]
            return f"0{digits[0:2]} {digits[2:5]} {digits[5:]}"
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
