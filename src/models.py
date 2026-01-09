"""Pydantic models for structured output."""

from typing import Optional, Any
from pydantic import BaseModel, Field


class ToolCall(BaseModel):
    """Record of a single tool invocation."""
    
    tool_name: str = Field(description="Name of the tool that was called")
    tool_input: dict = Field(description="Input arguments to the tool")
    tool_output: str = Field(description="Output returned by the tool")
    duration_ms: float = Field(default=0.0, description="Time taken for the tool call in ms")


class ThoughtStep(BaseModel):
    """A single step in the agent's reasoning process."""
    
    step_number: int = Field(description="Step number in the sequence")
    thought: Optional[str] = Field(default=None, description="Agent's reasoning/thought")
    action: Optional[str] = Field(default=None, description="Action taken (tool call or final answer)")
    action_input: Optional[Any] = Field(default=None, description="Input to the action")
    observation: Optional[str] = Field(default=None, description="Result/observation from the action")


class AgentTrace(BaseModel):
    """Complete trace of agent execution for debugging/observability."""
    
    steps: list[ThoughtStep] = Field(default_factory=list, description="Ordered reasoning steps")
    tool_calls: list[ToolCall] = Field(default_factory=list, description="All tool invocations")
    total_duration_ms: float = Field(default=0.0, description="Total execution time in ms")
    model_name: str = Field(default="", description="Model used for this run")
    token_usage: dict = Field(default_factory=dict, description="Token usage if available")


class AgentResponseOutput(BaseModel):
    """Structured output schema for the agent (used by LLM tool calling).
    
    This model is used with LangChain's structured output feature to ensure
    deterministic, validated responses from the LLM. It does not include
    the trace field, which is added post-hoc by the agent.
    """
    
    selected_action: str = Field(
        description="The ID of the selected integration action (e.g., 'slack_post_message')"
    )
    
    reasoning: str = Field(
        description="Explanation of why this action was selected and how the config was generated"
    )
    
    proposed_config: str = Field(
        description="A Liquid template string that renders to valid JSON for the API"
    )


class AgentResponse(BaseModel):
    """Response structure for the Integration Agent.
    
    The proposed_config field contains a Liquid template string that,
    when rendered with workflow context variables, produces valid JSON
    for the selected API action.
    """
    
    selected_action: str = Field(
        description="The ID of the selected integration action (e.g., 'slack_post_message')"
    )
    
    reasoning: str = Field(
        description="Explanation of why this action was selected and how the config was generated"
    )
    
    proposed_config: str = Field(
        description="A Liquid template string that renders to valid JSON for the API"
    )
    
    trace: Optional[AgentTrace] = Field(
        default=None,
        description="Execution trace for debugging (only populated when verbose=True)"
    )


class WorkflowContext(BaseModel):
    """Workflow context containing user request and available variables."""
    
    user_input: str = Field(
        description="The user's natural language request"
    )
    
    variables: dict = Field(
        default_factory=dict,
        description="Available workflow variables (key-value pairs)"
    )


class IntegrationAction(BaseModel):
    """Metadata for an integration action."""
    
    id: str = Field(description="Unique identifier for the action")
    name: str = Field(description="Human-readable name")
    description: str = Field(description="What the action does")
    api_reference: str = Field(description="Reference to the API documentation")
