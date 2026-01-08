#!/usr/bin/env python3
"""Integration Agent CLI.

A command-line interface for the Integration Agent that helps users
configure API integrations based on natural language requests.

Usage:
    python cli.py "Post the summary to Slack"
    python cli.py --context '{"summary": "test"}' "Post to Slack"
    python cli.py --verbose "Create a GitHub issue"
    python cli.py --interactive
"""

import argparse
import json
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.config import OPENAI_MODEL, validate_config
from src.models import AgentResponse
from src.vector_store import initialize_vector_store


def print_header():
    """Print the CLI header."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║              🔌 Integration Agent CLI                        ║
║         Configure API integrations with natural language     ║
╚══════════════════════════════════════════════════════════════╝
""")


def print_response(response: AgentResponse, verbose: bool = False):
    """Pretty print an agent response.
    
    Args:
        response: The AgentResponse to print
        verbose: Whether to show full details
    """
    print("\n" + "─" * 60)
    print("📋 AGENT RESPONSE")
    print("─" * 60)
    
    print(f"\n🎯 Selected Action: {response.selected_action}")
    
    print(f"\n💭 Reasoning:")
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
    
    print(f"\n📝 Proposed Configuration (Liquid Template):")
    
    if verbose:
        # Show full config
        print(f"   {response.proposed_config}")
    else:
        # Show truncated if very long
        config = response.proposed_config
        if len(config) > 200:
            print(f"   {config[:200]}...")
            print(f"   (truncated, use --verbose to see full config)")
        else:
            print(f"   {config}")
    
    print("\n" + "─" * 60)


def run_interactive(agent, verbose: bool = False):
    """Run the agent in interactive mode.
    
    Args:
        agent: IntegrationAgent instance
        verbose: Enable verbose output
    """
    print("\n🎤 Interactive Mode")
    print("Type your integration request, or 'quit' to exit.")
    print("Use 'set <key> <value>' to set workflow variables.")
    print()
    
    variables = {}
    
    while True:
        try:
            request = input("You> ").strip()
            
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
                    print(f"✓ Set {key} = {variables[key]}")
                else:
                    print("Usage: set <key> <value>")
                continue
            
            if request.lower() == 'vars':
                print("Current variables:", json.dumps(variables, indent=2))
                continue
            
            if request.lower() == 'clear':
                variables = {}
                print("✓ Cleared all variables")
                continue
            
            # Run the agent
            print("\n⏳ Processing...")
            context = {"variables": variables}
            response = agent.run(request, context)
            print_response(response, verbose)
            print()
            
        except KeyboardInterrupt:
            print("\nGoodbye! 👋")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Integration Agent CLI - Configure API integrations with natural language",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "Post the summary to Slack"
  %(prog)s --context '{"summary": "test", "slack_channel": "#alerts"}' "Post to Slack"
  %(prog)s --interactive
  %(prog)s --verbose "Create a GitHub issue for the error"
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
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
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
    
    # Validate we have either a request or interactive mode
    if not args.request and not args.interactive:
        parser.print_help()
        print("\nError: Provide a request or use --interactive mode")
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
            print(f"✓ Using model: {agent.model_name}")
        
        if args.interactive:
            run_interactive(agent, args.verbose)
        else:
            # Parse context
            if args.context_file:
                with open(args.context_file) as f:
                    variables = json.load(f)
            else:
                variables = json.loads(args.context)
            
            context = {"variables": variables}
            
            if not args.json:
                print(f"📨 Request: {args.request}")
                if variables:
                    print(f"📎 Variables: {list(variables.keys())}")
                print("\n⏳ Processing...\n")
            
            # Run the agent
            response = agent.run(args.request, context)
            
            if args.json:
                # Output as JSON
                output = {
                    "selected_action": response.selected_action,
                    "reasoning": response.reasoning,
                    "proposed_config": response.proposed_config
                }
                print(json.dumps(output, indent=2))
            else:
                print_response(response, args.verbose)
            
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
