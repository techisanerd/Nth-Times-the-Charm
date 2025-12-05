import pytest, bcrypt
import json

from datetime import date
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pathlib import Path
import random
from datetime import datetime, date

from managers.data_manager import DataManager
from controllers.controllers import UserController, ReviewController, MovieController, ProfilePicController
from managers.managers import UserManager, ReviewManager,MovieManager, SessionManager, AdminManager
from schemas.classes import Movie, Review,Session,ReviewCreate,User, Admin,ProfilePic
from main import app

originalMoviesFolder = " "


def testSingleton():
    """Testing that we only get one instance of DataManager"""
    dataManager1 = DataManager.getInstance()
    dataManager2 = DataManager.getInstance()
    assert dataManager1 == dataManager2

def testUserManager():
    UserManager.createUser(name="TESTUSER",email="mail@example.com", profilePicURL="https://profilepic.example.com", password="0xabcdefg")
    u = UserManager.readUser("TESTUSER")
    UserManager.deleteUser("TESTUSER")
    assert u.name == "TESTUSER" and u.email=="mail@example.com" and u.profilePicURL=="https://profilepic.example.com" and u.password == "0xabcdefg"
    assert UserManager.readUser("TESTUSER") == None

def testUpdateUser():
    UserManager.createUser(name="TESTUSER",email="mail@example.com", profilePicURL="https://profilepic.example.com", password="0xabcdefg")
    u = UserManager.readUser("TESTUSER")
    v = UserManager.updateUser(u, name="NEWTESTUSER")
    UserManager.deleteUser("NEWTESTUSER")
    assert UserManager.readUser("TESTUSER") == None and v.name == "NEWTESTUSER"

def testAdminManager():
    admin = Admin(name="TestAdmin",email="mail@example.com",profilePicURL="https://profilepic.example.com",password="0xabcdefg")
    AdminManager.writeUserToData(admin)
    u = AdminManager.readAdmin("TestAdmin")
    AdminManager.deleteAdmin("TestAdmin")
    assert u.name == "TestAdmin" and u.email=="mail@example.com" and u.profilePicURL=="https://profilepic.example.com" and u.password == "0xabcdefg"
    assert AdminManager.readAdmin("TestAdmin") == None

def testUserCreation():
    user = User(name="TestUser",email="mail@example.com",password="PlainTextPassword")
    UserController.createUser(user)
    u = UserManager.readUser("TestUser")
    assert u.name == "TestUser" and u.email == "mail@example.com" and u.profilePicURL in ProfilePicController.searchByTags()
    assert UserController.verifyPassword("TestUser","PlainTextPassword")
    UserManager.deleteUser("TestUser")

def testRepeatUsername():
    UserManager.createUser("TestUser","mail@example.com","https://profilepic.example.com","0xabcdef")
    with pytest.raises(HTTPException) as HTTPError:
        user = User(name="TestUser",email="mail@example.com",password="PlainTextPassword")
        UserController.createUser(user)
    UserManager.deleteUser("TestUser")
    assert "Username already in use" in str(HTTPError.value)

def testUpdatePasswordSuccess():
    user = User(name="TestUser",email="mail@example.com",password="oldPassword")
    UserController.createUser(user)
    user = UserManager.readUser("TestUser")
    result = UserController.updatePassword(user, "newPassword")
    assert result is True
    UserManager.deleteUser("TestUser")

def testHashChange():
    originalPassword = "MySecurePass123"
    newPassword = "MyNewSecurePass456"
    originalHash = UserController.hashPassword(originalPassword)
    newHash = UserController.hashPassword(newPassword)
    assert originalHash != newHash

def testTooShortPassword():
    with pytest.raises(HTTPException) as HTTPError:
        user = User(name="TestUser",email="mail@example.com",password="tiny")
        UserController.createUser(user)
    UserManager.deleteUser("TestUser")
    assert "Password should be 8 or more characters" in str(HTTPError.value)

def testAddReviewInvalidUser():
    with pytest.raises(HTTPException) as HTTPError:
        payload = ReviewCreate(reviewer ="Non-Existant-User",rating = 7, title = "hi", description = "hi")
        ReviewController.addReview("Joker",payload)
    assert "User not found" in str(HTTPError.value)

