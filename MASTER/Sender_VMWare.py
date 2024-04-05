import pika
import os
import time

queue_name="RenderServer"
host="localhost"
port=5672
persistent=True

def process_txt_files(folder_path):
    os.makedirs(folder_path, exist_ok=True)

    files = os.listdir(folder_path)

    txt_files = [f for f in files if f.endswith('.txt')]

    for txt_file in txt_files:
        file_path = os.path.join(folder_path, txt_file)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
              print(f"Nhận được job từ vmware: {os.path.join(os.getcwd(), content)}")
              send_message_to_rabbitmq(os.path.join(os.getcwd(), content))
            else:
              pass
        os.remove(file_path)

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
  print("Đang đợi nhận job từ vmware.....")
  while True:
    process_txt_files("JOB_READY_TO_RUN")
    time.sleep(30)
    
  
  
