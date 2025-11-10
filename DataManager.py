from Classes import *
from pathlib import Path

import json, os

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

    def createUser(self, name:str, email:str, profilePic:str, passwordHash:str, auth):
        usr = User(name, email, profilePic, passwordHash, auth)

        userList = [] 
        if os.path.exists(self.userFile):
            try:
                with open(self.userFile, "r") as f:
                    userList = json.load(f)
            except:
                print("something has gone wrong reading json file.")

        userList.append(usr)
    
        with open(self.userFile, "w") as file:
            #store as a json: each user is converted to a dict(ionary) of its attributes, within the list
            json.dump([user.__dict__ for user in userList], file, indent=4)

    # refactor candidate: move to usermanager
    def readUser(self, name:str):
        userList = self.getUsers()
        for u in userList:
            if u.name == name:
                return u 

        #if user does not exist return nothing
        return None


    
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
    def getReviews():
        pass

    # get list of all users in database
    def getUsers(self):
        dictList = [] 
        if os.path.exists(self.userFile):
            with open(".\\users.json", "r") as f:
                dictList = json.load(f)

        #deserialize: create new object for each user in the json dictionary
        userList = [User(**userData) for userData in dictList]
        return userList

    # get all reports in database
    def getReports():
        pass

# temp
if __name__ == "__main__":
    inst = DataManager.getInstance()
    inst.createUser("dorothy", "asdf","link goes here", "hash", None)
    print(inst.readUser("dorothy"))