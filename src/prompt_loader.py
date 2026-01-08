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


def load_config_prompt(
    api_docs: str,
    user_request: str,
    selected_action: str,
    variables: dict
) -> str:
    """Load and render the config generation prompt.
    
    Args:
        api_docs: Retrieved API documentation
        user_request: The user's request
        selected_action: The selected integration action ID
        variables: Workflow context variables dict
        
    Returns:
        Rendered config generation prompt string
    """
    template = _env.get_template("config_generation.j2")
    return template.render(
        api_docs=api_docs,
        user_request=user_request,
        selected_action=selected_action,
        variables=variables
    )


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
