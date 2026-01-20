import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import pandas as pd

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Config
config_mock = MagicMock()
config_mock.Config.TARGET_OWNERS = ['Owner A']
config_mock.Config.OPENAI_API_KEY = 'fake'
config_mock.Config.AI_MODEL = 'gpt-4o-mini'
sys.modules['config'] = config_mock

# Mock OpenAI
openai_mock = MagicMock()
sys.modules['openai'] = openai_mock

from crm_analyzer import CRMAnalyzer
from config import Config

class TestCRMAnalyzer(unittest.TestCase):

    def setUp(self):
        # Create a mock DataFrame with correct columns
        cols = [f"Col{i}" for i in range(22)]
        data = [
            # Account, ..., Brand(11), Product(12), ..., Value(17), Owner(18), Status(19), Note(20), Comp(21)
            ["Acc1"] + [""]*10 + ["BrandX", "Prod1", "", "", "", "", 1000, "Owner A", "Open", "Note", ""]
        ]
        self.df = pd.DataFrame(data, columns=cols)

        # Override Config for test (though mocking sys.modules should cover it)
        Config.TARGET_OWNERS = ['Owner A']
        Config.OPENAI_API_KEY = 'fake'
        Config.AI_MODEL = 'gpt-4'

    def test_init_validation(self):
        # Test validation of column count
        bad_df = pd.DataFrame([['A']*10]) # Only 10 columns
        with self.assertRaisesRegex(ValueError, "requires at least 22 columns"):
            CRMAnalyzer(bad_df)

    def test_analysis_logic(self):
        analyzer = CRMAnalyzer(self.df)
        self.assertEqual(len(analyzer.df), 1)
        self.assertEqual(analyzer.df.iloc[0]['col_18'], 'Owner A')
        self.assertEqual(analyzer.df.iloc[0]['col_17'], 1000)

    def test_generate_report(self):
        # Setup the mock for OpenAI
        # crm_analyzer imports OpenAI from openai module
        # We mocked sys.modules['openai'], so crm_analyzer.OpenAI is a Mock

        mock_client = openai_mock.OpenAI.return_value
        mock_client.chat.completions.create.return_value.choices = [
            MagicMock(message=MagicMock(content="<ul><li>AI Insight</li></ul>"))
        ]

        analyzer = CRMAnalyzer(self.df)
        report = analyzer.generate_report()

        self.assertIn("CRM Summary", report)
        self.assertIn("Owner A", report)
        self.assertIn("AI Insight", report)

if __name__ == '__main__':
    unittest.main()
