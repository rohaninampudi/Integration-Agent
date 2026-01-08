"""Evaluation Harness for Integration Agent.

This module provides the core evaluation framework for tracking agent performance.
It is built FIRST (before the agent) to enable eval-driven development.

Features:
- Test scenarios for the 4 required use cases
- Liquid template validation (syntax + JSON rendering)
- Metrics tracking (action_accuracy, liquid_valid, renders_to_json, latency)
- Git SHA and prompt version tracking for evolution history
- Results saved to results/ for git-tracked comparison
"""

import json
import hashlib
import subprocess
import time
import argparse
from datetime import datetime
from pathlib import Path
from typing import Callable, Optional
from dataclasses import dataclass, field, asdict

from liquid import Template

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import RESULTS_DIR, PROMPTS_DIR, DATA_DIR
from src.models import AgentResponse, WorkflowContext


@dataclass
class TestScenario:
    """A single test scenario for evaluation."""
    request: str
    expected_action: str
    context: dict
    description: str = ""


@dataclass
class ScenarioResult:
    """Result of running a single scenario."""
    scenario_id: int
    request: str
    expected_action: str
    actual_action: Optional[str] = None
    action_correct: bool = False
    liquid_valid: bool = False
    renders_to_json: bool = False
    reasoning: str = ""
    proposed_config: str = ""
    rendered_config: Optional[str] = None
    latency_ms: float = 0.0
    error: Optional[str] = None


@dataclass
class EvalResults:
    """Complete evaluation results."""
    timestamp: str
    git_sha: str
    prompt_hash: str
    total_scenarios: int
    metrics: dict = field(default_factory=dict)
    details: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


