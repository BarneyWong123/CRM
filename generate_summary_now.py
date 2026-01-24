"""Quick script to generate and send CRM summary using existing downloaded file."""
from config import Config
from excel_processor import ExcelProcessor
from crm_analyzer import CRMAnalyzer
from gmail_client import GmailClient
from datetime import datetime
import os

def main():
    print("=" * 60)
    print("GENERATING CRM SUMMARY FROM EXISTING DATA")
    print("=" * 60)
    
    Config.validate()
    
    # Use the most recent CRM.xlsx file
    excel_path = os.path.join(Config.DOWNLOAD_DIR, 'CRM.xlsx')
    
    if not os.path.exists(excel_path):
        print(f"❌ Error: No CRM.xlsx found in {Config.DOWNLOAD_DIR}")
        return
    
    print(f"📁 Using file: {excel_path}")
    
    # Process Excel file
    processor = ExcelProcessor()
    df = processor.extract_sheet(excel_path)
    
    if df is None or df.empty:
        print("❌ Error: Could not extract MY-Clinical sheet")
        return
    
    print(f"✓ Loaded {len(df)} rows from MY-Clinical sheet")
    print(f"✓ Filtering to owners: {Config.TARGET_OWNERS}")
    
    # Generate report
    analyzer = CRMAnalyzer(df)
    print("📊 Generating HTML report with charts...")
    html_report = analyzer.generate_report()
    
    # Send email
    gmail = GmailClient()
    subject = f"CRM Summary Report - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    
    print(f"📧 Sending to: {Config.SUMMARY_RECIPIENT}")
    gmail.send_email(Config.SUMMARY_RECIPIENT, subject, html_report)
    gmail.close()
    
    print("=" * 60)
    print("✅ CRM Summary sent successfully!")
    print("=" * 60)

if __name__ == "__main__":
    main()
