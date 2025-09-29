from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil

from app.model import train_model_from_file, predict_price
from app.schemas import PredictRequest, PredictResponse, TrainResponse

app = FastAPI(title="Lesson Price API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

@app.post("/train/fromfile", response_model=TrainResponse)
def train_from_default_csv():
    try:
        result = train_model_from_file("data/music_students_data.csv")
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

@app.post("/train/upload", response_model=TrainResponse)
def train_from_uploaded_csv(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".csv"):
        raise HTTPException(status_code=400, detail="Please upload a .csv file")

    data_dir = Path(__file__).resolve().parents[1] / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    tmp_path = data_dir / "uploaded.csv"

    try:
        with tmp_path.open("wb") as f:
            shutil.copyfileobj(file.file, f)

        rel_path = str(tmp_path.relative_to(Path(__file__).resolve().parents[1]))
        result = train_model_from_file(rel_path)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

@app.post("/predict", response_model=PredictResponse)
def predict(data: PredictRequest):
    try:
        yhat = predict_price(
            age=data.age,
            subject_instrument=data.subject_instrument,
            city=data.city,
            month=data.month
        )
        return PredictResponse(predicted_price=yhat)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Model not trained yet. Train first.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
