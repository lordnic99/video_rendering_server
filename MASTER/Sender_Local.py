import pika

queue_name="RenderServer"
host="localhost"
port=5672
persistent=True

def send_message_to_rabbitmq(message):
  connection = pika.BlockingConnection(
      pika.ConnectionParameters(host=host, port=port)
  )
  channel = connection.channel()
  channel.queue_declare(queue=queue_name, durable=True)
  message_body = message.encode("utf-8")
  message_properties = None
  if persistent:
    message_properties = pika.BasicProperties(delivery_mode=2)
  channel.basic_publish(exchange="", routing_key=queue_name, body=message_body, properties=message_properties)
  connection.close()
  print(f"Job đã được gữi tới: {queue_name}")

if __name__ == "__main__":
  import sys
  if len(sys.argv) < 2:
    sys.exit(1)

  message = ' '.join(sys.argv[1:])
  send_message_to_rabbitmq(message)
