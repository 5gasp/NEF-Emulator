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
from app.tools.prometheus import Prometheus

router = APIRouter()
db_collection= 'Statistics'


@router.get("/{scsAsId}/metrics",response_model=schemas.Metrics)
async def read_available_metrics(
    *,
    scsAsId: str = Path(..., title="The ID of the Netapp that creates a subscription", example="myNetapp"),
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request
) -> Any:
    """
    Get subscription by id
    """
    prometheus = Prometheus()

    http_response = JSONResponse(content=prometheus.getMetrics(), status_code=200,)
    return http_response

@router.post("/{scsAsId}/metric", response_model=schemas.Response)
def read_metric(
    *,
    scsAsId: str = Path(..., title="The ID of the Netapp that creates a subscription", example="myNetapp"),
    item_in: schemas.Metric,
    current_user: models.User = Depends(deps.get_current_active_user),
    http_request: Request
) -> Any:
    """
    Get subscription by id
    """
    prometheus_token = settings.PROMETHEUS_TOKEN
    payload = {}
    headers = {
    'Authorization': 'Basic %s' % prometheus_token
    }
    prometheus = Prometheus()
    metric = item_in.metric
    query = prometheus.query(metric=metric)
    if query:
        response = requests.request("GET", '%s?query=%s' % (settings.PROMETHEUS, query), headers=headers, data=payload, timeout=(3.05, 27))   
        if(response.status_code != 200):        
            raise HTTPException(status_code=response.status_code, detail=response.json())

        result = prometheus.response(response.json(),metric=metric)

        return result
    else:
        return JSONResponse(content={"message" : "Metric not available"},status_code=404)