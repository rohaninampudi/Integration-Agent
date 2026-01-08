"""Tests for the Integration Agent.

These tests verify the agent initialization, parsing, and integration
with tools. Full integration tests require API access.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import AgentResponse, WorkflowContext


class TestAgentImports:
    """Test that agent module imports correctly."""
    
    def test_can_import_agent_module(self):
        """Verify agent module can be imported."""
        from src import agent
        assert hasattr(agent, 'IntegrationAgent')
        assert hasattr(agent, 'create_agent')
        assert hasattr(agent, 'get_agent_function')
        assert hasattr(agent, 'run_agent')


class TestAgentResponseParsing:
    """Test agent response parsing logic."""
    
    def test_parse_valid_json_response(self):
        """Test parsing a valid JSON response."""
        from src.agent import IntegrationAgent
        
        # Create agent instance with mocked dependencies
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent.__new__(IntegrationAgent)
                    agent.verbose = False
        
        output = '''Here is the configuration:
```json
{
  "selected_action": "slack_post_message",
  "reasoning": "User wants to post to Slack",
  "proposed_config": "{ \\"channel\\": \\"{{ slack_channel }}\\", \\"text\\": \\"{{ summary }}\\" }"
}
```'''
        
        response = agent._parse_response(output)
        
        assert response.selected_action == "slack_post_message"
        assert "Slack" in response.reasoning
        assert "slack_channel" in response.proposed_config
    
    def test_parse_json_without_markdown(self):
        """Test parsing JSON without markdown code blocks."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent.__new__(IntegrationAgent)
                    agent.verbose = False
        
        output = '{"selected_action": "github_create_issue", "reasoning": "Creating issue", "proposed_config": "{}"}'
        
        response = agent._parse_response(output)
        
        assert response.selected_action == "github_create_issue"
    
    def test_parse_invalid_json_returns_error(self):
        """Test that invalid JSON returns an error response."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent.__new__(IntegrationAgent)
                    agent.verbose = False
        
        output = "This is not valid JSON at all"
        
        response = agent._parse_response(output)
        
        assert response.selected_action == "parse_error"
        assert "Failed to parse" in response.reasoning


class TestAgentInputFormatting:
    """Test agent input formatting."""
    
    def test_format_user_input_includes_request(self):
        """Test that formatted input includes the user request."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent.__new__(IntegrationAgent)
        
        request = "Post the summary to Slack"
        variables = {"summary": "Test summary", "slack_channel": "#test"}
        
        formatted = agent._format_user_input(request, variables)
        
        assert "Post the summary to Slack" in formatted
        assert "summary" in formatted
        assert "slack_channel" in formatted
    
    def test_format_user_input_includes_variables(self):
        """Test that formatted input includes all variables."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent.__new__(IntegrationAgent)
        
        request = "Test request"
        variables = {
            "var1": "value1",
            "var2": 42,
            "var3": ["a", "b", "c"]
        }
        
        formatted = agent._format_user_input(request, variables)
        
        assert "var1" in formatted
        assert "value1" in formatted
        assert "var2" in formatted
        assert "42" in formatted
        assert "var3" in formatted


class TestAgentFunctionWrapper:
    """Test the agent function wrapper for eval harness."""
    
    def test_get_agent_function_returns_callable(self):
        """Test that get_agent_function returns a callable."""
        from src.agent import get_agent_function
        
        # Create a mock agent
        mock_agent = Mock()
        mock_agent.run.return_value = AgentResponse(
            selected_action="test_action",
            reasoning="test reasoning",
            proposed_config="{}"
        )
        
        agent_fn = get_agent_function(mock_agent)
        
        assert callable(agent_fn)
    
    def test_agent_function_calls_agent_run(self):
        """Test that the wrapper function calls agent.run correctly."""
        from src.agent import get_agent_function
        
        mock_agent = Mock()
        mock_agent.run.return_value = AgentResponse(
            selected_action="slack_post_message",
            reasoning="test",
            proposed_config="{}"
        )
        
        agent_fn = get_agent_function(mock_agent)
        
        context = {"variables": {"summary": "test"}}
        result = agent_fn("Post to Slack", context)
        
        mock_agent.run.assert_called_once_with("Post to Slack", context)
        assert result.selected_action == "slack_post_message"


class TestWorkflowContextIntegration:
    """Test WorkflowContext integration."""
    
    def test_run_with_workflow_context(self):
        """Test running agent with WorkflowContext object."""
        from src.agent import IntegrationAgent
        
        # Create a mock agent
        mock_result = {
            "messages": [
                MagicMock(content='{"selected_action": "slack_post_message", "reasoning": "test", "proposed_config": "{}"}')
            ]
        }
        mock_agent_graph = Mock()
        mock_agent_graph.invoke.return_value = mock_result
        
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent', return_value=mock_agent_graph):
                    agent = IntegrationAgent()
        
        workflow_context = WorkflowContext(
            user_input="Post to Slack",
            variables={"summary": "test", "slack_channel": "#test"}
        )
        
        result = agent.run_with_workflow_context(workflow_context)
        
        assert result.selected_action == "slack_post_message"


class TestAgentConfiguration:
    """Test agent configuration options."""
    
    def test_agent_respects_temperature_setting(self):
        """Test that agent uses the provided temperature."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent(temperature=0.5)
        
        # Verify ChatOpenAI was called with correct temperature
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs['temperature'] == 0.5
    
    def test_agent_uses_default_model(self):
        """Test that agent uses the configured default model."""
        from src.agent import IntegrationAgent
        from src.config import OPENAI_MODEL
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent()
        
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs['model'] == OPENAI_MODEL
    
    def test_agent_allows_custom_model(self):
        """Test that agent accepts a custom model."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent(model="gpt-4-turbo")
        
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs['model'] == "gpt-4-turbo"


class TestCreateAgentFactory:
    """Test the create_agent factory function."""
    
    def test_create_agent_returns_integration_agent(self):
        """Test that create_agent returns an IntegrationAgent instance."""
        from src.agent import create_agent, IntegrationAgent
        
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = create_agent()
        
        assert isinstance(agent, IntegrationAgent)
    
    def test_create_agent_passes_arguments(self):
        """Test that create_agent passes arguments correctly."""
        from src.agent import create_agent
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = create_agent(
                        model="gpt-4",
                        temperature=0.8,
                        verbose=True
                    )
        
        call_kwargs = mock_llm.call_args[1]
        assert call_kwargs['model'] == "gpt-4"
        assert call_kwargs['temperature'] == 0.8
        assert agent.verbose == True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
