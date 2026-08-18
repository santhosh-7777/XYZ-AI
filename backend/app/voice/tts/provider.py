import pyttsx3

from backend.app.voice.tts.base import TTSProvider


class WindowsTTSProvider(TTSProvider):
    """
    Local Windows Text-To-Speech provider.
    """

    def synthesize(self, text: str) -> str:
        engine = pyttsx3.init()

        engine.say(text)
        engine.runAndWait()

        return "speech_completed"