def testAddReviewInvalidMovie():
    with pytest.raises(HTTPException) as HTTPError:
        payload = ReviewCreate(reviewer ="TestUser",rating = 7, title = "hi", description = "hi")
        ReviewController.addReview("Non-Existant-Movie",payload)
    assert "Movie not found" in str(HTTPError.value)

def testAddReviewInvalidRating():
    user = User(name="TestUser",email="mail@example.com",password="PlainTextPassword")
    UserController.createUser(user)
    with pytest.raises(HTTPException) as HTTPError:
        payload = ReviewCreate(reviewer ="TestUser",rating = 11, title = "hi", description = "hi")
        ReviewController.addReview("Joker",payload)
    UserManager.deleteUser("TestUser")
    assert "Rating needs to be an integer between 0 and 10" in str(HTTPError.value)

def testEditReview():
    user = User(name="TestUser",email="mail@example.com",password="PlainTextPassword")
    UserController.createUser(user)
    payload = ReviewCreate(reviewer ="TestUser", rating = 7, title = "hi", description = "hi")
    ReviewController.addReview("Joker",payload)
    payload2 = ReviewCreate(reviewer ="TestUser", rating = 7, title = "NEW TITLE", description = "NEW DESCRIPTION")
    ReviewController.editReview("Joker","hi",payload2)
    
    reviewList = ReviewManager.readReview("Joker","TestUser")
    for r in reviewList:
        assert r.title == "NEW TITLE" and r.description == "NEW DESCRIPTION"
        ReviewController.removeReview("Joker","TestUser","NEW TITLE")
    UserManager.deleteUser("TestUser")

def testSearchReviews():
    user = User(name="TestUser",email="mail@example.com",password="PlainTextPassword")
    UserController.createUser(user)
    user = User(name="TestUser2",email="mail@example.com",password="PlainTextPassword")
    UserController.createUser(user)
    payload = ReviewCreate(reviewer ="TestUser",rating = 7, title = "hi", description = "hi")
    ReviewController.addReview("Joker",payload)
    payload = ReviewCreate(reviewer ="TestUser2",rating = 7, title = "no", description = "hi")
    ReviewController.addReview("Joker",payload)
    reviewList = ReviewController.searchByName("Joker","H")
    reviewTitles = []
    ReviewController.removeReview("Joker","TestUser","hi")
    ReviewController.removeReview("Joker","TestUser2","no")
    UserManager.deleteUser("TestUser")
    UserManager.deleteUser("TestUser2")
    for r in reviewList:
        reviewTitles.append(r.title)
    assert "hi" in reviewTitles and "no" not in reviewTitles

#2 tests for exporting reviews to json files
client = TestClient(app)

ReviewData = [
    Review(
        reviewDate=datetime(2023, 1, 10).strftime("%Y-%m-%d"),
        reviewer="Alice",
        usefulnessVote=5,
        totalVotes=5,
        rating=7,
        title="Review Title",
        description="Hi"
    ),
    Review(
        reviewDate=datetime(2023, 1, 11).strftime("%Y-%m-%d"),
        reviewer="Bob",
        usefulnessVote=3,
        totalVotes=5,
        rating=8,
        title="Test Title",
        description="Okay"
    )
]

movies = [
    {"title": "Test Movie", "reviews": [
        {"reviewer": "Alice", "rating": 7},
        {"reviewer": "Bob", "rating": 8}
    ]},
]

def test_export_reviews_no_fields():
    response = client.get("/export/reviews?movie_title=Test Movie")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=movie_Test Movie_reviews.json"
    assert response.json() == [
    {"movie_title": "Test Movie", "reviewDate": "2023-01-10", "reviewer": "Alice", "rating": 7, "description": "Hi"},
    {"movie_title": "Test Movie", "reviewDate": "2023-01-11", "reviewer": "Bob", "rating": 8, "description": "Okay"},
]

def test_export_reviews_with_fields():
    response = client.get("/export/reviews?movie_title=Test Movie&fields=reviewer&fields=rating")
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=movie_Test Movie_reviews.json"
    assert response.json() == [
    {
        "movie_title": "Test Movie",
        "reviewDate": "2023-01-10",
        "reviewer": "Alice",
        "rating": 7,
        "description": "Hi"
    },
    {
        "movie_title": "Test Movie",
        "reviewDate": "2023-01-11",
        "reviewer": "Bob",
        "rating": 8,
        "description": "Okay"
    }
]

