from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead
from app.core.security import hash_password


#auth endpoints get their own router that is grouped under /auth 
#full path is POST/auth/register
router = APIRouter(prefix="/auth", tags=["auth"])

#response_model = w/e this function returns, reshape to match UserRead before going back out to client
@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db:Session=Depends(get_db)):

    #was not case sensitive before. took Mag and MAG as different
    normalize_email=payload.email.lower()

    #returns single matching user if one exists or None
    #if existing is None, then email is free and good to register
    existing=db.execute(
        select(User).where(User.email == normalize_email)
    ).scalar_one_or_none()

    #if existing, throw exception 
        #also means, cannot register with that email
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    #if all is good, no matching email THENNN user can register
    #plain text pwd from user, hash it, THEN store. plain text is never stored
    #building User..following db model
    user = User(
        username=payload.username,
        email= normalize_email,
        password_hash=hash_password(payload.password),
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    #since it follows UserRead, there is no chance of the password being sent back
        #good security
    return user