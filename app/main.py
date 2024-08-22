
from app.adapters.api.v1 import create_app

app = create_app()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Vector Database API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
