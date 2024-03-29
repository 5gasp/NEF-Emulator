import json
import logging
import os

import pika
from fastapi.encoders import jsonable_encoder

from app import crud
from app.db.session import SessionLocal, client
from app.tools.distance import check_distance

from .common import get_cells, subscriptions, ues, validate_location_reporting_sub

logging.basicConfig(level=logging.INFO)


def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode())
        supi = data.get("supi")
        lat = data.get("lat")
        lon = data.get("lon")

        db = SessionLocal()
        UE = crud.ue.get_supi(db=db, supi=supi)
        if UE and ~UE.is_simulated:
            try:
                active_subscriptions = subscriptions.copy()
                db_mongo = client.fastapi
                UE.longitude = lon
                UE.latitude = lat
                ues[f"{supi}"] = jsonable_encoder(UE)
                ues[f"{supi}"].pop("id")

                current_user = UE.owner
                is_superuser = crud.user.is_superuser(current_user)

                cells = get_cells(db=db, owner_id=current_user.id)
                cell_now, distances_now = check_distance(lat, lon, cells)

                if cell_now and cell_now["cell_id"] != UE.Cell_id:
                    ues[f"{supi}"]["cell_id_hex"] = cell_now["cell_id"]
                    ues[f"{supi}"]["gnb_id_hex"] = cell_now["gNB_id"]
                    ues[f"{supi}"]["Cell_id"] = cell_now["id"]

                    try:
                        validate_location_reporting_sub(
                            active_subscriptions,
                            current_user,
                            is_superuser,
                            supi,
                            UE,
                            db_mongo,
                        )
                    except Exception as ex:
                        logging.warning(ex)

                else:
                    ues[f"{supi}"]["cell_id_hex"] = None
                    ues[f"{supi}"]["gnb_id_hex"] = None
                    ues[f"{supi}"]["Cell_id"] = None

                crud.ue.update(
                    db=db,
                    db_obj=UE,
                    obj_in=ues[f"{supi}"],
                )

                logging.info(
                    f"Updated UE {supi} with latitude: {lat}, longitude: {lon}"
                )
            except Exception as ex:
                logging.warning("Failed to update coordinates")
                logging.warning(ex)

    except Exception as e:
        logging.error(f"Error processing message: {e}")


def consume_from_rabbitmq():
    try:
        rabbitmq_user = os.environ.get("RABBITMQ_DEFAULT_USER", "guest")
        rabbitmq_password = os.environ.get("RABBITMQ_DEFAULT_PASS", "guest")

        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = pika.ConnectionParameters(
            host="rabbitmq", port=5672, credentials=credentials
        )
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.exchange_declare(exchange="ue_coordinates", exchange_type="topic")

        result = channel.queue_declare("", exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(
            exchange="ue_coordinates", queue=queue_name, routing_key="gps_data"
        )

        channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True
        )

        logging.info("Waiting for messages...")
        channel.start_consuming()

    except Exception as e:
        logging.error(f"Error consuming from RabbitMQ: {e}")


if __name__ == "__main__":
    consume_from_rabbitmq()
