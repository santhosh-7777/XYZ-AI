from typing import Any, Callable

from backend.app.voice.stt.base import STTProvider
from backend.app.voice.tts.base import TTSProvider


class VoiceService:
    """
    Coordinates:

    Audio → STT → existing AI orchestration → TTS → Audio
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
        ai_handler: Callable[[str], dict[str, Any]],
    ) -> dict[str, Any]:
        # 1. Audio → text
        text = self.stt_provider.transcribe(audio_path)

        # 2. Text → existing AI orchestration
        ai_result = ai_handler(text)

        # 3. AI result → response text
        response_text = self._extract_response_text(ai_result)

        # 4. Response text → audio
        audio_output = self.tts_provider.synthesize(response_text)

        return {
            "text": text,
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