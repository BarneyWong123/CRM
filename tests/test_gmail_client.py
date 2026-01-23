import unittest
from unittest.mock import patch, MagicMock
from gmail_client import GmailClient
from config import Config

class TestGmailClient(unittest.TestCase):
    @patch('gmail_client.imaplib.IMAP4_SSL')
    def test_connect(self, mock_imap):
        client = GmailClient()
        mock_imap.assert_called_with(Config.IMAP_SERVER, Config.IMAP_PORT)
        client.imap.login.assert_called_with(Config.GMAIL_EMAIL, Config.GMAIL_APP_PASSWORD)

    @patch('gmail_client.imaplib.IMAP4_SSL')
    @patch('gmail_client.smtplib.SMTP_SSL')
    def test_send_email(self, mock_smtp, mock_imap):
        client = GmailClient()

        mock_server = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_server

        client.send_email('to@example.com', 'Subject', '<body></body>')

        mock_smtp.assert_called_with(Config.SMTP_SERVER, Config.SMTP_PORT)
        mock_server.login.assert_called_with(Config.GMAIL_EMAIL, Config.GMAIL_APP_PASSWORD)
        mock_server.send_message.assert_called()

    @patch('gmail_client.imaplib.IMAP4_SSL')
    def test_fetch_emails_with_attachments_no_emails(self, mock_imap):
        client = GmailClient()

        # Mock search return
        client.imap.select.return_value = ('OK', [b'1'])
        client.imap.search.return_value = ('OK', [None]) # No messages

        emails = client.fetch_emails_with_attachments()
        self.assertEqual(emails, [])
