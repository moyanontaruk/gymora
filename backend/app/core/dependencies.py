from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.core.security import decode_access_token

#--- login > get token > attacch it as Authorization header on future request >
    # server reads the header to know who it is


#FastAPI helper that extract the token from incoming request
    #oauth2_scheme is the tool that reads the label
# OAuth2PasswordBearer -->> get the bearer token from request header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


def get_current_user(
        
        #runs oauth2_scheme to pull token str out of request
        token: str = Depends(oauth2_scheme),
        db: Session = Depends(get_db),
    ) -> User:


    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",

        #tells client this endpoint expects a bearer token
        headers={"WWW-Authenticate" : "Bearer"},
    )

    #decode using that function to ensure it's not bad/expired/forged token
    user_id = decode_access_token(token)
    if user_id is None:
        raise credential_exception

    #if token valided, confirm user is in db
    #db.get(User, user_id) .. fetching by PK
    user =db.get(User, user_id)
    if user is None:
        raise credential_exception

    return user



#building on get_current_user...that one proves who you are
    #this one checks if that person is allowed to manage content

def get_current_admin(
        current_user:User =Depends(get_current_user),
    ) -> User:

    if current_user.role !="admin":
        raise HTTPException(
            status_code= status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    return current_user