class EvalHarness:
    """Evaluation harness for tracking Integration Agent performance.
    
    Usage:
        harness = EvalHarness()
        results = harness.run(agent_function)
        harness.save_results(results, "eval_v1.json")
    """
    
    # Default test scenarios from INSTRUCTIONS.MD
    DEFAULT_SCENARIOS = [
        TestScenario(
            request="Post the summary to Slack",
            expected_action="slack_post_message",
            context={
                "user_input": "Post the summary to Slack",
                "variables": {
                    "summary": "Found 3 products. Average price: $91.66. Lowest: USB-C Hub ($45.00)",
                    "slack_channel": "#product-alerts",
                    "scraper_results": [
                        {"name": "Wireless Headphones", "price": 79.99, "url": "https://store.example.com/p/1001"}
                    ]
                }
            },
            description="Simple variable interpolation for Slack message"
        ),
        TestScenario(
            request="Add these products to my Notion database",
            expected_action="notion_create_page",
            context={
                "user_input": "Add these products to my Notion database",
                "variables": {
                    "scraper_results": [
                        {"name": "Wireless Headphones", "price": 79.99, "url": "https://store.example.com/p/1001"},
                        {"name": "USB-C Hub", "price": 45.0, "url": "https://store.example.com/p/1002"},
                        {"name": "Mechanical Keyboard", "price": 149.99, "url": "https://store.example.com/p/1003"}
                    ],
                    "notion_database_id": "8a3b1c4d-5e6f-7a8b-9c0d-1e2f3a4b5c6d"
                }
            },
            description="Array loop for creating Notion pages"
        ),
        TestScenario(
            request="Create a GitHub issue for the failed scrape",
            expected_action="github_create_issue",
            context={
                "user_input": "Create a GitHub issue for the failed scrape",
                "variables": {
                    "summary": "Scrape failed: Connection timeout after 30s. URL: https://store.example.com",
                    "error_details": "TimeoutError: Request exceeded 30000ms"
                }
            },
            description="String interpolation for GitHub issue"
        ),
        TestScenario(
            request="Add these results to the existing spreadsheet",
            expected_action="google_sheets_append",
            context={
                "user_input": "Add these results to the existing spreadsheet",
                "variables": {
                    "scraper_results": [
                        {"name": "Wireless Headphones", "price": 79.99, "url": "https://store.example.com/p/1001"},
                        {"name": "USB-C Hub", "price": 45.0, "url": "https://store.example.com/p/1002"}
                    ],
                    "spreadsheet_id": "1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms"
                }
            },
            description="Array loop for appending to existing spreadsheet"
        ),
        # ===== Extended scenarios for all 13 actions =====
        TestScenario(
            request="Update the Notion block with the new status message",
            expected_action="notion_update_block",
            context={
                "user_input": "Update the Notion block with the new status message",
                "variables": {
                    "block_id": "b1c2d3e4-5f6a-7b8c-9d0e-1f2a3b4c5d6e",
                    "new_content": "Status: Completed ✅ - All tasks finished successfully.",
                    "status": "completed"
                }
            },
            description="Notion block update with text content"
        ),
        TestScenario(
            request="Create a record in my Airtable base with the product data",
            expected_action="airtable_create_record",
            context={
                "user_input": "Create a record in my Airtable base with the product data",
                "variables": {
                    "base_id": "appXYZ123456789",
                    "table_name": "Products",
                    "product_data": {
                        "name": "New Product",
                        "price": 99.99,
                        "category": "Electronics",
                        "in_stock": True
                    }
                }
            },
            description="Airtable record creation with product fields"
        ),
        TestScenario(
            request="Add this lead as a contact in HubSpot",
            expected_action="hubspot_create_contact",
            context={
                "user_input": "Add this lead as a contact in HubSpot",
                "variables": {
                    "lead": {
                        "email": "john.smith@acmecorp.com",
                        "first_name": "John",
                        "last_name": "Smith",
                        "company": "Acme Corporation",
                        "job_title": "VP of Engineering",
                        "phone": "+1-555-123-4567"
                    }
                }
            },
            description="HubSpot contact creation with lead data"
        ),
        TestScenario(
            request="Create a Trello card for this task",
            expected_action="trello_create_card",
            context={
                "user_input": "Create a Trello card for this task",
                "variables": {
                    "list_id": "5f1a2b3c4d5e6f7a8b9c0d1e",
                    "task": {
                        "name": "Review pull request #42",
                        "description": "Code review needed for the authentication module updates",
                        "due_date": "2024-01-15T17:00:00Z"
                    }
                }
            },
            description="Trello card creation with task details"
        ),
        TestScenario(
            request="Create a Jira ticket for this bug",
            expected_action="jira_create_issue",
            context={
                "user_input": "Create a Jira ticket for this bug",
                "variables": {
                    "project_key": "PROJ",
                    "bug": {
                        "summary": "Login page returns 500 error on mobile",
                        "description": "Users on iOS Safari cannot log in. Error occurs after entering credentials.",
                        "priority": "High"
                    },
                    "labels": ["mobile", "urgent", "login"]
                }
            },
            description="Jira issue creation for bug tracking"
        ),
        TestScenario(
            request="Create a new customer in Stripe for this signup",
            expected_action="stripe_create_customer",
            context={
                "user_input": "Create a new customer in Stripe for this signup",
                "variables": {
                    "customer": {
                        "email": "newuser@example.com",
                        "name": "Jane Doe",
                        "phone": "+1-555-987-6543"
                    },
                    "plan": "premium",
                    "signup_source": "landing_page"
                }
            },
            description="Stripe customer creation with metadata"
        ),
        TestScenario(
            request="Send an email notification via SendGrid about the order",
            expected_action="sendgrid_send_email",
            context={
                "user_input": "Send an email notification via SendGrid about the order",
                "variables": {
                    "recipient": {
                        "email": "customer@example.com",
                        "name": "John Customer"
                    },
                    "order": {
                        "id": "ORD-12345",
                        "total": "$149.99",
                        "status": "shipped"
                    },
                    "from_email": "orders@store.com",
                    "from_name": "Store Notifications"
                }
            },
            description="SendGrid email for order notification"
        ),
        TestScenario(
            request="Send an SMS alert via Twilio about the system status",
            expected_action="twilio_send_sms",
            context={
                "user_input": "Send an SMS alert via Twilio about the system status",
                "variables": {
                    "alert_phone": "+14155551234",
                    "twilio_number": "+14155559876",
                    "alert": {
                        "type": "warning",
                        "message": "CPU usage exceeded 90% on production server",
                        "timestamp": "2024-01-08T14:30:00Z"
                    }
                }
            },
            description="Twilio SMS for system alerts"
        ),
    ]
    
    def __init__(self, scenarios: Optional[list[TestScenario]] = None):
        """Initialize the eval harness with test scenarios.
        
        Args:
            scenarios: Custom scenarios or None for defaults
        """
        self.scenarios = scenarios or self.DEFAULT_SCENARIOS
    
    @staticmethod
    def get_git_sha() -> str:
        """Get current git commit SHA."""
        try:
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                cwd=Path(__file__).parent.parent
            )
            return result.stdout.strip() if result.returncode == 0 else "unknown"
        except Exception:
            return "unknown"
    
    @staticmethod
    def get_prompt_hash() -> str:
        """Get hash of prompt files for version tracking."""
        try:
            prompt_content = ""
            for prompt_file in sorted(PROMPTS_DIR.glob("*.j2")):
                prompt_content += prompt_file.read_text()
            
            if not prompt_content:
                return "no-prompts"
            
            return hashlib.md5(prompt_content.encode()).hexdigest()[:8]
        except Exception:
            return "unknown"
    
    def validate_liquid_template(
        self, 
        config_str: str, 
        context: dict
    ) -> tuple[bool, bool, Optional[str]]:
        """Validate proposed_config is valid Liquid that renders to valid JSON.
        
        Args:
            config_str: The Liquid template string
            context: Variables to render the template with
            
        Returns:
            Tuple of (is_valid_liquid, renders_to_valid_json, rendered_string)
        """
        try:
            template = Template(config_str)
            rendered = template.render(**context.get("variables", {}))
            
            # Try to parse as JSON
            json.loads(rendered)
            return True, True, rendered
            
        except json.JSONDecodeError:
            # Valid Liquid but doesn't render to valid JSON
            try:
                template = Template(config_str)
                rendered = template.render(**context.get("variables", {}))
                return True, False, rendered
            except Exception:
                return False, False, None
                
        except Exception:
            # Invalid Liquid syntax
            return False, False, None
    
    def run_scenario(
        self,
        scenario: TestScenario,
        scenario_id: int,
        agent_fn: Callable[[str, dict], AgentResponse]
    ) -> ScenarioResult:
        """Run a single test scenario.
        
        Args:
            scenario: The test scenario to run
            scenario_id: Index of the scenario
            agent_fn: Function that takes (request, context) and returns AgentResponse
            
        Returns:
            ScenarioResult with all metrics
        """
        result = ScenarioResult(
            scenario_id=scenario_id,
            request=scenario.request,
            expected_action=scenario.expected_action
        )
        
        try:
            # Time the agent call
            start_time = time.perf_counter()
            response = agent_fn(scenario.request, scenario.context)
            end_time = time.perf_counter()
            
            result.latency_ms = (end_time - start_time) * 1000
            result.actual_action = response.selected_action
            result.reasoning = response.reasoning
            result.proposed_config = response.proposed_config
            
            # Check action correctness
            result.action_correct = (
                response.selected_action == scenario.expected_action
            )
            
            # Validate Liquid template
            liquid_valid, renders_to_json, rendered = self.validate_liquid_template(
                response.proposed_config,
                scenario.context
            )
            result.liquid_valid = liquid_valid
            result.renders_to_json = renders_to_json
            result.rendered_config = rendered
            
        except Exception as e:
            result.error = str(e)
            result.latency_ms = 0.0
        
        return result
    
    def run(
        self,
        agent_fn: Callable[[str, dict], AgentResponse],
        verbose: bool = False
    ) -> EvalResults:
        """Run all scenarios and compute metrics.
        
        Args:
            agent_fn: Function that takes (request, context) and returns AgentResponse
            verbose: Print progress during evaluation
            
        Returns:
            EvalResults with all metrics and details
        """
        results = EvalResults(
            timestamp=datetime.now().isoformat(),
            git_sha=self.get_git_sha(),
            prompt_hash=self.get_prompt_hash(),
            total_scenarios=len(self.scenarios)
        )
        
        scenario_results = []
        
        for i, scenario in enumerate(self.scenarios):
            if verbose:
                print(f"Running scenario {i+1}/{len(self.scenarios)}: {scenario.request[:50]}...")
            
            result = self.run_scenario(scenario, i, agent_fn)
            scenario_results.append(result)
            
            if verbose:
                status = "✓" if result.action_correct else "✗"
                print(f"  {status} Expected: {scenario.expected_action}, Got: {result.actual_action}")
        
        # Compute aggregate metrics
        successful = [r for r in scenario_results if r.error is None]
        
        results.metrics = {
            "action_accuracy": (
                sum(1 for r in successful if r.action_correct) / len(successful) * 100
                if successful else 0
            ),
            "liquid_valid": (
                sum(1 for r in successful if r.liquid_valid) / len(successful) * 100
                if successful else 0
            ),
            "renders_to_json": (
                sum(1 for r in successful if r.renders_to_json) / len(successful) * 100
                if successful else 0
            ),
            "avg_latency_ms": (
                sum(r.latency_ms for r in successful) / len(successful)
                if successful else 0
            ),
            "error_rate": (
                sum(1 for r in scenario_results if r.error is not None) / len(scenario_results) * 100
            )
        }
        
        # Store detailed results
        results.details = [asdict(r) for r in scenario_results]
        
        return results
    
    def save_results(self, results: EvalResults, filename: str) -> Path:
        """Save evaluation results to the results directory.
        
        Args:
            results: The evaluation results to save
            filename: Filename (e.g., "eval_v1.json")
            
        Returns:
            Path to the saved file
        """
        filepath = RESULTS_DIR / filename
        
        with open(filepath, "w") as f:
            json.dump(results.to_dict(), f, indent=2)
        
        return filepath
    
    @staticmethod
    def load_results(filepath: Path) -> dict:
        """Load evaluation results from a file."""
        with open(filepath) as f:
            return json.load(f)
    
    @staticmethod
    def compare_results(baseline: dict, current: dict) -> dict:
        """Compare two evaluation results and show differences.
        
        Args:
            baseline: Previous evaluation results
            current: Current evaluation results
            
        Returns:
            Dictionary with comparison metrics
        """
        comparison = {
            "baseline_timestamp": baseline.get("timestamp"),
            "current_timestamp": current.get("timestamp"),
            "baseline_prompt_hash": baseline.get("prompt_hash"),
            "current_prompt_hash": current.get("prompt_hash"),
            "metric_changes": {}
        }
        
        baseline_metrics = baseline.get("metrics", {})
        current_metrics = current.get("metrics", {})
        
        for metric in ["action_accuracy", "liquid_valid", "renders_to_json", "avg_latency_ms"]:
            baseline_val = baseline_metrics.get(metric, 0)
            current_val = current_metrics.get(metric, 0)
            change = current_val - baseline_val
            
            comparison["metric_changes"][metric] = {
                "baseline": baseline_val,
                "current": current_val,
                "change": change,
                "improved": change > 0 if metric != "avg_latency_ms" else change < 0
            }
        
        return comparison
    
    def print_results(self, results: EvalResults):
        """Pretty print evaluation results."""
        print("\n" + "=" * 60)
        print("EVALUATION RESULTS")
        print("=" * 60)
        print(f"Timestamp: {results.timestamp}")
        print(f"Git SHA: {results.git_sha}")
        print(f"Prompt Hash: {results.prompt_hash}")
        print(f"Total Scenarios: {results.total_scenarios}")
        print()
        print("METRICS:")
        print(f"  Action Accuracy:  {results.metrics['action_accuracy']:.1f}%")
        print(f"  Liquid Valid:     {results.metrics['liquid_valid']:.1f}%")
        print(f"  Renders to JSON:  {results.metrics['renders_to_json']:.1f}%")
        print(f"  Avg Latency:      {results.metrics['avg_latency_ms']:.0f}ms")
        print(f"  Error Rate:       {results.metrics['error_rate']:.1f}%")
        print()
        print("SCENARIO DETAILS:")
        for detail in results.details:
            status = "✓" if detail["action_correct"] else "✗"
            print(f"  {status} [{detail['scenario_id']+1}] {detail['request'][:40]}...")
            print(f"      Expected: {detail['expected_action']}")
            print(f"      Got:      {detail['actual_action'] or 'N/A'}")
            if detail["error"]:
                print(f"      Error:    {detail['error'][:50]}...")
        print("=" * 60)


