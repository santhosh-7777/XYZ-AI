from backend.app.voice.stt.base import STTProvider


class MockSTTProvider(STTProvider):
    """Temporary STT provider for development and testing."""

    def transcribe(self, audio_path: str) -> str:
        return "mock transcribed text"