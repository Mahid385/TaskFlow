from fastapi import APIRouter,HTTPException,Depends
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel, EmailStr, field_validator
from uuid import uuid4
import jwt
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError
from sqlalchemy.orm import Session
from database import get_db
from models import User

oauth2_scheme=OAuth2PasswordBearer(
    tokenUrl="/auth/login"
)
pass_hash=PasswordHasher()
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 8:
            raise ValueError("Password must be at least 8 characters")
        return value



class RequestRefreshToken(BaseModel):
    refresh_token:str

router=APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


def get_current_user(token:str=Depends(oauth2_scheme),db:Session=Depends(get_db)):
    try:
        payload=jwt.decode_access_token(token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    if payload.get("type")!="access":
        raise HTTPException(
            status_code=401,
            detail="Invalid access token"
        )
    user_id=payload.get("sub")
    user=(
        db.query(User)
        .filter(User.id==str(user_id))
        .first()
    )
    if user:
        return user
    raise HTTPException(
        status_code=401,
        detail="User not found"
    )

@router.post("/reg")
def registration(request:RegisterRequest,db:Session=Depends(get_db)):
    hash_pass=pass_hash.hash(request.password)
    exsisting_user=(
        db.query(User)
        .filter(User.email==request.email)
        .first()
    )
    if exsisting_user:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )
    user_id=uuid4()
    user=User(
        id=str(user_id),
        email=request.email,
        password=hash_pass
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {
        "user_id":str(user_id),
        "user_email":request.email
    }
@router.post("/login")
def login(formdata:OAuth2PasswordRequestForm=Depends(),db:Session=Depends(get_db)):
    email=formdata.username
    password=formdata.password
    user=(
        db.query(User)
        .filter(User.email==email)
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    try:
        pass_hash.verify(user.password,password)

    except VerifyMismatchError:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )
    access_token=jwt.create_access_token(user.id)
    refresh_token=jwt.create_refresh_token(user.id)
    return {
        "access_token": access_token,
        "refresh_token":refresh_token,
        "token_type": "bearer"
    }
    

@router.post("/refresh")
def refresh_token(request:RequestRefreshToken,db:Session=Depends(get_db)):

    try:
        payload=jwt.decode_access_token(request.refresh_token)
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired token"
        )
    if payload.get("type")!="refresh":
        raise HTTPException(
            status_code=401,
            detail="Invalid token type"
        )
    user=(
            db.query(User)
            .filter(User.id==payload.get("sub"))
            .first()
        )
    if user:
        access_token=jwt.create_access_token(payload["sub"])
        return  {
                    "access_token": access_token,
                    "token_type": "bearer"
                }
    else:
        raise HTTPException(
            status_code=401,
            detail="User not found"
        )