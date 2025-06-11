from fastapi import FastAPI

app = FastAPI(title="Wine API", version="0.1.0")   # ✔️ instancia correcta


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/version")
def version():
    return {"version": app.version}