def create_mock_agent() -> Callable[[str, dict], AgentResponse]:
    """Create a mock agent for testing the eval harness itself."""
    def mock_agent(request: str, context: dict) -> AgentResponse:
        # Simple keyword matching for testing
        request_lower = request.lower()
        
        if "slack" in request_lower:
            action = "slack_post_message"
            config = '{ "channel": "{{ slack_channel }}", "text": "{{ summary }}" }'
        elif "notion" in request_lower:
            action = "notion_create_page"
            config = '{ "parent": { "database_id": "{{ notion_database_id }}" } }'
        elif "github" in request_lower or "issue" in request_lower:
            action = "github_create_issue"
            config = '{ "title": "Issue", "body": "{{ summary }}" }'
        elif "spreadsheet" in request_lower or "sheet" in request_lower:
            if "existing" in request_lower or "append" in request_lower:
                action = "google_sheets_append"
                config = '{ "spreadsheetId": "{{ spreadsheet_id }}", "values": [] }'
            else:
                action = "google_sheets_create"
                config = '{ "properties": { "title": "New Sheet" } }'
        else:
            action = "unknown"
            config = "{}"
        
        return AgentResponse(
            selected_action=action,
            reasoning=f"Mock agent selected {action} based on keywords",
            proposed_config=config
        )
    
    return mock_agent


