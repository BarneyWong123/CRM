"""Gmail client using IMAP and SMTP for robust autonomous operation."""
import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import base64
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config import Config


class GmailClient:
    """Robust client using IMAP for fetching and SMTP for sending."""
    
    def __init__(self):
        """Initialize connections."""
        self.imap = None
        self.connect()
    
    def connect(self):
        """Connect to Gmail IMAP."""
        try:
            print(f"Connecting to Gmail IMAP...")
            self.imap = imaplib.IMAP4_SSL(Config.IMAP_SERVER, Config.IMAP_PORT)
            self.imap.login(Config.GMAIL_EMAIL, Config.GMAIL_APP_PASSWORD)
            print(f"✓ IMAP Connected as {Config.GMAIL_EMAIL}")
        except Exception as e:
            raise ConnectionError(f"IMAP Connection failed: {e}")

    def send_email(self, to: str, subject: str, html_body: str):
        """Send HTML email via SMTP."""
        try:
            msg = MIMEMultipart()
            msg['From'] = Config.GMAIL_EMAIL
            msg['To'] = to
            msg['Subject'] = subject
            
            msg.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP_SSL(Config.SMTP_SERVER, Config.SMTP_PORT) as server:
                server.login(Config.GMAIL_EMAIL, Config.GMAIL_APP_PASSWORD)
                server.send_message(msg)
            
            print(f"✓ Email sent to {to}: {subject}")
        except Exception as e:
            print(f"❌ SMTP Error: {e}")

    def fetch_emails_with_attachments(self) -> List[Dict]:
        """Fetch emails from the 'CRM' label with Excel attachments."""
        try:
            # Refresh connection if needed
            try:
                self.imap.noop()
            except:
                self.connect()
            
            # Select the CRM label (Gmail uses label names as folders in IMAP)
            status, _ = self.imap.select(f'"{Config.EMAIL_LABEL}"')
            if status != 'OK':
                # Fallback to INBOX if label not found
                self.imap.select('INBOX')
                print(f"⚠ Label '{Config.EMAIL_LABEL}' not found, checking INBOX...")
            
            # Calculate date for SINCE criteria
            since_date = (datetime.now() - timedelta(days=Config.SEARCH_DAYS_BACK)).strftime("%d-%b-%Y")

            # Search for messages since that date
            print(f"Searching for emails since {since_date}...")
            status, messages = self.imap.search(None, f'(SINCE "{since_date}")')

            if status != 'OK' or not messages[0]:
                return []
            
            email_ids = messages[0].split()
            print(f"Checking {len(email_ids)} emails in '{Config.EMAIL_LABEL}'...")
            
            emails = []
            # Check last 10 for performance in polling
            for email_id in reversed(email_ids[-10:]):
                email_data = self._get_message_details(email_id)
                if email_data and email_data['attachments']:
                    emails.append(email_data)
                    
            return emails
            
        except Exception as e:
            print(f"❌ Error fetching emails: {e}")
            return []

    def _get_message_details(self, email_id: bytes) -> Optional[Dict]:
        """Fetch and parse email metadata and attachments."""
        try:
            status, msg_data = self.imap.fetch(email_id, '(RFC822)')
            if status != 'OK': return None
            
            msg = email.message_from_bytes(msg_data[0][1])
            
            # Use Message-ID as a unique identifier for deduplication
            msg_id_header = msg.get('Message-ID', email_id.decode())
            
            subject = self._decode_header(msg.get('Subject', 'No Subject'))
            sender = self._decode_header(msg.get('From', 'Unknown'))
            date = msg.get('Date', 'Unknown')
            
            attachments = []
            for part in msg.walk():
                if part.get_content_disposition() == 'attachment':
                    filename = part.get_filename()
                    if filename:
                        filename = self._decode_header(filename)
                        if filename.endswith(('.xlsx', '.xls')):
                            attachments.append({
                                'filename': filename,
                                'payload': part.get_payload(decode=True)
                            })
            
            return {
                'id': msg_id_header,
                'subject': subject,
                'from': sender,
                'date': date,
                'attachments': attachments
            }
        except Exception as e:
            print(f"Error parsing email {email_id}: {e}")
            return None

    def _decode_header(self, header: str) -> str:
        if not header: return ''
        decoded_parts = decode_header(header)
        return "".join([
            (p.decode(e or 'utf-8') if isinstance(p, bytes) else p) 
            for p, e in decoded_parts
        ])

    def close(self):
        if self.imap:
            try:
                self.imap.logout()
            except: pass
