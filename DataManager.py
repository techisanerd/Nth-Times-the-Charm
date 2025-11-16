from Classes import *
from pathlib import Path

import json, os, csv

class DataManager():
    __instance = None
    #moviesFolder is the path to the Movies folder
    moviesFolder = Path(__file__).resolve().parent / "Movies"
    #path to json file storing user data 
    userFile = ".\\users.json"
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

    def readReview(self, filename:str):
        filepath = self.moviesFolder / filename
        with open(filepath, 'r', encoding='utf-8') as file:
            data = csv.load(file)
            return Review.from_csv(data)
    
    def updateReview():
        pass

    def deleteReview():
        pass

    def createMovie():
        pass

    def readMovie(self, filename:str):
        filepath = self.moviesFolder / filename
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return Movie.from_json(data)
    
    def updateMovie():
        pass

    def deleteMovie():
        pass
    
    
    def getUsers(self):
        dictList = [] 
        if os.path.exists(self.userFile):
            with open(self.userFile, "r") as f:
                dictList = json.load(f)

        #deserialize: create new object for each user in the json dictionary
        userList = [User(**userData) for userData in dictList]
        return userList


    def writeUsers(self, users:list[User]):
        with open(self.userFile, "w") as file:
            #store as a json: each user is converted to a dict(ionary) of its attributes, within the list
            json.dump([user.__dict__ for user in users], file, indent=4)

    def createReport():
        pass

    # get a user's session
    def getSession():
        pass
    
    def deleteReport():
        pass
    
    # get list of all movie objects in database
    def getMovies(self) -> list:
        movies = []
        for file in self.moviesFolder.glob('*.json'):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                movies.append(Movie.from_json(data))
        return movies

    # get list of all reviews in database
    def getReviews(self) -> list:
        reviews = []
        for file in self.moviesFolder.glob():
            with open(file, 'r', encoding='utf-8') as f:
                data = csv.load(f)
                reviews.append(Review.from_csv(data))
        return reviews

    # get list of all users in database
        # get all reports in database
    def getReports():
        pass

