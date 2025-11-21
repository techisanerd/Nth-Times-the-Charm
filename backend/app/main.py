from fastapi import FastAPI 
from routers.fastapi import router

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)

