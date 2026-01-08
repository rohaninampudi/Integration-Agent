"""Integration Agent implementation using LangGraph ReAct pattern.

This module implements the core Integration Agent that:
1. Analyzes user requests and workflow context
2. Selects appropriate integration actions using tools
3. Retrieves API documentation for accurate config generation
4. Generates Liquid-templated configurations
"""

import json
from typing import Optional

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.prebuilt import create_react_agent

from src.config import OPENAI_API_KEY, OPENAI_MODEL, AGENT_VERBOSE, validate_config
from src.models import AgentResponse, WorkflowContext
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
    
    def run(self, request: str, context: dict) -> AgentResponse:
        """Run the agent to process a user request.
        
        Args:
            request: User's natural language request
            context: Workflow context dict with 'user_input' and 'variables' keys
            
        Returns:
            AgentResponse with selected_action, reasoning, and proposed_config
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
        
        # Run the agent
        result = self.agent.invoke({"messages": messages})
        
        # Extract the final message content
        final_messages = result.get("messages", [])
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
        
        # Parse and return the response
        return self._parse_response(output)
    
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
