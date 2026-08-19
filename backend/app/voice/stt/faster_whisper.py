from __future__ import annotations

from faster_whisper import WhisperModel

from backend.app.voice.stt.base import STTProvider


class FasterWhisperSTTProvider(STTProvider):
    """
    High-accuracy multilingual speech-to-text provider.

    Uses Faster-Whisper large-v3 for:
        audio -> transcription + automatic language detection

    The provider interface remains unchanged so the rest of the
    XYZ-AI voice pipeline does not need to change.
    """

    def __init__(self) -> None:
        self.model: WhisperModel | None = None

    def _get_model(self) -> WhisperModel:
        if self.model is None:
            self.model = WhisperModel(
                "tiny",
                device="cpu",
                compute_type="int8",
            )

        return self.model

    def transcribe(self, audio_path: str) -> dict[str, str]:
        """
        Convert audio to text and automatically detect language.

        Returns:
            {
                "text": "...",
                "language": "te"
            }
        """

        model = self._get_model()

        segments, info = model.transcribe(
            audio_path,
            beam_size=5,
            vad_filter=True,
            condition_on_previous_text=True,
        )

        text = " ".join(
            segment.text.strip()
            for segment in segments
            if segment.text.strip()
        ).strip()

        language = info.language

        return {
            "text": text,
            "language": language,
        }