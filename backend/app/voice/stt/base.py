from abc import ABC, abstractmethod


class STTProvider(ABC):
    """
    Speech-To-Text provider interface.

    Any STT engine (Whisper, Azure, Google, etc.)
    must implement this contract.
    """

    @abstractmethod
    def transcribe(self, audio_path: str) -> str:
        """
        Convert audio into normalized text.
        """
        pass