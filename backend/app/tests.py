import pytest, bcrypt
import json

from datetime import date
from fastapi import HTTPException
from fastapi.testclient import TestClient
from pathlib import Path
import random
from datetime import datetime, date
from managers.data_manager import DataManager
from controllers.controllers import UserController, ReviewController, MovieController, ProfilePicController, AdminReviewController
from managers.managers import UserManager, ReviewManager,MovieManager, SessionManager, AdminManager, WarningManager, ReportManager
from schemas.classes import Movie, Review,Session,ReviewCreate,User, Admin, Report, ProfilePic, AdminWarning
from main import app

originalMoviesFolder = " "


@pytest.fixture
def tempUserFolder(tmp_path):
    folder = tmp_path / "tempusers.json"
    data = [{"name":"TestUser1",
    "email": "Test@Email",
    "profilePicURL": "https://api.dicebear.com/9.x/shapes/svg",
    "password":"0xABCDEF"}]
    folder.write_text(json.dumps(data), encoding="utf-8")
    dm = DataManager.getInstance()
    dm.userFile = folder
    return dm

@pytest.fixture
def tempAdminFolder(tmp_path):
    folder = tmp_path / "tempadmins.json"
    data = [{"name":"TestAdmin1",
    "email": "Test@Email",
    "profilePicURL": "https://api.dicebear.com/9.x/shapes/svg",
    "password":"0xABCDEF"}]
    folder.write_text(json.dumps(data), encoding="utf-8")
    dm = DataManager.getInstance()
    dm.adminFile = folder
    return dm

@pytest.fixture
def tempMoviesFileWithMovie(tempMoviesFolder):
    folder = tempMoviesFolder.moviesFolder / "Test Movie" 
    folder.mkdir()
    tempMoviesFile = folder / "metadata.json"
    data = {"title": "Test Movie",
        "movieIMDbRating":7.5,
        "totalRatingCount":1500,
        "totalUserReviews":"300",
        "totalCriticReviews":50,
        "metaScore":65,
        "movieGenres":["Drama", "Thriller"],
        "directors":["Jane Doe"],
        "datePublished": "2017-11-03",
        "creators": ["John Smith"],
        "mainStars":["Actor A", "Actor B"],
        "description":"A test movie for unit testing.",
        "duration":125}
    tempMoviesFile.write_text(json.dumps(data),encoding="utf-8")
    folder2 = tempMoviesFolder.moviesFolder / "Test Movie 2" 
    folder2.mkdir()
    tempMoviesFile2 = folder2 / "metadata.json"
    data2 = {"title": "Test Movie 2",
        "movieIMDbRating":8.5,
        "totalRatingCount":1600,
        "totalUserReviews":"350",
        "totalCriticReviews":30,
        "metaScore":67,
        "movieGenres":["Drama", "Crime", "Humor"],
        "directors":["Jane Doe"],
        "datePublished": "2017-11-03",
        "creators": ["John Smith"],
        "mainStars":["Actor A", "Actor B"],
        "description":"A second test movie for unit testing.",
        "duration":125}
    tempMoviesFile2.write_text(json.dumps(data2),encoding="utf-8")
    dm = DataManager.getInstance()
    dm.moviesFolder = tempMoviesFolder.moviesFolder
    return folder

@pytest.fixture
def tempReviewFolder(tempMoviesFileWithMovie):
    folder = tempMoviesFileWithMovie /"testReviews.csv"
    folder.write_text("4 December 2025,TestUser1,0,1,6,Title,\"Test Description\"\n4 December 2025,TestUser1,0,1,6,Title2,\"Test Description for second review\"", encoding="utf-8")
    dm = DataManager.getInstance()
    dm.reviewFile = folder
    return dm

def testSingleton():
    """Testing that we only get one instance of DataManager"""
    dataManager1 = DataManager.getInstance()
    dataManager2 = DataManager.getInstance()
    assert dataManager1 == dataManager2

