import logging
from typing import Any, List
from fastapi import APIRouter, Depends, HTTPException, Path, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pymongo.database import Database
from sqlalchemy.orm import Session
from app import models, schemas
from app.api import deps
from app.crud import crud_mongo, user, ue
from app.db.session import client
from .utils import add_notifications
from .qosInformation import qos_reference_match
from enum import Enum
from app.core.config import settings
import requests
router = APIRouter()
db_collection= 'Statistics'



@router.get("/{scsAsId}/metrics",response_model=schemas.statistics.Metrics)
def read_available_metrics(
    *,
    scsAsId: str = Path(..., title="The ID of the Netapp that creates a subscription", example="myNetapp"),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request
) -> Any:
    """
    Get subscription by id
    """
    #print(schemas.statistics.Metrics)
    return schemas.statistics.Metrics.__dict__

@router.get("/{scsAsId}/metric/{query}")
def read_metric(
    *,
    scsAsId: str = Path(..., title="The ID of the Netapp that creates a subscription", example="myNetapp"),
    query : str = Path(...,title="The query for the desired metric", example="5GASP Network"),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request
) -> Any:
    """
    Get subscription by id
    """
    prometheus = settings.PROMETHEUS
    prometheus_token = settings.PROMETHEUS_TOKEN
    payload = {}
    headers = {
    'Authorization': 'Basic %s' % prometheus_token
    }
    response = requests.request("GET", '%s?query=%s' % (prometheus, query), headers=headers, data=payload, timeout=(3.05, 27))   
    if(response.status_code != 200):        
        raise HTTPException(status_code=response.status_code, detail=response.json())
    
    return  response.json()