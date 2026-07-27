#hashing tool
import bcrypt


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



