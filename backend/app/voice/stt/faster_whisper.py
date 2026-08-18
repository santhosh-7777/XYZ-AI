from faster_whisper import WhisperModel

from backend.app.voice.stt.base import STTProvider


class FasterWhisperSTTProvider(STTProvider):
    """
    Real offline speech-to-text provider using Faster Whisper.

    The model is loaded lazily on the first transcription request
    so application startup is not blocked.
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

    def transcribe(self, audio_path: str) -> str:
        model = self._get_model()

        segments, _ = model.transcribe(audio_path)

        text = "".join(segment.text for segment in segments)

        return text.strip()