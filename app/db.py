from pathlib import Path
from typing import Generator
from sqlmodel import SQLModel, Field, Session, create_engine

DB_PATH = (Path(__file__).resolve().parents[1] / "ml_server.db").as_posix()
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str
    tokens: int = 0

def init_db() -> None:
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
