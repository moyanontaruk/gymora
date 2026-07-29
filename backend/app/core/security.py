#hashing tool
import bcrypt

#timedelta is duration
from datetime import datetime, timedelta, timezone
import jwt
from app.config import get_settings


settings = get_settings()

#take pwd and return hash as str
#this func. is what is saved when a user register
def hash_password(plain_password: str) -> str:

    #turn str into bytes
    password_bytes = plain_password.encode("utf-8")

    #bcrypt.hashpw(...) takes the bytes + salts and makes hash
    #gensalt is when bcrypt "salts" in random stuff into each pwd 
        #so ppl with same pwd wont get same hash
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())

    #turn bytes back to str to store in db's password_hash'
    return hashed.decode("utf-8")


#when user logs in
#takes plain str user inputs, reads the salt from the stored hash, apply that salt into 
    #the typed pwd, hash it then return true/false for if they match
def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_bytes = plain_password.encode("utf-8")
    hashed_bytes = hashed_password.encode("utf-8")

    return bcrypt.checkpw(password_bytes, hashed_bytes)


#takes user_id(which user this token is for) and returns a signed JWT str.
def create_access_token(user_id:int) -> str:

    #sets expiry for token set to utc time so it's the same no matter what timezone
    expire = datetime.now(timezone.utc) + timedelta (
        minutes=settings.jwt_access_token_expire_minutes
    )

    #"sub" = subject (who is the token about)... when request comes in, server will know sub =use7
    #"exp" = expiration
    payload = {
        "sub": str(user_id),
        "exp": expire,
    }

    #encode, not encrypt so no sensitve info here
        #only id + expiry
    token = jwt.encode(

        #claims to embed
        payload,

        #secrey key, used to sign. it makes the token tamper-rpoof
            #the signature is generated from payload + secrety
        settings.jwt_secret_key,

        # HS246 method from config
        algorithm=settings.jwt_algorithm,
    )
    return token
