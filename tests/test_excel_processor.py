import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from excel_processor import ExcelProcessor
from config import Config

class TestExcelProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = ExcelProcessor()

    @patch('excel_processor.os.path.exists')
    @patch('excel_processor.load_workbook')
    @patch('excel_processor.pd.read_excel')
    def test_extract_sheet_success(self, mock_read_excel, mock_load_workbook, mock_exists):
        mock_exists.return_value = True

        # Mock workbook sheetnames
        mock_wb = MagicMock()
        mock_wb.sheetnames = [Config.TARGET_SHEET_NAME, 'OtherSheet']
        mock_load_workbook.return_value = mock_wb

        # Mock dataframe
        mock_df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        mock_read_excel.return_value = mock_df

        df = self.processor.extract_sheet('dummy.xlsx', header_row=2)

        self.assertIsNotNone(df)
        self.assertEqual(len(df), 2)
        mock_load_workbook.assert_called_with('dummy.xlsx', read_only=True)
        mock_read_excel.assert_called_with('dummy.xlsx', sheet_name=Config.TARGET_SHEET_NAME, header=2)

    @patch('excel_processor.os.path.exists')
    def test_extract_sheet_file_not_found(self, mock_exists):
        mock_exists.return_value = False
        df = self.processor.extract_sheet('nonexistent.xlsx')
        self.assertIsNone(df)

    @patch('excel_processor.os.path.exists')
    @patch('excel_processor.load_workbook')
    def test_extract_sheet_sheet_not_found(self, mock_load_workbook, mock_exists):
        mock_exists.return_value = True

        mock_wb = MagicMock()
        mock_wb.sheetnames = ['OtherSheet']
        mock_load_workbook.return_value = mock_wb

        df = self.processor.extract_sheet('dummy.xlsx')
        self.assertIsNone(df)