def testUserManager(tempUserFolder):
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

def testAdminManager(tempAdminFolder):
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

def testTakedownReview(tempAdminFolder, tempUserFolder, tempMoviesFileWithMovie,tempReviewFolder):
    assert len(ReviewController.getReviewsByTitle("Test Movie", "TestUser1", "Title")) == 1
    AdminReviewController.takedownReview("TestAdmin1", "Test Movie", "TestUser1", "Title", "TestWarning")
    assert len(ReviewController.getReviewsByTitle("Test Movie", "TestUser1", "Title")) == 0
    warning = AdminWarning(reviewer="TestUser1",admin="TestAdmin1", reviewTitle= "Title",reviewMovie="Test Movie", warningDescription= "TestWarning")
    assert WarningManager.readWarning("TestUser1", "Title", "Test Movie") == warning

def testAddReviewInvalidUser(tempReviewFolder, tempMoviesFileWithMovie):
    with pytest.raises(HTTPException) as HTTPError:
        payload = ReviewCreate(reviewer ="Non-Existant-User",rating = 7, title = "hi", description = "hi")
        ReviewController.addReview("Test Movie",payload)
    assert "User not found" in str(HTTPError.value)

def testAddReviewInvalidMovie():
    with pytest.raises(HTTPException) as HTTPError:
        payload = ReviewCreate(reviewer ="TestUser",rating = 7, title = "hi", description = "hi")
        ReviewController.addReview("Non-Existant-Movie",payload)
    assert "Movie not found" in str(HTTPError.value)

def testAddReviewInvalidRating():
    with pytest.raises(HTTPException) as HTTPError:
        payload = ReviewCreate(reviewer ="TestUser1",rating = 11, title = "hi", description = "hi")
        ReviewController.addReview("Test Movie",payload)
    assert "Rating needs to be an integer between 0 and 10" in str(HTTPError.value)

def testEditReview():
    payload2 = ReviewCreate(reviewer ="TestUser1", rating = 7, title = "NEW TITLE", description = "NEW DESCRIPTION")
    ReviewController.editReview("Test Movie","Title",payload2)
    
    reviewList = ReviewController.getReviewsByTitle("Test Movie","TestUser1", "Title")
    for r in reviewList:
        assert r.title == "NEW TITLE" and r.description == "NEW DESCRIPTION"
        ReviewController.removeReview("Test Movie","TestUser1","NEW TITLE")

def testSearchReviews():
    payload = ReviewCreate(reviewer ="TestUser1",rating = 7, title = "hi", description = "hi")
    ReviewController.addReview("Test Movie",payload)
    payload = ReviewCreate(reviewer ="TestUser1",rating = 7, title = "no", description = "hi")
    ReviewController.addReview("Test Movie",payload)
    reviewList = ReviewController.searchByName("Test Movie","H")
    reviewTitles = []
    ReviewController.removeReview("Test Movie","TestUser1","hi")
    ReviewController.removeReview("Test Movie","TestUser1","no")
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
    assert "Test Movie 2" in movieTitles and "Test Movie" not in movieTitles 

def testSearchMultipleTagsMovies():
    foundMovies = MovieController.searchByTags(["Drama","Thriller"])
    movieTitles = []
    for m in foundMovies:
        movieTitles.append(m.title)
    assert "Test Movie" in movieTitles and "Test Movie 2" not in movieTitles 
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

    review = ReviewManager.createReview(
            movie="Test Movie",
            reviewDate=datetime.now().date(),
            reviewer="TESTUSER",
            usefulnessVote=1,
            totalVotes=2,
            rating=3,
            title="test review",
            description="dest desc.")

    review = ReviewManager.updateReview(
        "Test Movie",
        review,
        title="updated title",
        description="updated desc"
    )
    assert review.title == "updated title"
    assert review.description == "updated desc"

    result = ReviewManager.deleteReview("Test Movie", review)
    assert result is True

