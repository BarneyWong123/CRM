# Audit Report

## Executive Summary
This report outlines the findings from a code audit of the File Automation Analyzer project. The audit focused on code quality, security, performance, and correctness.

## Findings

### 1. Configuration & Documentation Discrepancy
- **Issue**: The `README.md` file mentions a `SEARCH_DAYS_BACK` configuration option in the `.env` file, but this variable is not defined in the `Config` class in `config.py` nor used in the application logic.
- **Impact**: Users cannot control how far back the system searches for emails, potentially leading to performance issues or missing data if the default behavior (searching ALL) is not desired.

### 2. Performance: Inefficient Email Search
- **Issue**: `GmailClient.fetch_emails_with_attachments` uses `self.imap.search(None, 'ALL')`.
- **Impact**: This fetches the IDs of *every* email in the label. As the mailbox grows, this operation will become increasingly slow and consume unnecessary bandwidth. It should use the `SINCE` IMAP criteria to limit the search scope.

### 3. Fragility: Hardcoded Column Indices
- **Issue**: `CRMAnalyzer` uses hardcoded column indices (e.g., `col_0`, `col_11`, `col_12`) mapped to logical names.
- **Impact**: If the source Excel file structure changes (e.g., a column is inserted or moved), the analysis will break or produce incorrect results without warning.

### 4. Lack of Automated Tests
- **Issue**: There are no automated tests (unit or integration) in the repository.
- **Impact**: Refactoring or adding new features carries a high risk of regression. There is no automated way to verify that the system works as expected.

## Recommendations

1.  **Implement `SEARCH_DAYS_BACK`**: Add this to `config.py` and use it in `gmail_client.py` to filter emails by date.
2.  **Add Unit Tests**: specific focus on `CRMAnalyzer` to ensure reports are generated correctly from sample data.
3.  **Refactor Column Mapping**: (Future Work) Implement a more robust column mapping strategy, perhaps by searching for header names instead of fixed indices.
