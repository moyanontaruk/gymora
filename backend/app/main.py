from fastapi import FastAPI

app = FastAPI(title="Gymora API")


@app.get("/")
def read_root():
    return {"message": "Gymora API is running"}
