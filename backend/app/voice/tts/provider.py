import asyncio
import os
import uuid

import edge_tts

from backend.app.voice.tts.base import TTSProvider


class WindowsTTSProvider(TTSProvider):
    """
    Edge TTS provider for multilingual speech.

    Converts AI response text into an MP3 audio file
    that can later be returned to the browser.

    The provider selects an Indian voice based on the
    detected language.
    """

    VOICES = {
        "en": "en-IN-NeerjaNeural",
        "hi": "hi-IN-SwaraNeural",
        "bn": "bn-IN-TanishaaNeural",
        "gu": "gu-IN-DhwaniNeural",
        "kn": "kn-IN-SapnaNeural",
        "ml": "ml-IN-SobhanaNeural",
        "mr": "mr-IN-AarohiNeural",
        "ta": "ta-IN-PallaviNeural",
        "te": "te-IN-ShrutiNeural",
        "ur": "ur-IN-GulNeural",
    }

    DEFAULT_VOICE = "en-IN-NeerjaNeural"

    def synthesize(
        self,
        text: str,
        language: str,
    ) -> str:
        """
        Convert text into an MP3 file.

        Parameters
        ----------
        text:
            AI response text.

        language:
            Language detected by STT, for example:
            en, hi, ta, te, etc.

        Returns
        -------
        str:
            Path to the generated MP3 file.
        """

        # Normalize language.
        language = language.lower().strip()

        # Select appropriate Indian voice.
        voice = self.VOICES.get(
            language,
            self.DEFAULT_VOICE,
        )

        # Create audio directory.
        audio_dir = "generated_audio"

        os.makedirs(
            audio_dir,
            exist_ok=True,
        )

        # Generate unique filename.
        filename = (
            f"{uuid.uuid4()}.mp3"
        )

        audio_path = os.path.join(
            audio_dir,
            filename,
        )

        # Edge TTS is asynchronous.
        asyncio.run(
            self._generate_audio(
                text=text,
                voice=voice,
                output_path=audio_path,
            )
        )

        return audio_path

    @staticmethod
    async def _generate_audio(
        text: str,
        voice: str,
        output_path: str,
    ) -> None:
        """
        Generate speech using Edge TTS.
        """

        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
        )

        await communicate.save(
            output_path
        )