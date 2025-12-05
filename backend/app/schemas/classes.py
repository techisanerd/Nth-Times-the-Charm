import datetime, uuid
from pydantic import BaseModel
import hashlib

class User(BaseModel):
    name:str
    email:str
    profilePicURL:str = None
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

class AdminWarning(BaseModel):
    reviewer:str
    admin:str
    reviewTitle:str
    reviewMovie:str
    warningDescription:str
    
class Reply(BaseModel):
    reviewAuthor: str
    reviewTitle: str
    replyAuthor: str
    replyText: str
    replyDate: datetime.date

class ReplyCreate(BaseModel):
    replyAuthor: str
    replyText: str

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

    # represents a user login
class LoginRequest(BaseModel):
    username: str
    password: str


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

    # Check if the session token is valid
    def is_valid(self, expiration_minutes: int = 30) -> bool:
        now = datetime.datetime.now()
        return (now - self.created).total_seconds() < expiration_minutes * 60

    # Generate a new session token
    @staticmethod
    def generate_token(username: str) -> str:
        return hashlib.sha256(f"{username}{datetime.datetime.now()}".encode()).hexdigest()


class Report(BaseModel):
    reportId: str
    movie: str
    reviewer: str
    reviewTitle: str
    reporter: str
    reason: str
    reportDate: datetime.datetime



    

class ProfilePic(BaseModel):
    profilePicURL:str
    themes:list[str]

   
   
