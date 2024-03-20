from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session
from app import crud, models
from app.api import deps
from app.tools.ue_movement_utils.common import retrieve_ue, retrieve_ue_distances, retrieve_ue_path_losses, retrieve_ue_rsrps
from .utils import ReportLogging

router = APIRouter()
router.route_class = ReportLogging

@router.get("/{supi}/serving_cell")
def read_UE_serving_cell(*,
    db: Session = Depends(deps.get_db),
    supi: str = Path(...,
                     description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")

    if retrieve_ue(supi) == None:
        raise HTTPException(status_code=400, detail="The emulation needs to be ongoing")

    log = {
        "latitude":retrieve_ue(supi)["latitude"],
        "longitude": retrieve_ue(supi)["longitude"],
        "UE_id": retrieve_ue(supi)["name"],
        "S-PCI": retrieve_ue(supi)["Cell_id"]
    }
    return log


@router.get("/{supi}/distances")
def read_UE_distances(*,
    db: Session = Depends(deps.get_db),
    supi: str = Path(...,
                     description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return retrieve_ue_distances(supi)


@router.get("/{supi}/path_losses")
def read_UE_losses(*,
    db: Session = Depends(deps.get_db),
    supi: str = Path(...,
                     description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return retrieve_ue_path_losses(supi)


@router.get("/{supi}/rsrps")
def read_UE_rsrps(*,
    db: Session = Depends(deps.get_db),
    supi: str = Path(...,
                     description="The SUPI of the UE you want to retrieve"),
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    UE = crud.ue.get_supi(db=db, supi=supi)
    if not UE:
        raise HTTPException(status_code=404, detail="UE not found")
    if not crud.user.is_superuser(current_user) and (UE.owner_id != current_user.id):
        raise HTTPException(status_code=400, detail="Not enough permissions")
    return retrieve_ue_rsrps(supi)
