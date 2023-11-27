# -*- coding: utf-8 -*-
# @Author: Rafael Direito
# @Date:   2023-05-22 11:50:38
# @Last Modified by:   Rafael Direito
# @Last Modified time: 2023-06-07 20:30:44
from typing import Any
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse, FileResponse
import os
import json
import logging

logging.basicConfig(level=logging.DEBUG)

# Check the report base location
REPORT_DEFAULT_PATH = os.getenv("REPORT_PATH", "/shared/report.json") 
REPORT_BASE_PATH = os.path.dirname(REPORT_DEFAULT_PATH)

# On Boot, create the Report File
logging.debug(f"Is the file '{REPORT_DEFAULT_PATH}' already created? "
              f"{os.path.exists(REPORT_DEFAULT_PATH)}"
)
if not os.path.exists(REPORT_DEFAULT_PATH):
    logging.debug(f"Will create the file '{REPORT_DEFAULT_PATH}")
    with open(REPORT_DEFAULT_PATH, 'w') as jsonFile:
        data = []
        json.dump(data, jsonFile, indent=2)
    logging.debug(f"Was the file '{REPORT_DEFAULT_PATH}' created? "
              f"{os.path.exists(REPORT_DEFAULT_PATH)}"
)

app = FastAPI()

@app.get("/")
async def root():
    return {"Server says It's All Good"}

@app.post("/report")
def create_report(
    *,
    filename: str = 'report.json',
    http_request: Request
) -> Any:
    if not os.path.exists(os.path.join(REPORT_BASE_PATH, filename)):
        with open(os.path.join(REPORT_BASE_PATH, filename), 'x') as jsonFile:
            data = []
            json.dump(data, jsonFile, indent=2)
        return JSONResponse(content=f"Report named {filename} created",status_code=200)
    return JSONResponse(content=f"Report named {filename} already exists",status_code=409)


@app.get("/report")
def get_report(
    *,
    filename: str = 'report.json',
    http_request: Request
) -> Any:
    logging.info(os.path.join(REPORT_BASE_PATH, filename))
    if not os.path.exists(os.path.join(REPORT_BASE_PATH, filename)):
        return JSONResponse(content="File not Found",status_code=404)
    
    report_path = os.path.abspath(os.path.join(REPORT_BASE_PATH, filename))

    return FileResponse(report_path,filename=filename)

@app.delete("/report")
def delete_report(
    *,
    filename: str = 'report.json',
    http_request: Request
) -> Any:
    if os.path.exists(os.path.join(REPORT_BASE_PATH, filename)):
        os.remove(os.path.join(REPORT_BASE_PATH, filename))
        return JSONResponse(content="Report deleted",status_code=200)
    return JSONResponse(content="File not Found",status_code=404)
