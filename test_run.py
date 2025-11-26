import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import tempfile
import shutil
from scrapers.scraper import LeadScraper

class TestLeadGeneration(unittest.TestCase):

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

        # Create test directories
        os.makedirs('reports', exist_ok=True)
        os.makedirs('exports', exist_ok=True)

        # Sample test data
        self.sample_df = pd.DataFrame([
            {'name': 'Test Realty', 'phone': '6 12 345 678', 'address': 'Test St, Maseru', 'category': 'real_estate'},
            {'name': 'Sample Agents', 'phone': '6 23 456 789', 'address': 'Sample Rd, Qoaling', 'category': 'real_estate'},
            {'name': 'Demo Realty', 'phone': '6 34 567 890', 'address': 'Demo Ave, Butha-Buthe', 'category': 'real_estate'},
        ])

    def tearDown(self):
        """Clean up test fixtures after each test method."""
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    @patch('builtins.input')
    @patch('scrapers.scraper.LeadScraper.scrape_leads')
    @patch('cleaner.cleaner.LeadCleaner.clean_leads')
    @patch('reports.generate_pdf.LeadReportPDF.generate')
    @patch('reports.generate_excel.LeadReportExcel.generate')
    def test_full_pipeline_basic_package(self, mock_excel_gen, mock_pdf_gen, mock_clean, mock_scrape, mock_input):
        """Test the full pipeline with basic package selection."""
        # Mock user inputs
        mock_input.side_effect = ['real_estate', 'basic']

        # Mock scraper return
        mock_scrape.return_value = self.sample_df

        # Mock cleaner return (add id column)
        cleaned_df = self.sample_df.copy()
        cleaned_df['id'] = range(1, len(cleaned_df) + 1)
        mock_clean.return_value = cleaned_df

        # Mock generators return filenames
        mock_pdf_gen.return_value = 'reports/basic_20231126.pdf'
        mock_excel_gen.return_value = 'exports/basic_leads_20231126.xlsx'

        # Import and run main function
        from run import main
        main()

        # Verify scraper was called with correct niche
        mock_scrape.assert_called_once_with('real_estate')

        # Verify cleaner was called
        mock_clean.assert_called_once()

        # Verify PDF generator was called with basic package
        mock_pdf_gen.assert_called_once()
        pdf_call_args = mock_pdf_gen.call_args[0]
        self.assertEqual(pdf_call_args[1], 'basic')  # package parameter

        # Verify Excel generator was called with basic package
        mock_excel_gen.assert_called_once()
        excel_call_args = mock_excel_gen.call_args[0]
        self.assertEqual(excel_call_args[1], 'basic')  # package parameter

    @patch('builtins.input')
    @patch('scrapers.scraper.LeadScraper.scrape_leads')
    @patch('cleaner.cleaner.LeadCleaner.clean_leads')
    def test_pipeline_with_empty_data(self, mock_clean, mock_scrape, mock_input):
        """Test pipeline behavior when no leads are scraped."""
        # Mock user inputs
        mock_input.side_effect = ['real_estate', 'basic']

        # Mock empty scraper return
        mock_scrape.return_value = pd.DataFrame()

        # Mock cleaner return empty
        mock_clean.return_value = pd.DataFrame()

        # Import and run main function
        from run import main

        # Should handle empty data gracefully
        main()

        # Verify scraper was called
        mock_scrape.assert_called_once_with('real_estate')

        # Verify cleaner was called even with empty data
        mock_clean.assert_called_once()

    @patch('builtins.input')
    @patch('scrapers.scraper.LeadScraper.scrape_leads')
    @patch('cleaner.cleaner.LeadCleaner.clean_leads')
    @patch('reports.generate_pdf.LeadReportPDF.generate')
    @patch('reports.generate_excel.LeadReportExcel.generate')
    def test_standard_package(self, mock_excel_gen, mock_pdf_gen, mock_clean, mock_scrape, mock_input):
        """Test pipeline with standard package."""
        # Mock user inputs
        mock_input.side_effect = ['tutors', 'standard']

        # Mock scraper return with more data
        large_df = pd.concat([self.sample_df] * 10, ignore_index=True)  # 30 leads
        mock_scrape.return_value = large_df

        # Mock cleaner return
        cleaned_df = large_df.copy()
        cleaned_df['id'] = range(1, len(cleaned_df) + 1)
        mock_clean.return_value = cleaned_df

        # Mock generators
        mock_pdf_gen.return_value = 'reports/standard_20231126.pdf'
        mock_excel_gen.return_value = 'exports/standard_leads_20231126.xlsx'

        from run import main
        main()

        # Verify correct niche
        mock_scrape.assert_called_once_with('tutors')

        # Verify standard package used
        pdf_call_args = mock_pdf_gen.call_args[0]
        self.assertEqual(pdf_call_args[1], 'standard')

        excel_call_args = mock_excel_gen.call_args[0]
        self.assertEqual(excel_call_args[1], 'standard')

    def test_directory_creation(self):
        """Test that required directories are created."""
        # Directories should be created during setup
        self.assertTrue(os.path.exists('reports'))
        self.assertTrue(os.path.exists('exports'))

    @patch('builtins.input')
    def test_invalid_niche_fallback(self, mock_input):
        """Test that invalid niche falls back to default."""
        mock_input.side_effect = ['invalid_niche', 'basic']

        with patch('scrapers.scraper.LeadScraper.scrape_leads') as mock_scrape:
            with patch('cleaner.cleaner.LeadCleaner.clean_leads') as mock_clean:
                with patch('reports.generate_pdf.LeadReportPDF.generate') as mock_pdf:
                    with patch('reports.generate_excel.LeadReportExcel.generate') as mock_excel:
                        mock_scrape.return_value = self.sample_df
                        mock_clean.return_value = self.sample_df
                        mock_pdf.return_value = 'test.pdf'
                        mock_excel.return_value = 'test.xlsx'

                        from run import main
                        main()

                        # Should use default real_estate
                        mock_scrape.assert_called_once_with('real_estate')

    @patch('builtins.input')
    def test_invalid_package_fallback(self, mock_input):
        """Test that invalid package falls back to basic."""
        mock_input.side_effect = ['real_estate', 'invalid_package']

        with patch('scrapers.scraper.LeadScraper.scrape_leads') as mock_scrape:
            with patch('cleaner.cleaner.LeadCleaner.clean_leads') as mock_clean:
                with patch('reports.generate_pdf.LeadReportPDF.generate') as mock_pdf:
                    with patch('reports.generate_excel.LeadReportExcel.generate') as mock_excel:
                        mock_scrape.return_value = self.sample_df
                        mock_clean.return_value = self.sample_df
                        mock_pdf.return_value = 'test.pdf'
                        mock_excel.return_value = 'test.xlsx'

                        from run import main
                        main()

                        # Should use basic package
                        pdf_call_args = mock_pdf.call_args[0]
                        self.assertEqual(pdf_call_args[1], 'basic')

    def test_yep_source_real_estate(self):
        """Test scraping specifically from Yep source for real estate."""
        with patch('scrapers.scraper.requests.get') as mock_get:
            # Mock response for Yep
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.text = '''
            <html>
            <body>
                <div class="item">
                    <h2>ABC Realty</h2>
                    <span class="address">123 Main St, Johannesburg</span>
                    <span class="phone">011 123 4567</span>
                </div>
                <div class="card">
                    <h2>XYZ Properties</h2>
                    <span class="address">456 Oak Ave, Cape Town</span>
                    <span class="phone">021 987 6543</span>
                </div>
                <div class="result">
                    <h2>DEF Estates</h2>
                    <span class="address">789 Pine Rd, Durban</span>
                    <span class="phone">031 555 1234</span>
                </div>
            </body>
            </html>
            '''
            mock_get.return_value = mock_response

            scraper = LeadScraper()
            df = scraper.scrape_leads('real_estate', max_pages=1)

            # Should find 3 leads from the mocked Yep response
            self.assertEqual(len(df), 3)
            self.assertIn('ABC Realty', df['name'].values)
            self.assertIn('XYZ Properties', df['name'].values)
            self.assertIn('DEF Estates', df['name'].values)

if __name__ == '__main__':
    unittest.main()
