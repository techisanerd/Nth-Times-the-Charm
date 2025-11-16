import pytest
import json, csv
import datetime
from DataManager import DataManager
from Managers import UserManager
from Classes import Movie, Review 
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

#tests for review manager functions

#review object for tests
def sampleReview():
    return Review(
        reviewDate=datetime.date(2025, 11, 15),
        reviewer="Jane Doe",
        usefullnessVote=703,
        totalVotes=1040,
        rating=7.5,
        title="Test review",
        description="Good review here",
    )

def testCreateReview(tempMoviesFolder):
    dm = tempMoviesFolder
    review = sampleReview()

    created = dm.createReview(review)
    assert created is True
    filepath = dm.moviesFolder / "Test_Review.csv"
    assert filepath.exists()

    #check to see if data is correct
    with open(filepath, 'r', encoding='utf-8') as f:
        data = csv.load(f)

    assert data["reviewDate"] == datetime.date(2025, 11, 15)
    assert data["reviewer"] == "Jane Doe"
    assert data["usefullnessVote"] == 107
    assert data["totalVotes"] == 1040
    assert data["rating"] == 7.5
    assert data["title"] == "Test review"
    assert data["description"] == "Good review here"


def testUpdateReview(tempMoviesFolder):
    dm = tempMoviesFolder
    review = sampleReview()
    
    created = dm.createReview(review)
    assert created is True

    #modify some attributes
    review.rating = 7.0
    review.description = "An updated test description for a review."
    review.title = "Updated test review"

    #update review file
    updated = dm.updateReview(review)
    assert updated is True
    filepath = dm.moviesFolder / "Test_Review.csv"
    assert filepath.exists()

    #reload and verify
    with open(filepath, 'r', encoding='utf-8') as f:
        data = csv.load(f)

    assert data["rating"] == 7.0
    assert data["description"] == "An updated test description for a review."
    assert data["title"] == "Updated test review"





