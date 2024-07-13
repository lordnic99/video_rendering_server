import os
import shutil
import logging
import inspect
import os
import subprocess
from mutagen.mp3 import MP3
import glob

WORKING_MODE = "AUTO"


def list_files(path):
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return files


def get_first_jpg(path):
    file_list = list_files(path)
    for file_path in file_list:
        if file_path.lower().endswith(".jpg"):
            return file_path

    return None


def get_all_audio(path, extensions=(".m4b", ".mp3")):
    file_list = list_files(path)
    audio_files = []
    for file_path in file_list:
        if any(file_path.lower().endswith(ext) for ext in extensions):
            audio_files.append(file_path)

    return audio_files


def jpg_copy(file_path):
    file_name = os.path.basename(file_path)

    destination_folder = os.path.normpath(
        os.path.join(os.path.dirname(__file__), r"..\RenderService\input\video")
    )

    if not os.path.exists(file_path):
        log_message(f"File '{file_path}' does not exist.")
        return

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    try:
        # Move the file to the destination folder
        shutil.copy(file_path, os.path.join(destination_folder, file_name))
        log_message(f"File '{file_name}' đã được đưa vào input.")
    except Exception as e:
        log_message(f"Lỗi khi copy file: {e}")


def audio_copy(file_path):
    if file_path.endswith(".m4b"):
        log_message("Audio có dang m4b, cần chuyển đổi sang mp3")
        convert_m4b_to_mp3(
            file_path,
            os.path.join(
                os.path.normpath(
                    os.path.join(
                        os.path.dirname(__file__), r"..\RenderService\input\audio"
                    )
                ),
                str(file_path).rsplit(os.sep, 1)[-1],
            ).split(".")[0]
            + ".mp3",
        )
        return
    file_name = os.path.basename(file_path)

    destination_folder = os.path.normpath(
        os.path.join(os.path.dirname(__file__), r"..\RenderService\input\audio")
    )

    if not os.path.exists(file_path):
        log_message(f"File '{file_path}' không tồn tại.")
        return

    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)

    try:
        shutil.copy(file_path, os.path.join(destination_folder, file_name))
        log_message(f"File '{file_name}' đã được đưa vào input.")
    except Exception as e:
        log_message(f"Lỗi khi copy file: {e}")


def log_message(message, level="INFO"):
    previous_frame = inspect.currentframe().f_back
    (
        filename,
        line_number,
        function_name,
        lines,
        index,
    ) = inspect.getframeinfo(previous_frame)

    caller_filename = os.path.basename(filename)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    if level == "INFO":
        logging.info(f"{caller_filename}: {message}")
    elif level == "ERROR":
        logging.error(f"{caller_filename}: {message}")
    else:
        raise ValueError("Invalid log level. Please use 'INFO' or 'ERROR'.")