#3 tests for searchMovies by tag using Equivalence Partitioning
def testSearchMoviesNoTag():
    foundMovies = MovieController.searchByTags()
    dataMan = DataManager.getInstance()
    movies = dataMan.getMovies()
    assert len(movies)==len(foundMovies)

def testSearchMoviesTag():
    foundMovies = MovieController.searchByTags(["Crime"])
    movieTitles = []
    for m in foundMovies:
        movieTitles.append(m.title)
    assert "Joker" in movieTitles and "Forrest Gump" not in movieTitles #Note: joker has crime tag while forrest gump does not

def testSearchMultipleTagsMovies():
    foundMovies = MovieController.searchByTags(["Action","Fantasy"])
    movieTitles = []
    for m in foundMovies:
        movieTitles.append(m.title)
    assert "SpiderMan No Way Home" in movieTitles and "Morbius" not in movieTitles #Note: spiderman has both tags but morbius only has one
#tests for movie manager functions

#create temp movie directory for testing 
@pytest.fixture
def tempMoviesFolder(tmp_path):
    folder = tmp_path / "tempMovies"
    folder.mkdir()
    global originalMoviesFolder 
    dm = DataManager.getInstance()
    # make original movies path available, for older testing methods
    if originalMoviesFolder == " ":
        originalMoviesFolder = dm.moviesFolder
    dm.moviesFolder = folder
    return dm


#movie object for tests
def sampleMovie():
    return Movie(
        title="Test Movie",
        rating=7.5,
        ratingCount=1500,
        userReviews="300",
        criticReviews=50,
        metaScore=65,
        genres=["Drama", "Thriller"],
        directors=["Jane Doe"],
        dateReleased=date(2020, 5, 20),
        creators=["John Smith"],
        actors=["Actor A", "Actor B"],
        description="A test movie for unit testing.",
        duration=125
    )

#test creating a movie
def testCreateMovie(tempMoviesFolder):
    dm = tempMoviesFolder
    movie = sampleMovie()

    created = dm.createMovie(movie)
    assert created is True
    folder1 = dm.moviesFolder / "Test_Movie"
    filepath = folder1 / "metadata.json"
    assert filepath.exists()

    #check to see if data is correct
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert data["title"] == "Test Movie"
    assert data["movieIMDbRating"] == 7.5
    assert data["totalRatingCount"] == 1500
    assert data["totalUserReviews"] == "300"
    assert data["totalCriticReviews"] == 50
    assert data["metaScore"] == 65
    assert data["movieGenres"] == ["Drama", "Thriller"]
    assert data["directors"] == ["Jane Doe"]
    assert data["datePublished"] == "2020-05-20"
    assert data["creators"] == ["John Smith"]
    assert data["mainStars"] == ["Actor A", "Actor B"]
    assert data["description"] == "A test movie for unit testing."
    assert data["duration"] == 125

#test for updating a movie
def testUpdateMovie(tempMoviesFolder):
    dm = tempMoviesFolder
    movie = sampleMovie()
    
    created = dm.createMovie(movie)
    assert created is True

    #modify some attributes
    movie.rating = 8.0
    movie.description = "An updated test movie description."
    movie.duration = 130

    #update movie file
    updated = dm.updateMovie(movie)
    assert updated is True
    folder1 = dm.moviesFolder / "Test_Movie"
    filepath = folder1 / "metadata.json"
    assert filepath.exists()

    #reload and verify
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    assert data["movieIMDbRating"] == 8.0
    assert data["description"] == "An updated test movie description."
    assert data["duration"] == 130

#test for updating a non-existent movie
def testUpdateNonExistentMovie(tempMoviesFolder):
    dm = tempMoviesFolder
    movie = sampleMovie()

    #try to update without creating first
    updated = dm.updateMovie(movie)
    assert updated is False

#test for deleteing a movie
def testDeleteMovie(tempMoviesFolder):
    dm = tempMoviesFolder
    movie = sampleMovie()
    
    #create movie
    assert dm.createMovie(movie) is True
    folder1 = dm.moviesFolder / "Test_Movie"
    filepath = folder1 / "metadata.json"
    assert filepath.exists()

    #delete it
    deleted = dm.deleteMovie("Test Movie")
    assert deleted is True
    assert not filepath.exists()

