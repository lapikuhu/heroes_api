from passlib.context import CryptContext
from jose import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from fastapi.security import OAuth2PasswordBearer

# Setup password hashing context using passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 scheme for token-based authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def hash_password(raw: str) -> str:
    return pwd_context.hash(raw)
 
def verify_password(raw: str, hashed: str) -> bool:
    return pwd_context.verify(raw, hashed)
 
def create_access_token(sub: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return jwt.encode({"sub": sub, "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str) -> dict:
    return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

def  get_password_hash(password: str) -> str:
    return hash_password(password)
