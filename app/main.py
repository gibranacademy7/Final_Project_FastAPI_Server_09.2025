from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import shutil
import logging

from sqlmodel import Session, select

from app.model import train_model_from_file, predict_price
from app.schemas import (
    PredictRequest, PredictResponse, TrainResponse,
    SignupRequest, RemoveUserRequest, AddTokensRequest, TokensResponse
)
from app.db import init_db, get_session, User
from app.security import hash_password, verify_password
from app.token_gate import require_tokens

app = FastAPI(title="Lesson Price API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

LOG_PATH = Path(__file__).resolve().parents[1] / "server.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()]
)
app.logger = logging.getLogger("server")

@app.on_event("startup")
def on_startup():
    init_db()
    app.logger.info("DB initialized and server started")

@app.get("/")
def root():
    return {"message": "FastAPI is running!"}

# ---------- Users & Tokens ----------
@app.post("/signup")
def signup(body: SignupRequest, session: Session = Depends(get_session)):
    exists = session.exec(select(User).where(User.username == body.username)).first()
    if exists:
        raise HTTPException(status_code=400, detail="Username already exists")
    u = User(username=body.username, password_hash=hash_password(body.password), tokens=0)
    session.add(u)
    session.commit()
    app.logger.info(f"User {body.username} registered")
    return {"ok": True}

@app.delete("/remove_user")
def remove_user(body: RemoveUserRequest, session: Session = Depends(get_session)):
    u = session.exec(select(User).where(User.username == body.username)).first()
    if not u or not verify_password(body.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    session.delete(u)
    session.commit()
    app.logger.info(f"User {body.username} removed")
    return {"ok": True}

@app.get("/tokens/{username}", response_model=TokensResponse)
def tokens(username: str, session: Session = Depends(get_session)):
    u = session.exec(select(User).where(User.username == username)).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    return TokensResponse(tokens=u.tokens)

@app.post("/add_tokens")
def add_tokens(body: AddTokensRequest, session: Session = Depends(get_session)):
    u = session.exec(select(User).where(User.username == body.username)).first()
    if not u:
        raise HTTPException(status_code=404, detail="User not found")
    u.tokens += body.amount
    session.add(u)
    session.commit()
    app.logger.info(f"User {body.username} purchased {body.amount} tokens")
    return {"tokens": u.tokens}

# ---------- ML: Train & Predict (TOKEN-PROTECTED) ----------
# Train from default CSV (cost 1 token)
@app.post("/train/fromfile", response_model=TrainResponse)
def train_from_default_csv(
    username: str,
    password: str,
    _=Depends(require_tokens(cost=1))
):
    try:
        result = train_model_from_file("data/music_students_data.csv")
        app.logger.info(f"Train by {username} on default file: mse={result['mse']}, r2={result['r2']}")
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        app.logger.exception("Training failed")
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

# Train from uploaded CSV (cost 1 token)
@app.post("/train/upload", response_model=TrainResponse)
def train_from_uploaded_csv(
    file: UploadFile = File(...),
    username: str = "",
    password: str = "",
    _=Depends(require_tokens(cost=1))
):
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
        app.logger.info(f"Train by {username} on uploaded file: mse={result['mse']}, r2={result['r2']}")
        return result
    except Exception as e:
        app.logger.exception("Training failed")
        raise HTTPException(status_code=500, detail=f"Training failed: {e}")

# Predict price (cost 5 tokens)
@app.post("/predict", response_model=PredictResponse)
def predict(
    data: PredictRequest,
    username: str,
    password: str,
    _=Depends(require_tokens(cost=5))
):
    try:
        yhat = predict_price(
            age=data.age,
            subject_instrument=data.subject_instrument,
            city=data.city,
            month=data.month
        )
        app.logger.info(f"Predict by {username}: {data.dict()} -> {yhat}")
        return PredictResponse(predicted_price=yhat)
    except FileNotFoundError:
        raise HTTPException(status_code=400, detail="Model not trained yet. Train first.")
    except Exception as e:
        app.logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {e}")
