from fastapi import FastAPI

from src.api.router import api_router

app = FastAPI(title="Online Cinema API")

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Online Cinema API"}
