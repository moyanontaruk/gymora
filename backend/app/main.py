from fastapi import FastAPI
from app.routers import equipment, exercise,auth, workout_log, muscle_group
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Gymora API")

app.add_middleware(
    CORSMiddleware,

    #not doing ["*"] b/c then all origins(any webssite) would be able to access
        #listing exactly which so only the react dev server can enter
    allow_origins=["http://localhost:5173","http://127.0.0.1:5173"],

    #let browser send Authorization header with the JWT
    allow_credentials=True,

    #GET, POST, PUT, DELETE
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(equipment.router)
app.include_router(exercise.router)
app.include_router(auth.router)
app.include_router(workout_log.router)
app.include_router(muscle_group.router)


@app.get("/")
def read_root():
    return {"message": "Gymora API is running"}
