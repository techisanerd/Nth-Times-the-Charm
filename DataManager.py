from Classes import *
from pathlib import Path

import json, datetime

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

    def readMovie(self, filename:str):
        filepath = self.moviesFolder / filename
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return Movie.from_json(data)
    
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
        for file in self.reviewFolder.glob():
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                reviews.append(Review.from_json(data))
        return reviews

    # get list of all users in database
    def getMovies():
        pass

    # get all reports in database
    def getReports():
        pass

