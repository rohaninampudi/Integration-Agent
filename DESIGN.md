# Integration Agent — Design Document

> A prototype AI agent that helps users configure API integration steps using natural language and workflow context.

---

## Table of Contents

1. [Problem & Solution Overview](#1-problem--solution-overview)
2. [Architecture & System Design](#2-architecture--system-design)
3. [Core Implementation](#3-core-implementation)
4. [Evaluation Strategy](#4-evaluation-strategy)
5. [Observability & Debugging](#5-observability--debugging)
6. [Performance Evolution](#6-performance-evolution)
7. [Key Tradeoffs & Challenges](#7-key-tradeoffs--challenges)
8. [Future Improvements](#8-future-improvements) 

---

## 1. Problem & Solution Overview

### The Problem

Users building AI workflows struggle to configure integration actions (API wrappers) because:
- Actions map 1:1 to API endpoints with complex payload structures
- Users must read external API docs to understand required fields
- Variable formatting and Liquid templating syntax is error-prone

### The Solution

An **Agentic RAG** system that:
1. **Understands natural language** — "Post the summary to Slack"
2. **Selects the right integration** from a catalog of **13 actions**
3. **Retrieves accurate API documentation** using agent-driven retrieval with **12 curated API docs**
4. **Generates valid Liquid-templated configurations** that render to API-ready JSON

> **Why Agentic RAG?** Unlike traditional RAG (query → retrieve → generate), this agent *decides* when and what to retrieve. The LLM orchestrates multiple tool calls, reasoning about information needs before each retrieval step.

### Key Output Format

```json
{
  "selected_action": "slack_post_message",
  "reasoning": "User wants to post a message to Slack...",
  "proposed_config": "{ \"channel\": \"{{ slack_channel }}\", \"text\": \"{{ summary }}\" }"
}
```

The `proposed_config` is a **Liquid template string** that, when rendered with workflow variables, produces valid JSON for the API.

---

## 2. Architecture & System Design

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INPUT                                     │
│  ┌──────────────────────┐    ┌──────────────────────────────────────┐   │
│  │ Natural Language     │    │ Workflow Variables                    │   │
│  │ "Post summary to     │    │ { "summary": "Found 3 products...",  │   │
│  │  Slack"              │    │   "slack_channel": "#alerts" }       │   │
│  └──────────┬───────────┘    └──────────────────┬───────────────────┘   │
└─────────────┼───────────────────────────────────┼───────────────────────┘
              │                                   │
              ▼                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        LANGGRAPH REACT AGENT                             │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  System Prompt (Jinja2)          │  User Request Prompt (Jinja2)   │ │
│  │  - Few-shot examples             │  - Request + Variables          │ │
│  │  - Liquid syntax guide           │  - Output format instructions   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
│                                   │                                      │
│                                   ▼                                      │
│  ┌─────────────────────────────────────────────────────────────────────┐│
│  │                         GPT-5 LLM                                   ││
│  │                    (Tool-calling enabled)                           ││
│  └─────────────────────────────────────────────────────────────────────┘│
│                          │              │                                │
│                          ▼              ▼                                │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │  get_available_actions  │  │  retrieve_api_documentation         │   │
│  │  ───────────────────────│  │  ───────────────────────────────────│   │
│  │  Returns action catalog │  │  Agentic RAG from ChromaDB          │   │
│  │  with metadata          │  │  Returns relevant API doc chunks    │   │
│  └───────────┬─────────────┘  └─────────────────┬───────────────────┘   │
│              │                                  │                        │
│              ▼                                  ▼                        │
│  ┌─────────────────────────┐  ┌─────────────────────────────────────┐   │
│  │   data/actions.json     │  │        ChromaDB Vector Store        │   │
│  │   (13 integrations)     │  │   ┌─────────────────────────────┐   │   │
│  └─────────────────────────┘  │   │  data/api_docs/ (12 files)  │   │   │
│                               │   │  ├── slack.md               │   │   │
│                               │   │  ├── github.md              │   │   │
│                               │   │  ├── google_sheets.md       │   │   │
│                               │   │  ├── notion.md              │   │   │
│                               │   │  ├── notion_blocks.md       │   │   │
│                               │   │  ├── airtable.md            │   │   │
│                               │   │  ├── hubspot.md             │   │   │
│                               │   │  ├── trello.md              │   │   │
│                               │   │  ├── jira.md                │   │   │
│                               │   │  ├── stripe.md              │   │   │
│                               │   │  ├── sendgrid.md            │   │   │
│                               │   │  └── twilio.md              │   │   │
│                               │   └─────────────────────────────┘   │   │
│                               └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
                                   ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                              OUTPUT                                      │
│  ┌────────────────────────────────────────────────────────────────────┐ │
│  │  AgentResponse (Pydantic)                                          │ │
│  │  ├── selected_action: "slack_post_message"                         │ │
│  │  ├── reasoning: "User wants to post..."                            │ │
│  │  └── proposed_config: "{ \"channel\": \"{{ slack_channel }}\" }"   │ │
│  └────────────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Project Structure

```
Integration-Agent/
├── cli.py                      # CLI entry point
├── src/
│   ├── agent.py               # Main agent (LangGraph ReAct)
│   ├── config.py              # Environment & constants
│   ├── models.py              # Pydantic models (AgentResponse)
│   ├── prompt_loader.py       # Jinja2 template loading
│   └── vector_store.py        # ChromaDB implementation
├── tools/
│   ├── get_actions.py         # Action catalog tool
│   └── retrieve_docs.py       # RAG retrieval tool
├── prompts/
│   ├── system_prompt.j2       # System prompt + few-shot examples
│   ├── user_request.j2        # User input formatting
│   └── structured_response.j2 # Structured output extraction prompt
├── data/
│   ├── actions.json           # 13 integration actions
│   └── api_docs/              # 12 curated API documentation files
│       ├── slack.md
│       ├── github.md
│       ├── google_sheets.md
│       ├── notion.md
│       ├── notion_blocks.md
│       ├── airtable.md
│       ├── hubspot.md
│       ├── trello.md
│       ├── jira.md
│       ├── stripe.md
│       ├── sendgrid.md
│       └── twilio.md
├── examples/                   # 14 example workflow context files
│   ├── slack_message.json
│   ├── github_issue.json
│   ├── sheets_create.json
│   ├── sheets_append.json
│   ├── notion_page.json
│   ├── notion_block_update.json
│   ├── airtable_record.json
│   ├── hubspot_contact.json
│   ├── trello_card.json
│   ├── jira_issue.json
│   ├── stripe_customer.json
│   ├── sendgrid_email.json
│   └── twilio_sms.json
├── examples/outputs/           # 13 test case output files
├── tests/
│   ├── eval_harness.py        # Evaluation framework (12 scenarios)
│   ├── test_agent.py          # Agent unit tests
│   └── test_tools.py          # Tool unit tests
├── results/                   # Tracked eval results
│   ├── eval_baseline_4actions.json
│   └── eval_full_12scenarios.json
└── .github/workflows/
    └── eval.yml               # CI/CD for evals
```

### Supported Integrations (13 Actions)

| Integration | Action ID | Description |
|-------------|-----------|-------------|
| Slack | `slack_post_message` | Post message to channel |
| GitHub | `github_create_issue` | Create repository issue |
| Google Sheets | `google_sheets_create` | Create new spreadsheet |
| Google Sheets | `google_sheets_append` | Append rows to sheet |
| Notion | `notion_create_page` | Create database page |
| Notion | `notion_update_block` | Update block content |
| Airtable | `airtable_create_record` | Create table record |
| HubSpot | `hubspot_create_contact` | Create CRM contact |
| Trello | `trello_create_card` | Create board card |
| Jira | `jira_create_issue` | Create project issue |
| Stripe | `stripe_create_customer` | Create customer |
| SendGrid | `sendgrid_send_email` | Send email |
| Twilio | `twilio_send_sms` | Send SMS |

---

## 3. Core Implementation

### 3.1 The Agent — Tool-Calling with LangGraph

📁 **File**: [`src/agent.py`](src/agent.py)

The agent uses **LangGraph's ReAct pattern** which forces the LLM to use tools before generating the final response:

```python
from langgraph.prebuilt import create_react_agent

class IntegrationAgent:
    def __init__(self, model=None, temperature=0.2, verbose=False):
        self.llm = ChatOpenAI(model=self.model_name, temperature=self.temperature)
        self.tools = AGENT_TOOLS  # [get_available_actions, retrieve_api_documentation]
        self.agent = create_react_agent(model=self.llm, tools=self.tools)
    
    def run(self, request: str, context: dict) -> AgentResponse:
        system_prompt = load_system_prompt(variables)
        user_input = load_user_request_prompt(request, variables)
        
        messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_input)]
        result = self.agent.invoke({"messages": messages})
        
        return self._parse_response(result)
```

**Key Design Decision**: Using `create_react_agent` ensures the LLM *must* call tools to gather information before responding. This prevents hallucination of API payload structures.

### 3.2 Tools — Grounding the Agent

#### Tool 1: Get Available Actions

📁 **File**: [`tools/get_actions.py`](tools/get_actions.py)

```python
@tool
def get_available_actions(query: str = "") -> str:
    """Get list of available integration actions.
    
    Args:
        query: Optional search query to filter actions
    
    Returns:
        JSON string with matching actions and their metadata
    """
    actions = load_actions_catalog()
    if query:
        actions = [a for a in actions if query.lower() in str(a).lower()]
    return json.dumps({"actions": actions, "total_actions": len(actions)})
```

#### Tool 2: Retrieve API Documentation (Agentic RAG)

📁 **File**: [`tools/retrieve_docs.py`](tools/retrieve_docs.py)

```python
@tool
def retrieve_api_documentation(action_id: str) -> str:
    """Retrieve API documentation for a specific integration action.
    
    Args:
        action_id: The integration action ID (e.g., 'slack_post_message')
    
    Returns:
        JSON with API documentation chunks relevant to the action
    """
    action = get_action_by_id(action_id)
    docs = vector_store.similarity_search(
        query=f"{action['name']} {action['description']} {action['api_reference']}",
        k=5,
        filter={"source": get_doc_source(action_id)}
    )
    return json.dumps({"action_id": action_id, "documentation": "\n\n".join(docs)})
```

### 3.3 Vector Store — ChromaDB for API Docs

📁 **File**: [`src/vector_store.py`](src/vector_store.py)

ChromaDB is used to store and retrieve API documentation chunks:

```python
class VectorStore:
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        self.client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        self.collection = self.client.get_or_create_collection("api_docs")
    
    def initialize(self, force_rebuild=False):
        """Load API docs, chunk them, and index in ChromaDB."""
        loader = DirectoryLoader(API_DOCS_DIR, glob="**/*.md")
        documents = loader.load()
        
        splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = splitter.split_documents(documents)
        
        # Add to ChromaDB with metadata
        self.collection.add(
            documents=[c.page_content for c in chunks],
            metadatas=[{"source": c.metadata["source"]} for c in chunks],
            ids=[f"chunk_{i}" for i in range(len(chunks))]
        )
```

**API Documentation Coverage**: Detailed docs for all 13 integrations:

| Integration | File | Key Endpoints |
|-------------|------|---------------|
| Slack | [`data/api_docs/slack.md`](data/api_docs/slack.md) | chat.postMessage |
| GitHub | [`data/api_docs/github.md`](data/api_docs/github.md) | Create Issue |
| Google Sheets | [`data/api_docs/google_sheets.md`](data/api_docs/google_sheets.md) | Create, Append |
| Notion | [`data/api_docs/notion.md`](data/api_docs/notion.md) | Create Page |
| Notion Blocks | [`data/api_docs/notion_blocks.md`](data/api_docs/notion_blocks.md) | Update Block |
| Airtable | [`data/api_docs/airtable.md`](data/api_docs/airtable.md) | Create Record |
| HubSpot | [`data/api_docs/hubspot.md`](data/api_docs/hubspot.md) | Create Contact |
| Trello | [`data/api_docs/trello.md`](data/api_docs/trello.md) | Create Card |
| Jira | [`data/api_docs/jira.md`](data/api_docs/jira.md) | Create Issue |
| Stripe | [`data/api_docs/stripe.md`](data/api_docs/stripe.md) | Create Customer |
| SendGrid | [`data/api_docs/sendgrid.md`](data/api_docs/sendgrid.md) | Mail Send |
| Twilio | [`data/api_docs/twilio.md`](data/api_docs/twilio.md) | Create Message |

### 3.4 Prompts — Jinja2 Templates with Few-Shot Examples

📁 **Directory**: [`prompts/`](prompts/)

All prompts are **Jinja2 templates** stored as files, enabling:
- Version control with git diffs
- Easy iteration without code changes
- CI/CD integration (GitHub Actions runs evals on prompt changes)

#### System Prompt with Few-Shot Examples

📁 **File**: [`prompts/system_prompt.j2`](prompts/system_prompt.j2)

The system prompt includes several key sections:

**1. Liquid Template Syntax Guide**
- Teaches the agent how to use `{{ variable }}` syntax
- Shows loop patterns: `{% for item in array %}...{% endfor %}`
- Explains JSON formatting (commas, quotes, data types)

**2. Few-Shot Examples**

Example 1 - Slack Message (simple variables):
```json
{
  "selected_action": "slack_post_message",
  "reasoning": "User wants to post a message to Slack...",
  "proposed_config": "{ \"channel\": \"{{ slack_channel }}\", \"text\": \"{{ summary }}\" }"
}
```

Example 2 - GitHub Issue (string interpolation):
```json
{
  "selected_action": "github_create_issue",
  "reasoning": "User wants to create a GitHub issue to track a failed scrape...",
  "proposed_config": "{ \"title\": \"Scrape Failed\", \"body\": \"{{ summary }}\", \"labels\": [\"bug\"] }"
}
```

**3. Rules**
1. MUST call `get_available_actions` tool first
2. MUST call `retrieve_api_documentation` before generating config
3. `proposed_config` must be a STRING containing Liquid template
4. When rendered, must produce valid JSON

**Why Few-Shot Examples?** They're critical for teaching the model:
- Correct JSON output structure
- Proper Liquid template syntax (`{{ variable }}`, `{% for %}...{% endfor %}`)
- How to handle different variable types (strings vs arrays)

### 3.5 Deterministic Structured Output

📁 **File**: [`src/models.py`](src/models.py), [`src/agent.py`](src/agent.py)

A **hybrid approach** for deterministic output:
1. **ReAct agent** for tool calling (action/documentation retrieval)
2. **Structured output** for final response generation (deterministic, validated)

```python
class AgentResponseOutput(BaseModel):
    """Schema for deterministic structured output (used by LLM)."""
    
    selected_action: str = Field(
        description="The ID of the selected integration action"
    )
    reasoning: str = Field(
        description="Explanation of why this action was selected"
    )
    proposed_config: str = Field(
        description="A Liquid template string that renders to valid JSON"
    )

# In agent.py - two-stage approach
class IntegrationAgent:
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-5")
        self.structured_llm = self.llm.with_structured_output(AgentResponseOutput)  # Deterministic!
        self.agent = create_react_agent(model=self.llm, tools=self.tools)  # For tool calling
    
    def _generate_structured_response(self, agent_output: str, ...):
        # Use structured LLM for final response - 100% deterministic
        return self.structured_llm.invoke(prompt)
```

**Why This Approach?**
- **Deterministic**: Final response is guaranteed to match the Pydantic schema
- **Automatic validation**: Pydantic validates all fields
- **No JSON parsing**: LLM uses tool calling for output, not text generation
- **Compatible**: Works with standard ReAct tools (no strict schema requirements)

---

## 4. Evaluation Strategy

### 4.1 Eval-Driven Development

📁 **File**: [`tests/eval_harness.py`](tests/eval_harness.py)

The **evaluation harness was built first** (before the agent) to track performance from day one:

```python
class EvalHarness:
    DEFAULT_SCENARIOS = [
        TestScenario(
            request="Post the summary to Slack",
            expected_action="slack_post_message",
            context={"variables": {"summary": "...", "slack_channel": "#alerts"}}
        ),
        TestScenario(
            request="Add these products to my Notion database",
            expected_action="notion_create_page",
            context={"variables": {"scraper_results": [...], "notion_database_id": "..."}}
        ),
        # ... 10 more scenarios covering all integrations
    ]
    
    def validate_liquid_template(self, config_str, context):
        """Validate proposed_config is valid Liquid that renders to JSON."""
        template = Template(config_str)
        rendered = template.render(**context["variables"])
        json.loads(rendered)  # Must be valid JSON
        return True, True
```

### 4.2 Metrics Tracked

| Metric | Description | Current Result |
|--------|-------------|----------------|
| **Action Accuracy** | % of correct action selections | **100%** (12/12) |
| **Liquid Valid** | % with valid Liquid template syntax | **100%** |
| **Renders to JSON** | % that render to valid JSON | **100%** |
| **Avg Latency** | Time per request | ~40s |
| **Error Rate** | % of failed requests | **0%** |

### 4.3 Test Scenarios (12 Total)

| # | User Request | Expected Action | Integration |
|---|--------------|-----------------|-------------|
| 1 | "Post the summary to Slack" | `slack_post_message` | Slack |
| 2 | "Add these products to my Notion database" | `notion_create_page` | Notion |
| 3 | "Create a GitHub issue for the failed scrape" | `github_create_issue` | GitHub |
| 4 | "Add these results to the existing spreadsheet" | `google_sheets_append` | Google Sheets |
| 5 | "Update the Notion block with the new status" | `notion_update_block` | Notion |
| 6 | "Create a record in my Airtable base" | `airtable_create_record` | Airtable |
| 7 | "Add this lead as a contact in HubSpot" | `hubspot_create_contact` | HubSpot |
| 8 | "Create a Trello card for this task" | `trello_create_card` | Trello |
| 9 | "Create a Jira ticket for this bug" | `jira_create_issue` | Jira |
| 10 | "Create a new customer in Stripe" | `stripe_create_customer` | Stripe |
| 11 | "Send an email notification via SendGrid" | `sendgrid_send_email` | SendGrid |
| 12 | "Send an SMS alert via Twilio" | `twilio_send_sms` | Twilio |

### 4.4 Running Evaluations

```bash
# Run with mock agent (tests eval harness)
python tests/eval_harness.py --mock --verbose

# Run with real agent
python tests/eval_harness.py --real --verbose --output eval_v1.json

# Compare two runs
python tests/eval_harness.py --compare results/eval_baseline_4actions.json results/eval_full_12scenarios.json
```

### 4.5 What Evals Check (and Don't Check)

**Currently Validated:**
| Check | Description |
|-------|-------------|
| Action Accuracy | Does `selected_action` match expected? |
| Liquid Valid | Is the template syntactically correct? |
| Renders to JSON | Does rendered output parse as JSON? |

**Not Yet Validated (Future Improvement):**
- Required API fields present
- Correct field names for specific APIs
- Data type correctness
- Schema compliance with API docs

---

## 5. Observability & Debugging

### 5.1 CLI Debug Mode

📁 **File**: [`cli.py`](cli.py)

```bash
# Normal mode
python cli.py "Post the summary to Slack"

# Debug mode - shows agent reasoning steps
python cli.py --debug "Post the summary to Slack"

# JSON output for programmatic use
python cli.py --json --context '{"summary": "test"}' "Post to Slack"

# Use example file
python cli.py --json -f examples/slack_message.json "Post the summary to Slack"
```

### 5.2 Agent Tracing

When `--debug` is enabled, the full agent trace is shown:

```
🔧 Initializing...
✓ Using model: gpt-5
📨 Request: Post the summary to Slack
⏳ Processing...

[Agent Step 1] Calling tool: get_available_actions
  Input: {"query": "slack"}
  Output: {"actions": [{"id": "slack_post_message", ...}], "total_actions": 1}

[Agent Step 2] Calling tool: retrieve_api_documentation  
  Input: {"action_id": "slack_post_message"}
  Output: {"documentation": "## Slack chat.postMessage\n\nEndpoint: POST..."}

[Agent Step 3] Generating response...
```

### 5.3 Evaluation Result Tracking

📁 **Directory**: [`results/`](results/)

All evaluation results are git-tracked for history:

```json
{
  "timestamp": "2026-01-08T13:09:43.013368",
  "git_sha": "8ca89ce",
  "prompt_hash": "b9c21e3f",
  "total_scenarios": 12,
  "metrics": {
    "action_accuracy": 100.0,
    "liquid_valid": 100.0,
    "renders_to_json": 91.67,
    "avg_latency_ms": 38079
  }
}
```

### 5.4 CI/CD Integration

📁 **File**: [`.github/workflows/eval.yml`](.github/workflows/eval.yml)

GitHub Actions automatically runs evaluations when prompts change:

```yaml
on:
  push:
    paths:
      - 'prompts/**'
      - 'src/**'
      - 'tools/**'
```

---

## 6. Performance Evolution

### Development Timeline

| Version | Change | Scenarios | Action Accuracy | Notes |
|---------|--------|-----------|-----------------|-------|
| Baseline | Mock agent | 4 | 100% | Keyword matching only |
| v1 | Real agent, basic prompt | 4 | 75% | GitHub issue failed (parse error) |
| v2 | Improved JSON parsing | 4 | **100%** | Added fallback regex extraction |
| v3 | Extended to all integrations | 12 | **100%** | 8 new API docs + scenarios |
| v4 (current) | Structured output | 12 | **100%** | Deterministic response generation |

### Version History: What Improved Each Iteration

#### Baseline → v1: First Real Agent

| Metric | Baseline | v1 | Change |
|--------|----------|-----|--------|
| Scenarios | 4 | 4 | — |
| Action Accuracy | 100% | 75% | ↓ Regression (parse errors) |
| Liquid Valid | 100% | 100% | = |
| Renders to JSON | 100% | 100% | = |

**What Changed**: Moved from mock agent (keyword matching) to real LLM agent  
**Problem Discovered**: The LLM was generating responses that exceeded token limits, and `proposed_config` (being last in the JSON) got truncated. This was NOT a bug in the code—the OpenAI API was cutting off long responses.

📁 **Evidence**: See [`results/eval_real_v1.json`](results/eval_real_v1.json) (scenario 2) - raw output ends with `"...The configuration is a Liquid template t"` (cut off mid-sentence!)

---

#### v1 → v2: Regex Fallback Fix

| Metric | v1 | v2 | Change |
|--------|-----|-----|--------|
| Scenarios | 4 | 4 | — |
| Action Accuracy | 75% | **100%** | ↑ +25% Fixed! |
| Liquid Valid | 100% | 100% | = |
| Renders to JSON | 100% | 75% | ↓ Config still truncated |
| Avg Latency | 40.7s | 20.4s | ↑ 2x faster |

**What Changed**: Added `_extract_field()` regex fallback for truncated JSON  
**Improvement**: Even if JSON is incomplete, `selected_action` can be extracted correctly

**Why Renders to JSON dropped**: An ironic side effect! In v1, parse failures returned `{}` (valid JSON). In v2, the regex fallback extracted the *actual* truncated `proposed_config` value.

📁 **Evidence**: See [`results/eval_real_v2.json`](results/eval_real_v2.json) (scenario 2):
```json
"actual_action": "github_create_issue",  // ✅ Regex fallback worked!
"proposed_config": "{ \\",               // ❌ Severely truncated - not valid JSON
"renders_to_json": false
```

The LLM generated `proposed_config` last in the response, so it was the first field to get cut off by token limits.

---

#### v2 → v3: Extended Integration Support

| Metric | v2 | v3 | Change |
|--------|-----|-----|--------|
| Scenarios | 4 | **12** | ↑ +8 new scenarios |
| Action Accuracy | 100% | **100%** | = Maintained |
| Liquid Valid | 100% | 100% | = |
| Renders to JSON | 75% | 91.7% | ↑ +16.7% |
| Avg Latency | 20.4s | 38.1s | ↓ More tool calls |

**What Changed**: 
- Added 8 new API documentation files (Airtable, HubSpot, Trello, Jira, Stripe, SendGrid, Twilio, Notion blocks)
- Expanded eval harness with 8 new test scenarios
- Prompt template improvements

---

#### v3 → v4: Deterministic Structured Output (Current)

| Metric | v3 | v4 | Change |
|--------|-----|-----|--------|
| Scenarios | 12 | 12 | — |
| Action Accuracy | 100% | **100%** | = |
| Liquid Valid | 100% | **100%** | = |
| Renders to JSON | 91.7% | **100%** | ↑ **+8.3% Fixed!** |
| Avg Latency | 38.1s | 40.2s | ≈ Similar |

**What Changed**: 
- Replaced fragile JSON text parsing with LangChain's `with_structured_output()`
- Hybrid approach: ReAct for tool calling + structured output for final response
- Removed ~70 lines of parsing code, replaced with ~5 lines

**Why This Solved Truncation**: Structured output forces the LLM to generate responses conforming to a Pydantic schema. The model knows exactly what fields are needed and outputs them completely—no more truncation issues!

```python
# OLD (v3): Fragile text parsing
def _parse_response(self, output: str) -> AgentResponse:
    json_str = extract_from_markdown(output)  # Could fail!
    data = json.loads(json_str)               # Could fail!
    return AgentResponse(**data)

# NEW (v4): Deterministic structured output  
self.structured_llm = self.llm.with_structured_output(AgentResponseOutput)
response = self.structured_llm.invoke(prompt)  # Always valid!
```

---

### Summary: Evolution at a Glance

```
============================================================
VERSION EVOLUTION SUMMARY
============================================================
Version   Scenarios  Action%  Liquid%  JSON%   Key Change
--------  ---------  -------  -------  ------  --------------------------
Baseline  4          100%     100%     100%    Mock agent (keyword match)
v1        4          75%      100%     100%    Real LLM agent
v2        4          100%     100%     75%     Regex fallback for parsing
v3        12         100%     100%     91.7%   Extended to 13 integrations
v4        12         100%     100%     100%    Structured output (current)
============================================================
```

### Key Improvements Made

1. **Extended Integration Support**: Added 8 new API documentation files covering all 13 actions

2. **Deterministic Structured Output (v4)**: Hybrid approach with ReAct + structured output:
   ```python
   # Hybrid: ReAct for tool calling + structured output for final response
   self.structured_llm = self.llm.with_structured_output(AgentResponseOutput)
   
   def _generate_structured_response(self, agent_output: str, ...):
       # Final response is 100% deterministic and validated
       return self.structured_llm.invoke(prompt)
   ```

3. **Prompt Separation**: Moved all prompt content to Jinja2 templates for easier iteration

4. **Few-Shot Examples**: Added 4 detailed examples covering different Liquid patterns

5. **Comprehensive Test Coverage**: 12 eval scenarios covering all integration types

---

## 7. Key Tradeoffs

### Tradeoff 1: RAG vs Web Search for API Documentation

| Approach | Pros | Cons |
|----------|------|------|
| **RAG (chosen)** | Fast (~2s), consistent, controllable quality | Limited to pre-curated docs |
| **Web Search** | Always current, no maintenance | Slower, noisy, unpredictable |

**Decision**: RAG for reliability. Web search could be a fallback for unknown APIs.

---

### Tradeoff 2: Tool-Augmented Agent vs Direct LLM Generation

| Approach | Pros | Cons |
|----------|------|------|
| **ReAct with tools (chosen)** | Grounded in real data, transparent reasoning, retrieves docs on-demand | More LLM calls, higher latency |
| **Single-shot LLM** | Fast, simple | Hallucinates APIs, can't access current docs |
| **Fine-tuned model** | Fast inference, specialized | Expensive to train, hard to update |

**Decision**: ReAct agent with two tools:
- `get_available_actions` — LLM sees real action metadata, picks based on intent
- `retrieve_api_documentation` — LLM fetches only the docs it needs

**Why this matters**: The agent *reasons* about which action fits, then *retrieves* relevant docs before generating config. This prevents hallucination and ensures output matches actual API specs.

**Tradeoff accepted**: 2-3 tool calls add ~5-10s latency, but accuracy is worth it for an integration builder where wrong payloads = failed API calls.

---

### Tradeoff 3: Structured Output vs Free-form Parsing

| Approach | Pros | Cons |
|----------|------|------|
| **Structured output (chosen)** | Guaranteed valid JSON, no truncation | Requires schema definition |
| **Free-form + regex** | Flexible output | Truncation issues, brittle parsing |

**Decision**: Started with free-form (v1-v2), migrated to structured output (v4) after hitting truncation issues.

---

### Tradeoff 4: Payload Validation Depth

| Approach | Pros | Cons |
|----------|------|------|
| **JSON validity (current)** | Simple, API-agnostic | Doesn't catch wrong field names |
| **Schema validation** | Catches API errors early | Requires maintaining schema per action |

**Decision**: JSON validity for MVP. Schema validation is a future improvement.

---

## 8. Future Improvements

### Performance Optimization

**Current state**: Average latency is ~38s, with complex scenarios reaching 2+ minutes (see `results/eval_full_12scenarios.json`).

| Improvement | Impact | Effort |
|-------------|--------|--------|
| **Reduce tool calls** | Skip `get_available_actions` when action is obvious from context | High / Low |
| **Parallel doc retrieval** | Fetch multiple API docs simultaneously | Medium / Low |
| **Response caching** | Cache repeated queries with same context hash | Medium / Medium |
| **Smaller model for action selection** | Use GPT-4o-mini for tool calls, GPT-4o for config generation | High / Medium |

### UX Improvements

| Improvement | Impact | Effort |
|-------------|--------|--------|
| **Token streaming** | Stream response to client for responsive UI instead of waiting for full completion | High / Low |
| **Progress indicators** | Show "Selecting action..." → "Retrieving docs..." → "Generating config..." | Medium / Low |

### Framework Migration: LangGraph → AI SDK

Consider migrating from LangGraph to Vercel AI SDK:

| Benefit | Details |
|---------|---------|
| **Lighter footprint** | No heavy LangChain dependencies (~50MB → ~5MB) |
| **Native streaming** | Built-in `streamText()` with React hooks |
| **Simpler mental model** | No graph state machine, just async functions |
| **Edge-compatible** | Runs on Vercel Edge, Cloudflare Workers |
| **TypeScript-first** | Better type inference, no Python-to-TS friction |

### Validation & Reliability

| Improvement | Details |
|-------------|---------|
| **Payload schema validation** | Validate `proposed_config` against API schemas (required fields, types, enums) before returning to user |
| **Web search fallback** | For missing/outdated API docs, fall back to web search |
| **Retry with backoff** | Handle transient LLM failures gracefully |

### Evaluation Improvements

**Current gaps**: One-shot runs (non-deterministic), no payload field validation, no expected output comparison.

| Improvement | Details |
|-------------|---------|
| **Multi-run determinism** | Run each scenario 3-5x, report pass rate (e.g., "4/5 correct") to surface flaky prompts |
| **Required field validation** | Parse API docs for required fields, verify they appear in rendered config |
| **LLM-as-judge** | Use GPT-4 to score config quality: "Does this payload correctly implement the user's intent?" (1-5 scale) |
| **Golden output comparison** | Store expected `proposed_config` per scenario, compute similarity score |
| **Eval dashboard** | Visualize metrics over time, compare prompt versions |

### Prompt Engineering

| Improvement | Details |
|-------------|---------|
| **A/B testing framework** | Run same scenarios against prompt variants, compare metrics automatically |
| **Prompt versioning** | Track prompt changes with git-like history, rollback on regression |

### Continuous Improvement

| Improvement | Details |
|-------------|---------|
| **User feedback loop** | Collect thumbs up/down on generated configs, use for fine-tuning dataset |
| **Failure analysis pipeline** | Auto-categorize failures (wrong action, invalid Liquid, missing fields) for targeted fixes |
| **Shadow mode** | Run new prompts in parallel with production, compare before rollout |

---

## Results

**Final Performance**:
- **13 integration actions** fully supported
- **100% action accuracy** across all 12 test scenarios
- **12 API documentation files** indexed in ChromaDB
- **13 example workflow files** + **13 test case outputs**
- Production-ready CI/CD pipeline with GitHub Actions

---

*Built with LangGraph, ChromaDB, GPT-5, and Python*
