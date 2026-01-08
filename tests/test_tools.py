"""Tests for the Integration Agent tools."""

import json
import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools import (
    get_available_actions,
    retrieve_api_documentation,
    get_action_by_id,
    validate_action_id,
    AGENT_TOOLS,
)
from src.vector_store import initialize_vector_store


class TestGetAvailableActions:
    """Tests for the get_available_actions tool."""
    
    def test_returns_all_actions(self):
        """Test that all actions are returned when no query."""
        result = get_available_actions.invoke({})
        data = json.loads(result)
        
        assert "actions" in data
        assert data["total_actions"] >= 13  # We have 13 actions
    
    def test_search_slack(self):
        """Test searching for Slack actions."""
        result = get_available_actions.invoke({"query": "slack"})
        data = json.loads(result)
        
        assert "actions" in data
        action_ids = [a["id"] for a in data["actions"]]
        assert "slack_post_message" in action_ids
    
    def test_search_spreadsheet(self):
        """Test searching for spreadsheet actions."""
        result = get_available_actions.invoke({"query": "spreadsheet"})
        data = json.loads(result)
        
        assert "actions" in data
        action_ids = [a["id"] for a in data["actions"]]
        assert "google_sheets_create" in action_ids or "google_sheets_append" in action_ids
    
    def test_search_no_results(self):
        """Test search with no matching results."""
        result = get_available_actions.invoke({"query": "xyznonexistent"})
        data = json.loads(result)
        
        assert "message" in data or len(data.get("actions", [])) == 0
    
    def test_action_structure(self):
        """Test that actions have required fields."""
        result = get_available_actions.invoke({})
        data = json.loads(result)
        
        for action in data["actions"]:
            assert "id" in action
            assert "name" in action
            assert "description" in action
            assert "api_reference" in action


class TestGetActionById:
    """Tests for the get_action_by_id helper."""
    
    def test_find_existing_action(self):
        """Test finding an existing action."""
        action = get_action_by_id("slack_post_message")
        
        assert action is not None
        assert action["id"] == "slack_post_message"
        assert action["name"] == "Send Slack Message"
    
    def test_find_nonexistent_action(self):
        """Test finding a non-existent action."""
        action = get_action_by_id("nonexistent_action")
        
        assert action is None


class TestValidateActionId:
    """Tests for the validate_action_id helper."""
    
    def test_valid_action_ids(self):
        """Test validation of valid action IDs."""
        valid_ids = [
            "slack_post_message",
            "github_create_issue",
            "google_sheets_create",
            "notion_create_page",
        ]
        
        for action_id in valid_ids:
            assert validate_action_id(action_id) is True
    
    def test_invalid_action_id(self):
        """Test validation of invalid action ID."""
        assert validate_action_id("invalid_action") is False


class TestRetrieveApiDocumentation:
    """Tests for the retrieve_api_documentation tool."""
    
    @pytest.fixture(autouse=True)
    def setup(self):
        """Initialize vector store before tests."""
        initialize_vector_store()
    
    def test_retrieve_slack_docs(self):
        """Test retrieving Slack documentation."""
        result = retrieve_api_documentation.invoke({"action_id": "slack_post_message"})
        data = json.loads(result)
        
        assert "documentation" in data
        assert "channel" in data["documentation"].lower()
    
    def test_retrieve_github_docs(self):
        """Test retrieving GitHub documentation."""
        result = retrieve_api_documentation.invoke({"action_id": "github_create_issue"})
        data = json.loads(result)
        
        assert "documentation" in data
        assert "title" in data["documentation"].lower() or "issue" in data["documentation"].lower()
    
    def test_retrieve_sheets_docs(self):
        """Test retrieving Google Sheets documentation."""
        result = retrieve_api_documentation.invoke({"action_id": "google_sheets_create"})
        data = json.loads(result)
        
        assert "documentation" in data
        assert "spreadsheet" in data["documentation"].lower() or "sheets" in data["documentation"].lower()
    
    def test_retrieve_notion_docs(self):
        """Test retrieving Notion documentation."""
        result = retrieve_api_documentation.invoke({"action_id": "notion_create_page"})
        data = json.loads(result)
        
        assert "documentation" in data
        assert "page" in data["documentation"].lower() or "notion" in data["documentation"].lower()
    
    def test_invalid_action_id(self):
        """Test error handling for invalid action ID."""
        result = retrieve_api_documentation.invoke({"action_id": "invalid_action"})
        data = json.loads(result)
        
        assert "error" in data
    
    def test_includes_action_metadata(self):
        """Test that result includes action metadata."""
        result = retrieve_api_documentation.invoke({"action_id": "slack_post_message"})
        data = json.loads(result)
        
        assert "action" in data
        assert data["action"]["id"] == "slack_post_message"
        assert "api_reference" in data


class TestAgentTools:
    """Tests for the AGENT_TOOLS list."""
    
    def test_agent_tools_not_empty(self):
        """Test that AGENT_TOOLS contains tools."""
        assert len(AGENT_TOOLS) >= 2
    
    def test_tools_are_callable(self):
        """Test that all tools are callable."""
        for tool in AGENT_TOOLS:
            assert callable(tool.invoke)


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v"])
