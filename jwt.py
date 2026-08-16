from jose import jwt
from datetime import datetime,timedelta,timezone

SECRET_KEY = "change-this-in-production"
ALGORITHM = "HS256"


def create_access_token(user_id:str,expire_min:int=15):
    expire=datetime.now(timezone.utc)+timedelta(minutes=expire_min)
    payload={
        "sub":user_id,
        "exp":expire,
        "type":"access"
    }
    token=jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )
    return token
def verify_access_token(token:str):
    payload=jwt.decode(
        token,
        SECRET_KEY,
        algorithms=ALGORITHM
    )
    return payload

def create_refresh_token(user_id:str,expire_days:int=7):
    expire=datetime.now(timezone.utc)+timedelta(days=expire_days)
    payload={
        "sub":user_id,
        "exp":expire,
        "type":"refresh"
    }
    token=jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token