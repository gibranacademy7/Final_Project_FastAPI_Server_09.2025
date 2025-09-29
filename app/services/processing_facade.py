from pathlib import Path
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score

from .model_factory import make_model, ModelName
from .preprocess_strategy import basic_preprocessor

BASE_DIR = Path(__file__).resolve().parents[2]
MODEL_PATH = BASE_DIR / "saved_models" / "model.joblib"

DEFAULT_TARGET = "Price"
DEFAULT_CAT = ["Subject/Instrument", "City", "Month"]
DEFAULT_NUM = ["Age"]

def _ensure_required_columns(df: pd.DataFrame, cols: list[str]):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"CSV is missing required columns: {missing}. "
            f"Expected at least {cols}."
        )

def train_from_csv(
    csv_path: Path,
    model_name: ModelName = "linear",
    target: str = DEFAULT_TARGET,
    cat_cols = DEFAULT_CAT,
    num_cols = DEFAULT_NUM,
):
    df = pd.read_csv(csv_path)

    required = [*cat_cols, *num_cols, target]
    _ensure_required_columns(df, required)

    # تحويل الأنواع ثم إسقاط القيم المفقودة في الأعمدة المهمة
    if "Age" in df.columns:
        df["Age"] = pd.to_numeric(df["Age"], errors="coerce")

    df = df.dropna(subset=required)

    X = df[cat_cols + num_cols]
    y = df[target]

    pre = basic_preprocessor(cat_cols, num_cols)
    model = make_model(model_name)   # "linear" أو "random_forest"
    pipe = Pipeline([("pre", pre), ("model", model)])

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=0
    )
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_test)

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)

    return {
        "mse": float(mean_squared_error(y_test, y_pred)),
        "r2": float(r2_score(y_test, y_pred)),
    }

def predict_one(age: float, subject_instrument: str, city: str, month):
    pipe = joblib.load(MODEL_PATH)

    row = pd.DataFrame([{
        "Age": age,
        "Subject/Instrument": subject_instrument,
        "City": city,
        "Month": month
    }])

    return float(pipe.predict(row)[0])
