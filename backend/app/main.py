from fastapi import FastAPI 
from routers.fastapi import routerMovie,routerReview,routerUser,routerExport

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(routerMovie)
app.include_router(routerReview)
app.include_router(routerUser)
app.include_router(routerExport)
