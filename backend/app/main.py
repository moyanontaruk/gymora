from fastapi import FastAPI
from app.routers import equipment, exercise
from app.routers import auth

app = FastAPI(title="Gymora API")

app.include_router(equipment.router)
app.include_router(exercise.router)
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Gymora API is running"}
