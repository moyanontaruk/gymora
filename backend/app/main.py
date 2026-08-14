from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import equipment, exercise, auth, workout_log, muscle_group, assistant

app = FastAPI(title="Gymora API")

#browsers block requests between different origins by default
#react runs on 5173, this api on 8000, so they count as different
#this tells the browser those two are allowed to talk
app.add_middleware(
    CORSMiddleware,

    #only my react dev server. NOT "*", which would allow any website
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],

    #let the browser send the Authorization header with the JWT
    allow_credentials=True,

    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(equipment.router)
app.include_router(exercise.router)
app.include_router(auth.router)
app.include_router(workout_log.router)
app.include_router(muscle_group.router)
app.include_router(assistant.router)

@app.get("/")
def read_root():
    return {"message": "Gymora API is running"}

