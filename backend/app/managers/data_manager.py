from schemas.classes import Review, Movie, User, Session, Admin, Reply
from pathlib import Path
from datetime import datetime
import shutil
import json, os, csv

class DataManager():
    __instance = None

    dataFolder = Path(__file__).resolve().parent.parent / "data"
    moviesFolder = dataFolder / "Movies"
    userFile = dataFolder / "users.json"
    adminFile = dataFolder / "admins.json"
    # this one is different as the path will need the movie name added in
    reviewFile = "movieReviews.csv"
    #init raises an error since this is a singleton
    def __init__(self):
        raise RuntimeError("This Object cannot be made with this function, please use getInstance")
    
    def resetPath():
        dataFolder = Path(__file__).resolve().parent.parent / "data"


    @classmethod
    def getInstance(cls):
        if cls.__instance == None:
            cls.__instance = cls.__new__(cls)
        return cls.__instance
    

    def readReviews(self, movie):
        with open(self.moviesFolder / movie / self.reviewFile, mode ='r', newline='', encoding='utf8')as file:
            reviewList = []
            for lines in csv.reader(file):
                if lines[0].startswith("Date of Review"):# skips the first (header) line of reviews
                    continue
                if len(lines) < 3:
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
                reply = lines[7] if len(lines) > 7 else None

                review = Review(reviewDate=reviewDate, reviewer =  reviewer, 
                                usefulnessVote=usefulnessVote, totalVotes = totalVotes,
                                rating=rating, title=title, description=description, reply=reply)
                reviewList.append(review)
            return reviewList


    def writeReviews(self, movie, reviewList):
        with open(self.moviesFolder / movie / self.reviewFile, mode ='w', newline='', encoding='utf8') as file:
            writer = csv.writer(file)

            for review in reviewList:
                date = datetime.strftime(review.reviewDate, "%d %B %Y")
                l = [date, review.reviewer, str(review.usefulnessVote), str(review.totalVotes), str(review.rating), review.title, review.description]
                writer.writerow(l) 
    

    def readReplies(self, movie):
        path = self.moviesFolder / movie / "reviewReplies.json"
        if not path.exists():
            return []

        with open(path, "r", encoding="utf8") as f:
            reply_dicts = json.load(f)

        from schemas.classes import Reply
        return [Reply(**rd) for rd in reply_dicts]


    def writeReplies(self, movie, replies):
        path = self.moviesFolder / movie / "reviewReplies.json"

        with open(path, "w", encoding="utf8") as f:
            json.dump([r.dict() for r in replies], f, indent=4)


    def createMovie(self, movie: Movie) -> bool:
        filepath = f"{movie.title.replace(' ', '_')}"
        folder= self.moviesFolder / filepath
        folder.mkdir(parents=True, exist_ok=True)
        filepath = folder / "metadata.json"
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
        filepath = self.moviesFolder / filename / "metadata.json"
        with open(filepath, 'r', encoding='utf-8') as file:
            data = json.load(file)
            return Movie.from_json(data)
    
    def updateMovie(self, movie:Movie) -> bool:
        filename = f"{movie.title.replace(' ', '_')}"
        filepath = self.moviesFolder / filename / "metadata.json"

        # check if movie exists
        if not filepath.exists():
            return False
        
        # convert to json
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
        filename = f"{title.replace(' ', '_')}"
        filepath = self.moviesFolder / filename

        # check if exists
        if not filepath.exists():
            return False
        
        #delete file
        shutil.rmtree(filepath)
        return True
    
    def getUsersData(self, filepath):
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                return json.load(f)
    
    def getUsers(self):
        dictList = [] 
        dictList = self.getUsersData(self.userFile)

        #deserialize: create new object for each user in the json dictionary
        userList = [User(**userData) for userData in dictList]
        return userList
    
    def getAdmins(self):
        dictList = [] 
        dictList = self.getUsersData(self.adminFile)
        adminList = [Admin(**adminData) for adminData in dictList]
        return adminList


    def writeUsers(self, users:list[User]):
        with open(self.userFile, "w") as file:
            #store as a json: each user is converted to a dict(ionary) of its attributes, within the list
            json.dump([user.__dict__ for user in users], file, indent=4)

    def writeAdmins(self, admins:list[Admin]):
        with open(self.adminFile, "w") as file:
            json.dump([admin.__dict__ for admin in admins], file, indent=4)

    def createReport():
        pass

    #session functions

    def _loadSession(self) -> list:
        sessionFile = self.dataFolder / "sessions.json"

        if not sessionFile.exists():
            return []

        try:
            with open(sessionFile, 'r', encoding="utf-8") as f:
                dictList = json.load(f)
                return [Session.from_dict(s) for s in dictList]
        except (json.JSONDecodeError, TypeError, ValueError):
                #treat invalid file as empty session list
            return []
        
    def _writeSession(self, session: list):
        sessionFile = self.dataFolder / "sessions.json"

        with open(sessionFile, 'w', encoding="utf-8") as f:
            json.dump([s.to_dict() for s in session], f, indent=4)

    def createSession(self, session: Session) -> bool:
        sessions = self._loadSession()

        for s in sessions:
            if s.token == session.token:
                return False
            
        sessions.append(session)
        self._writeSession(sessions)
        return True
    
       
    def deleteSession(self, token: str) -> bool:
        sessions = self._loadSession()
        initialCount = len(sessions)

        sessions = [s for s in sessions if s.token != token]

        if len(sessions) == initialCount:
            return False

        self._writeSession(sessions)
        return True

    def getSession(self, token: str):
        sessions = self._loadSession()

        for s in sessions:
            if s.token == token:
                return s

        return None    
    
    def deleteReport():
        pass
    

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


        # get all reports in database
    def getReports():
        pass

