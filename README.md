# Integration Agent

An AI-powered agent that helps users configure API integrations for workflow automation using natural language.

## Features

- 🤖 **Natural Language Understanding**: Describe what you want in plain English
- 🔧 **Smart Action Selection**: Automatically chooses the right integration from the catalog
- 📝 **Liquid Template Generation**: Creates configuration templates with proper variable interpolation
- 📊 **Eval-Driven Development**: Built-in evaluation harness to track performance
- 🔄 **CI/CD Integration**: GitHub Actions workflow for automated testing on prompt changes

## Supported Integrations

- **Slack**: Post messages, create channels
- **GitHub**: Create issues, PRs, comments
- **Google Sheets**: Create/append to spreadsheets
- **Notion**: Create pages, update databases

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

### Usage

#### CLI Mode

```bash
# Simple request
python cli.py "Post the summary to Slack"

# With workflow variables
python cli.py --context '{"summary": "Test message", "slack_channel": "#alerts"}' "Post to Slack"

# JSON output
python cli.py --json "Create a GitHub issue for the error"

# Interactive mode
python cli.py --interactive

# Debug mode (shows agent reasoning)
python cli.py --debug "Create a spreadsheet with products"
```

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
│   ├── system_prompt.j2   # Main system prompt with few-shot examples
│   └── config_generation.j2
├── data/
│   ├── actions.json       # Integration action catalog
│   ├── api_docs/          # Curated API documentation
│   └── sample_context.json
├── tests/
│   ├── eval_harness.py    # Evaluation framework
│   ├── test_agent.py      # Agent unit tests
│   └── test_tools.py      # Tools unit tests
├── results/               # Evaluation results (git-tracked)
└── .github/workflows/
    └── eval.yml           # CI/CD workflow
```

## Running Tests

```bash
# Run all unit tests
python -m pytest tests/ -v --ignore=tests/eval_harness.py

# Run evaluation with mock agent
python tests/eval_harness.py --mock --verbose

# Run evaluation with real agent
python tests/eval_harness.py --real --verbose --output eval_v1.json

# Compare evaluation results
python tests/eval_harness.py --compare results/eval_v1.json results/eval_v2.json
```

## Evaluation Metrics

The evaluation harness tracks:

| Metric | Description |
|--------|-------------|
| **Action Accuracy** | % of correct action selections |
| **Liquid Valid** | % of valid Liquid template syntax |
| **Renders to JSON** | % of templates that render to valid JSON |
| **Avg Latency** | Average response time in ms |
| **Error Rate** | % of requests that failed |

## Iterating on Prompts

1. Edit prompts in `prompts/*.j2`
2. Run evaluation: `python tests/eval_harness.py --real --verbose`
3. Compare with previous results
4. Commit changes with results

The GitHub Actions workflow automatically runs evaluations on every prompt change.

## Architecture

```
User Request → Agent → Tools → LLM → Structured Response
                 │
                 ├── get_available_actions (lists integration catalog)
                 └── retrieve_api_documentation (RAG from ChromaDB)
```

The agent uses:
- **LangGraph ReAct pattern** for tool-calling and reasoning
- **ChromaDB** for vector storage of API documentation
- **Jinja2** for prompt templating and version control
- **Liquid** for configuration template generation

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key | Required |
| `OPENAI_MODEL` | Model to use | gpt-5 |
| `AGENT_VERBOSE` | Enable verbose logging | false |

## License

MIT
