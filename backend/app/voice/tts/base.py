from abc import ABC, abstractmethod


class TTSProvider(ABC):
    """
    Text-To-Speech provider interface.

    Any TTS engine must implement this contract.

    The provider receives the response text and the target
    language so that multilingual TTS providers can generate
    speech in the correct language.
    """

    @abstractmethod
    def synthesize(self, text: str, language: str) -> str:
        """
        Convert response text into audio in the requested language.

        Args:
            text: Response text to synthesize.
            language: ISO language code, for example:
                en = English
                hi = Hindi
                ta = Tamil
                te = Telugu
                mr = Marathi
                bn = Bengali
                gu = Gujarati
                pa = Punjabi
                kn = Kannada
                ml = Malayalam
                ur = Urdu

        Returns:
            Generated audio path/url or provider status.
        """
        pass