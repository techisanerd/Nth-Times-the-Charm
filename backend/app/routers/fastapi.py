from fastapi import APIRouter, status, FastAPI
from typing import List
#from Controllers import UserController,ReviewController
from managers.managers import MovieManager


router = APIRouter(prefix="/Movies", tags=["Movies"])

@router.get("", response_model=List)
def get_movies():
    return MovieManager.getMovies()

@router.get("/{movie_title}", response_model=None)
def get_movie(movieTitle: str):
    return MovieManager.readMovie(movieTitle)

@router.post("", response_model=None, status_code=201)
def post_movie(payload):
    return MovieManager.createMovie(payload)

@router.delete("/{movie_title}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(movieTitle: str):
    MovieManager.deleteMovie(movieTitle)
    return None

@router.put("/{movie_title}", response_model=None)
def put_item(movie_title: str, payload):
    return MovieManager.updateMovie(movie_title, payload)

#TODO: Add review endpoints
#@router.get("/{review_title},{reviewer},{movie_title}", response_model=None)
#def get_review():
    #return UserController.

