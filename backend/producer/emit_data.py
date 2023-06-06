import pika
import time

def establish_connection():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
            return connection
        except pika.exceptions.AMQPConnectionError:
            print("Connection failed. Retrying in 5 seconds...")
            time.sleep(5)

# Establish connection
connection = establish_connection()
channel = connection.channel()

# Declare a queue
channel.queue_declare(queue='my_queue')

while True:
    # Generate a message
    message = "Hello, RabbitMQ! Current time: " + time.ctime()

    try:
        # Publish the message
        channel.basic_publish(exchange='', routing_key='my_queue', body=message)
        print("Sent message:", message)
    except pika.exceptions.AMQPConnectionError:
        print("Failed to send message. Retrying in 5 seconds...")
        connection = establish_connection()
        channel = connection.channel()
        continue

    # Sleep for some time before sending the next message
    time.sleep(1)

# Close the connection (This code won't be reached in an infinite loop)
connection.close()