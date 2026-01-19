# Gmail IMAP Setup - Quick Guide

This application uses IMAP to connect to Gmail, which is much simpler than OAuth!

## Step 1: Enable 2-Factor Authentication

1. Go to your Google Account: https://myaccount.google.com/security
2. Under "Signing in to Google", enable **2-Step Verification** if not already enabled
3. Follow the prompts to set it up

## Step 2: Generate App Password

1. Go to: https://myaccount.google.com/apppasswords
2. Sign in if prompted
3. In the "App name" field, type: **File Automation Analyzer**
4. Click **Create**
5. Google will show you a 16-character password (like: `abcd efgh ijkl mnop`)
6. **Copy this password** - you'll need it in the next step

## Step 3: Update .env File

Edit the `.env` file in the project directory:

```bash
GMAIL_EMAIL=your-email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
SEARCH_DAYS_BACK=7
```

**Important:** 
- Remove spaces from the app password (use `abcdefghijklmnop` not `abcd efgh ijkl mnop`)
- Use your actual Gmail address
- `SEARCH_DAYS_BACK` controls how far back to search for emails

## Step 4: Run the Application

```bash
cd /Users/barneywong/.gemini/antigravity/file-automation-analyzer
./venv/bin/python main.py
```

That's it! The application will:
1. Connect to your Gmail via IMAP
2. Search for emails with Excel attachments
3. Download the Excel files
4. Extract the "MY-Clinical" sheet
5. Save as CSV files

## Troubleshooting

**"Authentication failed"**
- Double-check your email and app password in `.env`
- Make sure there are no spaces in the app password
- Verify 2-Step Verification is enabled

**"No messages found"**
- Try increasing `SEARCH_DAYS_BACK` in `.env`
- Make sure you have emails with Excel attachments in your inbox

**"IMAP access disabled"**
- Go to Gmail settings → Forwarding and POP/IMAP
- Enable IMAP access

## Security Note

The app password is stored in `.env` which is excluded from git by `.gitignore`. Keep this file secure and never share it.
