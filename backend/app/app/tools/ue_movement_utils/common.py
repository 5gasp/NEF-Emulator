import logging

import requests
from fastapi.encoders import jsonable_encoder

from app import crud, tools
from app.crud import crud_mongo
from app.tools import monitoring_callbacks

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


def validate_location_reporting_sub(
    active_subscriptions, current_user, is_superuser, supi, UE, db_mongo, location_reporting_sub=None
):
    if not location_reporting_sub and not active_subscriptions.get("location_reporting"):
        location_reporting_sub = crud_mongo.read_by_multiple_pairs(
            db_mongo,
            "MonitoringEvent",
            externalId=UE.external_identifier,
            monitoringType="LOCATION_REPORTING",
        )
        logging.info(f"Location Reporting Sub: {location_reporting_sub}")
        if location_reporting_sub:
            active_subscriptions.update({"location_reporting": True})

    # Validation of subscription
    if active_subscriptions.get("location_reporting"):
        sub_is_valid = monitoring_event_sub_validation(
            location_reporting_sub,
            is_superuser,
            current_user,
            location_reporting_sub.get("owner_id"),
        )
        if sub_is_valid:
            try:
                monitoring_callbacks.location_callback(
                    ues[f"{supi}"],
                    location_reporting_sub.get("notificationDestination"),
                    location_reporting_sub.get("link"),
                )

                location_reporting_sub.update(
                    {
                        "maximumNumberOfReports": location_reporting_sub.get(
                            "maximumNumberOfReports"
                        )
                        - 1
                    }
                )
                crud_mongo.update(
                    db_mongo,
                    "MonitoringEvent",
                    location_reporting_sub.get("_id"),
                    location_reporting_sub,
                )
            except requests.exceptions.ConnectionError as ex:
                logging.warning(ex)
                crud_mongo.delete_by_uuid(
                    db_mongo,
                    "MonitoringEvent",
                    location_reporting_sub.get("_id"),
                )
                active_subscriptions.update({"location_reporting": False})
                raise Exception("Failed to send the callback request")
        else:
            crud_mongo.delete_by_uuid(
                db_mongo,
                "MonitoringEvent",
                location_reporting_sub.get("_id"),
            )
            active_subscriptions.update({"location_reporting": False})
            logging.warning("Subscription has expired")
