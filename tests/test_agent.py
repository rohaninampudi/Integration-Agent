"""Tests for the Integration Agent.

These tests verify the agent initialization, structured output handling,
and integration with tools. Full integration tests require API access.
"""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.models import AgentResponse, AgentResponseOutput, WorkflowContext


class TestAgentImports:
    """Test that agent module imports correctly."""
    
    def test_can_import_agent_module(self):
        """Verify agent module can be imported."""
        from src import agent
        assert hasattr(agent, 'IntegrationAgent')
        assert hasattr(agent, 'create_integration_agent')
        assert hasattr(agent, 'get_agent_function')
        assert hasattr(agent, 'run_agent')
    
    def test_can_import_agent_response_output(self):
        """Verify AgentResponseOutput model is available."""
        from src.models import AgentResponseOutput
        assert AgentResponseOutput is not None


class TestAgentInputFormatting:
    """Test agent input formatting."""
    
    def test_format_user_input_includes_request(self):
        """Test that formatted input includes the user request."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI'):
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent.__new__(IntegrationAgent)
                    agent.model_name = "gpt-5"
                    agent.temperature = 0.2
                    agent.verbose = False
                    agent.tools = []
        
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
                    agent.model_name = "gpt-5"
                    agent.temperature = 0.2
                    agent.verbose = False
                    agent.tools = []
        
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


class TestStructuredOutput:
    """Test structured output handling."""
    
    def test_structured_llm_generates_valid_response(self):
        """Test that structured LLM generates valid AgentResponseOutput."""
        from src.agent import IntegrationAgent
        
        # Create mock structured output
        mock_structured = AgentResponseOutput(
            selected_action="slack_post_message",
            reasoning="User wants to post to Slack",
            proposed_config='{"channel": "{{ slack_channel }}"}'
        )
        
        # Create mock LLM with structured output
        mock_structured_llm = Mock()
        mock_structured_llm.invoke.return_value = mock_structured
        
        # Create mock ReAct agent result
        mock_react_result = {
            "messages": [
                MagicMock(content='I recommend using slack_post_message action.')
            ]
        }
        mock_react_agent = Mock()
        mock_react_agent.invoke.return_value = mock_react_result
        
        # Create mock LLM
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value = mock_structured_llm
        
        with patch('src.agent.validate_config'):
            with patch('src.agent.ChatOpenAI', return_value=mock_llm):
                with patch('src.agent.create_react_agent', return_value=mock_react_agent):
                    agent = IntegrationAgent()
        
        context = {"variables": {"slack_channel": "#test"}}
        result = agent.run("Post to Slack", context)
        
        assert result.selected_action == "slack_post_message"
        assert result.reasoning == "User wants to post to Slack"
        assert result.proposed_config == '{"channel": "{{ slack_channel }}"}'
    
    def test_structured_output_handles_errors(self):
        """Test that errors in structured output are handled gracefully."""
        from src.agent import IntegrationAgent
        
        # Create mock structured LLM that raises an error
        mock_structured_llm = Mock()
        mock_structured_llm.invoke.side_effect = Exception("API error")
        
        # Create mock ReAct agent result
        mock_react_result = {"messages": [MagicMock(content='Analysis...')]}
        mock_react_agent = Mock()
        mock_react_agent.invoke.return_value = mock_react_result
        
        # Create mock LLM
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value = mock_structured_llm
        
        with patch('src.agent.validate_config'):
            with patch('src.agent.ChatOpenAI', return_value=mock_llm):
                with patch('src.agent.create_react_agent', return_value=mock_react_agent):
                    agent = IntegrationAgent()
        
        context = {"variables": {}}
        result = agent.run("Test request", context)
        
        # Should return error response, not crash
        assert result.selected_action == "error"
        assert "failed" in result.reasoning.lower()


class TestWorkflowContextIntegration:
    """Test WorkflowContext integration."""
    
    def test_run_with_workflow_context(self):
        """Test running agent with WorkflowContext object."""
        from src.agent import IntegrationAgent
        
        mock_structured = AgentResponseOutput(
            selected_action="slack_post_message",
            reasoning="test",
            proposed_config="{}"
        )
        
        mock_structured_llm = Mock()
        mock_structured_llm.invoke.return_value = mock_structured
        
        mock_react_result = {"messages": [MagicMock(content='OK')]}
        mock_react_agent = Mock()
        mock_react_agent.invoke.return_value = mock_react_result
        
        mock_llm = Mock()
        mock_llm.with_structured_output.return_value = mock_structured_llm
        
        with patch('src.agent.validate_config'):
            with patch('src.agent.ChatOpenAI', return_value=mock_llm):
                with patch('src.agent.create_react_agent', return_value=mock_react_agent):
                    agent = IntegrationAgent()
        
        workflow_context = WorkflowContext(
            user_input="Post to Slack",
            variables={"summary": "test", "slack_channel": "#test"}
        )
        
        result = agent.run_with_workflow_context(workflow_context)
        
        assert result.selected_action == "slack_post_message"


class TestAgentConfiguration:
    """Test agent configuration options."""
    
    def test_agent_stores_temperature_setting(self):
        """Test that agent stores the provided temperature."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            mock_llm.return_value.with_structured_output.return_value = Mock()
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent(temperature=0.5)
        
        assert agent.temperature == 0.5
    
    def test_agent_uses_default_model(self):
        """Test that agent uses the configured default model."""
        from src.agent import IntegrationAgent
        from src.config import OPENAI_MODEL
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            mock_llm.return_value.with_structured_output.return_value = Mock()
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent()
        
        assert agent.model_name == OPENAI_MODEL
    
    def test_agent_allows_custom_model(self):
        """Test that agent accepts a custom model."""
        from src.agent import IntegrationAgent
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            mock_llm.return_value.with_structured_output.return_value = Mock()
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = IntegrationAgent(model="gpt-4-turbo")
        
        assert agent.model_name == "gpt-4-turbo"