#test for deleting a non-existent movie
def testDeleteNonExistentMovie(tempMoviesFolder):
    dm = tempMoviesFolder

    deleted = dm.deleteMovie("NonExistent Movie")
    assert deleted is False

#test for getMovies
def testGetMovies(tempMoviesFolder):
    dm = tempMoviesFolder
    
    #create movie in folder for testing
    folder1 = dm.moviesFolder / "Test_Movie1"
    folder1.mkdir(parents=True, exist_ok=True)
    metadata1 = folder1 / "metadata.json"

    metadata1.write_text(json.dumps({
        "title": "Test Movie1",
        "movieIMDbRating": 6.5,
        "totalRatingCount": 1000,
        "totalUserReviews": "200",
        "totalCriticReviews": 30,
        "metaScore": 55,
        "movieGenres": ["Action"],
        "directors": ["Director1"],
        "datePublished": "2019-03-15",
        "creators": ["Creator1"],
        "mainStars": ["Star1", "Star2"],
        "description": "First test movie",
        "duration": 110
    }), encoding='utf-8')

    #second movie
    folder2 = dm.moviesFolder / "Test_Movie2"
    folder2.mkdir(parents=True, exist_ok=True)
    metadata2 = folder2 / "metadata.json"

    metadata2.write_text(json.dumps({
        "title": "Test Movie2",
        "movieIMDbRating": 8.2,
        "totalRatingCount": 2500,
        "totalUserReviews": "500",
        "totalCriticReviews": 80,
        "metaScore": 75,
        "movieGenres": ["Comedy"],
        "directors": ["Director1"],
        "datePublished": "2021-07-22",
        "creators": ["Creator1"],
        "mainStars": ["Star1", "Star1"],
        "description": "Second test movie",
        "duration": 95
    }), encoding='utf-8')

    movies = dm.getMovies()
    assert len(movies) == 2
    
    #check if titles match
    titles = {movie.title for movie in movies}
    assert titles == {"Test Movie1", "Test Movie2"}
    #make sure movies are movie objects
    for movie in movies:
        assert isinstance(movie, Movie)


def testReviewManager():
    dm = DataManager.getInstance()
    dm.moviesFolder = originalMoviesFolder

    review = ReviewManager.createReview(
            movie="The Avengers",
            reviewDate=datetime.now().date(),
            reviewer="TESTUSER",
            usefulnessVote=1,
            totalVotes=2,
            rating=3,
            title="test review",
            description="dest desc.")

    review = ReviewManager.updateReview(
        "The Avengers",
        review,
        title="updated title",
        description="updated desc"
    )
    assert review.title == "updated title"
    assert review.description == "updated desc"

    result = ReviewManager.deleteReview("The Avengers", review)
    assert result is True

def testDataManagerReview():
    dm = DataManager.getInstance()
    dm.moviesFolder = originalMoviesFolder

    dataMan = DataManager.getInstance()
    reviewList = dataMan.readReviews("The Avengers")
    
    original_count = len(reviewList)
    review =Review(
        reviewDate=datetime.now().date(),
        reviewer="TESTUSER",
        usefulnessVote=1,
        totalVotes=2,
        rating=3,
        title="test review",
        description="dest desc."
    )


    reviewList.append(review)
    dataMan.writeReviews("The Avengers", reviewList)

    newList = dataMan.readReviews("The Avengers")
    assert len(newList) == original_count + 1

    newList.pop()
    dataMan.writeReviews("The Avengers", newList)



def testApiGetReviews():
    
    client = TestClient(app)
    response = client.get("/Reviews/Thor Ragnarok")
    assert response.status_code == 200
    assert {
    "reviewer": "auuwws",
    "usefulnessVote": 22,
    "totalVotes": 32,
    "rating": 9,
    "title": "Ragnarok",
    "description": "The best movie for a separate character from a Marvel movie is a very funny movie even though the villain is frustrated. After you smashed Thor's hammer, you didn't do the big thing.",
    "reviewDate": "2020-10-12",
    } in response.json()

