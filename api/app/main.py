from fastapi import FastAPI

app = FastAPI(title="Innovation ICI API")

@app.get("/health")
def health():
    return {"status": "ok"}

