from pathlib import Path
from .services.processing_facade import train_from_csv, predict_one, BASE_DIR

def train_model_from_file(csv_rel_path: str = "data/music_students_data.csv"):
    csv_path = (BASE_DIR / csv_rel_path).resolve()
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found at: {csv_path}")
    return train_from_csv(csv_path)

def predict_price(age: float, subject_instrument: str, city: str, month):
    return predict_one(age, subject_instrument, city, month)
