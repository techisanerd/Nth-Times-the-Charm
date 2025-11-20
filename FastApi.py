from fastapi import APIRouter, status
from typing import List
#from Controllers import UserController,ReviewController
from Managers import MovieManager
from Classes import Movie, MovieCreate
from fastapi import FastAPI




router = APIRouter(prefix="/Movies", tags=["Movies"])

@router.get("", response_model=List)
def get_movies():
    return MovieManager.getMovies()

@router.get("/{movie_title}", response_model=None)
def get_movie(movie_title: str):
    return MovieManager.readMovie(movie_title)

@router.post("", response_model=Movie, status_code=201)
def post_movie(payload: MovieCreate):
    return MovieManager.createMovie(payload)

@router.delete("/{movie_title}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(movieTitle: str):
    MovieManager.deleteMovie(movieTitle)
    return None

@router.put("/{movie_title}", response_model=Movie)
def put_item(movie_title: str, payload: MovieCreate):
    return MovieManager.updateMovie(movie_title, payload)

#TODO: Add review endpoints
#@router.get("/{review_title},{reviewer},{movie_title}", response_model=None)
#def get_review():
    #return UserController.

app = FastAPI()

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(router)

