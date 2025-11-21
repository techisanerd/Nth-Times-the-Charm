from Classes import *
from pathlib import Path
from datetime import datetime
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
    

    def readReviews(self, movie):
        #todo factor out this string
        with open('.\\Movies\\' + movie + '\\movieReviews.csv', mode ='r', newline='', encoding='utf8')as file:
            reviewList = []
            for lines in csv.reader(file):
                if lines[0].startswith("Date of Review"):# skips the first (header) line of reviews
                    continue
                reviewDate = datetime.strptime(lines[0], "%d %B %Y").date()
                reviewer = lines[1]
                usefulnessVote = int(lines[2])
                totalVotes = int(lines[3])
                try:
                    rating = int(lines[4])
                except ValueError: # the data is messy and doesn't show this sometimes 
                    rating = -1
                title = lines[5]
                description = lines[6]

                review = Review(reviewDate, reviewer, usefulnessVote, totalVotes, rating, title, description)
                reviewList.append(review)
            return reviewList


    def writeReviews(self, movie, reviewList):
        with open('.\\Movies\\' + movie + '\\movieReviews.csv', mode ='w', newline='', encoding='utf8') as file:
            writer = csv.writer(file)

            for review in reviewList:
                date = datetime.strftime(review.reviewDate, "%d %B %Y")
                l = [date, review.reviewer, str(review.usefulnessVote), str(review.totalVotes), str(review.rating), review.title, review.description]
                writer.writerow(l) 
        

    def createMovie(self, movie: Movie) -> bool:
        filepath = f"{movie.title.replace(' ', '_')}.json"
        filepath = self.moviesFolder / filepath

        # prevent overwriting exisiting movie files
        if filepath.exists():
            return False
        
        data = {
            "title": movie.title,
            "movieIMDbRating": movie.rating,
            "totalRatingCount": movie.ratingCount,
            "totalUserReviews": movie.userReviews,
            "totalCriticReviews": movie.criticReviews,
            "metaScore": movie.metaScore,
            "movieGenres": movie.genres,
            "directors": movie.directors,
            "datePublished": movie.dateReleased.strftime("%Y-%m-%d"),
            "creators": movie.creators,
            "mainStars": movie.actors,
            "description": movie.description,
            "duration": movie.duration
        }

        # write movie data to json file
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)   

        return True  

    def readMovie(self, filename:str):
        filepath = self.moviesFolder / filename
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return Movie.from_json(data)
    
    def updateMovie(self, movie:Movie) -> bool:
        filename = f"{movie.title.replace(' ', '_')}.json"
        filepath = self.moviesFolder / filename

        # check if movie exists
        if not filepath.exists():
            return False
        
        # convert to csv
        data = {
            "title": movie.title,
            "movieIMDbRating": movie.rating,
            "totalRatingCount": movie.ratingCount,
            "totalUserReviews": movie.userReviews,
            "totalCriticReviews": movie.criticReviews,
            "metaScore": movie.metaScore,
            "movieGenres": movie.genres,
            "directors": movie.directors,
            "datePublished": movie.dateReleased.strftime("%Y-%m-%d"),
            "creators": movie.creators,
            "mainStars": movie.actors,
            "description": movie.description,
            "duration": movie.duration
        }

        # overwrite existing file with updated data
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)

        return True

    def deleteMovie(self, title: str) -> bool:
        filename = f"{title.replace(' ', '_')}.json"
        filepath = self.moviesFolder / filename

        # check if exists
        if not filepath.exists():
            return False
        
        #delete file
        filepath.unlink()
        return True
    
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

        #look for subfolder inside movies folder
        for folder in self.moviesFolder.iterdir():
            if folder.is_dir():
                metadataFile = folder / "metadata.json"
                if metadataFile.exists():
                    with open(metadataFile, 'r', encoding='utf-8') as f:
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


