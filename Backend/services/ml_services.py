import joblib
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml_models" / "rf_vlr_mbps_v2.pkl"

package = joblib.load(MODEL_PATH)

model = package["model"]
features = package["features"]


def predict_vlr_mbps(capacity: float, municipality) -> float:

    values = {
        "LOG_CAP": np.log10(capacity),
        "Longitud": municipality.longitude,
        "Latitud": municipality.latitude
    }

    X = pd.DataFrame(
        [{f: values[f] for f in features}]
    )

    log_vlr = model.predict(X)[0]

    return float(10 ** log_vlr)

def get_model_info() -> dict:
    return {
        "algorithm": package["algorithm"],
        "version": package["version"],
        "features": package["features"],
        "target": package["target"],
        "model_path": str(MODEL_PATH.name)
    }