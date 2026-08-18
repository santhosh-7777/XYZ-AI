from pathlib import Path

import joblib
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.linear_model import LogisticRegression


ROOT = Path(__file__).resolve().parents[3]

DATA_PATH = ROOT / "Data" / "intent_ml_train.csv"
MODEL_DIR = ROOT / "ML" / "models" / "intent"
MODEL_PATH = MODEL_DIR / "intent_embeddings_classifier.joblib"


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    texts = df["text"].astype(str).tolist()
    labels = df["intent"].astype(str)

    print("Loading multilingual embedding model...")

    encoder = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    )

    print("Encoding training data...")

    embeddings = encoder.encode(
        texts,
        show_progress_bar=True,
        normalize_embeddings=True,
    )

    classifier = LogisticRegression(
        max_iter=2000,
        class_weight="balanced",
    )

    classifier.fit(embeddings, labels)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    joblib.dump(classifier, MODEL_PATH)

    print(f"Training rows: {len(df)}")
    print(f"Intent classes: {labels.nunique()}")
    print(f"Embedding dimensions: {embeddings.shape[1]}")
    print(f"Classifier saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()