# Gmail OAuth Setup Instructions

Since you've provided a Gmail API key, we need to set up OAuth 2.0 credentials to access Gmail.

## Quick Setup Steps:

### 1. Go to Google Cloud Console
Visit: https://console.cloud.google.com

### 2. Select or Create a Project
- Use your existing project (if you have one)
- Or create a new project

### 3. Enable Gmail API
- Go to "APIs & Services" → "Library"
- Search for "Gmail API"
- Click "Enable"

### 4. Create OAuth Credentials
- Go to "APIs & Services" → "Credentials"
- Click "Create Credentials" → "OAuth 2.0 Client ID"
- If prompted, configure the OAuth consent screen:
  - Choose "External" user type
  - Fill in required fields (app name, user support email)
  - Add your email as a test user
  - Save and continue
- Choose "Desktop app" as the application type
- Name it (e.g., "File Automation Analyzer")
- Click "Create"

### 5. Download Credentials
- Click the download icon next to your newly created OAuth client
- Save the downloaded file as `credentials.json` in this directory:
  ```
  /Users/barneywong/.gemini/antigravity/file-automation-analyzer/credentials.json
  ```

### 6. Run the Application
```bash
cd /Users/barneywong/.gemini/antigravity/file-automation-analyzer
./venv/bin/python main.py
```

On first run:
- A browser window will open
- Sign in with your Google account
- Grant the requested permissions
- The app will save a `token.json` file for future use

## Alternative: Use Existing credentials.json

If you already have a `credentials.json` file from a previous Gmail API project, simply copy it to this directory.

## Troubleshooting

**"Access blocked: This app's request is invalid"**
- Make sure you've added your email as a test user in the OAuth consent screen

**"The OAuth client was not found"**
- Re-download the credentials.json file from Google Cloud Console

**Need help?**
- Full guide: https://developers.google.com/gmail/api/quickstart/python
