from Classes import *
from pathlib import Path

class DataManager():
    __instance = None
    #moviesFolder is the path to the Movies folder
    moviesFolder = Path(__file__).resolve().parent / "Movies"

    #init raises an error since this is a singleton
    def __init__(self):
        raise RuntimeError("This Object cannot be made with this function, please use getInstance")
    
    #this is how to instantiate the class
    @classmethod
    def getInstance(cls):
        if cls.__instance == None:
            cls.__instance = cls.__new__(cls)
        return cls.__instance

    def createReview():
        pass

    def readReview():
        pass
    
    def updateReview():
        pass

    def deleteReview():
        pass

    def createMovie():
        pass

    def readMovie():
        pass
    
    def updateMovie():
        pass

    def deleteMovie():
        pass

    def createUser():
        pass

    def readUser():
        pass
    
    def updateUser():
        pass

    def deleteUser():
        pass

    def createSession():
        pass

    def deleteSession():
        pass

    def createReport():
        pass

    # get a user's session
    def getSession():
        pass
    
    def deleteReport():
        pass
    
    # get list of all movie objects in database
    def getMovies():
        pass

    # get list of all reviews in database
    def getReviews():
        pass

    # get list of all users in database
    def getMovies():
        pass

    # get all reports in database
    def getReports():
        pass

