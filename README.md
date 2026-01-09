# Integration Agent

An AI-powered agent that helps users configure API integrations for workflow automation using natural language. Built with an **Agentic RAG** architecture where the LLM orchestrates retrieval decisions.

## Features

- 🤖 **Natural Language Understanding**: Describe what you want in plain English
- 🔧 **Smart Action Selection**: Automatically chooses the right integration from the catalog
- 📝 **Liquid Template Generation**: Creates configuration templates with proper variable interpolation
- 📁 **Ready-to-Use Examples**: Pre-built workflow contexts for easy testing and demos
- 📊 **Eval-Driven Development**: Built-in evaluation harness to track performance
- 🔄 **CI/CD Integration**: GitHub Actions workflow for automated testing on prompt changes
- 🔍 **Debug Mode**: See the agent's step-by-step reasoning with tool calls and observations

## Supported Integrations

**13 integrations with curated API documentation:**

- **Slack**: Post messages to channels
- **GitHub**: Create issues with labels and assignees  
- **Google Sheets**: Create spreadsheets or append rows
- **Notion**: Create pages and update blocks
- **Airtable**: Create records in bases
- **HubSpot**: Create CRM contacts
- **Jira**: Create project issues
- **Trello**: Create cards on boards
- **Stripe**: Create customer objects
- **SendGrid**: Send emails via API
- **Twilio**: Send SMS messages

All integrations include full API documentation in `data/api_docs/` for accurate payload generation.

## What's Included

✅ **Functional Agent**: LangGraph ReAct agent with tool calling  
✅ **Agentic RAG**: Agent-driven retrieval from ChromaDB with OpenAI embeddings  
✅ **Evaluation Framework**: Harness with metrics tracking (action accuracy, Liquid validity, JSON rendering)  
✅ **Example Workflows**: 6+ pre-built context files for testing  
✅ **Debug/Trace Mode**: Full observability into agent reasoning  
✅ **Unit Tests**: 31 tests with automatic skip for integration tests  
✅ **CI/CD Pipeline**: GitHub Actions for automated testing  
✅ **Documentation**: Comprehensive README, examples guide, testing guide

## Quick Start

### Prerequisites

- Python 3.13+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd Integration-Agent

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set your API key
export OPENAI_API_KEY="your-key-here"
# Or create a .env file with: OPENAI_API_KEY=your-key-here
```

### Quick Test

Try the agent with our pre-built examples:

```bash
# Test with a Slack message example (request auto-loaded from file)
python cli.py --debug -f examples/slack_message.json

# See the agent's reasoning and generated configuration!
```

### Usage

#### Quick Start with Example Workflows

We provide **ready-to-use example workflows** in the `examples/` directory with `user_input` pre-configured:

```bash
# Example 1: Slack Message (simple variables)
python cli.py --debug -f examples/slack_message.json

# Example 2: GitHub Issue (error tracking)
python cli.py --debug -f examples/github_issue.json

# Example 3: Google Sheets Create (array loops)
python cli.py --debug -f examples/sheets_create.json

# Example 4: Google Sheets Append (discrimination test)
python cli.py --debug -f examples/sheets_append.json

# Example 5: Notion Database
python cli.py --debug -f examples/notion_page.json
```

**💡 Tip**: 
- Use `--debug` flag to see the agent's step-by-step reasoning process
- The `user_input` is auto-loaded from each example file, no need to specify it!
- You can override the file's `user_input` by passing a request as the last argument

See `examples/README.md` for more details and additional test scenarios.

#### CLI Usage

```bash
# Using example files (user_input auto-loaded)
python cli.py -f examples/slack_message.json

# JSON output (for programmatic use)
python cli.py --json -f examples/slack_message.json

# Debug mode (shows agent reasoning trace)
python cli.py --debug -f examples/slack_message.json

# Override the file's user_input
python cli.py -f examples/slack_message.json "Post a different message"

# Simple request with inline context
python cli.py --context '{"summary": "Test", "slack_channel": "#alerts"}' "Post to Slack"

# Interactive mode
python cli.py --interactive

