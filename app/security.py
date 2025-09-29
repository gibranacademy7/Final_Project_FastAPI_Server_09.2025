from passlib.context import CryptContext

_pwd = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(p: str) -> str:
    # bcrypt supports up to 72 bytes; schemas enforce this already
    return _pwd.hash(p)

def verify_password(p: str, h: str) -> bool:
    return _pwd.verify(p, h)

# (Optional JWT helpers if you later add JWT)
# import time, jwt
# JWT_SECRET = "change_me_in_env"
# JWT_ALGO = "HS256"
# JWT_TTL_SECONDS = 3600
# def create_jwt(username: str) -> str:
#     payload = {"sub": username, "exp": int(time.time()) + JWT_TTL_SECONDS}
#     return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)
# def verify_jwt(token: str) -> str:
#     data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
#     return data["sub"]
