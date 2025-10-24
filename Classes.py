import datetime
class User:
    #Creating a User object with all the same fields as in the UML
    def __init__(self, name:str, email:str, profilePic:str, passwordHash:str, auth):
        self.name = name
        self.email = email
        self.profilePic = profilePic
        self.passwordHash = passwordHash
        self.auth = auth

    def updatePassword():
        pass

class Review():

    #Creating a Review object with all the same fields as in the dataset
    def __init__(self, reviewDate:datetime.date, reviewer, usefullnessVote:int, totalVotes:int, rating:int, 
                 title:str, description:str): #note to self, make reviewer a User object
        self.reviewDate = reviewDate
        self.reviewer = reviewer
        self.usefullnessVote = usefullnessVote
        self.totalVotes = totalVotes
        self.rating = rating
        self.title = title
        self.description = description
    






# def Movie:

