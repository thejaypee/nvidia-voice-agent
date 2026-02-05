"""Speech-to-Text and Text-to-Speech service using NVIDIA Riva."""

import grpc
import riva.client
import numpy as np
import soundfile as sf
from pathlib import Path
from typing import Optional, Tuple
from .config import Config, logger


class SpeechService:
    """Interface to NVIDIA Riva ASR and TTS services."""

    def __init__(self, riva_uri: Optional[str] = None):
        """Initialize connection to Riva server.

        Args:
            riva_uri: Riva gRPC endpoint (default: localhost:50051)
        """
        self.riva_uri = riva_uri or Config.RIVA_URI
        self.connected = False
        self._connect()

    def _connect(self) -> bool:
        """Establish connection to Riva server."""
        try:
            self.channel = grpc.secure_channel(
                self.riva_uri,
                grpc.ssl_channel_credentials(),
            )
            self.asr_service = riva.client.ASRServiceStub(self.channel)
            self.tts_service = riva.client.SynthesizeServiceStub(
                self.channel
            )
            self.connected = True
            logger.info(f"Connected to Riva at {self.riva_uri}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Riva: {e}")
            self.connected = False
            return False

    def transcribe(self, audio_input: str | bytes) -> Optional[str]:
        """Convert speech to text.

        Args:
            audio_input: Path to audio file or audio bytes

        Returns:
            Transcribed text or None if failed
        """
        if not self.connected:
            logger.error("Not connected to Riva service")
            return None

        try:
            # Load audio data
            if isinstance(audio_input, str):
                if not Path(audio_input).exists():
                    logger.error(f"Audio file not found: {audio_input}")
                    return None
                audio_data, sr = sf.read(audio_input, dtype="int16")
                audio_bytes = audio_data.tobytes()
            else:
                audio_bytes = audio_input

            # Configure recognition
            config = riva.client.RecognitionConfig(
                encoding=riva.client.AudioEncoding.LINEAR_PCM,
                sample_rate_hz=Config.AUDIO_SAMPLE_RATE,
                language_code=Config.LANGUAGE_CODE,
                max_alternatives=1,
                enable_automatic_punctuation=True,
                profanity_filter=False,
            )

            # Create request
            request = riva.client.RecognizeRequest(
                config=config, audio=audio_bytes
            )

            # Call ASR service
            response = self.asr_service.Recognize(request)

            if response.results and response.results[0].alternatives:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                logger.info(
                    f"Transcribed: '{transcript}' (confidence: {confidence:.2%})"
                )
                return transcript

            logger.warning("No transcription result returned")
            return None

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

    def synthesize(
        self, text: str, output_file: Optional[str] = None
    ) -> Optional[bytes]:
        """Convert text to speech.

        Args:
            text: Text to synthesize
            output_file: Path to save audio file (optional)

        Returns:
            Audio bytes or None if failed
        """
        if not self.connected:
            logger.error("Not connected to Riva service")
            return None

        if not text or not text.strip():
            logger.error("Empty text provided for synthesis")
            return None

        try:
            # Create request
            request = riva.client.SynthesizeSpeechRequest(
                text=text,
                voice_name=Config.VOICE_NAME,
                language_code=Config.LANGUAGE_CODE,
                encoding=riva.client.AudioEncoding.LINEAR_PCM,
                sample_rate_hz=Config.AUDIO_SAMPLE_RATE,
            )

            # Call TTS service
            response = self.tts_service.Synthesize(request)

            # Convert to audio array
            audio_bytes = bytes(response.audio)

            # Save to file if requested
            if output_file:
                audio_array = np.frombuffer(audio_bytes, dtype=np.int16)
                sf.write(output_file, audio_array, Config.AUDIO_SAMPLE_RATE)
                logger.info(f"Audio saved to {output_file}")

            logger.info(f"Synthesized {len(text)} characters")
            return audio_bytes

        except Exception as e:
            logger.error(f"Synthesis failed: {e}")
            return None

    def health_check(self) -> bool:
        """Check if Riva service is healthy.

        Returns:
            True if service is responding, False otherwise
        """
        try:
            # Try to make a simple call
            request = riva.client.RecognizeRequest(
                config=riva.client.RecognitionConfig(
                    encoding=riva.client.AudioEncoding.LINEAR_PCM,
                    sample_rate_hz=Config.AUDIO_SAMPLE_RATE,
                ),
                audio=b"",
            )
            self.asr_service.Recognize(request)
            return True
        except grpc.RpcError as e:
            if e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                # Empty audio is expected to fail validation
                # This means the service is responding
                logger.info("Riva health check passed")
                return True
            logger.error(f"Health check failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return False

    def close(self):
        """Close connection to Riva server."""
        if self.channel:
            self.channel.close()
            logger.info("Closed connection to Riva")


def get_speech_service() -> Optional[SpeechService]:
    """Factory function to get SpeechService instance.

    Returns:
        SpeechService instance or None if connection fails
    """
    service = SpeechService()
    if not service.connected:
        return None
    return service


if __name__ == "__main__":
    # Test the speech service
    import sys

    service = get_speech_service()
    if not service:
        print("Failed to connect to Riva service")
        sys.exit(1)

    # Health check
    if service.health_check():
        print("✓ Riva service is healthy")
    else:
        print("✗ Riva service health check failed")

    # Test TTS
    text = "Hello, this is a test of the NVIDIA Riva text to speech system."
    print(f"\nTesting TTS: '{text}'")
    audio = service.synthesize(text, "test_output.wav")
    if audio:
        print("✓ TTS successful, audio saved to test_output.wav")
    else:
        print("✗ TTS failed")

    service.close()