def testApiGetReview():
    
    client = TestClient(app)
    response = client.get("/Reviews/Thor Ragnarok/rag")
    assert response.status_code == 200
    assert {
    "reviewer": "auuwws",
    "usefulnessVote": 22,
    "totalVotes": 32,
    "rating": 9,
    "title": "Ragnarok",
    "description": "The best movie for a separate character from a Marvel movie is a very funny movie even though the villain is frustrated. After you smashed Thor's hammer, you didn't do the big thing.",
    "reviewDate": "2020-10-12",
    } in response.json()
    assert {
        "reviewer": "twegienk-03403",
        "usefulnessVote": 14,
        "totalVotes": 24,
        "rating": 3,
        "title": "Everything was a pun",
        "description": "I did not enjoy this film. The humor was out of place with the narrative. Everything was a set up for a pun or joke. Their home explodes and boom! Someone makes a joke.",
        "reviewDate": "2021-02-25"
    } not in response.json()

def testApiGetReviewNoInput():
    
    client = TestClient(app)
    response = client.get("/Reviews/Thor Ragnarok/")
    assert response.status_code == 200
    assert {
    "reviewer": "auuwws",
    "usefulnessVote": 22,
    "totalVotes": 32,
    "rating": 9,
    "title": "Ragnarok",
    "description": "The best movie for a separate character from a Marvel movie is a very funny movie even though the villain is frustrated. After you smashed Thor's hammer, you didn't do the big thing.",
    "reviewDate": "2020-10-12",
    } in response.json()

def testApiPostDeleteReview():
    user = User(name="TestUser",email="mail@example.com",password="PlainTextPassword")
    UserController.createUser(user)
    client = TestClient(app)
    currentDate = datetime.now().date()
    currentDate = currentDate.strftime("%Y-%m-%d")
    response = client.post("/Reviews/Thor Ragnarok/", json = {
  "reviewer": "TestUser",
  "rating": 5,
  "title": "hi",
  "description": "this is a a test for api"
})
    assert response.status_code == 200
    assert {
  "reviewer": "TestUser",
  "usefulnessVote": 0,
  "totalVotes": 0,
  "rating": 5,
  "title": "hi",
  "description": "this is a a test for api",
  "reviewDate": f"{currentDate}",
} == response.json()
    
    response = client.delete("/Reviews/Thor Ragnarok/TestUser/hi")
    assert response.status_code == 204
    UserManager.deleteUser("TestUser")

def testApiGetMovies():
    
    client = TestClient(app)
    response = client.get("/Movies")
    assert response.status_code == 200
    assert {"title": "SpiderMan No Way Home", 
            "rating": 8.3, 
            "ratingCount": 675951, 
            "userReviews": "6K", 
            "criticReviews": 396, 
            "metaScore": 71, 
            "genres": ["Action", "Adventure", "Fantasy"], 
            "directors": ["Jon Watts"],
            "dateReleased": "2021-12-17", 
            "creators": ["Chris McKenna", "Erik Sommers", "Stan Lee"], 
            "actors": ["Tom Holland", "Zendaya", "Benedict Cumberbatch"], 
            "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear, forcing Peter to discover what it truly means to be Spider-Man.", 
            "duration": 148} in response.json()
    
def testApiGetMovie():
    
    client = TestClient(app)
    response = client.get("/Movies/SpiderMan No Way Home")
    assert response.status_code == 200
    assert {"title": "SpiderMan No Way Home", 
            "rating": 8.3, 
            "ratingCount": 675951, 
            "userReviews": "6K", 
            "criticReviews": 396, 
            "metaScore": 71, 
            "genres": ["Action", "Adventure", "Fantasy"], 
            "directors": ["Jon Watts"],
            "dateReleased": "2021-12-17", 
            "creators": ["Chris McKenna", "Erik Sommers", "Stan Lee"], 
            "actors": ["Tom Holland", "Zendaya", "Benedict Cumberbatch"], 
            "description": "With Spider-Man's identity now revealed, Peter asks Doctor Strange for help. When a spell goes wrong, dangerous foes from other worlds start to appear, forcing Peter to discover what it truly means to be Spider-Man.", 
            "duration": 148} == response.json()


def randomJson(tags):
    return ["https://api.dicebear.com/9.x/shapes/svg"]

