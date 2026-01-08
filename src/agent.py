"""Integration Agent implementation using LangGraph ReAct pattern.

This module implements the core Integration Agent that:
1. Analyzes user requests and workflow context
2. Selects appropriate integration actions using tools
3. Retrieves API documentation for accurate config generation
4. Generates Liquid-templated configurations
"""

import json
import time
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage
from langgraph.prebuilt import create_react_agent

from src.config import OPENAI_API_KEY, OPENAI_MODEL, AGENT_VERBOSE, validate_config
from src.models import AgentResponse, WorkflowContext, AgentTrace, ThoughtStep, ToolCall
from src.prompt_loader import load_system_prompt, load_user_request_prompt
from tools import AGENT_TOOLS


class IntegrationAgent:
    """Integration Agent that configures API integrations based on natural language.
    
    Usage:
        agent = IntegrationAgent()
        response = agent.run("Post the summary to Slack", context_variables)
    """
    
    def __init__(
        self, 
        model: Optional[str] = None,
        temperature: float = 0.2,
        verbose: bool = False
    ):
        """Initialize the Integration Agent.
        
        Args:
            model: OpenAI model name (defaults to config OPENAI_MODEL)
            temperature: Model temperature (lower = more deterministic)
            verbose: Enable verbose logging of agent steps
        """
        validate_config()
        
        self.model_name = model or OPENAI_MODEL
        self.temperature = temperature
        self.verbose = verbose or AGENT_VERBOSE
        
        # Initialize the LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=OPENAI_API_KEY
        )
        
        # Initialize tools
        self.tools = AGENT_TOOLS
        
        # Create the agent using LangGraph
        self._setup_agent()
    
    def _setup_agent(self):
        """Set up the LangGraph ReAct agent with tools."""
        # Create the ReAct agent using LangGraph
        self.agent = create_react_agent(
            model=self.llm,
            tools=self.tools
        )
    
    def _format_user_input(self, request: str, variables: dict) -> str:
        """Format the user input with workflow context.
        
        Args:
            request: User's natural language request
            variables: Available workflow variables
            
        Returns:
            Formatted user input string
        """
        return load_user_request_prompt(request, variables)
    
    def _parse_response(self, output: str) -> AgentResponse:
        """Parse the agent output into an AgentResponse.
        
        Args:
            output: Raw agent output string
            
        Returns:
            Parsed AgentResponse object
        """
        import re
        
        # Try to extract JSON from the output
        try:
            # Look for JSON block in markdown
            if "```json" in output:
                start = output.find("```json") + 7
                end = output.find("```", start)
                if end == -1:
                    # Unclosed markdown block - take rest of string
                    json_str = output[start:].strip()
                else:
                    json_str = output[start:end].strip()
            elif "```" in output:
                start = output.find("```") + 3
                end = output.find("```", start)
                if end == -1:
                    json_str = output[start:].strip()
                else:
                    json_str = output[start:end].strip()
            else:
                # Try to find JSON object in raw output
                # Look for { at start of line or after whitespace
                match = re.search(r'^\s*\{', output, re.MULTILINE)
                if match:
                    json_str = output[match.start():].strip()
                else:
                    json_str = output.strip()
            
            # Parse the JSON
            data = json.loads(json_str)
            
            return AgentResponse(
                selected_action=data.get("selected_action", "unknown"),
                reasoning=data.get("reasoning", "No reasoning provided"),
                proposed_config=data.get("proposed_config", "{}")
            )
            
        except (json.JSONDecodeError, KeyError) as e:
            # Try to extract fields using regex as fallback
            selected_action = self._extract_field(output, "selected_action") or "parse_error"
            reasoning = self._extract_field(output, "reasoning") or f"Parse failed: {str(e)}"
            proposed_config = self._extract_field(output, "proposed_config") or "{}"
            
            # If we found a valid action, return it
            if selected_action != "parse_error":
                return AgentResponse(
                    selected_action=selected_action,
                    reasoning=reasoning,
                    proposed_config=proposed_config
                )
            
            # Full fallback
            return AgentResponse(
                selected_action="parse_error",
                reasoning=f"Failed to parse agent output: {str(e)}\nRaw output: {output[:500]}",
                proposed_config="{}"
            )
    
    def _extract_field(self, text: str, field_name: str) -> str | None:
        """Extract a JSON field value using regex (fallback for truncated responses).
        
        Args:
            text: The text to search in
            field_name: The JSON field name to extract
            
        Returns:
            The field value or None if not found
        """
        import re
        
        # Pattern for "field_name": "value" or "field_name": value
        pattern = rf'"{field_name}"\s*:\s*"([^"]*(?:\\.[^"]*)*)"'
        match = re.search(pattern, text)
        if match:
            # Unescape JSON string escapes
            return match.group(1).replace('\\"', '"').replace('\\n', '\n')
        
        return None
    
    def _extract_trace(self, messages: list, total_duration_ms: float) -> AgentTrace:
        """Extract execution trace from LangGraph messages.
        
        This parses the message history to reconstruct the agent's
        reasoning process, tool calls, and observations.
        
        Args:
            messages: List of messages from the agent execution
            total_duration_ms: Total execution time
            
        Returns:
            AgentTrace with steps and tool calls
        """
        trace = AgentTrace(
            total_duration_ms=total_duration_ms,
            model_name=self.model_name
        )
        
        steps = []
        tool_calls_list = []
        step_number = 1
        current_thought = None
        
        # Track tool calls by ID for matching with tool messages
        pending_tool_calls = {}
        
        for msg in messages:
            # Skip system and human messages (they're the input)
            if isinstance(msg, (SystemMessage, HumanMessage)):
                continue
            
            # AI Message - contains thoughts and tool call decisions
            if isinstance(msg, AIMessage):
                content = msg.content if msg.content else ""
                tool_calls = getattr(msg, 'tool_calls', []) or []
                
                # If there's content before tool calls, it's a thought
                if content and not tool_calls:
                    # This is a final response (no more tool calls)
                    steps.append(ThoughtStep(
                        step_number=step_number,
                        thought="Generating final response",
                        action="Final Answer",
                        action_input=None,
                        observation=content[:200] + "..." if len(content) > 200 else content
                    ))
                    step_number += 1
                
                # Process tool calls
                for tc in tool_calls:
                    tool_name = tc.get('name', 'unknown')
                    tool_args = tc.get('args', {})
                    tool_id = tc.get('id', '')
                    
                    # Create a thought step for the tool call
                    thought = self._infer_thought(tool_name, tool_args)
                    
                    step = ThoughtStep(
                        step_number=step_number,
                        thought=thought,
                        action=f"Call tool: {tool_name}",
                        action_input=tool_args,
                        observation=None  # Will be filled in by ToolMessage
                    )
                    steps.append(step)
                    pending_tool_calls[tool_id] = (step, len(steps) - 1)
                    step_number += 1
            
            # Tool Message - contains tool output/observation
            elif isinstance(msg, ToolMessage):
                tool_id = getattr(msg, 'tool_call_id', '')
                tool_name = getattr(msg, 'name', 'unknown')
                content = msg.content if msg.content else ""
                
                # Truncate very long tool outputs for readability
                truncated_content = content[:500] + "..." if len(content) > 500 else content
                
                # Match with pending tool call
                if tool_id in pending_tool_calls:
                    step, idx = pending_tool_calls[tool_id]
                    steps[idx].observation = truncated_content
                
                # Also record as a tool call
                tool_calls_list.append(ToolCall(
                    tool_name=tool_name,
                    tool_input=pending_tool_calls.get(tool_id, ({}, 0))[0].action_input or {},
                    tool_output=truncated_content,
                    duration_ms=0  # We don't have per-tool timing
                ))
        
        trace.steps = steps
        trace.tool_calls = tool_calls_list
        
        return trace
    
    def _infer_thought(self, tool_name: str, tool_args: dict) -> str:
        """Infer the agent's reasoning based on which tool it called.
        
        Args:
            tool_name: Name of the tool being called
            tool_args: Arguments to the tool
            
        Returns:
            Human-readable thought/reasoning
        """
        if tool_name == "get_available_actions":
            return "I need to see what integration actions are available to handle this request."
        elif tool_name == "retrieve_api_documentation":
            action_id = tool_args.get('action_id', 'the selected action')
            return f"Now I need to retrieve the API documentation for '{action_id}' to understand the required payload structure."
        elif tool_name == "search_actions":
            query = tool_args.get('query', '')
            return f"Searching for actions matching '{query}' to find the best fit."
        else:
            return f"Calling {tool_name} to gather more information."
    
    def _print_trace(self, trace: AgentTrace):
        """Print the execution trace in a human-readable format.
        
        Args:
            trace: The execution trace to print
        """
        print("\n" + "═" * 60)
        print("🔍 AGENT EXECUTION TRACE")
        print("═" * 60)
        print(f"Model: {trace.model_name}")
        print(f"Total Duration: {trace.total_duration_ms:.0f}ms")
        print(f"Tool Calls: {len(trace.tool_calls)}")
        print("═" * 60)
        
        for step in trace.steps:
            print(f"\n📍 Step {step.step_number}")
            print("─" * 40)
            
            if step.thought:
                print(f"💭 Thought: {step.thought}")
            
            if step.action:
                print(f"🎬 Action: {step.action}")
            
            if step.action_input:
                # Pretty print the input, but keep it compact
                if isinstance(step.action_input, dict):
                    input_str = json.dumps(step.action_input, indent=2)
                    # Limit to 3 lines for readability
                    lines = input_str.split('\n')
                    if len(lines) > 5:
                        input_str = '\n'.join(lines[:5]) + '\n   ...'
                else:
                    input_str = str(step.action_input)
                print(f"📥 Input: {input_str}")
            
            if step.observation:
                # Truncate long observations
                obs = step.observation
                if len(obs) > 300:
                    obs = obs[:300] + "..."
                print(f"👁️  Observation: {obs}")
        
        print("\n" + "═" * 60)
    
    def run(self, request: str, context: dict) -> AgentResponse:
        """Run the agent to process a user request.
        
        Args:
            request: User's natural language request
            context: Workflow context dict with 'user_input' and 'variables' keys
            
        Returns:
            AgentResponse with selected_action, reasoning, proposed_config, and optional trace
        """
        # Extract variables from context
        variables = context.get("variables", {})
        
        # Load system prompt with variables
        system_prompt = load_system_prompt(variables)
        
        # Format user input
        user_input = self._format_user_input(request, variables)
        
        # Build messages
        messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_input)
        ]
        
        # Track execution time
        start_time = time.perf_counter()
        
        # Run the agent
        result = self.agent.invoke({"messages": messages})
        
        # Calculate duration
        end_time = time.perf_counter()
        duration_ms = (end_time - start_time) * 1000
        
        # Extract the final message content
        final_messages = result.get("messages", [])
        
        # Extract trace if verbose mode is enabled
        trace = None
        if self.verbose and final_messages:
            trace = self._extract_trace(final_messages, duration_ms)
            self._print_trace(trace)
        
        if final_messages:
            # Get the last AI message
            for msg in reversed(final_messages):
                if hasattr(msg, "content") and msg.content:
                    output = msg.content
                    break
            else:
                output = "{}"
        else:
            output = "{}"
        
        # Parse the response
        response = self._parse_response(output)
        
        # Attach trace if we have it
        if trace:
            response.trace = trace
        
        return response
    
    def run_with_workflow_context(self, workflow_context: WorkflowContext) -> AgentResponse:
        """Run the agent with a WorkflowContext object.
        
        Args:
            workflow_context: WorkflowContext with user_input and variables
            
        Returns:
            AgentResponse with selected_action, reasoning, and proposed_config
        """
        context = {
            "user_input": workflow_context.user_input,
            "variables": workflow_context.variables
        }
        return self.run(workflow_context.user_input, context)


