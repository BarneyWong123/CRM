"""Gmail client using IMAP and SMTP for robust autonomous operation."""
import imaplib
import smtplib
import email
from email.header import decode_header
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import base64
from typing import List, Dict, Optional
from datetime import datetime, timedelta
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
                # Strictly fail if label not found to avoid unintended processing
                print(f"❌ Label '{Config.EMAIL_LABEL}' not found. Please create this label in Gmail.")
                return []

            # Calculate date for search
            since_date = (datetime.now() - timedelta(days=Config.SEARCH_DAYS_BACK)).strftime("%d-%b-%Y")
            print(f"Searching for emails since {since_date}...")

            # Search for messages since date
            # Note: IMAP search criteria are space-separated
            status, messages = self.imap.search(None, f'(SINCE "{since_date}")')
            
            if status != 'OK' or not messages[0]:
                print("No emails found in search criteria.")
                return []
            
            email_ids = messages[0].split()
            print(f"Found {len(email_ids)} emails in '{Config.EMAIL_LABEL}' since {since_date}...")
            
            emails = []
            # Check last 10 (or all if less than 10) for performance
            # If we want to process all, we can remove the slicing, but slicing is safer for large results
            # Given we have a date filter, maybe we should process all returned?
            # But the original logic had deduplication. Let's stick to last 20 to be safe but better than 10.
            ids_to_check = email_ids[-20:] if len(email_ids) > 20 else email_ids

            for email_id in reversed(ids_to_check):
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
        try:
            decoded_parts = decode_header(header)
            return "".join([
                (p.decode(e or 'utf-8') if isinstance(p, bytes) else p)
                for p, e in decoded_parts
            ])
        except Exception:
            # Fallback if decoding fails
            try:
                return str(header)
            except:
                return "Unknown Header"

    def close(self):
        if self.imap:
            try:
                self.imap.logout()
            except: pass
