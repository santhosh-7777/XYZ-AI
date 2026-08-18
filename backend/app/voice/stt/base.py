from abc import ABC, abstractmethod


class STTProvider(ABC):
    """
    Speech-To-Text provider interface.

    Any STT engine (Whisper, Azure, Google, etc.)
    must implement this contract.

    The provider returns both:
    - transcribed text
    - detected language code
    """

    @abstractmethod
    def transcribe(self, audio_path: str) -> dict[str, str]:
        """
        Convert audio into normalized text and detect its language.

        Returns:
            {
                "text": "...",
                "language": "en"
            }

        Language uses standard short language codes such as:
        - en = English
        - hi = Hindi
        - ta = Tamil
        - te = Telugu
        - mr = Marathi
        - bn = Bengali
        - gu = Gujarati
        - pa = Punjabi
        - kn = Kannada
        - ml = Malayalam
        - ur = Urdu
        """
        pass