"""Tool for retrieving API documentation from the vector store.

This tool allows the agent to retrieve relevant API documentation
for a selected integration action to understand the payload structure.
"""

import json
from pathlib import Path
from typing import Optional

from langchain_core.tools import tool

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store import get_vector_store, initialize_vector_store
from tools.get_actions import get_action_by_id


# Mapping from action IDs to integration names (for filtering)
ACTION_TO_INTEGRATION = {
    "google_sheets_create": "google_sheets",
    "google_sheets_append": "google_sheets",
    "notion_create_page": "notion",
    "notion_update_block": "notion",
    "slack_post_message": "slack",
    "airtable_create_record": "airtable",
    "hubspot_create_contact": "hubspot",
    "github_create_issue": "github",
    "trello_create_card": "trello",
    "jira_create_issue": "jira",
    "stripe_create_customer": "stripe",
    "sendgrid_send_email": "sendgrid",
    "twilio_send_sms": "twilio",
}


def _ensure_initialized():
    """Ensure the vector store is initialized."""
    store = get_vector_store()
    if store._vectorstore is None:
        initialize_vector_store()


@tool
def retrieve_api_documentation(action_id: str, query: Optional[str] = None) -> str:
    """Retrieve API documentation for a specific integration action.
    
    Use this tool AFTER selecting an action to get the detailed API
    documentation including payload structure, required fields, and examples.
    
    Args:
        action_id: The integration action ID (e.g., 'slack_post_message', 'github_create_issue')
        query: Optional additional search terms to refine the documentation search
    
    Returns:
        Relevant API documentation including payload structure and examples
    """
    _ensure_initialized()
    
    # Validate action
    action = get_action_by_id(action_id)
    if not action:
        return json.dumps({
            "error": f"Unknown action: {action_id}",
            "suggestion": "Use get_available_actions tool first to see valid action IDs"
        })
    
    # Get integration name for filtering
    integration = ACTION_TO_INTEGRATION.get(action_id)
    
    # Build search query
    search_query = f"{action['name']} {action['description']} payload structure"
    if query:
        search_query = f"{search_query} {query}"
    
    # Search the vector store
    store = get_vector_store()
    
    if integration:
        # Filter to specific integration docs
        results = store.search(search_query, k=4, filter_integration=integration)
    else:
        # No filter for unknown integrations
        results = store.search(search_query, k=4)
    
    if not results:
        return json.dumps({
            "action": action,
            "documentation": "No documentation found for this action.",
            "note": "You may need to use your knowledge of the API or ask the user for more details."
        })
    
    # Combine results into a single documentation string
    doc_sections = []
    seen_chunks = set()
    
    for doc in results:
        # Deduplicate by content hash
        content_hash = hash(doc.page_content[:100])
        if content_hash in seen_chunks:
            continue
        seen_chunks.add(content_hash)
        
        doc_sections.append(doc.page_content)
    
    documentation = "\n\n---\n\n".join(doc_sections)
    
    return json.dumps({
        "action": action,
        "api_reference": action["api_reference"],
        "documentation": documentation,
        "chunks_retrieved": len(doc_sections)
    }, indent=2)


def get_documentation_for_action(action_id: str) -> str:
    """Convenience function to get documentation (non-tool version).
    
    Args:
        action_id: The integration action ID
        
    Returns:
        Documentation string
    """
    result = retrieve_api_documentation.invoke({"action_id": action_id})
    data = json.loads(result)
    return data.get("documentation", "")
