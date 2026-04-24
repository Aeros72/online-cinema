from fastapi import FastAPI

app = FastAPI(title="Online Cinema API")


@app.get("/")
def root():
    return {"message": "Online Cinema API"}