def testApiUser(monkeypatch):
    monkeypatch.setattr(ProfilePicController,"searchByTags", randomJson)
    client = TestClient(app)
    response = client.post("/Users", json = {
  "name": "Test",
  "email": "test.Email",
  "password": "PlainTextPassword"
})
    assert response.status_code == 200
    assert {"name": "Test", "profilePicURL" : "https://api.dicebear.com/9.x/shapes/svg"} == response.json()
    response = client.get("/Users")
    assert response.status_code == 200
    assert {"name": "Test", "profilePicURL" : "https://api.dicebear.com/9.x/shapes/svg"} in response.json()
    response = client.get("/Users/Test")
    assert response.status_code == 200
    assert {"name": "Test", "profilePicURL" : "https://api.dicebear.com/9.x/shapes/svg"} == response.json()
    UserManager.deleteUser("Test")

#session class testing

#test session
def testSession():
    now = datetime.now()
    s = Session("abcd1234", "bob", now)

    assert s.token == "abcd1234"
    assert s.username == "bob"
    assert s.created == now

#test to dict
def testSessionToDict():
    now = datetime(2024, 6, 2, 12, 30, 0)
    s = Session("abcd1234", "bob", now)

    d = s.to_dict()

    assert d["token"] == "abcd1234"
    assert d["username"] == "bob"
    assert d["created"] == "2024-06-02T12:30:00"

#test from dict
def testSessionFromDict():
    data = {
        "token": "abcd1234",
        "username": "bob",
        "created": "2024-06-02T12:30:00"
    }

    s = Session.from_dict(data)

    assert s.token == "abcd1234"
    assert s.username == "bob"
    assert s.created == datetime(2024, 6, 2, 12, 30, 0)

#temp folder for session testing
@pytest.fixture
def tempSessionFolder(tmp_path):
    folder = tmp_path / "tempData"
    folder.mkdir()

    dm = DataManager.getInstance()
    dm.dataFolder = folder

    return dm

def testLoadSession(tempSessionFolder):
    dm = tempSessionFolder
    
    sessions = dm._loadSession()
    assert sessions == []

    data = [{
        "token": "abcd1234",
        "username": "bob",
        "created": "2024-06-02T12:30:00"
    }]
    
    sessionFile = dm.dataFolder / "sessions.json"
    sessionFile.write_text(json.dumps(data), encoding="utf-8")

    sessions = dm._loadSession()
    assert len(sessions) == 1
    assert sessions[0].token == "abcd1234"
    assert sessions[0].username == "bob"
    assert sessions[0].created == datetime(2024, 6, 2, 12, 30, 0)

