"""Tests for speech service (STT/TTS)."""

import pytest
import sys
from pathlib import Path

# Add code to path
sys.path.insert(0, str(Path(__file__).parent.parent / "code"))

from speech_service import SpeechService
from config import Config


class TestSpeechService:
    """Test NVIDIA Riva speech service."""

    @pytest.fixture
    def speech_service(self):
        """Create speech service instance."""
        service = SpeechService()
        yield service
        if service:
            service.close()

    def test_connection(self, speech_service):
        """Test connection to Riva service."""
        assert speech_service is not None
        assert speech_service.connected

    def test_health_check(self, speech_service):
        """Test Riva service health check."""
        assert speech_service.health_check()

    def test_synthesize_basic(self, speech_service):
        """Test basic text-to-speech."""
        text = "Hello, this is a test."
        audio = speech_service.synthesize(text)

        assert audio is not None
        assert len(audio) > 0
        assert isinstance(audio, bytes)

    def test_synthesize_empty(self, speech_service):
        """Test TTS with empty text."""
        audio = speech_service.synthesize("")
        assert audio is None

    def test_config_loaded(self):
        """Test configuration is properly loaded."""
        assert Config.AUDIO_SAMPLE_RATE == 16000
        assert Config.AUDIO_CHANNELS == 1
        assert Config.LANGUAGE_CODE == "en-US"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
