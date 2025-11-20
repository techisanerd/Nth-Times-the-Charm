import datetime
from pydantic import BaseModel
class User():
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
    def __init__(self, reviewDate:datetime.date, reviewer, usefulnessVote:int, totalVotes:int, rating:int, 
                 title:str, description:str): #note to self, make reviewer a User object
        self.reviewDate = reviewDate
        self.reviewer = reviewer
        self.usefulnessVote = usefulnessVote
        self.totalVotes = totalVotes
        self.rating = rating
        self.title = title
        self.description = description
    
    
    

# def Movie:
class Movie(BaseModel):
    title:str
    rating:float
    ratingCount:int
    userReviews:str
    criticReviews:int
    metaScore:int
    genres:list
    directors:list
    dateReleased:datetime.date
    creators:list
    actors:list
    description:str
    duration:int



    @classmethod
    def from_json(cls, data:dict):
        return cls(
            title=data['title'],
            rating=data['movieIMDbRating'],
            ratingCount=data['totalRatingCount'],
            userReviews=data['totalUserReviews'],
            criticReviews=data['totalCriticReviews'],
            metaScore=data['metaScore'],
            genres=data['movieGenres'],
            directors=data['directors'],
            dateReleased=datetime.datetime.strptime(data['datePublished'], '%Y-%m-%d').date(),
            creators=data['creators'],
            actors=data['mainStars'],
            description=data['description'],
            duration=data['duration']
        )
    
class MovieCreate(BaseModel):

    title:str
    genres:list
    directors:list
    dateReleased:datetime.date
    creators:list
    actors:list
    description:str
    duration:int