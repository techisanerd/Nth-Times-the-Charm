import hashlib
from fastapi import HTTPException
from datetime import datetime
from managers.data_manager import DataManager
from managers.managers import UserManager
from managers.managers import ReviewManager, MovieManager
from schemas.classes import Review, User

class UserController():

    def createUser(username:str, email:str, profilePic:str, password:str,):
        if(UserManager.readUser(username)!=None):
            raise HTTPException(status_code = 400, detail = "400 Username already in use")
        if(len(password)<8):
            raise HTTPException(status_code = 400, detail = "400 Password should be 8 or more characters")
        hashedPassword = UserController.hashPassword(password)
        UserManager.createUser(username,email,profilePic,hashedPassword.hexdigest())
    
    def hashPassword(passwordPlaintext:str) -> hashlib.sha224:
        return hashlib.sha224(passwordPlaintext.encode(), usedforsecurity= True)

class ReviewController():

    def addReview(movie:str, username:str, rating:int, title:str,description:str):
        if(MovieManager.readMovie(movie) is None):
            raise HTTPException(status_code = 404, detail = "404 Movie not found")
        if(UserManager.readUser(username) is None):
            raise HTTPException(status_code = 404, detail = "404 User not found")
        if(rating >10 or rating <0):
            raise HTTPException(status_code = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        reviewList = ReviewManager.readReview(movie,username) 
        reviewList = [r for r in reviewList if r.title == title]
        if (reviewList == []):
            ReviewManager.createReview(movie, datetime.now().date(), username,0,0,rating,title,description)
        else:
            raise HTTPException(status_code=409, detail="409 Review with this username and title already exists for this movie")
    
    def editReview(movie:str, username:str, rating:int, title:str, newTitle:str, description:str):
        reviewList = ReviewManager.readReview(movie,username) 
        reviewList = [r for r in reviewList if r.title == title]
        if(reviewList == []):
            raise HTTPException(status_code = 404, detail = "404 Review '{title}' not found")
        if(rating >10 | rating <0):
            raise HTTPException(status_code = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        for r in reviewList:
            ReviewManager.updateReview(movie,r,datetime.now().date(),username,0,0,rating,newTitle,description)

    def removeReview(movie:str, username:str,title:str):
        reviewList = ReviewManager.readReview(movie,username) 
        reviewList = [r for r in reviewList if r.title == title]
        if(reviewList == []):
            raise HTTPException(status_code = 404, detail = "404 Review '{title}' not found")
        for r in reviewList:
            ReviewManager.deleteReview(movie, r)

    def searchByName(movie:str,title:str):
        reviews = ReviewManager.getReviews(movie)
        foundReviews = []
        for r in reviews:
            if (title.lower() in r.title.lower()):
                foundReviews.append(r)
        return foundReviews

class MovieController():
    
    def searchByTags(tags:list=[]):
        movies = MovieManager.getMovies()
        if(len(tags)==0):
            return movies
        foundMovies = []
        for t in tags:
            for m in movies:
                if (t in m.genres or t in m.directors or t in m.creators or t in m.actors):
                    foundMovies.append(m)
                else:
                    if(m in foundMovies):
                        foundMovies.remove(m)
        return foundMovies

    def searchByName(search:str):
        movies = MovieManager.getMovies()
        if(search == []):
            return movies
        foundMovies = []
        for m in movies:
            if (search.toLower() in movies.title.toLower()):
                foundMovies.append
        return foundMovies
    
    def getAllTags():
        tags = []
        movies = MovieManager.getMovies()
        for m in movies:
            tags += m.genres
            tags += m.directors
            tags += m.creators
            tags += m.actors
        tags = set(tags)
        return tags
     