def create_agent(
    model: Optional[str] = None,
    temperature: float = 0.2,
    verbose: bool = False
) -> IntegrationAgent:
    """Factory function to create an IntegrationAgent.
    
    Args:
        model: OpenAI model name
        temperature: Model temperature
        verbose: Enable verbose logging
        
    Returns:
        Configured IntegrationAgent instance
    """
    return IntegrationAgent(
        model=model,
        temperature=temperature,
        verbose=verbose
    )


def get_agent_function(agent: IntegrationAgent):
    """Get a simple function wrapper for the agent (for eval harness).
    
    Args:
        agent: IntegrationAgent instance
        
    Returns:
        Function that takes (request, context) and returns AgentResponse
    """
    def agent_fn(request: str, context: dict) -> AgentResponse:
        return agent.run(request, context)
    
    return agent_fn


# Module-level agent instance (lazy initialization)
_agent_instance: Optional[IntegrationAgent] = None


def get_agent() -> IntegrationAgent:
    """Get the shared agent instance (creates one if needed)."""
    global _agent_instance
    if _agent_instance is None:
        _agent_instance = IntegrationAgent()
    return _agent_instance


def run_agent(request: str, context: dict) -> AgentResponse:
    """Convenience function to run the agent.
    
    Args:
        request: User's natural language request
        context: Workflow context dict
        
    Returns:
        AgentResponse
    """
    return get_agent().run(request, context)
