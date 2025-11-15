import pytest
from DataManager import DataManager
from Managers import UserManager, ReviewManager
from Classes import Review
from datetime import datetime
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

def testReviewManager():
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
