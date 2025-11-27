from fastapi import FastAPI

app = FastAPI(title="TaskQuest API")

@app.get("/health")
def health():
    return {"status": "ok"}