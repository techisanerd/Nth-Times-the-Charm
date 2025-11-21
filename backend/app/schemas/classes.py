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
class Movie():

    def __init__(self, title:str, rating:float, ratingCount:int, userReviews:int, criticReviews:int,
                 metaScore:int, genres:list, directors:list, dateReleased:datetime.date,
                 creators:list, actors:list, description:str, duration:int):

        self.title = title
        self.rating = rating
        self.ratingCount = ratingCount
        self.userReviews = userReviews
        self.criticReviews = criticReviews
        self.metaScore = metaScore
        self.genres = genres
        self.directors = directors
        self.dateReleased = dateReleased
        self.creators = creators
        self.actors = actors
        self.description = description
        self.duration = duration

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

   