def testWriteSession(tempSessionFolder):
    dm = tempSessionFolder

    sess = Session(
        token="xyz999",
        username="alice",
        created=datetime(2024, 5, 10, 9, 0, 0)
    )
    dm._writeSession([sess])

    sessionFile = dm.dataFolder / "sessions.json"
    assert sessionFile.exists()
    data = json.loads(sessionFile.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["token"] == "xyz999"
    assert data[0]["username"] == "alice"
    assert data[0]["created"] == "2024-05-10T09:00:00"

def testCreateSession(tempSessionFolder):
    dm = tempSessionFolder
    s1 = Session("token123", "bob", datetime.now())
    
    created = dm.createSession(s1)
    assert created is True

    sessions = dm._loadSession()
    assert len(sessions) == 1
    assert sessions[0].token == "token123"

    s2 = Session("token123", "bob", datetime.now())
    created2 = dm.createSession(s2)
    assert created2 is False

    sessions = dm._loadSession()
    assert len(sessions) == 1

def testGetSession(tempSessionFolder):
    dm = tempSessionFolder
    s = Session("token123", "bob", datetime(2024, 6, 1, 10, 0, 0))
    dm.createSession(s)
    found = dm.getSession("token123")

    assert found is not None
    assert found.token == "token123"
    assert found.username == "bob"
    assert found.created == datetime(2024, 6, 1, 10, 0, 0)

def testGetSessionNoFile(tempSessionFolder):
    dm = tempSessionFolder

    result = dm.getSession("beeboop")
    assert result is None

def testDeleteSession(tempSessionFolder):
    dm = tempSessionFolder
    s1 = Session("token123", "bob", datetime.now())
    s2 = Session("token456", "randal", datetime.now())
    dm.createSession(s1)
    dm.createSession(s2)

    deleted = dm.deleteSession("token123")
    assert deleted is True

    remaining = dm._loadSession()
    assert len(remaining) == 1
    assert remaining[0].token == "token456"

def testDeleteSessionNotFound(tempSessionFolder):
    dm = tempSessionFolder
    s = Session("token123", "bob", datetime.now())
    dm.createSession(s)

    deleted = dm.deleteSession("wahooooo")
    assert deleted is False

    sessions = dm._loadSession()
    assert len(sessions) == 1
    assert sessions[0].token == "token123"

def testGetSessionCorruptFile(tempSessionFolder):
    dm = tempSessionFolder
    
    badFile = dm.dataFolder / "sessions.json"
    badFile.write_text("{.. wrong!", encoding="utf-8")

    #loading invalid session should return empty list
    sessions = dm._loadSession()
    assert sessions == []

def testSessionManagerCreate(tempSessionFolder):
    dm = tempSessionFolder  
    t = datetime.now()
    session = SessionManager.createSession("abc123", "bob", t)
    assert session is not None
    assert session.token == "abc123"
    assert session.username == "bob"
    assert session.created == t

    stored = dm.getSession("abc123")
    assert stored is not None
    assert stored.token == "abc123"
    assert stored.username == "bob"
    assert stored.created == t

def testSessionManagerPreventDuplicate(tempSessionFolder):
    dm = tempSessionFolder
    t = datetime.now()
    SessionManager.createSession("abc123", "bob", t)
    duplicate = SessionManager.createSession("abc123", "bob", t)
    assert duplicate is None

def testProfilePicSearchTags():
    assert ["https://api.dicebear.com/9.x/icons/svg"] == ProfilePicController.searchByTags(["Simple","Objects"])

def testProfilePic():
    assert "https://api.dicebear.com/9.x/icons/svg" == ProfilePicController.getProfilePic(["Simple","Objects"])

@pytest.fixture
def tempProfilePicFolder(tmp_path):
    folder = tmp_path / "tempProfilePics.json"
    data = [
    {
        "profilePicURL": "testICONS",
        "themes": ["Simple","Objects","Pastel"]
    },
    {
        "profilePicURL": "testADVENTURE",
        "themes": ["People","Colorful","Fantasy"]
    }]
    folder.write_text(json.dumps(data), encoding="utf-8")
    dm = DataManager.getInstance()
    dm.profilePicsFile = folder
    return dm

def testGetProfilePics(tempProfilePicFolder):
    pics = [ProfilePic(profilePicURL="testICONS",themes = ["Simple","Objects","Pastel"]),
            ProfilePic(profilePicURL="testADVENTURE", themes = ["People","Colorful","Fantasy"])] 
    assert pics == tempProfilePicFolder.getProfilePics()

def testGetAllTagsProfilePic():
    assert {"Simple","Objects","Pastel", "People","Colorful","Fantasy"} == ProfilePicController.getAllTags()

#sortMovies tests
def testSortMoviesByRatingAsc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="rating", order="asc")
    
    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].rating <= sortedMovies[i + 1].rating

def testSortMoviesByRatingDesc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="rating", order="desc")

    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].rating >= sortedMovies[i + 1].rating

def testSortMoviesByReleaseDateAsc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="dateReleased", order="asc")
    
    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].dateReleased <= sortedMovies[i + 1].dateReleased

def testSortMoviesByReleaseDateDesc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="dateReleased", order="desc")

    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].dateReleased >= sortedMovies[i + 1].dateReleased

def testSortMoviesByTitleAsc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="title", order="asc")
    
    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].title.lower() <= sortedMovies[i + 1].title.lower()

def testSortMoviesByTitleDesc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="title", order="desc")

    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].title.lower() >= sortedMovies[i + 1].title.lower()

def testSortMoviesByMetaScoreAsc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="metaScore", order="asc")
    
    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].metaScore <= sortedMovies[i + 1].metaScore

def testSortMoviesByMetaScoreDesc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="metaScore", order="desc")

    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].metaScore >= sortedMovies[i + 1].metaScore

def testSortMoviesByRatingCountAsc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="ratingCount", order="asc")
    
    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].ratingCount <= sortedMovies[i + 1].ratingCount

def testSortMoviesByRatingCountDesc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="ratingCount", order="desc")

    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].ratingCount >= sortedMovies[i + 1].ratingCount

def testSortMoviesByDurationAsc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="duration", order="asc")
    
    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].duration <= sortedMovies[i + 1].duration

