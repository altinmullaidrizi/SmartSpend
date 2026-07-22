from __future__ import annotations

"""Offline training script for the SmartSpend transaction categorizer.

Run from the backend/ directory:

    python -m app.ml.train

Generates a labeled dataset with the Kosovo seed generator, trains a
TF-IDF + LogisticRegression pipeline, prints the test accuracy and a
classification report, and saves the fitted pipeline to models/categorizer.pkl.
"""

import os

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

from app.seed.generate import generate_transactions

MODEL_PATH = "models/categorizer.pkl"


def build_pipeline() -> Pipeline:
    """Build the TF-IDF + LogisticRegression pipeline.

    Character n-grams (char_wb) work well for short merchant strings because
    they capture sub-word patterns and are robust to the small suffix variants
    ("- card", "- online", "- POS") appended by the seed generator.
    """
    return Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    analyzer="char_wb",
                    ngram_range=(1, 4),
                ),
            ),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )


def main() -> float:
    # Generate a large labeled dataset in-process so training does not depend
    # on the DB or anyone hitting the API.
    txns = generate_transactions(n=3000, user_id=0, seed=42)
    X = [t.description for t in txns]
    y = [t.category for t in txns]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, stratify=y, random_state=42
    )

    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    print(classification_report(y_test, y_pred))
    print(f"TEST ACCURACY: {accuracy:.4f}")

    os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"Saved model to {MODEL_PATH}")

    return accuracy


if __name__ == "__main__":
    main()
