from fastapi import APIRouter, status, FastAPI
from typing import List
from controllers.controllers import ReviewController,MovieController
from managers.managers import MovieManager,ReviewManager
from schemas.classes import Movie,Review,MovieCreate,ReviewCreate
from fastapi import FastAPI




routerMovie = APIRouter(prefix="/Movies", tags=["Movies"])

@routerMovie.get("", response_model=List[Movie])
def get_movies():
    return MovieManager.getMovies()

@routerMovie.get("/{movie_title}", response_model=Movie)
def get_movie(movie_title: str):
    return MovieController.getMovie(movie_title)


routerReview = APIRouter(prefix="/Reviews", tags=["Reviews"])


@routerReview.get("/{movie_title}",response_model = List[Review])
def get_reviews(movie_title:str):
    return ReviewManager.getReviews(movie_title)

@routerReview.get("/{movie_title}/{review_search_title}", response_model=List[Review])
def get_review(review_search_title:str,movie_title:str):
    return ReviewController.searchByName(movie_title,review_search_title)

@routerReview.post("/{movie_title}", response_model=Review)
def post_review(movie_title:str,payload:ReviewCreate):
    return ReviewController.addReview(movie_title,payload)

@routerReview.delete("/{movie_title}/{reviewer}/{review_title}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(movie_title: str,reviewer:str,review_title:str):
    ReviewController.removeReview(movie_title,reviewer,review_title)
    return None

@routerReview.put("/{movie_title}/{reviewer}/{review_title}", response_model=Review)
def put_item(movie_title: str, reviewer:str, review_title:str, payload:ReviewCreate):
    return ReviewController.editReview(movie_title, reviewer, review_title, payload)


