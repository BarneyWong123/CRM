"""Configuration management for the autonomous CRM analyzer."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration."""
    
    # Gmail Credentials (IMAP/SMTP)
    GMAIL_EMAIL = os.getenv('GMAIL_EMAIL')
    GMAIL_APP_PASSWORD = os.getenv('GMAIL_APP_PASSWORD')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Servers
    IMAP_SERVER = 'imap.gmail.com'
    SMTP_SERVER = 'smtp.gmail.com'
    IMAP_PORT = 993
    SMTP_PORT = 465
    
    # Email search settings
    # We poll for the CRM label
    EMAIL_LABEL = 'CRM'
    SEARCH_DAYS_BACK = int(os.getenv('SEARCH_DAYS_BACK', '7'))
    
    # Analysis settings
    TARGET_OWNERS = ['Arora Johney', 'Jiun Hao (Barney) Wong']
    SUMMARY_RECIPIENT = 'barney.w@biomedglobal.com'
    
    # Automated Scheduling
    DAILY_SCHEDULE_TIME = "18:00"
    POLL_INTERVAL_SECONDS = 300  # Poll every 5 minutes to stay within bandwidth limits
    
    # AI Settings
    AI_MODEL = "gpt-4o-mini"
    
    # Excel processing settings
    TARGET_SHEET_NAME = 'MY-Clinical'
    DOWNLOAD_DIR = 'downloads'
    STATE_FILE = 'processed_messages.json'
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.GMAIL_EMAIL or not cls.GMAIL_APP_PASSWORD:
            raise ValueError("GMAIL_EMAIL and GMAIL_APP_PASSWORD must be set in .env")
        
        # Create download directory if it doesn't exist
        os.makedirs(cls.DOWNLOAD_DIR, exist_ok=True)
