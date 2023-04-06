from typing import Any
from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse, FileResponse
import os
import json

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
    if not os.path.exists("../shared/" + filename):
        with open("../shared/" + filename, 'x') as jsonFile:
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

    if not os.path.exists("../shared/" + filename):
        return JSONResponse(content="File not Found",status_code=404)
    
    report_path = os.path.abspath("../shared/" + filename)

    return FileResponse(report_path,filename=filename)

@app.delete("/report")
def delete_report(
    *,
    filename: str = 'report.json',
    http_request: Request
) -> Any:
    if os.path.exists("../shared/" + filename):
        os.remove("../shared/" + filename)
        return JSONResponse(content="Report deleted",status_code=200)
    return JSONResponse(content="File not Found",status_code=404)