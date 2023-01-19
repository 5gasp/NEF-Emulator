import math
from app.tools.distance import distance

def cartesian_from_haversine(lat, lng, lat0, lng0):
    """Uses haversine distance approximation to transform lat, lnt into cartesian
    coordinates
    """
    avg_lat = (lat0 + lat) / 2
    avg_lng = (lng0 + lng) / 2

    x = distance(avg_lat, lng0, avg_lat, lng)
    y = distance(lat0, avg_lng, lat, avg_lng)
    return x, y


def check_path_loss(UE_lat, UE_long, cells):
    losses_by_cell = {}
    for cell in cells:
        loss = calc_path_loss(UE_lat, UE_long, cell.get("latitude"), cell.get("longitude"))
        losses_by_cell[f"{cell.get('id')}"]= loss
    return losses_by_cell


def calc_path_loss(UE_lat, UE_long, cell_lat, cell_long, fc=2.6475):
    distance_3d = distance(UE_lat, UE_long, cell_lat, cell_long)
    path_loss = 28 + 22*math.log(distance_3d) + 20* math.log(fc) 
    return path_loss


def check_rsrp(UE_lat, UE_long, cells, power=30):
    rsrps_by_cell = {}
    losses = check_path_loss(UE_lat, UE_long, cells)
    for key in losses:
        rsrp= power - losses[key]
        rsrps_by_cell[f"{key}"] = rsrp
    return rsrps_by_cell