def convert_m4b_to_mp3(input_file, output_file):
    log_message("Đang chuyển đổi từ m4b sang mp3....")
    ffmpeg_path = os.path.join(os.getcwd(), "bin", "ffmpeg")
    result = subprocess.run(
        [ffmpeg_path, "-i", input_file, "-acodec", "libmp3lame", output_file],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return result.returncode


def prepare_job_before_receive():
    try:
        current_directory = os.getcwd()

        audio_input_directory = os.path.join(
            current_directory, "../RenderService/input/audio"
        )

        video_input_directory = os.path.join(
            current_directory, "../RenderService/input/video"
        )

        temp_input_directory = os.path.join(
            current_directory, "../RenderService/input/audio/temp"
        )

        video_tmp_mp4 = os.path.join(current_directory, "../RenderService/input")
        output_dir = os.path.join(current_directory, "../RenderService/output")

        for directory in [
            audio_input_directory,
            video_input_directory,
            temp_input_directory,
            video_tmp_mp4,
            output_dir,
        ]:
            for filename in os.listdir(directory):
                file_path = os.path.join(directory, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
    except Exception as e:
        log_message(f"Error deleting files: {e}")


def get_audio_duration_hours(file_path):
    try:
        audio = MP3(file_path)
        duration_seconds = audio.info.length
        duration_hours = (
            duration_seconds / 3600
        )  # Convert duration from seconds to hours
        return duration_hours
    except Exception as e:
        print(f"Error: {e}")
        return None


def split_audio(input_file, output_pattern, segment_duration_minutes):
    try:
        segment_duration_seconds = int(segment_duration_minutes) * 60

        ffmpeg_path = os.path.join(os.getcwd(), "bin", "ffmpeg")

        subprocess.run(
            [
                ffmpeg_path,
                "-i",
                input_file,
                "-f",
                "segment",
                "-segment_time",
                str(segment_duration_seconds),
                "-c",
                "copy",
                output_pattern,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError as e:
        log_message(f"Lỗi khi cắt video: {e}", level="ERROR")


def move_to_result(job_name):
    result_mp4s = sorted(glob.glob("../RenderService/output/*"))
    os.makedirs("../Job_Result/" + job_name, exist_ok=True)
    for mp4 in result_mp4s:
        shutil.move(mp4, "../Job_Result/" + job_name)


def save_job_to_file(job_path):
    try:
        with open("job_without_jpg.txt", "a", encoding="utf-8") as file:
            file.write(r"Sender_Local.exe " + job_path + "\n")
            log_message(f"{job_path} đã được lưu vào file để chạy lại!")
    except FileNotFoundError:
        with open("job_without_jpg.txt", "w", encoding="utf-8") as file:
            file.write(r"Sender_Local.exe " + job_path + "\n")
            log_message(f"{job_path} đã được lưu vào file để chạy lại!")


def join_all_audio(audio_list, output_file):
    mp3_list = []
    m4b_list = []

    remove_mp3 = False

    ffmpeg_path = os.path.join(os.getcwd(), "bin", "ffmpeg")

    # Separate mp3 and m4b files
    for audio_file in audio_list:
        if audio_file.endswith(".mp3"):
            mp3_list.append(audio_file)
        elif audio_file.endswith(".m4b"):
            m4b_list.append(audio_file)

    for m4b_file in m4b_list:
        log_message(f"Đang chuyển {m4b_file} sang mp3....")
        mp3_file = (
            os.path.normpath(
                os.path.join(os.path.dirname(__file__), r"..\RenderService\input\audio")
            )
            + "\\"
            + os.path.splitext(os.path.basename(m4b_file))[0]
            + ".mp3"
        )
        convert_m4b_to_mp3(m4b_file, mp3_file)
        mp3_list.append(mp3_file)
        log_message(f"Chuyển thành công {m4b_file} sang mp3")
        remove_mp3 = True

    mp3_list.sort(key=lambda x: int("".join(filter(str.isdigit, x))))

    log_message("Đang tiến hành gộp tất cả mp3 thành 1 audio...")

    mp3_list_ = mp3_list.copy()

    mp3_list[:] = [
        (lambda string: string.replace("'", r"'\''"))(path) for path in mp3_list
    ]

    mp3_list = [r"file '" + file + r"'" for file in mp3_list]

    audio_list_txt = (
        os.path.normpath(os.path.join(os.path.dirname(__file__), r"..\RenderService"))
        + "\\"
        + "audio_list.txt"
    )

    with open(audio_list_txt, "w", encoding="utf-8") as f:
        for mp3 in mp3_list:
            f.write(f"{mp3}\n")
        f.close()

    current_dir = os.getcwd()

    os.chdir(
        os.path.normpath(os.path.join(os.path.dirname(__file__), r"..\RenderService"))
    )
    command = [
        "./bin/ffmpeg",
        "-f",
        "concat",
        "-safe",
        "0",
        "-i",
        "audio_list.txt",
        "-c",
        "copy",
        f"./input/audio/{output_file}",
    ]
    subprocess.run(command, check=True)
    os.chdir(current_dir)

    if remove_mp3:
        for mp3 in mp3_list_:
            os.remove(mp3)


def get_job_result():
    return os.listdir("../Job_Result")
