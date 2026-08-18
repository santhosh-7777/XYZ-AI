from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """
    Text-To-Speech provider interface.

    Any TTS engine must implement this contract.
    """

    @abstractmethod
    def synthesize(self, text: str) -> str:
        """
        Convert response text into audio.

        Returns generated audio path/url.
        """
        pass