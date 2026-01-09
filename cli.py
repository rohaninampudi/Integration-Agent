#!/usr/bin/env python3
"""Integration Agent CLI.

A command-line interface for the Integration Agent that helps users
configure API integrations based on natural language requests.

Usage:
    python cli.py "Post the summary to Slack"
    python cli.py --context '{"summary": "test"}' "Post to Slack"
    python cli.py --debug -f examples/slack_message.json  # Shows reasoning trace
    python cli.py --interactive
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import OPENAI_MODEL, validate_config
from src.models import AgentResponse, AgentTrace
from src.vector_store import initialize_vector_store


# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


def print_trace(trace: AgentTrace):
    """Pretty print the agent execution trace.
    
    Args:
        trace: The execution trace to display
    """
    print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}🔍 AGENT REASONING TRACE{Colors.RESET}")
    print(f"{Colors.BOLD}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.DIM}Model: {trace.model_name} | Duration: {trace.total_duration_ms:.0f}ms | Tool Calls: {len(trace.tool_calls)}{Colors.RESET}")
    print(f"{'═' * 70}")
    
    for step in trace.steps:
        print(f"\n{Colors.BOLD}{Colors.YELLOW}📍 Step {step.step_number}{Colors.RESET}")
        print(f"{'─' * 50}")
        
        if step.thought:
            print(f"{Colors.CYAN}💭 Thought:{Colors.RESET}")
            # Word wrap the thought
            thought_words = step.thought.split()
            line = "   "
            for word in thought_words:
                if len(line) + len(word) > 67:
                    print(line)
                    line = "   " + word
                else:
                    line += " " + word if line.strip() else "   " + word
            if line.strip():
                print(line)
        
        if step.action:
            print(f"\n{Colors.GREEN}🎬 Action:{Colors.RESET} {step.action}")
        
        if step.action_input:
            print(f"{Colors.BLUE}📥 Input:{Colors.RESET}")
            if isinstance(step.action_input, dict):
                # Pretty print JSON input
                for key, value in step.action_input.items():
                    val_str = str(value)
                    if len(val_str) > 50:
                        val_str = val_str[:50] + "..."
                    print(f"      {Colors.DIM}{key}:{Colors.RESET} {val_str}")
            else:
                print(f"      {step.action_input}")
        
        if step.observation:
            print(f"\n{Colors.YELLOW}👁️  Observation:{Colors.RESET}")
            # Truncate and format observation
            obs = step.observation
            if len(obs) > 400:
                obs = obs[:400] + f"{Colors.DIM}... (truncated){Colors.RESET}"
            
            # Indent observation lines
            for line in obs.split('\n')[:10]:  # Max 10 lines
                if line.strip():
                    print(f"      {line[:80]}")
    
    print(f"\n{Colors.BOLD}{'═' * 70}{Colors.RESET}")
    print(f"{Colors.GREEN}✓ Agent completed reasoning in {len(trace.steps)} steps{Colors.RESET}")
    print(f"{'═' * 70}\n")


def print_header():
    """Print the CLI header."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🔌 Integration Agent CLI                        ║
