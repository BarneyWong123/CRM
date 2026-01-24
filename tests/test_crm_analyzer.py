import unittest
import pandas as pd
from unittest.mock import MagicMock, patch
from crm_analyzer import CRMAnalyzer
from config import Config

class TestCRMAnalyzer(unittest.TestCase):
    def setUp(self):
        # Create a sample DataFrame
        # We need enough columns to avoid index errors.
        # Max index used is 20. So 21 columns.
        data = {f"col_{i}": [None]*2 for i in range(21)}

        # Populate relevant columns
        # Row 0: Target Owner, Open
        data['col_0'] = ['Account A', 'Account B'] # Account
        data['col_11'] = ['Brand X', 'Brand Y']    # Brand
        data['col_12'] = ['Prod 1', 'Prod 2']      # Product
        data['col_17'] = [1000, 5000]              # Value
        data['col_18'] = [Config.TARGET_OWNERS[0], 'Other Owner'] # Owner
        data['col_19'] = ['Open', 'Won']           # Status
        data['col_20'] = ['Note A', 'Note B']      # Notes

        self.df = pd.DataFrame(data)

        # We need to bypass the column renaming in __init__ because we passed a dict with already correct names
        # BUT the class renames them based on position.
        # So we should pass a dataframe with default integer columns or random names,
        # and ensure the positions are correct.

        data_list = [[None]*21 for _ in range(2)]

        # Row 0
        data_list[0][0] = 'Account A'
        data_list[0][11] = 'Brand X'
        data_list[0][12] = 'Prod 1'
        data_list[0][17] = 1000
        data_list[0][18] = Config.TARGET_OWNERS[0]
        data_list[0][19] = 'Open'
        data_list[0][20] = 'Note A'

        # Row 1 (Non-target owner)
        data_list[1][0] = 'Account B'
        data_list[1][11] = 'Brand Y'
        data_list[1][12] = 'Prod 2'
        data_list[1][17] = 5000
        data_list[1][18] = 'Other Owner'
        data_list[1][19] = 'Won'
        data_list[1][20] = 'Note B'

        self.raw_df = pd.DataFrame(data_list)

    def test_init_filters_owners(self):
        analyzer = CRMAnalyzer(self.raw_df)
        # Should only keep row 0
        self.assertEqual(len(analyzer.df), 1)
        self.assertEqual(analyzer.df.iloc[0]['col_0'], 'Account A')

    @patch('crm_analyzer.OpportunityTracker')
    @patch('crm_analyzer.CRMAnalyzer._get_ai_insights')
    def test_generate_report(self, mock_ai, mock_tracker_cls):
        # Mock the tracker instance and its methods
        mock_tracker_instance = mock_tracker_cls.return_value
        mock_tracker_instance.compare_and_update.return_value = ([], [])
        mock_tracker_instance.generate_changes_html.return_value = "<div>Changes</div>"

        mock_ai.return_value = "<ul><li>Insight 1</li></ul>"
        analyzer = CRMAnalyzer(self.raw_df)
        report = analyzer.generate_report()

        self.assertIn("CRM Summary", report)
        self.assertIn("Account A", report)
        self.assertNotIn("Account B", report) # Filtered out
        self.assertIn("Insight 1", report)

    def test_section_generation(self):
        analyzer = CRMAnalyzer(self.raw_df)
        html = analyzer._section2_executive_overview()
        self.assertIn("RM 1,000.00", html) # Check formatting
