from __future__ import annotations

from datetime import date
from pathlib import Path
from typing import Any

import joblib
from sentence_transformers import SentenceTransformer

from ML.training.entities.extractor import extract_entities

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "ML" / "models" / "intent" / "intent_embeddings_classifier.joblib"

_encoder: SentenceTransformer | None = None
_classifier = None


def _load() -> None:
    global _encoder, _classifier
    if _encoder is None:
        _encoder = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
    if _classifier is None:
        _classifier = joblib.load(MODEL_PATH)


def understand(text: str, reference_date: date | None = None) -> dict[str, Any]:
    _load()

    embedding = _encoder.encode([text], normalize_embeddings=True)
    intent = _classifier.predict(embedding)[0]
    confidence = float(_classifier.predict_proba(embedding).max())

    entities = extract_entities(text, reference_date=reference_date)

    return {
        "intent": intent,
        "confidence": round(confidence, 4),
        "entities": entities,
    }