from fastapi import FastAPI
from app.routers import equipment, exercise,auth, workout_log, muscle_group


app = FastAPI(title="Gymora API")

app.include_router(equipment.router)
app.include_router(exercise.router)
app.include_router(auth.router)
app.include_router(workout_log.router)
app.include_router(muscle_group.router)


@app.get("/")
def read_root():
    return {"message": "Gymora API is running"}
