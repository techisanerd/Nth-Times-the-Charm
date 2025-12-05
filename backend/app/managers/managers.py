from managers.data_manager import DataManager
from schemas.classes import User, Movie, Review, Session, Admin, AdminWarning
from datetime import datetime
from pathlib import Path

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
    
    def writeUserToData(user:User):
        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        userList.append(user)
        dataMan.writeUsers(userList)


    def createUser(name:str, email:str, profilePicURL:str, password:str) -> User | None:
        #ensure no duplicates
        if UserManager.readUser(name) is not None:
            return None            

        
        user = User(name=name, email=email, profilePicURL=profilePicURL, password=password)
        UserManager.writeUserToData(user)
        return user


    def updateUser(user, name:str=None, email:str=None, profilePicURL:str=None, password:str=None) -> User:
        UserManager.deleteUser(user.name)

        if name is not None:
            user.name = name
        if email is not None:
            user.email = email
        if profilePicURL is not None:
            user.profilePicURL = profilePicURL
        if password is not None:
            user.password = password 

        UserManager.writeUserToData(user)
        
        return user


    def deleteUser(name:str) -> bool:
        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        initialSize = len(userList)
        userList = [user for user in userList if user.name != name]

        dataMan.writeUsers(userList)
        return initialSize > len(userList)
    
class ReviewManager():
    def createReview(movie, reviewDate:datetime.date, reviewer, usefulnessVote:int, totalVotes:int, rating:int, 
                 title:str, description:str) -> Review | None:
        review = Review(reviewDate=reviewDate, reviewer =  reviewer, 
                                usefulnessVote=usefulnessVote, totalVotes = totalVotes,
                                rating=rating, title=title, description=description)
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
    

    def updateReview(movie, review, reviewDate:datetime.date=None, reviewer=None, usefulnessVote:int=None, totalVotes:int=None, rating:int=None, 
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
        for r in reviewList:
            if (r.reviewer == review.reviewer and r.title == review.title):
                reviewList.remove(r)
        dataMan.writeReviews(movie,reviewList)
        return initialSize > len(reviewList)
    

    def getReviews(movie):
        dataMan = DataManager.getInstance()
        return dataMan.readReviews(movie)
 
class MovieManager():
    pass

# movie manager class
class MovieManager():

    def createMovie(movie:Movie):
        dataMan = DataManager.getInstance()
        #check if exists 
        for m in dataMan.getMovies():
            if m.title == movie.title:
                return None
            
        success = dataMan.createMovie(movie)
        return movie if success else None

    def readMovie(title:str):
        dataMan = DataManager.getInstance()

        try:
            return dataMan.readMovie(title)
        except FileNotFoundError:
            return None
    
    def updateMovie(movie:Movie):
        dataMan = DataManager.getInstance()
        success = dataMan.updateMovie(movie)
        return movie if success else None

    def deleteMovie(title:str):
        dataMan = DataManager.getInstance()
        return dataMan.deleteMovie(title)
        
    def getMovies():
        dataMan = DataManager.getInstance()
        return dataMan.getMovies()

class SessionManager():

    def createSession(token: str, username: str, created: datetime):
        dm = DataManager.getInstance()
        session = Session(token, username, created)
        success = dm.createSession(session)
        return session if success else None
    
    

class AdminManager():

    def readAdmin(name:str):
        dataMan = DataManager.getInstance()
        userList = dataMan.getAdmins()
        for u in userList:
            if u.name == name:
                return u 
        return None
    
    def writeUserToData(admin):
        dataMan = DataManager.getInstance()
        userList = dataMan.getAdmins()
        userList.append(admin)
        dataMan.writeAdmins(userList)

    def updateAdmin(name,admin:Admin):
        if (AdminManager.readAdmin(name) is not None):
            AdminManager.deleteAdmin(name)
            AdminManager.writeUserToData(admin)

    def deleteAdmin(name):
        dataMan = DataManager.getInstance()
        userList = dataMan.getAdmins()
        initialSize = len(userList)
        userList = [user for user in userList if user.name != name]

        dataMan.writeAdmins(userList)
        return initialSize < len(userList)
    
class WarningManager():
    
    def readWarning(reviewer:str, reviewTitle:str, reviewMovie:str):
        warningList = WarningManager.getWarnings(reviewer)
        for i in warningList:
            if i.reviewTitle == reviewTitle and i.reviewMovie == reviewMovie:
                return i

    def getWarnings(reviewer:str=None):
        dataMan = DataManager.getInstance()
        dictList = dataMan.getData(dataMan.warningFile)
        warningList = [AdminWarning(**warningdata) for warningdata in dictList]
        if reviewer is not None:
            warningList = [warning for warning in warningList if warning.reviewer == reviewer]
        return warningList 
    
    def createWarning(warning:AdminWarning):
        warningList = WarningManager.getWarnings()
        dataMan = DataManager.getInstance()
        warningList.append(warning)
        dataMan.writeData(dataMan.warningFile,  warningList)

    def deleteWarning(reviewer:str, reviewTitle:str, reviewMovie:str):
        warningList = WarningManager.getWarnings()
        dataMan = DataManager.getInstance()
        warningList = [warning for warning in warningList if reviewer != warning.reviewer or warning.reviewTitle != reviewTitle
                       or warning.reviewMovie != reviewMovie]
        dataMan.writeData(dataMan.warningFile,  warningList)

    def updateWarning(reviewTitle:str, warning:AdminWarning):
        WarningManager.deleteWarning(warning.reviewer, reviewTitle, warning.reviewMovie)
        WarningManager.createWarning(warning)