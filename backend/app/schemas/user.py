from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict


#shape of what comes in from user. has to be in this shape.
#FastAPI rejects before code runs if not in this shape
#guards door coming in(input from user)
class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


#for security, nothing about pwd is noted here. no slot at all. good protection for password leak
#guards door going out
class UserRead (BaseModel):
    user_id: int
    username: str
    email: EmailStr
    role: str
    experience_level: str | None = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str

    #whoever has this token, grant access
    token_type: str = "bearer"


class UserLogin(BaseModel):
    email: EmailStr
    password: str