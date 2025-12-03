import datetime
from pydantic import BaseModel
class User(BaseModel):
    name:str
    email:str
    profilePicURL:str
    password:str


class UserView(BaseModel):
    name:str
    profilePicURL:str

class Admin(User):
    pass

class Review(BaseModel):
    reviewDate:datetime.date
    reviewer:str
    usefulnessVote:int
    totalVotes:int
    rating:int
    title:str
    description:str

class ReviewCreate(BaseModel):
    reviewer:str
    rating:int
    title:str
    description:str
    

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
    
# session class
# represents a logged in user session
class Session:

    def __init__(self, token: str, username: str, created: datetime.datetime):
        self.token = token
        self.username = username
        self.created = created
    
    #to_dict to convert session object to be json friendly
    def to_dict(self) -> dict:
        return{
            'token': self.token,
            'username': self.username,
            'created': self.created.isoformat()
        }
    
    #from_dict to convert back to session object from json
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            token=data['token'],
            username=data['username'],
            created=datetime.datetime.fromisoformat(data['created'])
        )

    

class ProfilePic(BaseModel):
    profilePicURL:str
    themes:list[str]

   
   