def main():
    """CLI entry point for the eval harness."""
    parser = argparse.ArgumentParser(description="Run Integration Agent Evaluations")
    parser.add_argument(
        "--output", "-o",
        type=str,
        help="Output filename (e.g., eval_v1.json)"
    )
    parser.add_argument(
        "--compare",
        type=str,
        nargs=2,
        metavar=("BASELINE", "CURRENT"),
        help="Compare two result files"
    )
    parser.add_argument(
        "--mock",
        action="store_true",
        help="Run with mock agent (for testing harness)"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Run with real Integration Agent (requires OPENAI_API_KEY)"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Print progress during evaluation"
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Override the model to use (e.g., gpt-4o, gpt-5)"
    )
    
    args = parser.parse_args()
    
    harness = EvalHarness()
    
    if args.compare:
        baseline = harness.load_results(Path(args.compare[0]))
        current = harness.load_results(Path(args.compare[1]))
        comparison = harness.compare_results(baseline, current)
        
        print("\n" + "=" * 60)
        print("COMPARISON RESULTS")
        print("=" * 60)
        for metric, data in comparison["metric_changes"].items():
            change_str = f"+{data['change']:.1f}" if data['change'] >= 0 else f"{data['change']:.1f}"
            status = "↑" if data['improved'] else "↓" if data['change'] != 0 else "="
            print(f"  {metric}: {data['baseline']:.1f} → {data['current']:.1f} ({change_str}) {status}")
        print("=" * 60)
        return
    
    if args.mock:
        print("Running with mock agent...")
        agent_fn = create_mock_agent()
        results = harness.run(agent_fn, verbose=args.verbose)
        harness.print_results(results)
        
        if args.output:
            filepath = harness.save_results(results, args.output)
            print(f"\nResults saved to: {filepath}")
    
    elif args.real:
        print("Running with real Integration Agent...")
        try:
            from src.agent import IntegrationAgent, get_agent_function
            
            # Initialize the vector store first
            from src.vector_store import initialize_vector_store
            print("Initializing vector store...")
            initialize_vector_store()
            
            # Create the agent
            agent = IntegrationAgent(
                model=args.model,
                verbose=args.verbose
            )
            agent_fn = get_agent_function(agent)
            
            print(f"Using model: {agent.model_name}")
            print(f"Running {len(harness.scenarios)} scenarios...\n")
            
            results = harness.run(agent_fn, verbose=args.verbose)
            harness.print_results(results)
            
            if args.output:
                filepath = harness.save_results(results, args.output)
                print(f"\nResults saved to: {filepath}")
            else:
                # Auto-generate filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"eval_{timestamp}.json"
                filepath = harness.save_results(results, filename)
                print(f"\nResults auto-saved to: {filepath}")
                
        except ImportError as e:
            print(f"Error importing agent: {e}")
            print("Make sure all dependencies are installed.")
        except Exception as e:
            print(f"Error running evaluation: {e}")
            raise
    
    else:
        print("No agent mode specified.")
        print("Use --mock to test with mock agent")
        print("Use --real to run with real Integration Agent (requires OPENAI_API_KEY)")


if __name__ == "__main__":
    main()