def testDataManagerReview():

    dataMan = DataManager.getInstance()
    reviewList = dataMan.readReviews("Test Movie")
    
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
    dataMan.writeReviews("Test Movie", reviewList)

    newList = dataMan.readReviews("Test Movie")
    assert len(newList) == original_count + 1

    newList.pop()
    dataMan.writeReviews("Test Movie", newList)


def testApiGetReviews( tempMoviesFileWithMovie,tempReviewFolder):
    
    client = TestClient(app)
    response = client.get("/Reviews/Test Movie")
    assert response.status_code == 200
    assert { 
    "reviewer": "TestUser1",
    "usefulnessVote": 0,
    "totalVotes": 1,
    "rating": 6,
    "title": "Title",
    "description": "Test Description",
    "reviewDate": "2025-12-04",
    } in response.json()

def testApiGetReview():
    
    client = TestClient(app)
    response = client.get("/Reviews/Test Movie/2")
    assert response.status_code == 200
    assert { 
    "reviewer": "TestUser1",
    "usefulnessVote": 0,
    "totalVotes": 1,
    "rating": 6,
    "title": "Title",
    "description": "Test Description",
    "reviewDate": "2025-12-04",
    } not in response.json()
    assert { 
    "reviewer": "TestUser1",
    "usefulnessVote": 0,
    "totalVotes": 1,
    "rating": 6,
    "title": "Title2",
    "description": "Test Description for second review",
    "reviewDate": "2025-12-04",
    } in response.json()

def testApiGetReviewNoInput(tempReviewFolder):
    
    client = TestClient(app)
    response = client.get("/Reviews/Test Movie/")
    assert response.status_code == 200
    assert { 
    "reviewer": "TestUser1",
    "usefulnessVote": 0,
    "totalVotes": 1,
    "rating": 6,
    "title": "Title",
    "description": "Test Description",
    "reviewDate": "2025-12-04",
    } in response.json()

