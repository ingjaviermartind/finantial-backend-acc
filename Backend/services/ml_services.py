import joblib
from pathlib import Path
import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "ml_models" / "rf_vlr_mbps.pkl"
model = joblib.load(MODEL_PATH)

def predict_vlr_mbps(capacity : float) -> float:
    X = pd.DataFrame({
        "LOG_CAP": [np.log10(capacity)]
    })
    log_vlr = model.predict(X)[0]
    vlr_mbps = float(np.power(10, log_vlr))
    return vlr_mbps
