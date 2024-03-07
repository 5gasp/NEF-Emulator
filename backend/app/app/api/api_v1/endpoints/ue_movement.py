from fastapi import APIRouter, Path, Depends, HTTPException
from typing import Any
from app import models
from app.api import deps
from app.schemas import Msg
from app.tools.ue_movement_utils.common import threads, ues, retrieve_ue_state
from app.tools.ue_movement_utils import BackgroundTasks


# API
router = APIRouter()


@router.post("/start-loop", status_code=200)
def initiate_movement(
    *,
    msg: Msg,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Start the loop.
    """
    if msg.supi in threads:
        raise HTTPException(
            status_code=409,
            detail=f"There is a thread already running for this supi:{msg.supi}",
        )
    t = BackgroundTasks(
        args=(
            current_user,
            msg.supi,
        )
    )
    threads[f"{msg.supi}"] = {}
    threads[f"{msg.supi}"][f"{current_user.id}"] = t
    t.start()
    # print(threads)
    return {"msg": "Loop started"}


@router.post("/stop-loop", status_code=200)
def terminate_movement(
    *,
    msg: Msg,
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Stop the loop.
    """
    try:
        threads[f"{msg.supi}"][f"{current_user.id}"].stop()
        threads[f"{msg.supi}"][f"{current_user.id}"].join()
        threads.pop(f"{msg.supi}")
        return {"msg": "Loop ended"}
    except KeyError as ke:
        print("Key Not Found in Threads Dictionary:", ke)
        raise HTTPException(
            status_code=409,
            detail="There is no thread running for this user! Please initiate a new thread",
        )


@router.get("/state-loop/{supi}", status_code=200)
def state_movement(
    *,
    supi: str = Path(...),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the state
    """
    return {"running": retrieve_ue_state(supi, current_user.id)}


@router.get("/state-ues", status_code=200)
def state_ues(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the state
    """
    return ues
