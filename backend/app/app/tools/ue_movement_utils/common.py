from fastapi.encoders import jsonable_encoder

from app import crud, tools

# Dictionary holding threads that are running per user id.
threads = {}

# Dictionary holding UEs' information
ues = {}

# Dictionary holding UEs' distances to cells
distances = {}

# Dictionary holding UEs' path losses in reference to cells
path_losses = {}

# Dictionary holding UEs' path losses in reference to cells
rsrps = {}

subscriptions = {
    "location_reporting": False,
    "ue_reachability": False,
    "loss_of_connectivity": False,
    "as_session_with_qos": False,
}


def get_cells(db, owner_id):
    Cells = crud.cell.get_multi_by_owner(db=db, owner_id=owner_id, skip=0, limit=100)
    return jsonable_encoder(Cells)


def get_points(db, path_id):
    points = crud.points.get_points(db=db, path_id=path_id)
    return jsonable_encoder(points)


def retrieve_ue_state(supi: str, user_id: int) -> bool:
    try:
        return threads[f"{supi}"][f"{user_id}"].is_alive()
    except KeyError as ke:
        print("Key Not Found in Threads Dictionary:", ke)
        return False


def retrieve_ues() -> dict:
    return ues


def retrieve_ue(supi: str) -> dict:
    return ues.get(supi)


def retrieve_ue_distances(supi: str) -> dict:
    return distances.get(supi)


def retrieve_ue_path_losses(supi: str) -> dict:
    return path_losses.get(supi)


def retrieve_ue_rsrps(supi: str) -> dict:
    return rsrps.get(supi)


def monitoring_event_sub_validation(
    sub: dict, is_superuser: bool, current_user_id: int, owner_id
) -> bool:

    if not is_superuser and (owner_id != current_user_id):
        # logging.warning("Not enough permissions")
        return False
    else:
        sub_validate_time = tools.check_expiration_time(
            expire_time=sub.get("monitorExpireTime")
        )
        sub_validate_number_of_reports = tools.check_numberOfReports(
            sub.get("maximumNumberOfReports")
        )
        if sub_validate_time and sub_validate_number_of_reports:
            return True
        else:
            return False
