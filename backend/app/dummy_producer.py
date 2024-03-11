import pika
import json
import time
import os

def publish_to_rabbitmq(message):
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
        channel.basic_publish(exchange='topic_exchange', routing_key='gps_data', body=json.dumps(message))

        print(" [x] Sent message:", message)

        connection.close()

    except Exception as e:
        print("Error publishing message to RabbitMQ:", e)

def simulate_movement(supi, initial_lat, initial_lon, update_interval=1, lat_increment=0.001, lon_increment=0.001):
    lat = initial_lat
    lon = initial_lon

    while True:
        lat += lat_increment
        lon += lon_increment

        message = {"supi": supi, "lat": lat, "lon": lon}

        publish_to_rabbitmq(message)

        time.sleep(update_interval)

if __name__ == "__main__":
    simulate_movement("202010000000009", 37.998202, 23.819648)
