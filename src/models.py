"""Pydantic models for structured output."""

from pydantic import BaseModel, Field


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
