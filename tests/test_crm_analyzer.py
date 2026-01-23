import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from crm_analyzer import CRMAnalyzer
from config import Config

class TestCRMAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a sample dataframe that matches expected structure
        # Columns 0-20 are expected.
        # col_18 is owner
        # col_19 is status
        # col_17 is value
        # col_11 is brand
        # col_12 is product
        # col_0 is account
        # col_20 is note

        # Create a list of dictionaries to build DataFrame
        rows = []

        # Row 0: Target Owner, Open
        row0 = {f'Existing_{i}': f'val_{i}' for i in range(22)}
        row0['Existing_18'] = Config.TARGET_OWNERS[0]
        row0['Existing_19'] = 'Open'
        row0['Existing_17'] = 1000
        row0['Existing_11'] = 'BrandA'
        rows.append(row0)

        # Row 1: Target Owner, Won
        row1 = {f'Existing_{i}': f'val_{i}' for i in range(22)}
        row1['Existing_18'] = Config.TARGET_OWNERS[0] # Assuming at least one target owner
        if len(Config.TARGET_OWNERS) > 1:
             row1['Existing_18'] = Config.TARGET_OWNERS[1]
        row1['Existing_19'] = 'Won'
        row1['Existing_17'] = 2000
        row1['Existing_11'] = 'BrandB'
        rows.append(row1)

        # Row 2: Other Owner (Should be filtered out)
        row2 = {f'Existing_{i}': f'val_{i}' for i in range(22)}
        row2['Existing_18'] = 'Other Owner'
        row2['Existing_19'] = 'Open'
        rows.append(row2)

        self.df = pd.DataFrame(rows)

    @patch('crm_analyzer.plt')
    @patch('crm_analyzer.CRMAnalyzer._get_ai_insights')
    def test_generate_report(self, mock_get_ai, mock_plt):
        mock_get_ai.return_value = "<ul><li>Insight 1</li></ul>"

        # Mock figure and savefig
        mock_fig = MagicMock()
        mock_plt.figure.return_value = None # figure() returns None usually, but we need gcf
        mock_plt.gcf.return_value = mock_fig

        analyzer = CRMAnalyzer(self.df)
        report = analyzer.generate_report()

        self.assertIn("CRM Summary", report)
        self.assertIn("BrandA", report)
        self.assertIn("BrandB", report)
        self.assertIn("Insight 1", report)

        # Verify filtered df
        # Total rows should be 2 (Row 0 and Row 1)
        self.assertEqual(len(analyzer.df), 2)

    def test_init_filtering(self):
        analyzer = CRMAnalyzer(self.df)
        self.assertEqual(len(analyzer.df), 2)
        self.assertTrue(all(analyzer.df['col_18'].isin(Config.TARGET_OWNERS)))
