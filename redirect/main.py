from fastapi import FastAPI
from fastapi.responses import RedirectResponse

app = FastAPI()

@app.get("/")
def root():
    return RedirectResponse("https://drishti-ai-1.onrender.com")

@app.get("/docs")
def docs_redirect():
    return RedirectResponse("https://drishti-ai-szyx.onrender.com/docs")

@app.get("/{path:path}")
def catch_all(path: str):
    return RedirectResponse("https://drishti-ai-1.onrender.com")