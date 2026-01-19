# File Automation Analyzer

Automatically connects to Gmail via IMAP, downloads Excel file attachments, and extracts the "MY-Clinical" sheet for analysis.

## Features

- 🔐 Simple IMAP authentication (no OAuth needed!)
- 📧 Automatic email fetching with Excel attachment filtering
- 📊 Excel file processing with specific sheet extraction
- 📈 Data preview and summary statistics
- 💾 CSV export functionality

## Quick Setup (3 Steps!)

### 1. Install Dependencies

```bash
cd /Users/barneywong/.gemini/antigravity/file-automation-analyzer

# Install packages (already done if you set up earlier)
./venv/bin/pip install -r requirements.txt
```

### 2. Get Gmail App Password

1. Go to https://myaccount.google.com/apppasswords
2. Create an app password named "File Automation Analyzer"
3. Copy the 16-character password

**Detailed instructions:** See [SETUP_IMAP.md](SETUP_IMAP.md)

### 3. Configure .env File

Edit `.env`:

```bash
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=your16charpassword
SEARCH_DAYS_BACK=7
```

## Run the Application

```bash
./venv/bin/python main.py
```

The app will:
1. Connect to Gmail via IMAP
2. Search for emails with Excel attachments (last 7 days)
3. Download Excel files to `downloads/` directory
4. Extract the "MY-Clinical" sheet
5. Display data preview
6. Save as CSV files

## Configuration

Edit `.env` to customize:

```bash
# Your Gmail credentials
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop

# How many days back to search for emails
SEARCH_DAYS_BACK=7
```

## Project Structure

```
file-automation-analyzer/
├── main.py              # Main application
├── gmail_client.py      # IMAP Gmail client
├── excel_processor.py   # Excel processing
├── config.py           # Configuration
├── requirements.txt    # Dependencies
├── .env                # Your credentials (not in git)
├── SETUP_IMAP.md      # Setup instructions
└── downloads/         # Downloaded files
```

## Output Example

```
================================================================================
FILE AUTOMATION ANALYZER
================================================================================

Connecting to Gmail IMAP server...
✓ Successfully connected as your-email@gmail.com

Searching for emails with attachments from the last 7 days...
✓ Found 2 email(s) with Excel attachments

================================================================================
FOUND EMAILS WITH EXCEL ATTACHMENTS:
================================================================================

1. Subject: Monthly Report
   From: sender@example.com
   Date: Mon, 19 Jan 2026 10:30:00 +0800
   Attachments:
     - data.xlsx (245678 bytes)

✓ Downloaded: data.xlsx (245678 bytes)
✓ Successfully extracted sheet 'MY-Clinical'
  Rows: 150, Columns: 12

✓ Saved to CSV: downloads/data_MY-Clinical.csv

================================================================================
SUMMARY: Successfully processed 1 file(s)
================================================================================
```

## Troubleshooting

**"Authentication failed"**
- Check your email and app password in `.env`
- Remove spaces from app password
- Enable 2-Step Verification in Google Account

**"No messages found"**
- Increase `SEARCH_DAYS_BACK` in `.env`
- Check if you have emails with Excel attachments

**"Sheet 'MY-Clinical' not found"**
- The Excel file doesn't have this sheet
- Check available sheets in the output
- Update `TARGET_SHEET_NAME` in `config.py`

## Security

- `.env` file is excluded from git
- Never commit your app password
- App passwords can be revoked anytime at https://myaccount.google.com/apppasswords

## License

MIT
