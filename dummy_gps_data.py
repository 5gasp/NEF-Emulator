import argparse
import json
import os
import time

import pika


def get_rabbitmq_connection():
    rabbitmq_user = os.environ.get("RABBITMQ_DEFAULT_USER", "user")
    rabbitmq_password = os.environ.get("RABBITMQ_DEFAULT_PASS", "pass")

    credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_password)
    parameters = pika.ConnectionParameters(
        host="localhost", port=5672, credentials=credentials
    )
    connection = pika.BlockingConnection(parameters)
    return connection


def publish_to_rabbitmq(connection, message):
    try:
        channel = connection.channel()

        channel.exchange_declare(exchange="topic_exchange", exchange_type="topic")
        channel.basic_publish(
            exchange="topic_exchange", routing_key="gps_data", body=json.dumps(message)
        )

        print(" [x] Sent message:", message)

    except Exception as e:
        print("Error publishing message to RabbitMQ:", e)


def simulate_movement(
    supi,
    initial_lat,
    initial_lon,
    update_interval=1,
    lat_increment=0.0001,
    lon_increment=0.0001,
):
    connection = get_rabbitmq_connection()
    lat = initial_lat
    lon = initial_lon

    try:
        while True:
            lat += lat_increment
            lon += lon_increment

            message = {"supi": supi, "lat": lat, "lon": lon}

            publish_to_rabbitmq(connection, message)

            time.sleep(update_interval)

    except KeyboardInterrupt:
        print("Simulation stopped.")

    finally:
        connection.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Simulate UE GPS coordinates and publish to RabbitMQ"
    )
    parser.add_argument(
        "--supi",
        type=str,
        default="202010000000009",
        help="SUPI value (default: %(default)s)",
    )
    parser.add_argument(
        "--initial_lat",
        type=float,
        default=37.998202,
        help="Initial latitude (default: %(default)s)",
    )
    parser.add_argument(
        "--initial_lon",
        type=float,
        default=23.819648,
        help="Initial longitude (default: %(default)s)",
    )
    parser.add_argument(
        "--update_interval",
        type=int,
        default=1,
        help="Update interval (default: %(default)s)",
    )
    parser.add_argument(
        "--lat_increment",
        type=float,
        default=0.0001,
        help="Latitude increment (default: %(default)s)",
    )
    parser.add_argument(
        "--lon_increment",
        type=float,
        default=0.0001,
        help="Longitude increment (default: %(default)s)",
    )

    args = parser.parse_args()

    simulate_movement(
        args.supi,
        args.initial_lat,
        args.initial_lon,
        args.update_interval,
        args.lat_increment,
        args.lon_increment,
    )
