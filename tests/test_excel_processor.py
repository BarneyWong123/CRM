import unittest
from unittest.mock import MagicMock, patch
import sys
import os
import pandas as pd

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from excel_processor import ExcelProcessor
import config

class TestExcelProcessor(unittest.TestCase):

    def setUp(self):
        # Ensure Config has the right values even if mocked by other tests
        if isinstance(config.Config, MagicMock) or hasattr(config.Config, 'TARGET_SHEET_NAME'):
             config.Config.TARGET_SHEET_NAME = 'MY-Clinical'
             config.Config.EXCEL_HEADER_ROW = 2

        self.processor = ExcelProcessor()
        # Create a mock excel file
        self.filename = "tests/test_mock_data.xlsx"
        self._create_mock_excel(self.filename)

    def tearDown(self):
        if os.path.exists(self.filename):
            os.remove(self.filename)

    def _create_mock_excel(self, filename):
        cols = [f"Col{i}" for i in range(22)]
        data = [["Data"] * 22]

        from openpyxl import Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = "MY-Clinical"

        # Row 1 (Index 1) - Garbage
        ws.append(["Row 1"] * 22)
        # Row 2 (Index 2) - Garbage
        ws.append(["Row 2"] * 22)
        # Row 3 (Index 3) - Header
        ws.append(cols)
        # Row 4 (Index 4) - Data
        for row in data:
            ws.append(row)

        wb.save(filename)

    def test_extract_sheet_default(self):
        # Should use Config.EXCEL_HEADER_ROW which is 2
        df = self.processor.extract_sheet(self.filename, header_row=2)
        self.assertIsNotNone(df)
        self.assertEqual(list(df.columns), [f"Col{i}" for i in range(22)])
        self.assertEqual(len(df), 1)

    def test_extract_sheet_wrong_header(self):
        # If we use header=0, we get "Row 1" as header
        df = self.processor.extract_sheet(self.filename, header_row=0)
        self.assertIsNotNone(df)
        self.assertIn("Row 1", df.columns[0])

if __name__ == '__main__':
    unittest.main()
