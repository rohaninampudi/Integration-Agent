"""Prompt loader for Jinja2 templates.

This module handles loading and rendering Jinja2 prompt templates
from the prompts/ directory.
"""

from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from src.config import PROMPTS_DIR


# Initialize Jinja2 environment
_env = Environment(
    loader=FileSystemLoader(PROMPTS_DIR),
    autoescape=select_autoescape(default=False),
    trim_blocks=True,
    lstrip_blocks=True
)


def load_system_prompt(variables: dict) -> str:
    """Load and render the system prompt with workflow variables.
    
    Args:
        variables: Workflow context variables dict
        
    Returns:
        Rendered system prompt string
    """
    template = _env.get_template("system_prompt.j2")
    return template.render(variables=variables)


def get_prompt_templates() -> list[str]:
    """Get list of available prompt template names."""
    return [f.name for f in PROMPTS_DIR.glob("*.j2")]


def load_user_request_prompt(request: str, variables: dict) -> str:
    """Load and render the user request prompt.
    
    Args:
        request: The user's natural language request
        variables: Workflow context variables dict
        
    Returns:
        Rendered user request prompt string
    """
    template = _env.get_template("user_request.j2")
    return template.render(request=request, variables=variables)


def load_structured_response_prompt(agent_output: str, request: str, variables: dict) -> str:
    """Load and render the structured response extraction prompt.
    
    Args:
        agent_output: Raw text output from the ReAct agent
        request: Original user request
        variables: Workflow variables dict
        
    Returns:
        Rendered structured response prompt string
    """
    template = _env.get_template("structured_response.j2")
    return template.render(
        agent_output=agent_output,
        request=request,
        variables=variables
    )


def render_template(template_name: str, **kwargs) -> str:
    """Render any template by name with provided variables.
    
    Args:
        template_name: Name of the template file (e.g., "system_prompt.j2")
        **kwargs: Variables to pass to the template
        
    Returns:
        Rendered template string
    """
    template = _env.get_template(template_name)
    return template.render(**kwargs)
