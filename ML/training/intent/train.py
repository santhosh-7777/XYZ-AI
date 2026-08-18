from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


ROOT = Path(__file__).resolve().parents[3]
DATA_PATH = ROOT / "Data" / "intent_ml_train.csv"
MODEL_DIR = ROOT / "ML" / "models" / "intent"
MODEL_PATH = MODEL_DIR / "intent_classifier.joblib"


def main() -> None:
    df = pd.read_csv(DATA_PATH)

    X = df["text"].astype(str)
    y = df["intent"].astype(str)

    model = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    sublinear_tf=True,
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                ),
            ),
        ]
    )

    model.fit(X, y)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    print(f"Training rows: {len(df)}")
    print(f"Intent classes: {y.nunique()}")
    print(f"Model saved to: {MODEL_PATH}")


if __name__ == "__main__":
    main()