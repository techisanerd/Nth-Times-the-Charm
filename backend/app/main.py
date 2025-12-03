from fastapi import FastAPI 
from routers.fastapi import routerMovie,routerReview,routerUser

title = "Nth Times the Charm Movie Review Api"
description  = "Allows the retrivial of  movies, reviews and users infomation, " \
"the creation of reviews and new users, and editing and deleting of reviews."

app = FastAPI(title = title, description = description)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(routerMovie)
app.include_router(routerReview)
app.include_router(routerUser)

