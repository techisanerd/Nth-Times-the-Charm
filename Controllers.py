import hashlib
from fastapi import HTTPException
from DataManager import *
import uuid

class UserController():

    def createUser(username:str, email:str, password:str):
        """Create a new user profile.
          To add profile pic call addProfilePic(username, url)"""
        hashedPassword = hashPassword(password)
        UserManager.createUser(username,email,password)

    def addProfilePic(username:str, url:str):
        """Add a profile picture. Requires username and the url of the picture being added"""
        User = UserManager.getUser(username)
        UserManager.updateUser(username, User.email, url)
    
    def hashPassword(passwordPlaintext:str) -> hashlib.sha224:
        return hashlib.sha224(passwordPlaintext, True)

class ReviewController():

    def addReview(username:str, rating:int, title:str,description:str):
        if(UserManager.getUser(username) is None):
            raise HTTPException(statuscode = 404, detail = "404 User not found")
        if(rating >10 | rating <0):
            raise HTTPException(statuscode = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        new_id = str(uuid.uuid4())
        if (ReviewManager.getReview(new_id) is None):
            UserManager.createReview(new_id, username,rating,title,description)
        else:
            raise HTTPException(status_code=409, detail="ID collision; retry.")
    
    def editReview(reviewId:str,rating:int,title:str,description:str):
        review = ReviewManager.getReview(reviewId)
        if(review is None):
            raise HTTPException(statuscode = 404, detail = "404 Review '{reviewId}' not found")
        if(rating >10 | rating <0):
            raise HTTPException(statuscode = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        ReviewManager.updateReview(reviewId, review.rating if rating is None else rating, review.title if title is None else title,
                                    review.description if description is None else description)

    def removeReview(reviewId:str):
        review = ReviewManager.getReview(reviewId)
        if(review is None):
            raise HTTPException(statuscode = 404, detail = "404 Review '{reviewId}' not found")
        ReviewManager.deleteReview(reviewId)

    def searchByName(title:str) -> Review:
        reviews = DataManager.getReviews()
        for r in reviews:
            if (r.title.toLower() == title.toLower()):
                return  r
        raise HTTPException(statuscode = 404, detail = "404 Review '{reviewId}' not found")
    


        
