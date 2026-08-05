from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserLogin, Token


from app.core.security import hash_password, verify_password, create_access_token

from app.core.dependencies import get_current_user

from fastapi.security import OAuth2PasswordRequestForm

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


@router.post("/login", response_model=Token)

#reusing UserCreate b/c it has the email/pass that we need for login
def login(payload:UserLogin, db:Session =Depends(get_db)):
    normalized_email = payload.email.lower()
    user=db.execute(
        select(User).where(User.email == normalized_email)
    ).scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,

            #not being specific by saying which one is wrong adds extra protection 
                #b/c attacker would then know "OH, only the email is wrong"
            detail="Incorrect email or password",
        )

    #if login is all good, create the token with the user's ID then wrap/shape it in the token schema
        #return it
    access_token = create_access_token(user_id=user.user_id)
    return Token(access_token=access_token)



#same at the auth/login but it's for the OAuth2 form format that authroize button uses in /docs
    #instead of JSON
    #testing
@router.post("/token", response_model=Token)
def login_for_docs(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):

    normalize_email = form_data.username.lower()

    user = db.execute(
        select(User).where(User.email == normalize_email)
    ).scalar_one_or_none()

    if user is None or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    access_token = create_access_token(user_id=user.user_id)
    return Token(access_token=access_token)




#"who am i?" endpoint
@router.get("/me", response_model=UserRead)

#the protection, this parameter runs the whole token-checking chain
    #handes the logged-in user as current_user
def read_current_user(current_user: User = Depends(get_current_user)):
    return current_user