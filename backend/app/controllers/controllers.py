import hashlib, bcrypt
from fastapi import HTTPException
from datetime import datetime
from managers.data_manager import DataManager
from managers.managers import UserManager
from managers.managers import ReviewManager, MovieManager
from schemas.classes import Review, User,ReviewCreate

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
    
    def updatePassword(self, new_password: str):
        #Hash the new password and update the internal passwordHash.
        if not isinstance(new_password, str) or len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        hashed = bcrypt.hashpw(new_password.encode(), bcrypt.gensalt())
        self.passwordHash = hashed.decode()
        return True
    
    def verifyPassword(self, password: str) -> bool:
        return bcrypt.checkpw(password.encode(), self.passwordHash.encode())

class ReviewController():

    def addReview(movie:str, payload:ReviewCreate):
        if(MovieManager.readMovie(movie) is None):
            raise HTTPException(status_code = 404, detail = "404 Movie not found")
        if(UserManager.readUser(payload.reviewer) is None):
            raise HTTPException(status_code = 404, detail = "404 User not found")
        if(payload.rating >10 or payload.rating <0):
            raise HTTPException(status_code = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        reviewList = ReviewManager.readReview(movie,payload.reviewer) 
        reviewList = [r for r in reviewList if r.title == payload.title]
        if (reviewList == []):
            ReviewManager.createReview(movie, datetime.now().date(), payload.reviewer,0,0,payload.rating,
                                       payload.title,payload.description)
        else:
            raise HTTPException(status_code=409, detail="409 Review with this username and title already exists for this movie")
        return Review(reviewDate = datetime.now().date(),reviewer= payload.reviewer,
                      usefulnessVote=0,totalVotes=0,rating =payload.rating,
                      title = payload.title,description =payload.description)

    def editReview(movie:str, currentTitle:str, payload:ReviewCreate):
        """Note: put the current title of the review in currentTitle and the new one in the payload. 
        Make sure the reviewer in the payload is the original reviewer"""
        reviewList = ReviewManager.readReview(movie,payload.reviewer) 
        reviewList = [r for r in reviewList if r.title == currentTitle]
        if(reviewList == []):
            raise HTTPException(status_code = 404, detail = f"404 Review '{currentTitle}' not found")
        if(payload.rating >10 | payload.rating <0):
            raise HTTPException(status_code = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        for r in reviewList:
            ReviewManager.updateReview(movie,r,datetime.now().date(),payload.reviewer,0,0,
                                       payload.rating,payload.title,payload.description)

    def removeReview(movie:str, username:str,title:str):
        if(MovieManager.readMovie(movie) is None):
            raise HTTPException(status_code = 404, detail = "404 Movie not found")
        if(UserManager.readUser(username) is None):
            raise HTTPException(status_code = 404, detail = "404 User not found")
        reviewList = ReviewManager.readReview(movie,username) 
        reviewList = [r for r in reviewList if r.title == title]
        if(reviewList == []):
            raise HTTPException(status_code = 404, detail = "404 Review '{title}' not found")
        for r in reviewList:
            ReviewManager.deleteReview(movie, r)

    def searchByName(movie:str,title:str):
        if(MovieManager.readMovie(movie) is None):
            raise HTTPException(status_code = 404, detail = "404 Movie not found")
        reviews = ReviewManager.getReviews(movie)
        if(len(title)==0):
            return reviews
        foundReviews = []
        for r in reviews:
            if (title.lower() in r.title.lower()):
                foundReviews.append(r)
        return foundReviews

class MovieController():

    def getMovie(title):
        if(MovieManager.readMovie(title) is None):
            raise HTTPException(status_code = 404, detail = "404 Movie not found")
        return MovieManager.readMovie(title)
    
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
     
