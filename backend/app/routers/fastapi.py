from fastapi import APIRouter, status, Query
from typing import List, Optional
from datetime import datetime
from managers.data_manager import DataManager
from controllers.controllers import ReviewController,MovieController,UserController,ReplyController
from managers.managers import MovieManager,ReviewManager, UserManager, SessionManager
from schemas.classes import Movie,Review,MovieCreate,ReviewCreate,User,UserView,Reply,ReplyCreate, LoginRequest
from fastapi import FastAPI
import bcrypt
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Depends
routerSession = APIRouter(tags=["Auth"])

@routerSession.post("/login")
def login(request: LoginRequest):
    matchingUsername = UserManager.readUser(request.name)
    if matchingUsername is None or not bcrypt.checkpw(request.password.encode(), matchingUsername.password.encode()):
        print(matchingUsername)
        print(UserController.hashPassword(request.password))
        raise HTTPException(status_code=401, detail="Invalid credentials")

    session = SessionManager.create_session(request.name)
    return {"token": session.token}

@routerSession.post("/logout")
def logout(token: str):
    return SessionManager.deleteSession(token)

@routerSession.get("/protected-route")
def protected_route(token: str):
    session = SessionManager.getSession(token)
    if not session or not session.is_valid():
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"message": "Access granted"}

routerMovie = APIRouter(prefix="/Movies", tags=["Movies"])

@routerMovie.get("", response_model=List[Movie])
def get_movies():
    """Returns a json with the metadata for each movie."""
    return MovieManager.getMovies()

@routerMovie.get("/{movie_title}", response_model=Movie)
def get_movie(movie_title: str):
    """Return a json with the metadata for a specific movie matching the title exactly."""
    return MovieController.getMovie(movie_title)


routerReview = APIRouter(prefix="/Reviews", tags=["Reviews"])


@routerReview.get("/{movie_title}",response_model = List[Review])
def get_reviews(movie_title:str):
    """Gets every review for a specific movie. May take a couple minutes for popular movies."""
    return ReviewController.getReviews(movie_title)

@routerReview.get("/{movie_title}/{review_search_title}", response_model=List[Review])
def get_review(review_search_title:str,movie_title:str):
    """Gets reviews that are for movie_title (case-sensistive) and include review_search_title in the review title (non-case-sensitive).
    Returns 404 if movie not found and an empty list if no matches for the review search title."""
    return ReviewController.searchByName(movie_title,review_search_title)

@routerReview.post("/{movie_title}", response_model=Review)
def post_review(movie_title:str,payload:ReviewCreate):
    """Post a review for a specific movie. Reviewer must be a valid existing user or it will throw a 404 error.
    Movie must also exist in our records or it will throw a 404 error"""
    return ReviewController.addReview(movie_title,payload)

@routerReview.delete("/{movie_title}/{reviewer}/{review_title}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item(movie_title: str,reviewer:str,review_title:str):
    """Deletes a review. This action cannot be reversed."""
    ReviewController.removeReview(movie_title,reviewer,review_title)
    return None

@routerReview.put("/{movie_title}/{review_title}", response_model=Review)
def put_item(movie_title: str, review_title:str, payload:ReviewCreate):
    """Edits a review. Note that review_title must be the current title of the review. 
    You can change the review title in the payload. Reviewer in payload must be original reviewer."""
    return ReviewController.editReview(movie_title, review_title, payload)

@routerReview.post("/{movie_title}/{reviewer}/{review_title}/reply", response_model=Reply)
def post_reply(movie_title: str, reviewer: str, review_title: str, payload: ReplyCreate):
    """Add a reply to an existing review. Multiple replies allowed."""
    return ReplyController.addReply(movie_title, reviewer, review_title, payload)

@routerReview.get("/{movie_title}/{reviewer}/{review_title}/replies", response_model=list[Reply])
def get_replies(movie_title: str, reviewer: str, review_title: str):
    """Get all replies for a specific review."""
    return ReplyController.getReplies(movie_title, reviewer, review_title)


routerUser = APIRouter(prefix="/Users", tags=["Users"])


@routerUser.get("",response_model = List[UserView])
def get_users():
    """Returns a json with all current user's usernames and profile picture urls."""
    return UserManager.getUsers()

@routerUser.get("/{username}", response_model=UserView)
def get_user(username):
    """Returns a json with a specific user's username and profile picture url."""
    return UserController.getUser(username)

@routerUser.post("", response_model=UserView)
def post_user(payload:User):
    """Create a new user. Profile Pic URL must be a valid url from https://api.dicebear.com"""
    return UserController.createUser(payload)


routerExport = APIRouter()

ReviewData = [
    {"movie_title": "Test Movie", "reviewDate": datetime(2023, 1, 10), "reviewer": "Alice", "rating": 7, "description": "Hi"},
    {"movie_title": "Test Movie", "reviewDate": datetime(2023, 1, 11), "reviewer": "Bob", "rating": 8, "description": "Okay"},
]

def serialize_record(record: dict) -> dict:
    out = {}
    for k, v in record.items():
        if isinstance(v, datetime):
            out[k] = v.date().isoformat()
        else:
            out[k] = v
    return out

@routerExport.get("/export/reviews")
async def export_reviews(movie_title: str = Query(..., description="Title of the movie"), fields: Optional[List[str]] = None):
    
    data = [r.copy() for r in ReviewData if r["movie_title"] == movie_title]

    data = [serialize_record(r) for r in data]

    if fields:
        data = [{key: review[key] for key in fields if key in review} for review in data]

    return JSONResponse(
        content=data,
        media_type="application/json",
        headers={
            "Content-Disposition": f"attachment; filename=movie_{movie_title}_reviews.json"
        }
    )