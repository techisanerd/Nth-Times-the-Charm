from fastapi import APIRouter, status, Query, FastAPI
from typing import List, Optional
from controllers.controllers import ReviewController,MovieController,UserController
from managers.managers import MovieManager,ReviewManager, UserManager
from schemas.classes import Movie,Review,MovieCreate,ReviewCreate,User,UserView
from fastapi import FastAPI
from fastapi.responses import JSONResponse




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
    return ReviewController.getReviews(movie_title)

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

@routerReview.put("/{movie_title}/{review_title}", response_model=Review)
def put_item(movie_title: str, review_title:str, payload:ReviewCreate):
    return ReviewController.editReview(movie_title, review_title, payload)


routerUser = APIRouter(prefix="/Users", tags=["Users"])


@routerUser.get("",response_model = List[UserView])
def get_users():
    return UserManager.getUsers()

@routerUser.get("/{username}", response_model=UserView)
def get_user(username):
    return UserController.getUser(username)

@routerUser.post("", response_model=UserView)
def post_user(payload:User):
    return UserController.createUser(payload)


routerExport = APIRouter()

ReviewData = [
    {"movie_title": "Test Movie", "reviewDate": "2023-01-10", "reviewer": "Alice", "rating": 7, "description": "Hi"},
    {"movie_title": "Test Movie", "reviewDate": "2023-01-11", "reviewer": "Bob", "rating": 8, "description": "Okay"},
]

@routerExport.get("/export/reviews")
async def export_reviews(movie_title: str = Query(..., description="Title of the movie"), fields: Optional[List[str]] = None):
    
    data = [r for r in ReviewData if r["movie_title"] == movie_title]

    if fields:
        data = [{key: review[key] for key in fields if key in review} for review in data]

    return JSONResponse(
        content=data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=movie_{movie_title}_reviews.json"
        }
    )