def testApiPostDeleteReview():
    user = User(name="TestUser",email="mail@example.com",password="PlainTextPassword")
    UserController.createUser(user)
    client = TestClient(app)
    currentDate = datetime.now().date()
    currentDate = currentDate.strftime("%Y-%m-%d")
    response = client.post("/Reviews/Test Movie/", json = {
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
    
    response = client.delete("/Reviews/Test Movie/TestUser/hi")
    assert response.status_code == 204
    UserManager.deleteUser("TestUser")

def testApiGetMovies(tempMoviesFileWithMovie):
    
    client = TestClient(app)
    response = client.get("/Movies")
    assert response.status_code == 200
    assert {"title": "Test Movie",
        "rating":7.5,
        "ratingCount":1500,
        "userReviews":"300",
        "criticReviews":50,
        "metaScore":65,
        "genres":["Drama", "Thriller"],
        "directors":["Jane Doe"],
        "dateReleased": "2017-11-03",
        "creators": ["John Smith"],
        "actors":["Actor A", "Actor B"],
        "description":"A test movie for unit testing.",
        "duration":125} in response.json()
    
def testApiGetMovie():
    
    client = TestClient(app)
    response = client.get("/Movies/Test Movie")
    assert response.status_code == 200
    assert {"title": "Test Movie",
        "rating":7.5,
        "ratingCount":1500,
        "userReviews":"300",
        "criticReviews":50,
        "metaScore":65,
        "genres":["Drama", "Thriller"],
        "directors":["Jane Doe"],
        "dateReleased": "2017-11-03",
        "creators": ["John Smith"],
        "actors":["Actor A", "Actor B"],
        "description":"A test movie for unit testing.",
        "duration":125} == response.json()


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
    with pytest.raises(HTTPException) as excinfo:
        UserController.deleteAccount("NonExistentUser")
    assert "User not found" in str(excinfo.value)

@pytest.fixture
def tempWarningFile(tmp_path):
    folder = tmp_path / "tempData.json"
    data = [{"reviewer": "TestUser",
    "admin": "TestAdmin",
    "reviewTitle": "TestTitle",
    "reviewMovie": "TestMovie",
    "warningDescription": "TestDescription"}]
    folder.write_text(json.dumps(data), encoding="utf-8")

    dm = DataManager.getInstance()
    dm.warningFile = folder
    return dm

def testUpdateWarning(tempWarningFile):
    warning = AdminWarning(reviewer = "TestUser", admin= "TestAdmin", reviewTitle = "NewTitle", reviewMovie = "TestMovie",
                           warningDescription= "New Description", warningDate = date(2025,12,4))
    WarningManager.updateWarning("TestTitle", warning)
    assert WarningManager.readWarning("TestUser", "NewTitle", "TestMovie") == warning
#tests for report review
@pytest.fixture
def tempReportFolder(tmp_path):
    folder = tmp_path / "tempData"
    folder.mkdir()
    dm = DataManager.getInstance()
    dm.dataFolder = folder

    return dm

def testGetReportsEmpty(tempReportFolder):
    dm = tempReportFolder
    reports = dm.getReports()
    assert reports == []

def testGetReports(tempReportFolder):
    dm = tempReportFolder
    
    report1 = Report(
        reportId = "testId1",
        movie = "Joker",
        reviewer = "User1",
        reviewTitle = "bad bad movie",
        reporter = "User2",
        reason = "Inappropriate content",
        reportDate = datetime(2022, 6, 12, 10, 0, 0)
    )
    dm.writeReports([report1])

    reports = dm.getReports()
    assert len(reports) == 1
    assert reports[0].reportId == "testId1"
    assert reports[0].movie == "Joker"
    assert reports[0].reviewer == "User1"
    assert reports[0].reviewTitle == "bad bad movie"
    assert reports[0].reporter == "User2"
    assert reports[0].reason == "Inappropriate content"
    assert reports[0].reportDate == datetime(2022, 6, 12, 10, 0, 0)

def testWriteReports(tempReportFolder):
    dm = tempReportFolder
    
    report1 = Report(
        reportId = "testId1",
        movie = "Joker",
        reviewer = "User1",
        reviewTitle = "bad bad movie",
        reporter = "User2",
        reason = "Inappropriate content",
        reportDate = datetime(2022, 6, 12, 10, 0, 0)
    )
    report2 = Report(
        reportId = "testId2",
        movie = "Morbius",
        reviewer = "User3",
        reviewTitle = "blah blah blah",
        reporter = "User4",
        reason = "Spam",
        reportDate = datetime(2023, 1, 5, 15, 30, 0)
    )
    dm.writeReports([report1, report2])

    reportFile = dm.dataFolder / "reports.json"
    assert reportFile.exists()

    with open(reportFile, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert len(data) == 2
    assert data[0]['reportId'] == "testId1"
    assert data[1]['reportId'] == "testId2"
    assert data[0]['movie'] == "Joker"
    assert data[1]['movie'] == "Morbius"

def testDeleteReports(tempReportFolder):
    dm = tempReportFolder
    
    report1 = Report(
        reportId = "testId1",
        movie = "Joker",
        reviewer = "User1",
        reviewTitle = "bad bad movie",
        reporter = "User2",
        reason = "Inappropriate content",
        reportDate = datetime(2022, 6, 12, 10, 0, 0)
    )
    report2 = Report(
        reportId = "testId2",
        movie = "Morbius",
        reviewer = "User3",
        reviewTitle = "blah blah blah",
        reporter = "User4",
        reason = "Spam",
        reportDate = datetime(2023, 1, 5, 15, 30, 0)
    )
    dm.writeReports([report1, report2])

    result = dm.deleteReports("testId1")
    assert result is True

    reports = dm.getReports()
    assert len(reports) == 1
    assert reports[0].reportId == "testId2"

def testDeleteReportNotFound(tempReportFolder):
    dm = tempReportFolder
    
    report1 = Report(
        reportId = "testId1",
        movie = "Joker",
        reviewer = "User1",
        reviewTitle = "bad bad movie",
        reporter = "User2",
        reason = "Inappropriate content",
        reportDate = datetime(2022, 6, 12, 10, 0, 0)
    )
    dm.writeReports([report1])

    result = dm.deleteReports("weebleworble")
    assert result is False

    reports = dm.getReports()
    assert len(reports) == 1
    assert reports[0].reportId == "testId1"

def testDeleteReportEmptyList(tempReportFolder):
    dm = tempReportFolder

    result = dm.deleteReports("weebleworble")
    assert result is False




def testReportManagerCreate():
    user1 = User(name="reviewer1", email="reviewer1@gmail.com", password="password123")
    user2 = User(name="reporter1", email="reporter1@gmail.com", password="password456")
    UserController.createUser(user1)
    UserController.createUser(user2)

    reviewStuff = ReviewCreate(reviewer="reviewer1", rating=5, title="test review 1", description="this movie was terrible")
    ReviewController.addReview("Test Movie", reviewStuff)

    report = ReportManager.createReport(
        movie="Test Movie",
        reviewer="reviewer1",
        reviewTitle="test review 1",
        reporter="reporter1",
        reason="Inappropriate content"
    )

    assert report is not None
    assert report.movie == "Test Movie"
    assert report.reviewer == "reviewer1"
    assert report.reviewTitle == "test review 1"
    assert report.reporter == "reporter1"
    assert report.reason == "Inappropriate content"
    assert report.reportId is not None

    ReportManager.deleteReports(report.reportId)
    ReviewController.removeReview("Test Movie", "reviewer1", "test review 1")
    UserManager.deleteUser("reviewer1")
    UserManager.deleteUser("reporter1")

def testGetReportsManager():
    user1 = User(name="reviewer2", email="reviewer2@gmail.com", password="password123")
    user2 = User(name="reporter2", email="reporter2@gmail.com", password="password456")
    UserController.createUser(user1)
    UserController.createUser(user2)

    reviewStuff = ReviewCreate(reviewer="reviewer2", rating=5, title="test review 2", description="this movie was terrible")
    ReviewController.addReview("Test Movie", reviewStuff)

    report1 = ReportManager.createReport("Test Movie", "reviewer2", "test review 2", "reporter2", "Inappropriate content")
    report2 = ReportManager.createReport("Test Movie", "reviewer2", "test review 2", "reporter2", "Spam")

    allReports = ReportManager.getReports()
    assert len(allReports) >= 2
    reportIds = [report.reportId for report in allReports]
    assert report1.reportId in reportIds
    assert report2.reportId in reportIds

    ReportManager.deleteReports(report1.reportId)
    ReportManager.deleteReports(report2.reportId)
    ReviewController.removeReview("Test Movie", "reviewer2", "test review 2")
    UserManager.deleteUser("reviewer2")
    UserManager.deleteUser("reporter2")

def testCreateReportMovieNotFound():
    with pytest.raises(HTTPException) as HTTPError:
        ReportManager.createReport(
            movie="NonExistentMovie",
            reviewer="someuser",
            reviewTitle="title",
            reporter="reporter",
            reason="spam"
        )
    assert "Movie not found" in str(HTTPError.value)

def testCreateReportReviewerNotFound():
    with pytest.raises(HTTPException) as HTTPError:
        ReportManager.createReport(
            movie="Test Movie",
            reviewer="NonExistentUser",
            reviewTitle="title",
            reporter="reporter",
            reason="spam"
        )
    assert "Reviewer not found" in str(HTTPError.value)

def testCreateReportReporterNotFound():
    user1 = User(name="reviewer3", email="reviewer3@gmail.com", password="password123")
    UserController.createUser(user1)
    
    with pytest.raises(HTTPException) as HTTPError:
        ReportManager.createReport(
            movie="Test Movie",
            reviewer="reviewer3",
            reviewTitle="title",
            reporter="NonExistentReporter",
            reason="spam"
        )
    assert "Reporter not found" in str(HTTPError.value)
    
    UserManager.deleteUser("reviewer3")

def testCreateReportReviewNotFound():
    user1 = User(name="reviewer4", email="reviewer4@gmail.com", password="password123")
    user2 = User(name="reporter4", email="reporter4@gmail.com", password="password456")
    UserController.createUser(user1)
    UserController.createUser(user2)

    with pytest.raises(HTTPException) as HTTPError:
        ReportManager.createReport(
            movie="Test Movie",
            reviewer="reviewer4",
            reviewTitle="NonExistentReviewTitle",
            reporter="reporter4",
            reason="spam"
        )
    assert "Review not found" in str(HTTPError.value)

    UserManager.deleteUser("reviewer4")
    UserManager.deleteUser("reporter4")

def testCreateReportSelf():
    user1 = User(name="reviewer5", email="reviewer5@gmail.com", password="password123")
    UserController.createUser(user1)

    reviewStuff = ReviewCreate(reviewer="reviewer5", rating=5, title="test review 5", description="this movie was terrible")
    ReviewController.addReview("Test Movie", reviewStuff)

    with pytest.raises(HTTPException) as HTTPError:
        ReportManager.createReport(
            movie="Test Movie",
            reviewer="reviewer5",
            reviewTitle="test review 5",
            reporter="reviewer5",
            reason="spam"
        )
    assert "You can't report your own review" in str(HTTPError.value)

    ReviewController.removeReview("Test Movie", "reviewer5", "test review 5")
    UserManager.deleteUser("reviewer5")

def testCreateReportEmptyReason():
    user1 = User(name="reviewer6", email="reviewer6@gmail.com", password="password123")
    user2 = User(name="reporter6", email="reporter6@gmail.com", password="password456")
    UserController.createUser(user1)
    UserController.createUser(user2)

    reviewStuff = ReviewCreate(reviewer="reviewer6", rating=5, title="test review 6", description="this movie was terrible")
    ReviewController.addReview("Test Movie", reviewStuff)

    with pytest.raises(HTTPException) as HTTPError:
        ReportManager.createReport(
            movie="Test Movie",
            reviewer="reviewer6",
            reviewTitle="test review 6",
            reporter="reporter6",
            reason=""
        )
    assert "Reason can't be empty" in str(HTTPError.value)
    
    ReviewController.removeReview("Test Movie", "reviewer6", "test review 6")
    UserManager.deleteUser("reviewer6")
    UserManager.deleteUser("reporter6")

def testDeleteReportManager():
    user1 = User(name="reviewer7", email="reviewer7@gmail.com", password="password123")
    user2 = User(name="reporter7", email="reporter7@gmail.com", password="password456")
    UserController.createUser(user1)
    UserController.createUser(user2)

    reviewStuff = ReviewCreate(reviewer="reviewer7", rating=5, title="test review 7", description="this movie was terrible")
    ReviewController.addReview("Test Movie", reviewStuff)

    report = ReportManager.createReport("Test Movie", "reviewer7", "test review 7", "reporter7", "Inappropriate content")
    reportId = report.reportId

    result = ReportManager.deleteReports(reportId)
    assert result is True

    allReports = ReportManager.getReports()
    reportIds = [r.reportId for r in allReports]
    assert reportId not in reportIds

    ReviewController.removeReview("Test Movie", "reviewer7", "test review 7")
    UserManager.deleteUser("reviewer7")
    UserManager.deleteUser("reporter7")

def testDeleteReportManagerNotFound():
    result = ReportManager.deleteReports("wahhhhoooooble")
    assert result is False 




