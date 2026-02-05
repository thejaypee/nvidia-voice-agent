"""Tests for conversational AI agent."""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add code to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from agent import ConversationAgent, AgentFactory
from config import Config


class TestConversationAgent:
    """Test conversational AI agent."""

    @pytest.fixture
    def agent(self):
        """Create agent instance."""
        return ConversationAgent()

    def test_agent_initialization(self, agent):
        """Test agent initializes correctly."""
        assert agent is not None
        assert agent.model == Config.MODEL_NAME
        assert agent.api_key == Config.NVIDIA_API_KEY
        assert agent.conversation_history == []

    def test_agent_missing_api_key(self):
        """Test agent requires API key."""
        with pytest.raises(ValueError):
            ConversationAgent(api_key="")

    def test_conversation_history(self, agent):
        """Test conversation history management."""
        assert agent.get_turn_count() == 0
        assert len(agent.conversation_history) == 0

    def test_context_trimming(self, agent):
        """Test conversation context trimming."""
        # Add many turns to exceed limit
        for i in range(20):
            agent.conversation_history.append(
                {"role": "user", "content": f"Message {i}"}
            )
            agent.conversation_history.append(
                {"role": "assistant", "content": f"Response {i}"}
            )

        initial_count = len(agent.conversation_history)
        agent._trim_context()

        # Should trim to reasonable size
        assert len(agent.conversation_history) <= initial_count

    def test_reset_conversation(self, agent):
        """Test clearing conversation history."""
        agent.conversation_history.append(
            {"role": "user", "content": "Test"}
        )
        agent.reset_conversation()

        assert len(agent.conversation_history) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
