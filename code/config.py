"""Configuration management for voice agent."""

import os
import logging
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration."""

    # Paths
    PROJECT_ROOT = Path(__file__).parent.parent
    SRC_DIR = Path(__file__).parent
    TESTS_DIR = PROJECT_ROOT / "tests"
    NOTEBOOKS_DIR = PROJECT_ROOT / "notebooks"

    # Nvidia API Configuration
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_BASE_URL: str = "https://integrate.api.nvidia.com/v1"
    MODEL_NAME: str = os.getenv(
        "MODEL_NAME", "qwen/qwen3-coder-480b-a35b-instruct"
    )

    # Riva Configuration
    RIVA_URI: str = os.getenv("RIVA_URI", "localhost:50051")
    RIVA_HTTP_URI: str = os.getenv("RIVA_HTTP_URI", "http://localhost:9000")

    # Audio Configuration
    AUDIO_SAMPLE_RATE: int = 16000  # Riva requires 16kHz
    AUDIO_CHANNELS: int = 1  # Mono
    AUDIO_FRAME_LENGTH: int = 32000  # 2 seconds at 16kHz
    AUDIO_FORMAT: str = "PCM"  # Linear PCM
    AUDIO_DEVICE_INDEX: int = int(os.getenv("AUDIO_DEVICE_INDEX", "0"))

    # Conversation Configuration
    MAX_CONTEXT_TURNS: int = 10  # Keep last N turns
    CONVERSATION_TIMEOUT: int = 30  # Seconds
    RESPONSE_TEMPERATURE: float = 0.7
    MAX_RESPONSE_TOKENS: int = 1024

    # Logging Configuration
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = (
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

    # Voice Configuration
    VOICE_NAME: str = os.getenv("VOICE_NAME", "en-US-Neural2-C")
    LANGUAGE_CODE: str = "en-US"

    # System prompt for conversational behavior
    SYSTEM_PROMPT: str = """You are a helpful and friendly voice assistant powered by NVIDIA.
You communicate clearly and concisely in spoken conversation.
Keep responses brief (1-3 sentences) for comfortable voice interaction.
Be helpful, harmless, and honest."""

    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        errors = []

        if not cls.NVIDIA_API_KEY:
            errors.append("NVIDIA_API_KEY environment variable not set")

        if not cls.MODEL_NAME:
            errors.append("MODEL_NAME environment variable not set")

        if errors:
            logging.error("Configuration validation failed:")
            for error in errors:
                logging.error(f"  - {error}")
            return False

        return True

    @classmethod
    def get_logger(cls, name: str) -> logging.Logger:
        """Get configured logger."""
        logger = logging.getLogger(name)
        logger.setLevel(cls.LOG_LEVEL)

        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(cls.LOG_FORMAT)
            handler.setFormatter(formatter)
            logger.addHandler(handler)

        return logger


# Global logger
logger = Config.get_logger(__name__)

if __name__ == "__main__":
    print("Configuration loaded successfully!")
    print(f"NVIDIA API Base URL: {Config.NVIDIA_BASE_URL}")
    print(f"Model: {Config.MODEL_NAME}")
    print(f"Riva URI: {Config.RIVA_URI}")
    print(f"Audio Sample Rate: {Config.AUDIO_SAMPLE_RATE} Hz")
    print(f"Log Level: {Config.LOG_LEVEL}")
