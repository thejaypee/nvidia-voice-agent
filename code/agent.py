"""Conversational AI agent using NVIDIA models."""

from typing import Optional, List, Dict
from openai import OpenAI
from .config import Config, logger


class ConversationAgent:
    """AI agent for conversational responses using NVIDIA models."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize the conversational agent.

        Args:
            api_key: Nvidia API key (default: from config)
            model: Model name (default: from config)
            system_prompt: System instruction (default: from config)
        """
        self.api_key = api_key or Config.NVIDIA_API_KEY
        self.model = model or Config.MODEL_NAME
        self.system_prompt = system_prompt or Config.SYSTEM_PROMPT

        if not self.api_key:
            raise ValueError("NVIDIA_API_KEY not provided and not in config")

        # Initialize OpenAI client for Nvidia API (OpenAI-compatible)
        self.client = OpenAI(
            base_url=Config.NVIDIA_BASE_URL, api_key=self.api_key
        )

        # Conversation history
        self.conversation_history: List[Dict[str, str]] = []

        logger.info(
            f"Initialized agent with model: {self.model} "
            f"(max context: {Config.MAX_CONTEXT_TURNS} turns)"
        )

    def _build_messages(self) -> List[Dict[str, str]]:
        """Build message list with system prompt and history.

        Returns:
            List of messages for API call
        """
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(self.conversation_history)
        return messages

    def _trim_context(self):
        """Keep only the most recent turns to stay within context limit."""
        if len(self.conversation_history) > Config.MAX_CONTEXT_TURNS * 2:
            # Keep system context + last N turns (each turn = user + assistant)
            self.conversation_history = self.conversation_history[
                -(Config.MAX_CONTEXT_TURNS * 2) :
            ]
            logger.debug(
                f"Trimmed context to last {Config.MAX_CONTEXT_TURNS} turns"
            )

    def respond(self, user_input: str) -> Optional[str]:
        """Generate a response to user input.

        Args:
            user_input: User's message/question

        Returns:
            Agent's response or None if failed
        """
        if not user_input or not user_input.strip():
            logger.warning("Empty user input")
            return None

        try:
            # Add user message to history
            self.conversation_history.append(
                {"role": "user", "content": user_input}
            )

            # Trim context if needed
            self._trim_context()

            # Build messages
            messages = self._build_messages()

            # Call Nvidia API
            logger.debug(f"Calling {self.model} with {len(messages)} messages")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=Config.MAX_RESPONSE_TOKENS,
                temperature=Config.RESPONSE_TEMPERATURE,
            )

            # Extract response
            assistant_message = response.choices[0].message.content

            # Add to history
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

            logger.info(
                f"Agent response: '{assistant_message[:100]}...' "
                f"({response.usage.completion_tokens} tokens)"
            )
            return assistant_message

        except Exception as e:
            logger.error(f"Failed to get response: {e}")
            return None

    def reset_conversation(self):
        """Clear conversation history."""
        self.conversation_history = []
        logger.info("Conversation history cleared")

    def get_conversation_history(
        self, format_string: bool = True
    ) -> str | List[Dict[str, str]]:
        """Get conversation history.

        Args:
            format_string: If True, return formatted string; else return list

        Returns:
            Conversation history as string or list
        """
        if not format_string:
            return self.conversation_history

        # Format as string
        history = []
        for msg in self.conversation_history:
            role = msg["role"].upper()
            content = msg["content"]
            history.append(f"{role}: {content}")

        return "\n\n".join(history)

    def get_turn_count(self) -> int:
        """Get number of conversation turns."""
        # Each turn = 1 user message + 1 assistant response = 2 messages
        return len(self.conversation_history) // 2


class AgentFactory:
    """Factory for creating agent instances."""

    _instance: Optional[ConversationAgent] = None

    @classmethod
    def get_agent(cls) -> Optional[ConversationAgent]:
        """Get or create singleton agent instance.

        Returns:
            ConversationAgent instance or None if initialization fails
        """
        if cls._instance is None:
            try:
                cls._instance = ConversationAgent()
            except Exception as e:
                logger.error(f"Failed to create agent: {e}")
                return None
        return cls._instance

    @classmethod
    def reset(cls):
        """Reset the singleton instance."""
        if cls._instance:
            cls._instance.reset_conversation()


if __name__ == "__main__":
    # Test the agent
    import sys

    agent = ConversationAgent()

    print("Voice Agent Test")
    print("=" * 50)
    print("Type 'quit' to exit\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("quit", "exit", "bye"):
            print("Agent: Goodbye!")
            break

        if not user_input:
            continue

        response = agent.respond(user_input)
        if response:
            print(f"Agent: {response}\n")
        else:
            print("Agent: (failed to generate response)\n")

    print("\n" + "=" * 50)
    print("Conversation History:")
    print(agent.get_conversation_history(format_string=True))
