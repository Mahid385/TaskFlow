from jose import jwt
from datetime import datetime, timedelta, timezone
from config import settings


SECRET_KEY = settings.secret_key
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is not set")


ALGORITHM = "HS256"


def create_access_token(user_id, expire_min=15):
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expire_min
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access"
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token


def decode_access_token(token):
    payload = jwt.decode(
        token,
        SECRET_KEY,
        algorithms=[ALGORITHM]
    )

    return payload


def create_refresh_token(user_id, expire_days=7):
    expire = datetime.now(timezone.utc) + timedelta(
        days=expire_days
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh"
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token