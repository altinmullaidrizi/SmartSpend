import os
from typing import Optional

import joblib

_model = None


def load_model(path: str = "models/categorizer.pkl") -> bool:
    """Load the trained pipeline. Returns False if the file is missing."""
    global _model
    if not os.path.exists(path):
        return False
    _model = joblib.load(path)
    return True


def is_loaded() -> bool:
    return _model is not None


def predict_category(description: str) -> Optional[str]:
    """Predict a category from the transaction description."""
    if _model is None:
        return None
    return _model.predict([description])[0]
