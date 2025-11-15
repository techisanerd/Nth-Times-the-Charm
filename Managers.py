from DataManager import DataManager
from Classes import User, Movie, Review
from datetime import datetime

class UserManager():
    def readUser(name:str) -> User|None:
        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        for u in userList:
            if u.name == name:
                return u 
        #if user does not exist return nothing
        return None
    

    def getUsers() -> list[User]:
        dataMan = DataManager.getInstance()
        return dataMan.getUsers()


    def createUser(name:str, email:str, profilePic:str, passwordHash:str, auth=None) -> User | None:
        #ensure no duplicates
        if UserManager.readUser(name) is not None:
            return None            

        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        user = User(name, email, profilePic, passwordHash, auth)
        userList.append(user)
        dataMan.writeUsers(userList)
        return user


    def updateUser(user, name:str=None, email:str=None, profilePic:str=None, passwordHash:str=None, auth=None) -> User:
        UserManager.deleteUser(user.name)

        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if profilePic is not None:
            user.profilePic = profilePic
        if passwordHash is not None:
            user.passwordHash = passwordHash 
        if auth is not None:
            user.auth = auth 

        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        userList.append(user)
        dataMan.writeUsers(userList)
        
        return user


    def deleteUser(name:str) -> bool:
        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        initialSize = len(userList)
        userList = [user for user in userList if user.name != name]

        dataMan.writeUsers(userList)
        return initialSize < len(userList)
    
class ReviewManager():
    def createReview(movie, reviewDate:datetime.date, reviewer, usefulnessVote:int, totalVotes:int, rating:int, 
                 title:str, description:str) -> Review | None:
        review = Review(reviewDate, reviewer, usefulnessVote, totalVotes, rating, title, description)
        dataMan = DataManager.getInstance()
        reviewList = dataMan.readReviews(movie)
        reviewList.append(review)
        dataMan.writeReviews(movie, reviewList)
        return review

    def readReview(movie:str, reviewer:str) -> list[Review]:
        dataMan = DataManager.getInstance()
        reviewList = dataMan.readReviews(movie)
        foundList = []
        for r in reviewList:
            if r.reviewer == reviewer:
                foundList.append(r)
        #if reviewer does not exist return nothing
        return foundList 
    

    def updateReview(movie, review, reviewDate:datetime=None, reviewer=None, usefulnessVote:int=None, totalVotes:int=None, rating:int=None, 
                 title:str=None, description:str=None) -> Review:
        ReviewManager.deleteReview(movie, review)
 
        if reviewDate is not None:
            review.reviewDate = reviewDate
        if reviewer is not None:
            review.reviewer = reviewer
        if usefulnessVote is not None:
            review.usefulnessVote = usefulnessVote
        if totalVotes is not None:
            review.totalVotes = totalVotes
        if rating is not None:
            review.rating = rating
        if title is not None:
            review.title = title
        if description is not None:
            review.description = description

        dataMan = DataManager.getInstance()
        reviewList = dataMan.readReviews(movie)
        reviewList.append(review)
        dataMan.writeReviews(movie, reviewList)
        return review

    def deleteReview(movie, review:Review) -> bool:
        dataMan = DataManager.getInstance()
        reviewList = dataMan.readReviews(movie)
        
        initialSize = len(reviewList)
        reviewList = [r for r in reviewList if r.reviewer == review.reviewer and
        r.title == review.title]
        return initialSize > len(reviewList)
    

    def getReviews(movie):
        dataMan = DataManager.getInstance()
        return dataMan.getReviews(movie)
 
class MovieManager():
    pass