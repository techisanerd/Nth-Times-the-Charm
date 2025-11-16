import hashlib
from fastapi import HTTPException
from datetime import date
from DataManager import DataManager
from Managers import UserManager
from Managers import ReviewManager
from Classes import Review
from Classes import User

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
            raise HTTPException(statuscode = 404, detail = "404 Movie not found")
        if(UserManager.readUser(username) is None):
            raise HTTPException(statuscode = 404, detail = "404 User not found")
        if(rating >10 | rating <0):
            raise HTTPException(statuscode = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        reviewList = ReviewManager.readReview(movie,username) 
        reviewList = [r for r in reviewList if r.title == title]
        if (reviewList == []):
            UserManager.createReview(movie, date.today, username,0,0,rating,title,description)
        else:
            raise HTTPException(status_code=409, detail="409 Review with this username and title already exists for this movie")
    
    def editReview(movie:str, username:str, rating:int, title:str, newTitle:str, description:str):
        reviewList = ReviewManager.readReview(movie,username) 
        reviewList = [r for r in reviewList if r.title == title]
        if(reviewList == []):
            raise HTTPException(statuscode = 404, detail = "404 Review '{title}' not found")
        if(rating >10 | rating <0):
            raise HTTPException(statuscode = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        for r in reviewList:
            ReviewManager.updateReview(movie,r,date.now,username,0,0,rating,newTitle,description)

    def removeReview(movie:str, username:str,title:str):
        reviewList = ReviewManager.readReview(movie,username) 
        reviewList = [r for r in reviewList if r.title == title]
        if(reviewList == []):
            raise HTTPException(statuscode = 404, detail = "404 Review '{title}' not found")
        for r in reviewList:
            ReviewManager.deleteReview(movie, r)

    def searchByName(title:str):
        reviews = DataManager.getReviews()
        foundReviews = []
        for r in reviews:
            if (title.toLower() in r.title.toLower()):
                foundReviews.append(r)
        return foundReviews



        
