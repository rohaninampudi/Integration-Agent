# Example Workflow Contexts

This directory contains example workflow context files for testing and demoing the Integration Agent.

**📊 See [`outputs/`](outputs/) for actual agent responses to these examples.**

## Quick Start

Run any example with the CLI:

```bash
# Basic usage
python cli.py -f examples/slack_message.json "Post the summary to Slack"

# With debug mode (shows agent reasoning)
python cli.py --debug -f examples/github_issue.json "Create a GitHub issue for the failed scrape"

# Verbose output (shows full config)
python cli.py --verbose -f examples/sheets_create.json "Create a spreadsheet with my scraped product data"

# JSON output (for programmatic use)
python cli.py --json -f examples/slack_message.json "Post the summary to Slack"
```

## Available Examples

| File | Scenario | Expected Action |
|------|----------|-----------------|
| `slack_message.json` | Post a summary to Slack | `slack_post_message` |
| `github_issue.json` | Create issue for failed job | `github_create_issue` |
| `sheets_create.json` | Create new spreadsheet | `google_sheets_create` |
| `sheets_append.json` | Append to existing spreadsheet | `google_sheets_append` |
| `notion_page.json` | Add products to Notion database | `notion_create_page` |
| `complex_workflow.json` | Rich data for multiple scenarios | (varies by request) |

## Example Commands for Demo

### 1. Slack Message (Simple Variables)
```bash
python cli.py --debug -f examples/slack_message.json "Post the summary to Slack"
```

### 2. GitHub Issue (Error Handling)
```bash
python cli.py --debug -f examples/github_issue.json "Create a GitHub issue for the failed scrape"
```

### 3. Google Sheets Create (Array Loop)
```bash
python cli.py --debug --verbose -f examples/sheets_create.json "Create a spreadsheet with my scraped product data"
```

### 4. Google Sheets Append (Discrimination Test)
```bash
# Note: This should select 'append' because spreadsheet_id is present
python cli.py --debug -f examples/sheets_append.json "Add these results to the existing spreadsheet"
```

### 5. Notion Database (Complex Objects)
```bash
python cli.py --debug -f examples/notion_page.json "Add these products to my Notion database"
```

### 6. Complex Workflow (Multiple Use Cases)
```bash
# Try different requests with the same rich context:
python cli.py --debug -f examples/complex_workflow.json "Create a spreadsheet with the product data"
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

2. **Verbose Mode** (`--verbose`): Shows full config without truncation

3. **Action Selection**: How the agent chooses between similar actions
   - `sheets_create` vs `sheets_append` based on context

4. **Liquid Templates**: How variables are interpolated
   - Simple: `{{ summary }}`
   - Arrays: `{% for product in scraper_results %}`

5. **JSON Output** (`--json`): Machine-readable output for integration