║         Configure API integrations with natural language     ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_response(response: AgentResponse, show_trace: bool = False):
    """Pretty print an agent response.
    
    Args:
        response: The AgentResponse to print
        show_trace: Whether to display the execution trace
    """
    # Show trace first if available and requested
    if show_trace and response.trace:
        print_trace(response.trace)
    
    print("\n" + "─" * 60)
    print(f"{Colors.BOLD}📋 AGENT RESPONSE{Colors.RESET}")
    print("─" * 60)
    
    print(f"\n{Colors.GREEN}🎯 Selected Action:{Colors.RESET} {Colors.BOLD}{response.selected_action}{Colors.RESET}")
    
    print(f"\n{Colors.CYAN}💭 Reasoning:{Colors.RESET}")
    # Wrap reasoning text
    reasoning_lines = response.reasoning.split('\n')
    for line in reasoning_lines:
        if len(line) > 70:
            # Simple word wrap
            words = line.split()
            current_line = "   "
            for word in words:
                if len(current_line) + len(word) > 73:
                    print(current_line)
                    current_line = "   " + word
                else:
                    current_line += " " + word if current_line.strip() else "   " + word
            if current_line.strip():
                print(current_line)
        else:
            print(f"   {line}")
    
    print(f"\n{Colors.BLUE}📝 Proposed Configuration (Liquid Template):{Colors.RESET}")
    
    # Always show full config (no truncation)
    try:
        # Try to pretty print if it's valid JSON
        config_parsed = json.loads(response.proposed_config.replace('{{', '__LBRACE__').replace('}}', '__RBRACE__'))
        config_str = json.dumps(config_parsed, indent=2).replace('__LBRACE__', '{{').replace('__RBRACE__', '}}')
        for line in config_str.split('\n'):
            print(f"   {line}")
    except:
        # If not valid JSON, just print as-is
        print(f"   {response.proposed_config}")
    
    # Show trace summary if available but not fully displayed
    if response.trace and not show_trace:
        print(f"\n{Colors.DIM}💡 Tip: Use --debug to see the agent's reasoning trace ({len(response.trace.steps)} steps, {len(response.trace.tool_calls)} tool calls){Colors.RESET}")
    
    print("\n" + "─" * 60)


