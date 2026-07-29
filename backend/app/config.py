#using later so Settingg onject is created only once then reused when get_settings() is called
from functools import lru_cache
from pathlib import Path

#BaseSettings = reads/validates envir/config values
#SettingsConfigDict = configs how BaseSettings should act
from pydantic_settings import BaseSettings, SettingsConfigDict


current_file = Path(__file__)
absolute_file = current_file.resolve()
app_folder = absolute_file.parent
backend_folder = app_folder.parent
ENV_FILE = backend_folder / ".env"


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "gymora"

    #adding JWT lines so app can access for log in stuff
    
    #no default so is required
        #if .env is missing "jwt_secret_key" then app not start flagging error
            #good safety measure rather than silently running the app insecurely 
    jwt_secret_key:str

    #default from .env so this is optional
    jwt_algorithm: str ="HS256"
    jwt_access_token_expire_minutes:int =30


    model_config= SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:

    #where file gets validated
    #Settings() reads/validates the config. values from .env
    return Settings()
