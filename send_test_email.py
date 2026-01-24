"""Script to send a test email to verify CRM analyzer configuration."""
from config import Config
from gmail_client import GmailClient
from datetime import datetime

def send_test():
    print("Initializing Gmail Client...")
    try:
        Config.validate()
    except Exception as e:
        print(f"❌ Configuration Error: {e}")
        return

    gmail = GmailClient()
    
    recipient = Config.SUMMARY_RECIPIENT
    subject = f"Test Email from CRM Analyzer - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    html_body = f"""
    <html>
        <body>
            <h1 style="color: #2c3e50;">CRM Analyzer Test</h1>
            <p>This is a test email sent from the CRM Analyzer automation script.</p>
            <p><strong>Configured Recipient:</strong> {recipient}</p>
            <p><strong>Time Sent:</strong> {datetime.now().strftime('%B %d, %Y at %H:%M:%S')}</p>
            <hr>
            <p style="font-size: 0.8em; color: #7f8c8d;">This email was generated automatically to verify SMTP connectivity.</p>
        </body>
    </html>
    """
    
    print(f"Sending test email to {recipient}...")
    gmail.send_email(recipient, subject, html_body)
    gmail.close()
    print("Done.")

if __name__ == "__main__":
    send_test()
