import unittest
from unittest.mock import MagicMock, patch
import sys
import os
from datetime import datetime, timedelta

# Add root directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gmail_client import GmailClient
from config import Config

class TestGmailSearch(unittest.TestCase):

    @patch('imaplib.IMAP4_SSL')
    def test_search_criteria(self, mock_imap_cls):
        mock_imap = mock_imap_cls.return_value
        mock_imap.login.return_value = 'OK'
        mock_imap.select.return_value = ('OK', [b'1'])

        # Setup mock messages
        # Search returns 'OK', [b'1 2']
        mock_imap.search.return_value = ('OK', [b'1 2'])

        # Setup mock fetch
        mock_imap.fetch.return_value = ('OK', [(b'1', b'Message-ID: <1>\r\nSubject: Test\r\n\r\nBody')])

        client = GmailClient()

        # Set config days back
        Config.SEARCH_DAYS_BACK = 7
        Config.EMAIL_LABEL = 'CRM'

        # Mock decode_header to avoid complex mocking of email package
        with patch.object(client, '_get_message_details', return_value={'id': '1', 'attachments': []}):
            client.fetch_emails_with_attachments()

            # Verify search call
            since_date = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
            expected_criteria = f'(SINCE "{since_date}")'

            mock_imap.search.assert_called_with(None, expected_criteria)

if __name__ == '__main__':
    unittest.main()