# Interactive mode with debug tracing
python cli.py --interactive --debug
```

**Available Flags:**
- `-f, --file` - Load workflow context from JSON file
- `-c, --context` - Provide workflow variables as JSON string
- `--debug` - Show agent's step-by-step reasoning and tool calls
- `--json` - Output response as JSON (default shows formatted output)
- `--model` - Override model (default: gpt-5)
- `-i, --interactive` - Start interactive REPL mode

#### 📁 Example Workflows

The `examples/` directory contains pre-configured workflow contexts for all 13 integrations. Each file follows the INSTRUCTIONS.MD format:

```json
{
  "user_input": "Post the summary to Slack",
  "variables": {
    "summary": "...",
    "slack_channel": "#alerts"
  }
}
```

| File | Scenario | What It Tests |
|------|----------|---------------|
| `slack_message.json` | Post summary to Slack | Simple variable interpolation |
| `github_issue.json` | Create issue for errors | Multi-line strings, error handling |
| `sheets_create.json` | Create new spreadsheet | Array loops, product data |
| `sheets_append.json` | Append to existing sheet | Action discrimination (has `spreadsheet_id`) |
| `notion_page.json` | Add to Notion database | Complex objects, nested properties |
| `notion_block_update.json` | Update Notion block | Block ID, content updates |
| `airtable_record.json` | Create Airtable record | Nested objects, tags array |
| `hubspot_contact.json` | Create HubSpot contact | CRM contact properties |
| `trello_card.json` | Create Trello card | Card creation with checklist |
| `jira_issue.json` | Create Jira issue | Bug tracking, labels |
| `stripe_customer.json` | Create Stripe customer | Payment customer metadata |
| `sendgrid_email.json` | Send email via SendGrid | Email templates, order data |
| `twilio_sms.json` | Send SMS via Twilio | SMS alerts, system monitoring |

**Usage**: The `user_input` is auto-loaded from each file:
```bash
# Request is loaded from file's user_input field
python cli.py -f examples/slack_message.json

# Or override with your own request
python cli.py -f examples/slack_message.json "Post a custom message"
```

**See `examples/README.md` for complete usage guide and expected outputs.**

#### Programmatic Usage

```python
from src.agent import IntegrationAgent, get_agent_function

# Create agent
agent = IntegrationAgent()

# Run a request
context = {
    "variables": {
        "summary": "Found 3 products",
        "slack_channel": "#alerts"
    }
}
response = agent.run("Post the summary to Slack", context)

print(response.selected_action)   # e.g., "slack_post_message"
print(response.reasoning)         # Explanation of why this action was chosen
print(response.proposed_config)   # Liquid template string
```

## Project Structure

```
Integration-Agent/
├── cli.py                  # CLI entry point
├── src/
│   ├── agent.py           # Main agent implementation
│   ├── config.py          # Configuration and environment
│   ├── models.py          # Pydantic models
│   ├── prompt_loader.py   # Jinja2 prompt loading
│   └── vector_store.py    # ChromaDB vector store
├── tools/
│   ├── get_actions.py     # Action catalog tool
│   └── retrieve_docs.py   # API documentation retrieval
├── prompts/
│   ├── system_prompt.j2       # Main system prompt with few-shot examples
│   ├── user_request.j2        # User input formatting
│   └── structured_response.j2 # Structured output extraction
├── data/
│   ├── actions.json       # Integration action catalog
│   ├── api_docs/          # Curated API documentation
│   └── sample_context.json
├── examples/              # 📁 Ready-to-use workflow examples
│   ├── README.md          # Example usage guide
│   ├── slack_message.json
│   ├── github_issue.json
│   ├── sheets_create.json
│   └── ...                # More examples
├── tests/
│   ├── eval_harness.py    # Evaluation framework
│   ├── test_agent.py      # Agent unit tests
│   └── test_tools.py      # Tools unit tests
├── results/               # Evaluation results (git-tracked)
└── .github/workflows/
    └── eval.yml           # CI/CD workflow
