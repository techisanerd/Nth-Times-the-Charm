from fastapi import APIRouter, status, Query
from typing import List, Optional
from datetime import datetime
from controllers.controllers import AdminController
from schemas.classes import UserView
from fastapi import FastAPI
from managers.data_manager import DataManager
import bcrypt
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Depends

routerAdmin = APIRouter(prefix="/Admins", tags=["Admins"])

@routerAdmin.get("",response_model = List[UserView])
def get_users():
    """Returns a json with all current admin's usernames and profile picture urls."""
    dm = DataManager.getInstance()
    return dm.getAdmins()

@routerAdmin.get("/{username}", response_model=UserView)
def get_user(username):
    """Returns a json with a specific user's username and profile picture url."""
    return AdminController.getAdmin(username)