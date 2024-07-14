import sys

sys.path.insert(0, "../MASTER")

import Common
import GUI_Service
import os
import glob
import subprocess
import shutil
from PIL import Image

is_there_is_cut_audio = False


def resize_image_to_720p(image_path):
    image = Image.open(image_path)
    target_width = 1280
    target_height = 720

    scale = max(target_width / image.width, target_height / image.height)
    new_width = target_width
    new_height = target_height

    new_width = round(image.width * scale)
    new_height = round(image.height * scale)

    resized_image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
    if resized_image.mode == "RGBA":
        resized_image = resized_image.convert("RGB")

    output_path = os.path.join(os.path.dirname(image_path), "image.jpg")
    resized_image.save(output_path)
    return output_path


def create_video_from_jpg():
    Common.log_message("Tiến hành tạo video từ file jpg")
    jpg_files = glob.glob("./input/video/*")
    if jpg_files:
        jpg_file_after = resize_image_to_720p(jpg_files[0])

        ffmpeg_cmd = [
            "./bin/ffmpeg.exe",
            "-loop",
            "1",
            "-i",
            jpg_file_after,
            "-c:v",
            "libx264",
            "-b:v",
            "192K",
            "-t",
            "4",
            "-s",
            "1280x720",
            "-pix_fmt",
            "yuv420p",
            "./input/video/audio_video_only.mp4",
        ]
        subprocess.run(
            ffmpeg_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
        )


def get_mp3_files(directory):
    mp3_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".mp3"):
                mp3_files.append(os.path.join(root, file))
    return mp3_files


def join_audio_and_video():
    Common.log_message("Tiến hành gộp audio và video....")
    video_files = sorted(glob.glob("./input/video/*.mp4"))
    audio_files = sorted(glob.glob("./input/audio/*.mp3"))
    output_video_name = (
        r"./output/" + audio_files[0].split("\\")[-1].rsplit(".", 1)[0] + ".mp4"
    )
    print(output_video_name)
    subprocess.run(
        [
            "./bin/ffmpeg.exe",
            "-i",
            audio_files[0],
            "-i",
            video_files[0],
            "-c",
            "copy",
            output_video_name,
        ]
    )
    os.remove(video_files[0])
    os.remove(audio_files[0])


def multiple_audio_handling():
    audio_files = sorted(glob.glob("./input/audio/temp/*.mp3"))
    for audio_file in audio_files:
        shutil.move(audio_file, "./input/audio")
        create_video_from_jpg()
        Common.log_message("Tạo video từ JPG thành công")
        Common.log_message("Tiến hành render......")
        command = ["powershell.exe", "-File", "run.ps1"]
        subprocess.run(command, check=True)
        join_audio_and_video()


if __name__ == "__main__":
    mp3_files = get_mp3_files(r"input/audio/")
    mp3_length = -1
    if len(mp3_files) == 1:
        mp3_length = Common.get_audio_duration_hours(mp3_files[0])
        Common.log_message(f"Audio có thời lượng: {round(mp3_length, 2)} tiếng")
        audio_cut_duration = ""

        if Common.WORKING_MODE == "MANUAL":
            audio_cut_duration = GUI_Service.get_audio_cut_time(
                round(mp3_length, 2), " ".join(sys.argv[1:])
            )

        if Common.WORKING_MODE == "AUTO":
            audio_cut_duration = "300"

        if int(mp3_length) < 5:
            audio_cut_duration = ""

        if audio_cut_duration is not None and audio_cut_duration not in "":
            Common.log_message(
                f"Tiến hành cắt audio theo thời lượng: {audio_cut_duration} phút"
            )
            os.makedirs(r"input/audio/temp/", exist_ok=True)

            Common.split_audio(
                mp3_files[0],
                mp3_files[0]
                .replace("input/audio/", "input/audio/temp/")
                .replace(".mp3", "_%03d.mp3"),
                audio_cut_duration,
            )
            os.remove(mp3_files[0])
            is_there_is_cut_audio = True

    # trường hợp ko cắt
    if is_there_is_cut_audio == False and int(mp3_length) < 12:
        Common.log_message("Không cắt audio, và audio có thời lượng < 12 tiếng")
        Common.log_message("Tiến hành render")
        create_video_from_jpg()
        Common.log_message("Tạo video từ JPG thành công")
        Common.log_message("Tiến hành render......")
        command = ["powershell.exe", "-File", "run.ps1"]
        subprocess.run(command, check=True)
        join_audio_and_video()

    if is_there_is_cut_audio == False and int(mp3_length) >= 12:
        Common.log_message(
            "Lỗi, audio lớn hơn 12 tiếng, cần phải cắt để tiếp tục", level="ERROR"
        )
        GUI_Service.audio_must_be_cut(" ".join(sys.argv[1:]))
        os._exit()

    if is_there_is_cut_audio:
        Common.log_message("Tiến hành render")
        multiple_audio_handling()