```

## Running Tests

### Unit Tests (31 tests)

```bash
# Run all unit tests
python -m pytest tests/ -v --ignore=tests/eval_harness.py

# Note: 6 tests require OPENAI_API_KEY for vector store initialization
# They will automatically skip in CI if the key is not set
```

### Evaluation Framework

```bash
# Run evaluation with mock agent (no API key needed)
python tests/eval_harness.py --mock --verbose

# Run evaluation with real agent (requires OPENAI_API_KEY)
python tests/eval_harness.py --real --verbose --output results/eval_v1.json

# Compare evaluation results to track improvements
python tests/eval_harness.py --compare results/eval_v1.json results/eval_v2.json
```

**See `tests/README.md` for detailed testing documentation.**

## Evaluation Metrics

The evaluation harness tracks:

| Metric | Description |
|--------|-------------|
| **Action Accuracy** | % of correct action selections |
| **Liquid Valid** | % of valid Liquid template syntax |
| **Renders to JSON** | % of templates that render to valid JSON |
| **Avg Latency** | Average response time in ms |
| **Error Rate** | % of requests that failed |

## Debug Mode & Observability

The agent includes comprehensive tracing to show its reasoning process:

```bash
# Enable debug mode to see the agent's thought process
python cli.py --debug -f examples/slack_message.json
```

**Debug output shows:**
- 💭 **Thought**: Agent's reasoning at each step
- 🎬 **Action**: Which tool it decides to call
- 📥 **Input**: Arguments passed to the tool
- 👁️ **Observation**: Result from the tool
- ⏱️ **Timing**: Duration and step count

**Output Modes:**
- **Default**: Formatted output with colors and agent response
- **`--json`**: Clean JSON output (for programmatic use)
- **`--debug`**: Full reasoning trace + formatted output
- **`--debug --json`**: Reasoning trace + JSON output

This ReAct (Reasoning + Acting) trace makes it easy to:
- Understand agent decisions
- Debug incorrect action selections
- Demo the agent's capabilities
- Track tool usage and performance

## Iterating on Prompts

1. Edit prompts in `prompts/*.j2`
2. Run evaluation: `python tests/eval_harness.py --real --verbose`
3. Compare with previous results
4. Commit changes with results

The GitHub Actions workflow automatically runs evaluations on every prompt change.

## How It Works

The Integration Agent follows a multi-step ReAct workflow:

1. **Analyze Request**: Understands user's intent and available variables
2. **Select Action**: Uses `get_available_actions` to find matching integrations
3. **Retrieve Docs**: Uses `retrieve_api_documentation` with Agentic RAG to get payload structure
4. **Generate Config**: Creates a Liquid template with proper variable interpolation
5. **Return Response**: Provides action ID, reasoning, and templated configuration

### Example Flow

```
User: "Create a spreadsheet with my scraped product data"
Variables: { scraper_results: [...], summary: "Found 3 products" }

Agent Reasoning:
  Step 1: "Need to see available actions" → get_available_actions()
  Step 2: "Need docs for google_sheets_create" → retrieve_api_documentation()
  Step 3: Generate configuration with {% for product in scraper_results %}

Output:
  action: "google_sheets_create"
  reasoning: "User wants to CREATE (not append) because no spreadsheet_id..."
  config: "{ \"properties\": { \"title\": \"...\" }, \"sheets\": [...] }"
```

## Architecture

```
User Request → Agent → Tools → LLM → Structured Response
                 │
                 ├── get_available_actions (lists integration catalog)
                 └── retrieve_api_documentation (Agentic RAG from ChromaDB)
```

**Technology Stack:**
- **LangGraph ReAct pattern** for tool-calling and reasoning
- **LangChain Structured Output** for deterministic, validated responses (100% reliable)
- **ChromaDB** for vector storage of API documentation
- **OpenAI Embeddings** (`text-embedding-3-small`) for semantic search
- **Jinja2** for prompt templating and version control
- **Liquid** for configuration template generation
- **Pydantic** for schema-validated structured outputs

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | gpt-5 |
| `AGENT_VERBOSE` | Enable verbose logging | false |

## License

MIT
