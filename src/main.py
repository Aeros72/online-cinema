from fastapi import FastAPI

from src.api.router import api_router

app = FastAPI(
    title="Online Cinema API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"message": "Online Cinema API v1"}
