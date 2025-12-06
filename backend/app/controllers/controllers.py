import bcrypt
from fastapi import HTTPException
from datetime import datetime
from managers.data_manager import DataManager
from managers.managers import UserManager
from managers.managers import ReviewManager, MovieManager, AdminManager, ReplyManager
from schemas.classes import Review, User, ReviewCreate, Admin, Movie
from random import randrange

class UserController():

    def createUser(payload:User):
        if(UserManager.readUser(payload.name)!=None):
            raise HTTPException(status_code = 400, detail = "400 Username already in use")
        if(len(payload.password)<8):
            raise HTTPException(status_code = 400, detail = "400 Password should be 8 or more characters")
        if(payload.profilePicURL == None):
            payload.profilePicURL = ProfilePicController.getProfilePic()
        else:
            picURLs = ProfilePicController.searchByTags()
            if(payload.profilePicURL not in picURLs):
                raise HTTPException(status_code = 400, detail = "400 URL must be from our list of accepted profile URLs")
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
    
    def deleteAccount(name:str):
        user = UserManager.readUser(name)
        if user is None:
            raise HTTPException(status_code= 404, detail = "404 User not found")
        
        success = UserManager.deleteUser(name)

        if not success:
            raise HTTPException(status_code = 500, detail= "500 Something went wrong, please try again")
        
        return True
    
    def editUser(name:str, newUserDetails:User):
        if(UserController.deleteAccount(name)):
            user = UserController.createUser(newUserDetails)
        return user

class ReviewController():

    def addReview(movie:str, payload:ReviewCreate):
        reviewList = ReviewController.getReviewsByTitle(movie,payload.reviewer,payload.title)
        if(UserManager.readUser(payload.reviewer) is None):
            raise HTTPException(status_code = 404, detail = "404 User not found")
        if(payload.rating >10 or payload.rating <0):
            raise HTTPException(status_code = 400, detail = "400 Rating needs to be an integer between 0 and 10")
        if (len(reviewList)>0):
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

    def sortReviews(reviews: list[Review], sortBy: str, order: str = "asc") -> list[Review]:
        if sortBy not in ['rating', 'reviewDate', 'title', 'usefulnessVote', 'totalVotes']:
            raise ValueError("Invalid sortBy value")
        if order not in ['asc', 'desc']:
            raise ValueError("Order must be 'asc' or 'desc'")
        
        reverse = (order == "desc")

        if sortBy == 'rating':
            sorted_reviews = sorted(reviews, key=lambda r: r.rating, reverse=reverse)
        elif sortBy == 'reviewDate':
            sorted_reviews = sorted(reviews, key=lambda r: r.reviewDate, reverse=reverse)
        elif sortBy == 'title':
            sorted_reviews = sorted(reviews, key=lambda r: r.title.lower(), reverse=reverse)
        elif sortBy == 'usefulnessVote':
            sorted_reviews = sorted(reviews, key=lambda r: r.usefulnessVote, reverse=reverse)
        elif sortBy == 'totalVotes':
            sorted_reviews = sorted(reviews, key=lambda r: r.totalVotes, reverse=reverse)
        
        return sorted_reviews
    
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
            if search.lower() in (m.title).lower():
                foundMovies.append(m)
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
    
    def sortMovies(movies: list[Movie], sortBy: str, order: str = "asc") -> list[Movie]:
        if sortBy not in ["rating", "dateReleased", "title", "metaScore", "ratingCount", "duration"]:
            raise ValueError("Invalid sortBy value")

        if order not in ["asc", "desc"]:
            raise ValueError("Order must be 'asc' or 'desc'")
        
        reverse = (order == "desc")

        if sortBy == "rating":
            sorted_movies = sorted(movies, key=lambda m: m.rating, reverse=reverse)
        elif sortBy == "dateReleased":
            sorted_movies = sorted(movies, key=lambda m: m.dateReleased, reverse=reverse)
        elif sortBy == "title":
            sorted_movies = sorted(movies, key=lambda m: m.title.lower(), reverse=reverse)
        elif sortBy == "metaScore":
            sorted_movies = sorted(movies, key=lambda m: m.metaScore, reverse=reverse)
        elif sortBy == "ratingCount":
            sorted_movies = sorted(movies, key=lambda m: m.ratingCount, reverse=reverse)
        elif sortBy == "duration":
            sorted_movies = sorted(movies, key=lambda m: m.duration, reverse=reverse)

        return sorted_movies
     
class ProfilePicController():

    def getProfilePic(tags:list=[]):
        pics = ProfilePicController.searchByTags(tags)
        if(len(pics)==0):
            raise HTTPException(status_code = 404, detail = f"404 Picture with all tags not found")
        if(len(pics)>1):
            randomNum = randrange(0,len(pics))
            return pics[randomNum]
        return pics[0]
    

    def searchByTags(tags:list=[]):
        dataMan = DataManager.getInstance()
        pics = dataMan.getProfilePics()
        dm = DataManager.getInstance()
        picURLs = []
        for p in dm.getProfilePics():
            picURLs.append(p.profilePicURL)
        if(len(tags)==0):
            return picURLs
        foundPics = []
        for t in tags:
            for p in pics:
                if (t in p.themes):
                    foundPics.append(p.profilePicURL)
                else:
                    if(p.profilePicURL in foundPics):
                        foundPics.remove(p.profilePicURL)
        foundPics = list(set(foundPics))
        return foundPics
    
    def getAllTags():
        dataMan = DataManager.getInstance()
        tags = []
        pics = dataMan.getProfilePics()
        for p in pics:
            tags += p.themes
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

    
        
