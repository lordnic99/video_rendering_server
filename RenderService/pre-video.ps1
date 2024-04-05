$audioDuration = $args[0]
$audioSplitDuration = $args[1]

$img = Get-ChildItem .\input\video *.jpg | Select FullName

if ($img) {
    .\bin\ffmpeg.exe -loop 1 -i $img.FullName -c:v libx264 -b:v 192K -t 4 -s 1920x1080 -pix_fmt yuv420p ".\input\video\audio_video_only.mp4"
}

& .\run.ps1  $audioDuration $audioSplitDuration