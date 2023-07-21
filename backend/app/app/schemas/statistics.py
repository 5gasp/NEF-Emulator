from threading import Event
from typing import List
from pydantic import BaseModel, Field
from enum import Enum
import json 

with open('app/core/config/prometheusQueries.json') as json_file:
    keys = json.load(json_file).keys()
    json_data = dict(zip(keys,keys))

class TempEnum(str, Enum):
    pass

MetricsEnum = TempEnum("MetricsEnum",json_data)

class Response(BaseModel):
    timestamp: float
    value: float
    
    
class Metrics(BaseModel):
    metrics:List[MetricsEnum]= Field(None, title="Metrics", description="All available metrics")

class Metric(BaseModel):
    metric:MetricsEnum = Field(None, description="Metric")
    

    