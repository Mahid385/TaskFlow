from fastapi import FastAPI,HTTPException,Depends
import uvicorn
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from pydantic import BaseModel, EmailStr, field_validator
from uuid import uuid4
import jwt
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
from jose import JWTError
database=[]
tasks=[]
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

app=FastAPI()


def get_current_user(token:str=Depends(oauth2_scheme)):
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
    for user in database:
        if str(user.get("user_id"))==user_id:
            return user
    raise HTTPException(
        status_code=401,
        detail="User not found"
    )

@app.post("/auth/reg")
def registration(request:RegisterRequest):
    hash_pass=pass_hash.hash(request.password)
    for inst in database:
        if request.email==inst.get("user_email"):
            raise HTTPException(
                status_code=409,
                detail="Email already registered"
            )
    user_id=uuid4()
    database.append(
        {
            "user_id":user_id,
            "user_email":request.email,
            "password":hash_pass
        }
    )

    return {
        "user_id":user_id,
        "user_email":request.email
    }
@app.post("/auth/login")
def login(formdata:OAuth2PasswordRequestForm=Depends()):
    email=formdata.username
    password=formdata.password
    for inst in database:
        if email==inst.get("user_email"):
            try:
                pass_hash.verify(inst.get("password"),password)
                access_token=jwt.create_access_token(inst.get("user_id"))
                refresh_token=jwt.create_refresh_token(inst.get("user_id"))
                return {
                "access_token": access_token,
                "refresh_token":refresh_token,
                "token_type": "bearer"
                }
            except VerifyMismatchError:
                raise HTTPException(
                    status_code=401,
                    detail="Incorrect email or password"
                )
    else:
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password"
        )


@app.post("/auth/refresh")
def refresh_token(request:RequestRefreshToken):

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
    for user in database:
        if str(user.get("user_id"))==payload.get("sub"):
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
if __name__=="__main__":
    uvicorn.run("regitser:app",reload=True,port=8000,host="127.0.0.1")