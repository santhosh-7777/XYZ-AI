import os
import uuid
from pathlib import Path
from typing import Any

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from backend.app.api.ai import act_on_message
from backend.app.db.session import get_db
from backend.app.models.user import User
from backend.app.schemas.ai import UnderstandRequest
from backend.app.security.deps import get_current_user
from backend.app.voice.service import VoiceService
from backend.app.voice.stt.faster_whisper import (
    FasterWhisperSTTProvider,
)
from backend.app.voice.tts.provider import (
    WindowsTTSProvider,
)


router = APIRouter(
    prefix="/voice",
    tags=["Voice"],
)


# =========================================================
# DIRECTORIES
# =========================================================

TEMP_AUDIO_DIR = "temp_audio"
GENERATED_AUDIO_DIR = "generated_audio"


os.makedirs(
    TEMP_AUDIO_DIR,
    exist_ok=True,
)

os.makedirs(
    GENERATED_AUDIO_DIR,
    exist_ok=True,
)


# =========================================================
# VOICE PROVIDERS
# =========================================================

stt_provider = FasterWhisperSTTProvider()

tts_provider = WindowsTTSProvider()

voice_service = VoiceService(
    stt_provider=stt_provider,
    tts_provider=tts_provider,
)


# =========================================================
# /voice/process
# =========================================================

@router.post("/process")
def process_voice(
    audio: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """
    Voice pipeline:

        Browser microphone
              ↓
        Uploaded audio
              ↓
        Faster Whisper
              ↓
        Text + detected language
              ↓
        Existing AI orchestration
              ↓
        RBAC / Tools / Persona
              ↓
        Edge TTS
              ↓
        MP3 audio file
              ↓
        Browser
              ↓
        Avatar speaks
    """

    # =====================================================
    # SAVE UPLOADED AUDIO TEMPORARILY
    # =====================================================

    filename = audio.filename or "voice.webm"

    audio_path = os.path.join(
        TEMP_AUDIO_DIR,
        f"{uuid.uuid4()}_{filename}",
    )

    with open(audio_path, "wb") as f:
        f.write(audio.file.read())

    # =====================================================
    # AI HANDLER
    # =====================================================

    def ai_handler(
        text: str,
        language: str,
    ) -> dict[str, Any]:
        """
        Reuse the existing AI orchestration.

        The authenticated JWT/user role remains
        authoritative.

        Voice input cannot change the user's role.
        """

        request = UnderstandRequest(
            text=text,
            language=language,
        )

        try:
            response = act_on_message(
                data=request,
                user=user,
                db=db,
                is_voice=True,
            )

            return response.model_dump()

        except HTTPException as exc:

            # =================================================
            # RBAC DENIAL
            # =================================================

            if exc.status_code == 403:
                return {
                    "result": {
                        "message": str(exc.detail),
                    },
                    "status": "FORBIDDEN",
                }

            raise

    # =====================================================
    # RUN VOICE PIPELINE
    # =====================================================

    try:

        result = voice_service.process(
            audio_path=audio_path,
            ai_handler=ai_handler,
        )

        # =================================================
        # CONVERT AUDIO PATH → BROWSER URL
        # =================================================

        audio_path_result = result.get("audio")

        if audio_path_result:

            audio_filename = Path(
                audio_path_result
            ).name

            result["audio_url"] = (
                f"/voice/audio/{audio_filename}"
            )

        return result

    finally:

        # =================================================
        # CLEANUP TEMPORARY INPUT AUDIO
        # =================================================

        try:
            os.remove(audio_path)
        except Exception:
            pass


# =========================================================
# /voice/audio/{filename}
# =========================================================

@router.get("/audio/{filename}")
def get_voice_audio(
    filename: str,
) -> FileResponse:
    """
    Serve generated TTS audio to the browser.
    """

    # =====================================================
    # SECURITY
    # =====================================================

    # Only allow the filename itself.
    #
    # This prevents paths such as:
    #
    # ../../some_file
    #
    # from being used.

    safe_filename = Path(
        filename
    ).name

    audio_path = (
        Path(GENERATED_AUDIO_DIR)
        / safe_filename
    )

    # =====================================================
    # FILE EXISTENCE
    # =====================================================

    if not audio_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Audio file not found.",
        )

    # =====================================================
    # RETURN MP3
    # =====================================================

    return FileResponse(
        path=str(audio_path),
        media_type="audio/mpeg",
        filename=safe_filename,
    )