class TestCreateAgentFactory:
    """Test the create_integration_agent factory function."""
    
    def test_create_agent_returns_integration_agent(self):
        """Test that create_integration_agent returns an IntegrationAgent instance."""
        from src.agent import create_integration_agent, IntegrationAgent
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            mock_llm.return_value.with_structured_output.return_value = Mock()
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = create_integration_agent()
        
        assert isinstance(agent, IntegrationAgent)
    
    def test_create_agent_passes_arguments(self):
        """Test that create_integration_agent passes arguments correctly."""
        from src.agent import create_integration_agent
        
        with patch('src.agent.ChatOpenAI') as mock_llm:
            mock_llm.return_value.with_structured_output.return_value = Mock()
            with patch('src.agent.validate_config'):
                with patch('src.agent.create_react_agent'):
                    agent = create_integration_agent(
                        model="gpt-4",
                        temperature=0.8,
                        verbose=True
                    )
        
        assert agent.model_name == "gpt-4"
        assert agent.temperature == 0.8
        assert agent.verbose == True


class TestAgentResponseOutputModel:
    """Test the AgentResponseOutput Pydantic model."""
    
    def test_agent_response_output_validation(self):
        """Test that AgentResponseOutput validates correctly."""
        output = AgentResponseOutput(
            selected_action="slack_post_message",
            reasoning="Valid reasoning",
            proposed_config='{"channel": "#test"}'
        )
        
        assert output.selected_action == "slack_post_message"
        assert output.reasoning == "Valid reasoning"
        assert output.proposed_config == '{"channel": "#test"}'
    
    def test_agent_response_output_to_agent_response(self):
        """Test converting AgentResponseOutput to AgentResponse."""
        output = AgentResponseOutput(
            selected_action="github_create_issue",
            reasoning="Creating issue",
            proposed_config='{"title": "Bug"}'
        )
        
        response = AgentResponse(
            selected_action=output.selected_action,
            reasoning=output.reasoning,
            proposed_config=output.proposed_config
        )
        
        assert response.selected_action == output.selected_action
        assert response.reasoning == output.reasoning
        assert response.proposed_config == output.proposed_config
        assert response.trace is None  # No trace by default


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
