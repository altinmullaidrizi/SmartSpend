from __future__ import annotations

import os
from typing import Optional

import joblib

# Module-level singleton holding the loaded pipeline. None until a model is
# successfully loaded (or injected in tests).
_model = None


def load_model(path: str = "models/categorizer.pkl") -> bool:
    """Load the trained categorizer pipeline into the module-level `_model`.

    Returns True on success, False if the file is missing. Does not raise on a
    missing file so the app can start without a trained model present.
    """
    global _model
    if not os.path.exists(path):
        return False
    _model = joblib.load(path)
    return True


def is_loaded() -> bool:
    """Return True if a model is currently loaded/injected."""
    return _model is not None


def predict_category(description: str) -> Optional[str]:
    """Predict a category for a transaction description.

    Returns None if no model is loaded, otherwise the predicted label.
    """
    if _model is None:
        return None
    return _model.predict([description])[0]
