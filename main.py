from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Morning"}

@app.get("/hello")
def read_hello():
    return {"message": "Hello"}

@app.get("/api")
def read_api(name: str = "Guest"):
    return {
        "status": "success",
        "message": f"Welcome to the new API endpoint, {name}!",
        "data": {
            "version": "1.0.0",
            "features": ["FastAPI", "Uvicorn", "Render"]
        }
    }


