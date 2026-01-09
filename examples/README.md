# Example Workflow Contexts

This directory contains example workflow context files for testing and demoing the Integration Agent.

**📊 See [`outputs/`](outputs/) for actual agent responses to these examples.**

## File Format

Each example file follows the INSTRUCTIONS.MD workflow context format:

```json
{
  "user_input": "Post the summary to Slack",
  "variables": {
    "summary": "...",
    "slack_channel": "#alerts"
  }
}
```

The `user_input` field contains the natural language request, and `variables` contains the workflow data.

## Quick Start

Run any example with the CLI (request auto-loaded from file):

```bash
# Basic usage (user_input from file)
python cli.py -f examples/slack_message.json

# With debug mode (shows agent reasoning trace)
python cli.py --debug -f examples/github_issue.json

# JSON output (for programmatic use)
python cli.py --json -f examples/slack_message.json

# Override the file's user_input with custom request
python cli.py -f examples/slack_message.json "Post a different message"
```

## Available Examples

| File | User Input | Expected Action |
|------|------------|-----------------|
| `slack_message.json` | "Post the summary to Slack" | `slack_post_message` |
| `github_issue.json` | "Create a GitHub issue for the failed scrape" | `github_create_issue` |
| `sheets_create.json` | "Create a spreadsheet with my scraped product data" | `google_sheets_create` |
| `sheets_append.json` | "Add these results to the existing spreadsheet" | `google_sheets_append` |
| `notion_page.json` | "Add these products to my Notion database" | `notion_create_page` |
| `notion_block_update.json` | "Update the Notion block with the new status message" | `notion_update_block` |
| `airtable_record.json` | "Create a record in my Airtable base with the product data" | `airtable_create_record` |
| `hubspot_contact.json` | "Add this lead as a contact in HubSpot" | `hubspot_create_contact` |
| `trello_card.json` | "Create a Trello card for this task" | `trello_create_card` |
| `jira_issue.json` | "Create a Jira ticket for this bug" | `jira_create_issue` |
| `stripe_customer.json` | "Create a new customer in Stripe for this signup" | `stripe_create_customer` |
| `sendgrid_email.json` | "Send an email notification via SendGrid about the order" | `sendgrid_send_email` |
| `twilio_sms.json` | "Send an SMS alert via Twilio about the system status" | `twilio_send_sms` |
| `complex_workflow.json` | "Create a spreadsheet with the product data" | `google_sheets_create` |

## Example Commands for Demo

### 1. Slack Message (Simple Variables)
```bash
python cli.py --debug -f examples/slack_message.json
```

### 2. GitHub Issue (Error Handling)
```bash
python cli.py --debug -f examples/github_issue.json
```

### 3. Google Sheets Create (Array Loop)
```bash
python cli.py --debug -f examples/sheets_create.json
```

### 4. Google Sheets Append (Discrimination Test)
```bash
# Note: This should select 'append' because spreadsheet_id is present
python cli.py --debug -f examples/sheets_append.json
```

### 5. Notion Database (Complex Objects)
```bash
python cli.py --debug -f examples/notion_page.json
```

### 6. Complex Workflow (Can override user_input)
```bash
# Use built-in user_input
python cli.py --debug -f examples/complex_workflow.json

# Or override with different requests:
python cli.py --debug -f examples/complex_workflow.json "Post the summary to Slack"
python cli.py --debug -f examples/complex_workflow.json "Create a GitHub issue for the errors"
```

## Interactive Mode Demo

For live demos, use interactive mode:

```bash
python cli.py --interactive --debug
```

Then type:
```
set summary "Build completed with 0 errors"
set slack_channel "#ci-alerts"
Post the summary to Slack
```

## What to Show in Demo

1. **Debug Mode** (`--debug`): Shows the ReAct reasoning trace
   - Thought → Action → Observation loop
   - Tool calls and their results
   - Total execution time
   - Full configuration output (no truncation)

2. **Action Selection**: How the agent chooses between similar actions
   - `sheets_create` vs `sheets_append` based on context

3. **Liquid Templates**: How variables are interpolated
   - Simple: `{{ summary }}`
   - Arrays: `{% for product in scraper_results %}`

4. **JSON Output** (`--json`): Machine-readable output for integration

5. **Auto-loaded Requests**: No need to type the request—it's in the file!