def testSortMoviesByDurationDesc():
    movies = MovieManager.getMovies()
    sortedMovies = MovieController.sortMovies(movies, sortBy="duration", order="desc")

    for i in range(len(sortedMovies) - 1):
        assert sortedMovies[i].duration >= sortedMovies[i + 1].duration

def testSortMoviesInvalidSortBy():
    movies = MovieManager.getMovies()
    
    with pytest.raises(ValueError) as excinfo:
        MovieController.sortMovies(movies, sortBy="invalidField", order="asc")

    assert "Invalid sortBy value" in str(excinfo.value)

def testSortMoviesInvalidOrder():
    movies = MovieManager.getMovies()
    
    with pytest.raises(ValueError) as excinfo:
        MovieController.sortMovies(movies, sortBy="rating", order="invalidOrder")

    assert "Order must be 'asc' or 'desc'" in str(excinfo.value)
 
#sortReview tests
def testSortReviewsByRatingAsc():
    reviews = ReviewManager.getReviews("Joker")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="rating", order="asc")
    
    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].rating <= sortedReviews[i + 1].rating

def testSortReviewsByRatingDesc():
    reviews = ReviewManager.getReviews("Joker")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="rating", order="desc")

    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].rating >= sortedReviews[i + 1].rating

def testSortReviewsByReviewDateAsc():
    reviews = ReviewManager.getReviews("Morbius")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="reviewDate", order="asc")
    
    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].reviewDate <= sortedReviews[i + 1].reviewDate

def testSortReviewsByReviewDateDesc():
    reviews = ReviewManager.getReviews("Morbius")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="reviewDate", order="desc")

    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].reviewDate >= sortedReviews[i + 1].reviewDate

def testSortReviewsByTitleAsc():
    reviews = ReviewManager.getReviews("Pulp Fiction")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="title", order="asc")
    
    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].title.lower() <= sortedReviews[i + 1].title.lower()

def testSortReviewsByTitleDesc():
    reviews = ReviewManager.getReviews("Pulp Fiction")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="title", order="desc")

    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].title.lower() >= sortedReviews[i + 1].title.lower()

def testSortReviewsByUsefulnessVoteAsc():
    reviews = ReviewManager.getReviews("Forrest Gump")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="usefulnessVote", order="asc")
    
    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].usefulnessVote <= sortedReviews[i + 1].usefulnessVote

def testSortReviewsByUsefulnessVoteDesc():
    reviews = ReviewManager.getReviews("Forrest Gump")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="usefulnessVote", order="desc")

    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].usefulnessVote >= sortedReviews[i + 1].usefulnessVote

def testSortReviewsByTotalVotesAsc():
    reviews = ReviewManager.getReviews("The Dark Knight")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="totalVotes", order="asc")
    
    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].totalVotes <= sortedReviews[i + 1].totalVotes

def testSortReviewsByTotalVotesDesc():
    reviews = ReviewManager.getReviews("The Dark Knight")
    sortedReviews = ReviewController.sortReviews(reviews, sortBy="totalVotes", order="desc")

    for i in range(len(sortedReviews) - 1):
        assert sortedReviews[i].totalVotes >= sortedReviews[i + 1].totalVotes

def testSortReviewsInvalidSortBy():
    reviews = ReviewManager.getReviews("Thor Ragnarok")
    
    with pytest.raises(ValueError) as excinfo:
        ReviewController.sortReviews(reviews, sortBy="invalidField", order="asc")

    assert "Invalid sortBy value" in str(excinfo.value)

def testSortReviewsInvalidOrder():
    reviews = ReviewManager.getReviews("Thor Ragnarok")
    
    with pytest.raises(ValueError) as excinfo:
        ReviewController.sortReviews(reviews, sortBy="rating", order="invalidOrder")

    assert "Order must be 'asc' or 'desc'" in str(excinfo.value)

def testDeleteAccount():
    user = User(name="TestUser",email="delete@gmail.com", password="kittens123")
    UserController.createUser(user)

    user = UserManager.readUser("TestUser")
    assert user is not None
    assert user.name == "TestUser"

    result = UserController.deleteAccount("TestUser")
    assert result is True

    user = UserManager.readUser("TestUser")
    assert user is None

def testDeleteAccountNotFound():
    with pytest.raises(ValueError) as excinfo:
        UserController.deleteAccount("NonExistentUser")
    assert "User not found" in str(excinfo.value)
