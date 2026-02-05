"""Main conversation loop orchestrating speech and AI components."""

import os
import sys
import time
from pathlib import Path
from typing import Optional

try:
    import pyaudio
except ImportError:
    pyaudio = None

from .config import Config, logger
from .speech_service import SpeechService
from .agent import ConversationAgent


class VoiceConversation:
    """Orchestrates voice conversation between user and AI agent."""

    def __init__(self, use_microphone: bool = False):
        """Initialize voice conversation system.

        Args:
            use_microphone: Whether to use live microphone input
                           (requires pyaudio and system audio)
        """
        self.use_microphone = use_microphone and pyaudio is not None
        self.speech_service: Optional[SpeechService] = None
        self.agent: Optional[ConversationAgent] = None
        self.conversation_count = 0

        # Initialize components
        self._initialize()

    def _initialize(self):
        """Initialize speech service and AI agent."""
        logger.info("Initializing voice conversation system...")

        # Initialize speech service
        try:
            self.speech_service = SpeechService()
            if not self.speech_service.connected:
                logger.error("Failed to connect to Riva service")
                raise RuntimeError("Riva connection failed")
            logger.info("✓ Riva speech service initialized")
        except Exception as e:
            logger.error(f"Failed to initialize speech service: {e}")
            raise

        # Initialize AI agent
        try:
            self.agent = ConversationAgent()
            logger.info("✓ Conversational AI agent initialized")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise

        logger.info("✓ Voice conversation system ready")

    def process_audio_file(self, audio_file: str) -> bool:
        """Process audio from a file.

        Args:
            audio_file: Path to audio file

        Returns:
            True if successful, False otherwise
        """
        if not Path(audio_file).exists():
            logger.error(f"Audio file not found: {audio_file}")
            return False

        logger.info(f"Processing audio file: {audio_file}")

        # Transcribe
        transcript = self.speech_service.transcribe(audio_file)
        if not transcript:
            logger.error("Failed to transcribe audio")
            return False

        print(f"\nYou: {transcript}")

        # Get AI response
        response = self.agent.respond(transcript)
        if not response:
            logger.error("Failed to get AI response")
            return False

        print(f"Agent: {response}")

        # Synthesize response
        output_file = (
            Path(audio_file).parent / f"response_{time.time():.0f}.wav"
        )
        audio_bytes = self.speech_service.synthesize(
            response, str(output_file)
        )

        if audio_bytes:
            print(f"Response audio saved to: {output_file}")
        else:
            logger.warning("Failed to synthesize response audio")

        self.conversation_count += 1
        return True

    def process_text_input(self, text: str) -> bool:
        """Process text input (simulating speech).

        Args:
            text: User input text

        Returns:
            True if successful, False otherwise
        """
        print(f"\nYou: {text}")

        # Get AI response
        response = self.agent.respond(text)
        if not response:
            logger.error("Failed to get AI response")
            return False

        print(f"Agent: {response}")

        # Synthesize response
        output_file = f"response_{time.time():.0f}.wav"
        audio_bytes = self.speech_service.synthesize(response, output_file)

        if audio_bytes:
            print(f"Response audio saved to: {output_file}")

        self.conversation_count += 1
        return True

    def start_interactive(self):
        """Start interactive conversation loop."""
        print("\n" + "=" * 60)
        print("NVIDIA Voice Agent - Interactive Mode")
        print("=" * 60)
        print("Type your message to chat with the agent.")
        print("Commands: 'history' to see conversation, 'quit' to exit\n")

        try:
            while True:
                user_input = input("You: ").strip()

                if not user_input:
                    continue

                if user_input.lower() == "quit":
                    print("Agent: Goodbye!")
                    break

                if user_input.lower() == "history":
                    print("\n" + "=" * 60)
                    print("Conversation History:")
                    print("=" * 60)
                    history = self.agent.get_conversation_history(
                        format_string=True
                    )
                    print(history if history else "(empty)")
                    print("=" * 60 + "\n")
                    continue

                if user_input.lower() == "reset":
                    self.agent.reset_conversation()
                    print("Conversation cleared.\n")
                    continue

                # Process input
                print()
                self.process_text_input(user_input)
                print()

        except KeyboardInterrupt:
            print("\n\nInterrupted by user")
        except Exception as e:
            logger.error(f"Error during conversation: {e}")
        finally:
            self.close()

    def start_batch(self, audio_files: list):
        """Process multiple audio files in batch.

        Args:
            audio_files: List of audio file paths
        """
        print("\n" + "=" * 60)
        print(f"NVIDIA Voice Agent - Batch Processing ({len(audio_files)} files)")
        print("=" * 60 + "\n")

        successful = 0
        failed = 0

        for audio_file in audio_files:
            if self.process_audio_file(audio_file):
                successful += 1
            else:
                failed += 1

        print("\n" + "=" * 60)
        print(f"Results: {successful} successful, {failed} failed")
        print("=" * 60)

        self.close()

    def close(self):
        """Clean up resources."""
        if self.speech_service:
            self.speech_service.close()
        logger.info(
            f"Closed conversation (processed {self.conversation_count} turns)"
        )


def main():
    """Main entry point for command-line usage."""
    import argparse

    parser = argparse.ArgumentParser(
        description="NVIDIA Voice Agent - Interactive voice conversation with AI"
    )
    parser.add_argument(
        "--audio",
        type=str,
        nargs="+",
        help="Process audio files (batch mode)",
    )
    parser.add_argument(
        "--microphone",
        action="store_true",
        help="Use microphone input (requires PyAudio)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Verbose logging"
    )

    args = parser.parse_args()

    # Configure logging
    if args.verbose:
        os.environ["LOG_LEVEL"] = "DEBUG"

    try:
        conversation = VoiceConversation(use_microphone=args.microphone)

        if args.audio:
            # Batch mode
            conversation.start_batch(args.audio)
        else:
            # Interactive mode
            conversation.start_interactive()

    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
