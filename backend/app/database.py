#create_engine is a function that creates the ain connection
#between python and postgresql database
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.orm import DeclarativeBase, sessionmaker

#to read the database config.
from app.config import get_settings


settings = get_settings()

DATABASE_URL = URL.create(
    drivername="postgresql+psycopg",
    username=settings.db_user,
    password=settings.db_password,
    host=settings.db_host,
    port=settings.db_port,
    database=settings.db_name,
)

#pool_pre... check whether db connection still works before reusing existing db connection
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

#creating a factory that can make db sessions
SessionLocal = sessionmaker(
    #connect sessions created here to the database
    bind=engine,
    #don't auto send changes before every query
    autoflush=False,
    #don't auto commit database changes
    autocommit=False,
)

class Base(DeclarativeBase):
    pass

#FastAPI routes will use this function when they need database access
def get_db():
    #create 1 db session and store it
    database = SessionLocal()
    try:
        #give db session to fastapi temporarily
        yield database
    finally:
        #close db session/release connection
        database.close()
