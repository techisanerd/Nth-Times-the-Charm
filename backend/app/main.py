from fastapi import FastAPI 
from routers.fastapi import routerMovie,routerReview

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(routerMovie)
app.include_router(routerReview)


