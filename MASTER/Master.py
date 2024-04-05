import pika
import Common
import threading
import os
import functools
import subprocess
import GUI_Service
import sys

if len(sys.argv) == 1:
    Common.WORKING_MODE = "AUTO"
    # Common.log_message("MASTER chạy ở chế độ AUTO")
    
if len(sys.argv) == 2:
    _WORKING_MODE = sys.argv[1]
    if "MANUAL" in _WORKING_MODE:
        Common.WORKING_MODE = "MANUAL"
        # Common.log_message("MASTER chạy ở chế độ MANUAL")
    else:
        Common.WORKING_MODE = "AUTO"
        # Common.log_message("MASTER chạy ở chế độ AUTO")

def ack_message(channel, delivery_tag):
    if channel.is_open:
        channel.basic_ack(delivery_tag)
    else:
        Common.log_message("Channel đã đóng, ko thể gữi ack", level="ERROR")
        pass

def do_work(connection, channel, delivery_tag, body):
    current_path = os.getcwd()
    message = body.decode('utf-8')
    if not os.path.isdir(message):
        Common.log_message(f"Lỗi, job ko hợp lệ {message}", level="ERROR")
        cb = functools.partial(ack_message, channel, delivery_tag)
        connection.add_callback_threadsafe(cb)
        return
    job_name = str(message).rsplit(os.sep, 1)[-1]
    Common.log_message(f"Đã nhận được job mới: {str(message).rsplit(os.sep, 1)[-1]}")
    Common.log_message(f"Tiến hành chuẩn bị cho job mới")
    Common.prepare_job_before_receive()
    jpg_path = Common.get_first_jpg(message)
    audio_path = Common.get_all_audio(message)
    if jpg_path is not None:
        Common.log_message(f"Tìm thấy JPG: {str(jpg_path).rsplit(os.sep, 1)[-1]}")
        jpg = threading.Thread(target=Common.jpg_copy, args=(jpg_path, ))
        jpg.start()
        jpg.join()
    else:
        Common.log_message(f"Job {job_name}, không tìm thấy JPG!", level="ERROR")
        Common.log_message(f"Bỏ qua job: {job_name}.")
        Common.save_job_to_file(message)
        # GUI_Service.jpg_not_existed(job_name)
        # os._exit(1)
        cb = functools.partial(ack_message, channel, delivery_tag)
        connection.add_callback_threadsafe(cb)
        return
    if len(audio_path) == 1:
        Common.log_message(f"Chỉ có một audio được tìm thấy: {str(audio_path[0]).rsplit(os.sep, 1)[-1]}")
        audio = threading.Thread(target=Common.audio_copy, args= (audio_path[0], ))
        audio.start()
        audio.join()
        
    if len(audio_path) > 1:
        Common.log_message(f"Job có tổng cộng {len(audio_path)} audio")
        Common.log_message(f"Tiến hành gộp audio....")
        Common.join_all_audio(audio_path, job_name + ".mp3")
        Common.log_message("Gộp audio thành công.")
        # os._exit(0)
    
    Common.log_message("Công việc đã chuẩn bị xong, đang gọi Render Service!")
    os.chdir(os.path.abspath("..\\RenderService"))
    subprocess.run(['python', "RenderService.py"] + [job_name], check=True, text=True, shell=True)
    Common.log_message("Render Service đã chạy xong!")
    Common.move_to_result(job_name)
    Common.log_message("Kiểm tra thư mục Job_Result để lấy video!")
    os.chdir(current_path)
    cb = functools.partial(ack_message, channel, delivery_tag)
    connection.add_callback_threadsafe(cb)
    
    
def on_message(channel, method_frame, header_frame, body, args):
    (connection, threads) = args
    delivery_tag = method_frame.delivery_tag
    t = threading.Thread(target=do_work, args=(connection, channel, delivery_tag, body))
    t.start()
    threads.append(t)
    
# def callback(ch, method, properties, body):
#   message = body.decode('utf-8')
#   Common.log_message(f"Đã nhận được job mới: {str(message).rsplit(os.sep, 1)[-1]}")
#   Common.log_message(f"Tiến hành chuẩn bị cho job mới")
#   Common.prepare_job_before_receive()
#   jpg_path = Common.get_first_jpg(message)
#   audio_path = Common.get_all_audio(message)
#   if jpg_path is not None:
#     Common.log_message(f"Tìm thấy JPG: {str(jpg_path).rsplit(os.sep, 1)[-1]}")
#     jpg = threading.Thread(target=Common.jpg_copy, args=(jpg_path, ))
#     jpg.start()
#     jpg.join()
    
#   if len(audio_path) == 1:
#     Common.log_message(f"Chỉ có một audio được tìm thấy: {str(audio_path[0]).rsplit(os.sep, 1)[-1]}")
#     audio = threading.Thread(target=Common.audio_copy, args= (audio_path[0], ))
#     audio.start()
#     audio.join()
    
#   Common.log_message("Công việc đã chuẩn bị xong, đang gọi Render Service!")
  
  
#   ch.basic_ack(delivery_tag=method.delivery_tag)

connection_parameters = pika.ConnectionParameters(host='localhost', heartbeat=5)

connection = pika.BlockingConnection(connection_parameters)

channel = connection.channel()

channel.queue_declare(queue='RenderServer', durable=True)

channel.basic_qos(prefetch_count=1)

threads = []

on_message_callback = functools.partial(on_message, args=(connection, threads))

# channel.basic_consume(on_message_callback, 'RenderServer')

channel.basic_consume(queue='RenderServer', on_message_callback=on_message_callback)

Common.log_message("MASTER Server khởi tạo thành công!")

Common.log_message("Đang đợi nhận job.....")

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
    
for thread in threads:
    thread.join()

connection.close()