def run_interactive(agent, debug: bool = False):
    """Run the agent in interactive mode.
    
    Args:
        agent: IntegrationAgent instance
        debug: Enable debug mode (shows reasoning trace)
    """
    print(f"\n{Colors.BOLD}🎤 Interactive Mode{Colors.RESET}")
    print("Type your integration request, or 'quit' to exit.")
    print("Commands: 'set <key> <value>', 'vars', 'clear', 'debug', 'quit'")
    if debug:
        print(f"{Colors.GREEN}✓ Debug mode enabled - showing reasoning traces{Colors.RESET}")
    print()
    
    variables = {}
    show_trace = debug
    
    while True:
        try:
            request = input(f"{Colors.BOLD}You>{Colors.RESET} ").strip()
            
            if not request:
                continue
            
            if request.lower() in ('quit', 'exit', 'q'):
                print("Goodbye! 👋")
                break
            
            if request.lower().startswith('set '):
                # Set a variable
                parts = request[4:].split(' ', 1)
                if len(parts) == 2:
                    key, value = parts
                    # Try to parse value as JSON
                    try:
                        variables[key] = json.loads(value)
                    except json.JSONDecodeError:
                        variables[key] = value
                    print(f"{Colors.GREEN}✓ Set {key} = {variables[key]}{Colors.RESET}")
                else:
                    print("Usage: set <key> <value>")
                continue
            
            if request.lower() == 'vars':
                print(f"{Colors.CYAN}Current variables:{Colors.RESET}", json.dumps(variables, indent=2))
                continue
            
            if request.lower() == 'clear':
                variables = {}
                print(f"{Colors.GREEN}✓ Cleared all variables{Colors.RESET}")
                continue
            
            if request.lower() == 'debug':
                show_trace = not show_trace
                status = "enabled" if show_trace else "disabled"
                print(f"{Colors.GREEN}✓ Debug mode {status}{Colors.RESET}")
                continue
            
            if request.lower() == 'help':
                print(f"""
{Colors.BOLD}Available Commands:{Colors.RESET}
  set <key> <value>  - Set a workflow variable
  vars               - Show current variables
  clear              - Clear all variables
  debug              - Toggle debug mode (show/hide reasoning trace)
  help               - Show this help
  quit               - Exit interactive mode
  
{Colors.BOLD}Example:{Colors.RESET}
  set summary "Build completed successfully"
  set slack_channel "#alerts"
  Post the summary to Slack
""")
                continue
            
            # Run the agent
            print(f"\n{Colors.YELLOW}⏳ Processing...{Colors.RESET}")
            context = {"variables": variables}
            response = agent.run(request, context)
            print_response(response, show_trace=show_trace)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Integration Agent CLI - Configure API integrations with natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Post the summary to Slack"
  %(prog)s --context '{"summary": "test", "slack_channel": "#alerts"}' "Post to Slack"
  %(prog)s --debug -f examples/slack_message.json
  %(prog)s --interactive
        """
    )
    
    parser.add_argument(
        "request",
        nargs="?",
        help="Natural language request for the integration"
    )
    
    parser.add_argument(
        "-c", "--context",
        type=str,
        default="{}",
        help="JSON string with workflow variables (default: {})"
    )
    
    parser.add_argument(
        "-f", "--context-file",
        type=str,
        help="Path to JSON file with workflow variables"
    )
    
    parser.add_argument(
        "-i", "--interactive",
        action="store_true",
        help="Run in interactive mode"
    )
    
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode (shows agent reasoning steps)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help=f"Override the model (default: {OPENAI_MODEL})"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output response as JSON"
    )
    
    parser.add_argument(
        "--no-header",
        action="store_true",
        help="Suppress the header banner"
    )
    
    args = parser.parse_args()
    
    # Validate we have either a request, interactive mode, or a context file
    # (context file may contain user_input)
    if not args.request and not args.interactive and not args.context_file:
        parser.print_help()
        print("\nError: Provide a request, use --interactive mode, or provide a context file with user_input")
        sys.exit(1)
    
    # Print header
    if not args.no_header and not args.json:
        print_header()
    
    try:
        # Validate config
        validate_config()
        
        # Initialize vector store
        if not args.json:
            print("🔧 Initializing...")
        initialize_vector_store()
        
        # Import and create agent
        from src.agent import IntegrationAgent
        agent = IntegrationAgent(
            model=args.model,
            verbose=args.debug
        )
        
        if not args.json:
            print(f"{Colors.GREEN}✓ Using model: {agent.model_name}{Colors.RESET}")
            if args.debug:
                print(f"{Colors.CYAN}✓ Debug mode enabled - will show reasoning trace{Colors.RESET}")
        
        if args.interactive:
            run_interactive(agent, debug=args.debug)
        else:
            # Parse context
            if args.context_file:
                with open(args.context_file) as f:
                    context_data = json.load(f)
                    # Support both formats:
                    # 1. INSTRUCTIONS.MD format: {"user_input": "...", "variables": {...}}
                    # 2. Direct variables: {...} (backward compatible)
                    if "variables" in context_data:
                        variables = context_data["variables"]
                        # If user_input is in file but no request arg, use it
                        if not args.request and "user_input" in context_data:
                            args.request = context_data["user_input"]
                    else:
                        # Legacy format: entire JSON is variables
                        variables = context_data
            else:
                variables = json.loads(args.context)
            
            # Final validation: ensure we have a request
            if not args.request:
                print("❌ Error: No request provided. Either pass a request as an argument or include 'user_input' in your context file.")
                sys.exit(1)
            
            context = {"variables": variables}
            
            if not args.json:
                print(f"{Colors.BLUE}📨 Request:{Colors.RESET} {args.request}")
                if variables:
                    print(f"{Colors.BLUE}📎 Variables:{Colors.RESET} {list(variables.keys())}")
                print(f"\n{Colors.YELLOW}⏳ Processing...{Colors.RESET}\n")
            
            # Run the agent
            response = agent.run(args.request, context)
            
            if args.json:
                # Output as JSON
                output = {
                    "selected_action": response.selected_action,
                    "reasoning": response.reasoning,
                    "proposed_config": response.proposed_config
                }
                # Include trace if available
                if response.trace:
                    output["trace"] = {
                        "steps": [s.model_dump() for s in response.trace.steps],
                        "tool_calls": [t.model_dump() for t in response.trace.tool_calls],
                        "total_duration_ms": response.trace.total_duration_ms
                    }
                print(json.dumps(output, indent=2))
            else:
                print_response(response, show_trace=args.debug)
            
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nCancelled.")
        sys.exit(0)
    except Exception as e:
        if args.debug:
            raise
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
