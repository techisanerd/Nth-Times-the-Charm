import pytest
import json
import datetime
from DataManager import DataManager
from Managers import UserManager
from Controllers import UserController
from Controllers import ReviewController
from Controllers import MovieController
from Classes import Review
from datetime import date
from fastapi import HTTPException
from Classes import Movie 
from pathlib import Path

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
    with pytest.raises(HTTPException) as HTTPError:
        UserController.createUser("TestUser","mail@example.com","https://profilepic.example.com","PlainTextPassword")
        ReviewController.addReview("Joker","TestUser",11,"hi","hi")
        UserManager.deleteUser("TestUser")
    assert "Rating needs to be an integer between 0 and 10" in str(HTTPError.value)

def testEditReview():
    ReviewController.addReview("Joker","TestUser",7,"hi","hi")
    ReviewController.editReview("Joker","TestUser",7,"hi","NEW TITLE","NEW DESCRIPTION")
    reviewList = ReviewManager.readReview("Joker","TestUser")
    for r in reviewList:
        assert r.title == "NEW TITLE" and r.description == "NEW DESCRIPTION"
        ReviewController.removeReview("Joker","TestUser","NEW TITLE")

def testSearchReviews():
    ReviewController.addReview("Joker","TestUser",7,"hi","hi")
    ReviewController.addReview("Joker","TestUser2",7,"no","hi")
    reviewList = ReviewController.searchByName("H")
    reviewTitles = []
    ReviewController.removeReview("Joker","TestUser","hi")
    ReviewController.removeReview("Joker","TestUser2","no")
    for r in reviewList:
        reviewTitles.append(r.title)
    assert "hi" in reviewTitles and "no" not in reviewTitles

def testSearchMovies():
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

    dm = DataManager.getInstance()
    dm.moviesFolder = folder
    return dm

#movie object for tests
def sampleMovie():
    return Movie(
        title="Test Movie",
        rating=7.5,
        ratingCount=1500,
        userReviews=300,
        criticReviews=50,
        metaScore=65,
        genres=["Drama", "Thriller"],
        directors=["Jane Doe"],
        dateReleased=datetime.date(2020, 5, 20),
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
    filepath = dm.moviesFolder / "Test_Movie.json"
    assert filepath.exists()

    #check to see if data is correct
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    assert data["title"] == "Test Movie"
    assert data["movieIMDbRating"] == 7.5
    assert data["totalRatingCount"] == 1500
    assert data["totalUserReviews"] == 300
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
    filepath = dm.moviesFolder / "Test_Movie.json"
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
    filepath = dm.moviesFolder / "Test_Movie.json"
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







