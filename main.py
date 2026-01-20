"""Fully autonomous CRM Analyzer runner."""
import time
import os
import pandas as pd
from config import Config
from gmail_client import GmailClient
from excel_processor import ExcelProcessor
from crm_analyzer import CRMAnalyzer
from state_manager import StateManager
from datetime import datetime

def run_once(gmail, processor, state):
    """Perform a single check-and-process cycle."""
    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking for new CRM emails...")
    
    emails = gmail.fetch_emails_with_attachments()
    
    # Filter for unprocessed IDs
    new_emails = [e for e in emails if not state.is_processed(e['id'])]
    
    if not new_emails:
        print("No new emails found.")
        return
    
    print(f"Found {len(new_emails)} new email(s). Processing...")
    
    for email_data in new_emails:
        print(f"Processing: '{email_data['subject']}' from {email_data['from']}")
        
        for att in email_data['attachments']:
            try:
                filename = os.path.basename(att['filename'])
                filepath = os.path.join(Config.DOWNLOAD_DIR, filename)
                
                # Save attachment
                with open(filepath, 'wb') as f:
                    f.write(att['payload'])
                
                print(f"✓ Downloaded {filename}")
                
                # Analyze
                df_precise = processor.extract_sheet(filepath, header_row=Config.EXCEL_HEADER_ROW)
                if df_precise is None:
                    print(f"Skipping analysis for {filename} (Sheet extraction failed)")
                    continue

                analyzer = CRMAnalyzer(df_precise)
                html_report = analyzer.generate_report()
                
                # Send Summary
                date_str = datetime.now().strftime("%B %d, %Y")
                subject = f"CRM summary - {date_str}"
                gmail.send_email(Config.SUMMARY_RECIPIENT, subject, html_report)
                
                # Record as processed
                state.mark_processed(email_data['id'])
                
            except Exception as e:
                print(f"❌ Error processing {att['filename']}: {e}")
                # Optional: mark as processed anyway to avoid infinite loops on bad files
                # state.mark_processed(email_data['id'])

def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--once", action="store_true", help="Run once and exit (for cloud jobs)")
    args = parser.parse_args()

    print("="*80)
    print("AUTONOMOUS CRM ANALYZER (IMAP/SMTP MODE)")
    print("="*80)
    
    try:
        Config.validate()
    except ValueError as e:
        print(f"❌ Config Error: {e}")
        return

    gmail = GmailClient()
    processor = ExcelProcessor()
    state = StateManager(Config.STATE_FILE)
    
    print(f"Trigger: Emails in label '{Config.EMAIL_LABEL}'")
    print(f"Recipient: {Config.SUMMARY_RECIPIENT}")
    print(f"Polling Interval: 60s")
    print("Press Ctrl+C to stop.")
    
    # Run once immediately
    print("\n--- Initial catch-up check ---")
    try:
        run_once(gmail, processor, state)
    except Exception as e:
        print(f"❌ Initial check error: {e}")
        
    if args.once:
        print("\nSingle run complete (--once flag). Exiting.")
        gmail.close()
        return

    try:
        while True:
            try:
                run_once(gmail, processor, state)
            except Exception as e:
                print(f"⚠ Cycle error: {e}. Retrying in 10s...")
                time.sleep(10)
                continue
                
            time.sleep(60) # Poll every minute for "instant" trigger
    except KeyboardInterrupt:
        print("\nStopping automation...")
    finally:
        gmail.close()

if __name__ == "__main__":
    main()
