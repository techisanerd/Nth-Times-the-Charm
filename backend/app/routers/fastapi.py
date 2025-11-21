from fastapi import APIRouter, status, FastAPI
from typing import List
from controllers.controllers import ReviewController
from managers.managers import MovieManager,ReviewManager
from schemas.classes import Movie,Review
from fastapi import FastAPI




routerMovie = APIRouter(prefix="/Movies", tags=["Movies"])

@routerMovie.get("", response_model=List)
def get_movies():
    return MovieManager.getMovies()

@routerMovie.get("/{movie_title}", response_model=None)
def get_movie(movieTitle: str):
    return MovieManager.readMovie(movieTitle)

@routerMovie.post("", response_model=None, status_code=201)
def post_movie(payload):
    return MovieManager.createMovie(payload)

@routerMovie.delete("/{movie_title}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(movieTitle: str):
    MovieManager.deleteMovie(movieTitle)
    return None

@routerMovie.put("/{movie_title}", response_model=None)
def put_item(movie_title: str, payload):
    return MovieManager.updateMovie(movie_title, payload)

routerReview = APIRouter(prefix="/Reviews", tags=["Reviews"])

#TODO: Add review endpoints
@routerReview.get("/{movie_title}",response_model = List[Review])
def get_reviews(movie_title:str):
    return ReviewManager.getReviews(movie_title)

#@routerReview.get("/{movie_title}/{review_title}", response_model=Review)
#def get_review(review_search_title:str,movie_title:str):
    #return ReviewController.searchByName(review_search_title,movie_title)


