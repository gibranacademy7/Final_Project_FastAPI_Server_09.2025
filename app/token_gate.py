from fastapi import HTTPException, Depends
from sqlmodel import Session, select
from app.db import User, get_session
from app.security import verify_password

def require_tokens(cost: int):
    """
    Dependency:
      - reads username/password from query params
      - verifies credentials
      - checks >= cost tokens
      - deducts tokens
    """
    def dep(username: str, password: str, session: Session = Depends(get_session)):
        u = session.exec(select(User).where(User.username == username)).first()
        if not u or not verify_password(password, u.password_hash):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        if u.tokens < cost:
            raise HTTPException(status_code=402, detail="Not enough tokens")

        u.tokens -= cost
        session.add(u)
        session.commit()
        return u.username
    return dep
