import os
import uuid
from typing import Any

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from backend.app.api.ai import act_on_message
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.ai import UnderstandRequest
from backend.app.security.deps import get_current_user
from backend.app.voice.service import VoiceService
from backend.app.voice.stt.faster_whisper import FasterWhisperSTTProvider
from backend.app.voice.tts.provider import WindowsTTSProvider


router = APIRouter(prefix="/voice", tags=["Voice"])


# Providers
stt_provider = FasterWhisperSTTProvider()
tts_provider = WindowsTTSProvider()


voice_service = VoiceService(
    stt_provider=stt_provider,
    tts_provider=tts_provider,
)


@router.post("/process")
async def process_voice(
    audio: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Voice pipeline:

    Audio
      ↓
    STT
      ↓
    Existing AI orchestration
      ↓
    TTS
    """

    # Save uploaded audio temporarily
    temp_dir = "temp_audio"

    os.makedirs(temp_dir, exist_ok=True)

    audio_path = os.path.join(
        temp_dir,
        f"{uuid.uuid4()}_{audio.filename}",
    )

    with open(audio_path, "wb") as f:
        f.write(await audio.read())


    def ai_handler(text: str) -> dict[str, Any]:
        """
        Reuse existing /ai/act logic.
        """

        request = UnderstandRequest(
            text=text
        )

        response = act_on_message(
            data=request,
            user=user,
            db=db,
        )

        return response.model_dump()


    result = voice_service.process(
        audio_path=audio_path,
        ai_handler=ai_handler,
    )


    # Optional cleanup after processing
    try:
        os.remove(audio_path)
    except Exception:
        pass


    return result