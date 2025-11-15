from DataManager import DataManager
from Classes import User, Movie, Review

class UserManager():
    def readUser(name:str):
        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        for u in userList:
            if u.name == name:
                return u 
        #if user does not exist return nothing
        return None
    

    def getUsers():
        dataMan = DataManager.getInstance()
        return dataMan.getUsers()


    def createUser(name:str, email:str, profilePic:str, passwordHash:str, auth=None):
        #ensure no duplicates
        if UserManager.readUser(name) is not None:
            return None            

        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        user = User(name, email, profilePic, passwordHash, auth)
        userList.append(user)
        dataMan.writeUsers(userList)
        return user


    def updateUser(user, name:str=None, email:str=None, profilePic:str=None, passwordHash:str=None, auth=None):
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


    def deleteUser(name:str):
        dataMan = DataManager.getInstance()
        userList = dataMan.getUsers()
        initialSize = len(userList)
        userList = [user for user in userList if user.name != name]

        dataMan.writeUsers(userList)
        return initialSize < len(userList)
    
class ReviewManager():
    pass