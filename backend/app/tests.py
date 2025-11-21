import pytest
import json

from datetime import date
from fastapi import HTTPException
from pathlib import Path
from datetime import datetime, date

from managers.data_manager import DataManager
from controllers.controllers import UserController, ReviewController, MovieController
from managers.managers import UserManager, ReviewManager
from schemas.classes import Movie, Review,Session

originalMoviesFolder = " "

def testSingleton():
    """Testing that we only get one instance of DataManager"""
    dataManager1 = DataManager.getInstance()
    dataManager2 = DataManager.getInstance()
    assert dataManager1 == dataManager2

def testUserManager():
    UserManager.createUser(name="TESTUSER",email="mail@example.com", profilePic="https://profilepic.example.com", passwordHash="0xabcdefg")
    u = UserManager.readUser("TESTUSER")
    UserManager.deleteUser("TESTUSER")
    assert u.name == "TESTUSER" and u.email=="mail@example.com" and u.profilePic=="https://profilepic.example.com" and u.passwordHash == "0xabcdefg"
    assert UserManager.readUser("TESTUSER") == None

def testUpdateUser():
    UserManager.createUser(name="TESTUSER",email="mail@example.com", profilePic="https://profilepic.example.com", passwordHash="0xabcdefg")
    u = UserManager.readUser("TESTUSER")
    v = UserManager.updateUser(u, name="NEWTESTUSER")
    UserManager.deleteUser("NEWTESTUSER")
    assert UserManager.readUser("TESTUSER") == None and v.name == "NEWTESTUSER"

def testUserCreation():
    UserController.createUser("TestUser","mail@example.com","https://profilepic.example.com","PlainTestPassword")
    u = UserManager.readUser("TestUser")
    hashPassword = UserController.hashPassword("PlainTestPassword").hexdigest()
    UserManager.deleteUser("TestUser")
    assert u.name == "TestUser" and u.email == "mail@example.com" and u.profilePic == "https://profilepic.example.com"
    assert u.passwordHash == hashPassword

def testRepeatUsername():
    UserManager.createUser("TestUser","mail@example.com","https://profilepic.example.com","0xabcdef")
    with pytest.raises(HTTPException) as HTTPError:
        UserController.createUser("TestUser","mail@example.com","https://profilepic.example.com","PlainTestPassword")
    UserManager.deleteUser("TestUser")
    assert "Username already in use" in str(HTTPError.value)

def testTooShortPassword():
    with pytest.raises(HTTPException) as HTTPError:
        UserController.createUser("TestUser","mail@example.com","https://profilepic.example.com","tiny")
    UserManager.deleteUser("TestUser")
    assert "Password should be 8 or more characters" in str(HTTPError.value)

def testAddReviewInvalidUser():
    with pytest.raises(HTTPException) as HTTPError:
        ReviewController.addReview("Joker","Non-Existant-User",0,"hi","hi")
    assert "User not found" in str(HTTPError.value)

def testAddReviewInvalidMovie():
    with pytest.raises(HTTPException) as HTTPError:
        ReviewController.addReview("Non-Existant-Movie","User",0,"hi","hi")
    assert "Movie not found" in str(HTTPError.value)

def testAddReviewInvalidRating():
    UserController.createUser("TestUser","mail@example.com","https://profilepic.example.com","PlainTextPassword")
    with pytest.raises(HTTPException) as HTTPError:
        ReviewController.addReview("Joker","TestUser",11,"hi","hi")
    UserManager.deleteUser("TestUser")
    assert "Rating needs to be an integer between 0 and 10" in str(HTTPError.value)

def testEditReview():
    UserController.createUser("TestUser","mail@example.com","https://profilepic.example.com","PlainTextPassword")
    ReviewController.addReview("Joker","TestUser",7,"hi","hi")
    ReviewController.editReview("Joker","TestUser",7,"hi","NEW TITLE","NEW DESCRIPTION")
    UserManager.deleteUser("TestUser")
    reviewList = ReviewManager.readReview("Joker","TestUser")
    for r in reviewList:
        assert r.title == "NEW TITLE" and r.description == "NEW DESCRIPTION"
        ReviewController.removeReview("Joker","TestUser","NEW TITLE")

def testSearchReviews():
    UserController.createUser("TestUser","mail@example.com","https://profilepic.example.com","PlainTextPassword")
    UserController.createUser("TestUser2","mail@example.com","https://profilepic.example.com","PlainTextPassword")
    ReviewController.addReview("Joker","TestUser",7,"hi","hi")
    ReviewController.addReview("Joker","TestUser2",7,"no","hi")
    reviewList = ReviewController.searchByName("Joker","H")
    reviewTitles = []
    ReviewController.removeReview("Joker","TestUser","hi")
    ReviewController.removeReview("Joker","TestUser2","no")
    UserManager.deleteUser("TestUser")
    UserManager.deleteUser("TestUser2")
    for r in reviewList:
        reviewTitles.append(r.title)
    assert "hi" in reviewTitles and "no" not in reviewTitles

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