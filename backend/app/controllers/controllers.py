import bcrypt
from fastapi import HTTPException
from datetime import datetime
from managers.data_manager import DataManager
from managers.managers import UserManager
from managers.managers import ReviewManager, MovieManager, AdminManager, ReplyManager
from schemas.classes import Review, User,ReviewCreate, Admin

class UserController():

    def createUser(payload:User):
        if(UserManager.readUser(payload.name)!=None):
            raise HTTPException(status_code = 400, detail = "400 Username already in use")
        if(len(payload.password)<8):
            raise HTTPException(status_code = 400, detail = "400 Password should be 8 or more characters")
        hashedPassword = UserController.hashPassword(payload.password)
        return UserManager.createUser(payload.name,payload.email,payload.profilePicURL,hashedPassword)
    
    def hashPassword(passwordPlaintext:str):
        hashed = bcrypt.hashpw(passwordPlaintext.encode(), bcrypt.gensalt())
        return hashed.decode()
    
    def getUser(username:str):
        if(UserManager.readUser(username)==None):
            raise HTTPException(status_code = 404, detail = "404 User Not Found")
        return UserManager.readUser(username)
    
    def updatePassword(user, new_password: str):
        if user is None:
            raise HTTPException(status_code=404, detail="404 User not found")
        
        if not isinstance(new_password, str) or len(new_password) < 8:
            raise ValueError("Password must be at least 8 characters long")

        user.password = UserController.hashPassword(new_password)
        return True
    
    def verifyPassword(user, password: str) -> bool:
        user = UserManager.readUser(user)
        return bcrypt.checkpw(password.encode(), user.password.encode())

class ReviewController():

    def addReview(movie:str, payload:ReviewCreate):
        reviewList = ReviewController.getReviewsByTitle(movie,payload.reviewer,payload.title)
        if(UserManager.readUser(payload.reviewer) is None):
            raise HTTPException(status_code = 404, detail = "404 User not found")
        if(payload.rating >10 or payload.rating <0):
            raise HTTPException(status_code = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        for r in reviewList:
            if r.reviewer == payload.reviewer:
                raise HTTPException(status_code=409, detail="409 Review with this username and title already exists for this movie") 
        return ReviewManager.createReview(movie, datetime.now().date(), payload.reviewer,0,0,payload.rating,
                                       payload.title,payload.description)

    def editReview(movie:str, currentTitle:str, payload:ReviewCreate):
        """Note: put the current title of the review in currentTitle and the new one in the payload. 
        Make sure the reviewer in the payload is the original reviewer"""
        reviewList = ReviewController.getReviewsByTitle(movie,payload.reviewer,currentTitle)
        if(reviewList == []):
            raise HTTPException(status_code = 404, detail = f"404 Review '{currentTitle}' not found")
        if(payload.rating >10 | payload.rating <0):
            raise HTTPException(status_code = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        for r in reviewList:
            return ReviewManager.updateReview(movie,r,datetime.now().date(),payload.reviewer,0,0,
                                       payload.rating,payload.title,payload.description)

    def removeReview(movie:str, username:str,title:str):
        reviewList = ReviewController.getReviewsByTitle(movie,username,title)
        if(reviewList == []):
            raise HTTPException(status_code = 404, detail = f"404 Review '{title}' not found")
        from managers.managers import ReplyManager
        for r in reviewList:
            ReviewManager.deleteReview(movie, r)
            ReplyManager.deleteRepliesForReview(movie, username, title)

    def searchByName(movie:str,title:str):
        reviews = ReviewController.getReviews(movie)
        if(len(title)==0):
            return reviews
        foundReviews = []
        for r in reviews:
            if (title.lower() in r.title.lower()):
                foundReviews.append(r)
        return foundReviews
    
    def getReviews(movie:str):
        MovieController.getMovie(movie)
        return ReviewManager.getReviews(movie)
    
    def getReviewsByTitle(movie:str, username:str,title:str) -> list[Review]:
        MovieController.getMovie(movie)
        reviewList = ReviewManager.readReview(movie,username) 
        reviewList = [r for r in reviewList if r.title == title]
        return reviewList
    
    @staticmethod
    def replyToReview(movie: str, reviewer: str, title: str, reply: str):
        reviewList = ReviewController.getReviewsByTitle(movie, reviewer, title)

        if not reviewList:
            raise HTTPException(status_code=404, detail="Review not found")

        review = reviewList[0]
        if review.reply is not None:
            raise HTTPException(status_code=409, detail="Review already has a reply")

        return ReviewManager.updateReview(movie, review, reply=reply)

class ReplyController:
    @staticmethod
    def addReply(movie, reviewAuthor, reviewTitle, payload):
        from controllers.controllers import ReviewController
        reviewList = ReviewController.getReviewsByTitle(movie, reviewAuthor, reviewTitle)

        if not reviewList:
            raise HTTPException(status_code=404, detail="Review not found")

        return ReplyManager.addReply(movie, reviewAuthor, reviewTitle, payload.replyAuthor, payload.replyText)

    @staticmethod
    def getReplies(movie, reviewAuthor, reviewTitle):
        return ReplyManager.getReplies(movie, reviewAuthor, reviewTitle)

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
     
class AdminController():

    def createAdmin(payload:Admin):
        admin = UserController.createUser(Admin)
        if(AdminManager.readAdmin(payload.name) is not None):
            raise HTTPException(status_code = 400, detail = "400 Admin already exist with this name")
        AdminManager.writeUserToData(admin)

    def getAdmin(username):
        if(AdminManager.readAdmin(username)==None):
            raise HTTPException(status_code = 404, detail = "404 Admin Not Found")
        return AdminManager.readAdmin(username)
    

class AdminReviewController():

    def takedownReview(adminName:str, movie:str, username:str, reviewTitle:str):
        AdminController.getAdmin(adminName)
        MovieController.getMovie(movie)
        try:
            UserController.getUser(username)
            #TODO give warning to user
        except:
            pass
        ReviewController.removeReview(movie, username, reviewTitle) #TODO make it so only admins can delete a review that isn't theirs

    
        