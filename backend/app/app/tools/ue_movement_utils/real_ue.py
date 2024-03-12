import pika
import json
import os
import logging
from fastapi.encoders import jsonable_encoder
from app.db.session import SessionLocal
from app import crud
from .common import ues

logging.basicConfig(level=logging.INFO)

def callback(ch, method, properties, body):
    try:
        data = json.loads(body.decode())
        supi = data.get('supi')
        lat = data.get('lat')
        lon = data.get('lon')

        db = SessionLocal()
        UE = crud.ue.get_supi(db=db, supi=supi)

        if UE and ~UE.is_simulated:
            UE.latitude = lat
            UE.longitude = lon

            ues[f"{supi}"] = jsonable_encoder(UE)
            ues[f"{supi}"].pop("id")

            db.commit()
            logging.info(f"Updated UE {supi} with latitude: {lat}, longitude: {lon}")

    except Exception as e:
        logging.error(f"Error processing message: {e}")

def consume_from_rabbitmq():
    try:
        rabbitmq_user = os.environ.get('RABBITMQ_DEFAULT_USER', 'guest')
        rabbitmq_password = os.environ.get('RABBITMQ_DEFAULT_PASS', 'guest')

        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
        parameters = pika.ConnectionParameters(host='rabbitmq',
                                               port=5672,
                                               credentials=credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()

        channel.exchange_declare(exchange='topic_exchange', exchange_type='topic')

        result = channel.queue_declare('', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='topic_exchange', queue=queue_name, routing_key='gps_data')

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

        logging.info('Waiting for messages...')
        channel.start_consuming()

    except Exception as e:
        logging.error(f"Error consuming from RabbitMQ: {e}")

if __name__ == "__main__":
    consume_from_rabbitmq()