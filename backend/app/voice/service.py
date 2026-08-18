from typing import Any, Callable

from backend.app.voice.stt.base import STTProvider
from backend.app.voice.tts.base import TTSProvider


class VoiceService:
    """
    Coordinates:

    Audio
        ↓
    STT + language detection
        ↓
    existing AI orchestration + persona
        ↓
    TTS in detected language
        ↓
    Audio
    """

    def __init__(
        self,
        stt_provider: STTProvider,
        tts_provider: TTSProvider,
    ) -> None:
        self.stt_provider = stt_provider
        self.tts_provider = tts_provider

    def process(
        self,
        audio_path: str,
        ai_handler: Callable[[str, str], dict[str, Any]],
    ) -> dict[str, Any]:
        # 1. Audio → text + detected language
        transcription = self.stt_provider.transcribe(audio_path)

        text = transcription["text"]
        language = transcription["language"]

        # 2. Text + language → existing AI orchestration
        ai_result = ai_handler(text, language)

        # 3. AI result → response text
        response_text = self._extract_response_text(ai_result)

        # 4. Response text → audio in the detected language
        audio_output = self.tts_provider.synthesize(
            response_text,
            language,
        )

        return {
            "text": text,
            "language": language,
            "ai_result": ai_result,
            "audio": audio_output,
        }

    @staticmethod
    def _extract_response_text(ai_result: dict[str, Any]) -> str:
        """
        Extract a human-readable message from the existing AI response.
        """

        result = ai_result.get("result")

        if isinstance(result, dict):
            message = result.get("message")

            if isinstance(message, str):
                return message

        message = ai_result.get("message")

        if isinstance(message, str):
            return message

        return str(ai_result)