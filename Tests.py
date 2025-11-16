import pytest
from DataManager import DataManager
from Managers import UserManager
from Controllers import UserController
from Controllers import ReviewController
from Classes import Review
from datetime import date
from fastapi import HTTPException
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