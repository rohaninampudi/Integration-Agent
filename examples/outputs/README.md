# Test Case Outputs

This directory contains the actual agent outputs for each test scenario, demonstrating the Integration Agent's performance across all 13 supported integrations.

## Overview

Each output file contains:
- **Input**: The user request and workflow variables
- **Agent Output**: The selected action, reasoning, and proposed Liquid-templated configuration
- **Validation**: Confirmation that the output meets all requirements
- **Rendered Example**: What the final JSON looks like after Liquid rendering (for demonstration)

## Test Results Summary

| Test | Scenario | Integration | Action Accuracy | Liquid Valid | Renders to JSON |
|------|----------|-------------|----------------|--------------|-----------------|
| 1 | Slack Message | Slack | Yes | Yes | Yes |
| 2 | GitHub Issue | GitHub | Yes | Yes | Yes |
| 3 | Sheets Create | Google Sheets | Yes | Yes | Yes |
| 4 | Sheets Append | Google Sheets | Yes | Yes | Yes |
| 5 | Notion Page | Notion | Yes | Yes | Yes |
| 6 | Notion Block Update | Notion | Yes | Yes | Yes |
| 7 | Airtable Record | Airtable | Yes | Yes | Yes |
| 8 | HubSpot Contact | HubSpot | Yes | Yes | Yes |
| 9 | Trello Card | Trello | Yes | Yes | Yes |
| 10 | Jira Issue | Jira | Yes | Yes | Yes |
| 11 | Stripe Customer | Stripe | Yes | Yes | Yes |
| 12 | SendGrid Email | SendGrid | Yes | Yes | Yes |
| 13 | Twilio SMS | Twilio | Yes | Yes | Yes |

**Overall: 100% action accuracy (13/13), 100% valid Liquid templates, 100% render to valid JSON**

## Files

### Original Test Cases (Priority Integrations)

- `1_slack_message.json` - Basic Liquid variable interpolation
- `2_github_issue.json` - Error handling with structured formatting
- `3_sheets_create.json` - Complex array loops with mixed data types
- `4_sheets_append.json` - Action discrimination (append vs create)
- `5_notion_page.json` - Complex nested structures

### Extended Test Cases (All 13 Actions)

- `6_notion_block_update.json` - Update existing block content
- `7_airtable_record.json` - Create record in Airtable base
- `8_hubspot_contact.json` - Create CRM contact from lead data
- `9_trello_card.json` - Create task card on Trello board
- `10_jira_issue.json` - Create bug ticket in Jira project
- `11_stripe_customer.json` - Create customer for payments
- `12_sendgrid_email.json` - Send transactional email
- `13_twilio_sms.json` - Send SMS alert notification

## Reproducing Results

To regenerate these outputs:

```bash
# Original 5 test cases
python cli.py --json -f examples/slack_message.json "Post the summary to Slack"
python cli.py --json -f examples/github_issue.json "Create a GitHub issue for the failed scrape"
python cli.py --json -f examples/sheets_create.json "Create a spreadsheet with my scraped product data"
python cli.py --json -f examples/sheets_append.json "Add these results to the existing spreadsheet"
python cli.py --json -f examples/notion_page.json "Add these products to my Notion database"

# Extended 8 test cases
python cli.py --json -f examples/notion_block_update.json "Update the Notion block with the new status message"
python cli.py --json -f examples/airtable_record.json "Create a record in my Airtable base with the product data"
python cli.py --json -f examples/hubspot_contact.json "Add this lead as a contact in HubSpot"
python cli.py --json -f examples/trello_card.json "Create a Trello card for this task"
python cli.py --json -f examples/jira_issue.json "Create a Jira ticket for this bug"
python cli.py --json -f examples/stripe_customer.json "Create a new customer in Stripe for this signup"
python cli.py --json -f examples/sendgrid_email.json "Send an email notification via SendGrid about the order"
python cli.py --json -f examples/twilio_sms.json "Send an SMS alert via Twilio about the system status"
```

## Performance Notes

- Average latency: ~38 seconds per request
- Token usage: ~2000-4000 tokens per request
- Success rate: 100% (13/13 scenarios)
- No hallucinations: All configurations grounded in actual API docs
- 100% Action Accuracy across all 13 integration types
