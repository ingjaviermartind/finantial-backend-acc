import joblib
from pathlib import Path

import numpy as np
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH_NW = BASE_DIR / "ml_models" / "rf_vlr_mbps_v4.pkl"


package_nw = joblib.load(MODEL_PATH_NW)

model_nw = package_nw["model"]
model_nw.set_params(n_jobs=1)
features = package_nw["features"]
encoded_features = package_nw["encoded_features"]

def predict_vlr_mbps_nw(capacity : float, municipality, contract_time : float, tipo_producto : str, producto : str, subsegment : str) -> float:
    values = {
        "LOG_CAP": np.log10(capacity),
        "Longitud": municipality.longitude,
        "Latitud": municipality.latitude,
        "CONTRACT_TIME": contract_time,
        "TIPO_PRODUCTO": tipo_producto,
        "PRODUCTO" : producto.upper(),
        "subsegment": subsegment
    }
    X = pd.DataFrame([values])
    X = pd.get_dummies(
        X,
        columns=[
            "TIPO_PRODUCTO",
            "PRODUCTO",
            "subsegment"
        ],
        dtype=int
    )
    X = X.reindex(
        columns=encoded_features,
        fill_value=0
    )

    print("\n========== PREDICCIÓN ==========")
    print("Producto:", producto)
    print("Tipo:", tipo_producto)
    print("Subsegment:", subsegment)
    print("\nDummies:")
    print(X.filter(regex="TIPO_PRODUCTO|PRODUCTO_|subsegment_").T)

    log_vlr = model_nw.predict(X)[0]

    print("\nLOG_VLR:", log_vlr)
    print("VLR:", 10 ** log_vlr)
    print("================================")

    return float(10 ** log_vlr)


def get_model_info() -> dict:
    return {
        "algorithm": package_nw["algorithm"],
        "version": package_nw["version"],
        "features": package_nw["features"],
        "encoded_features": package_nw["encoded_features"],
        "target": package_nw["target"],
        "model_path": str(MODEL_PATH_NW.name)
    }