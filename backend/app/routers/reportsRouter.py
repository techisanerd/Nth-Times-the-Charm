from fastapi import APIRouter, status, Query
from typing import List, Optional
from datetime import datetime
from managers.managers import ReportManager
from schemas.classes import Report
from fastapi import FastAPI
from managers.data_manager import DataManager
import bcrypt
from fastapi.responses import JSONResponse
from fastapi import HTTPException, Depends

routerReport = APIRouter(prefix="/Reports", tags=["Reports"])

@routerReport.get("",response_model = List[Report])
def get_reports():
    return ReportManager.getReports()


