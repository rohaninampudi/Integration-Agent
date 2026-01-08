"""Tool for retrieving available integration actions.

This tool provides the agent with the list of available integration
actions so it can select the most appropriate one for the user's request.
"""

import json
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import DATA_DIR


def _load_actions() -> list[dict]:
    """Load integration actions from the JSON catalog."""
    actions_file = DATA_DIR / "actions.json"
    with open(actions_file) as f:
        return json.load(f)


@tool
def get_available_actions(query: Optional[str] = None) -> str:
    """Get the list of available integration actions.
    
    Use this tool to see what integration actions are available before
    selecting one. Each action has an id, name, description, and API reference.
    
    Args:
        query: Optional search term to filter actions (searches name and description)
    
    Returns:
        JSON string containing the list of available actions
    """
    actions = _load_actions()
    
    # Filter if query provided
    if query:
        query_lower = query.lower()
        actions = [
            a for a in actions
            if query_lower in a["name"].lower() 
            or query_lower in a["description"].lower()
            or query_lower in a["id"].lower()
        ]
    
    if not actions:
        return json.dumps({
            "message": f"No actions found matching '{query}'",
            "available_count": len(_load_actions()),
            "suggestion": "Try a broader search or call without a query to see all actions"
        })
    
    # Format for LLM readability
    result = {
        "total_actions": len(actions),
        "actions": actions
    }
    
    return json.dumps(result, indent=2)


def get_actions_for_prompt() -> str:
    """Get a formatted string of actions suitable for prompts.
    
    Returns a more readable format for including in system prompts.
    """
    actions = _load_actions()
    
    lines = ["Available Integration Actions:"]
    for action in actions:
        lines.append(f"\n- **{action['id']}**: {action['name']}")
        lines.append(f"  Description: {action['description']}")
        lines.append(f"  API Reference: {action['api_reference']}")
    
    return "\n".join(lines)


def get_action_by_id(action_id: str) -> Optional[dict]:
    """Get a specific action by its ID.
    
    Args:
        action_id: The action ID (e.g., 'slack_post_message')
        
    Returns:
        Action dict if found, None otherwise
    """
    actions = _load_actions()
    for action in actions:
        if action["id"] == action_id:
            return action
    return None


def validate_action_id(action_id: str) -> bool:
    """Check if an action ID is valid.
    
    Args:
        action_id: The action ID to validate
        
    Returns:
        True if the action exists, False otherwise
    """
    return get_action_by_id(action_id) is not None
