from fastapi import FastAPI
from app.routers import equipment
app = FastAPI(title="Gymora API")

app.include_router(equipment.router)

@app.get("/")
def read_root():
    return {"message": "Gymora API is running"}
