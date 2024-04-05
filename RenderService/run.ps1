# $audioDuration = $args[0]
# $audioSplitDuration = $args[1]

$video = Get-ChildItem .\input\video *.mp4 | Select FullName, duration | Group-Object -Property fullname -AsHashTable
$map_video_duration = @{}
foreach($key in $video.Keys)
{
    $value = .\bin\ffprobe -i $key -show_entries format=duration -v quiet -of csv="p=0"
    $map_video_duration.add( $key, $value )
	.\bin\ffmpeg -i $key -c copy -bsf:v h264_mp4toannexb -f mpegts "$($key).ts"
}

Clear-Content -Path .\audio_list.txt
$audio = Get-ChildItem .\input\audio *.mp3 | Select FullName | Sort-Object -Property FullName
$total_audio_duration = 0.0;

foreach($audio_path in $audio)
{
    $audio_duration = .\bin\ffprobe -i $audio_path.FullName -show_entries format=duration -v quiet -of csv="p=0"
    Add-Content -Path .\audio_list.txt -Value "file '$($audio_path.FullName)'"
    $total_audio_duration = $total_audio_duration + $audio_duration
}

# .\bin\ffmpeg -f concat -safe 0 -i audio_list.txt -c copy .\input\audio.mp3

Clear-Content -Path .\video_list.txt
$total_video_duration = 0.0;
Do {
    $key = ($map_video_duration.Keys | Get-Random -Count 1)
    $total_video_duration = $total_video_duration + $map_video_duration[$key]
    Add-Content -Path .\video_list.txt -Value "file '$($key)'.ts"
} while (($total_audio_duration - $total_video_duration) -gt 0)


Write-Host "total audios duration $total_audio_duration"
Write-Host "total videos duration $total_video_duration"

.\bin\ffmpeg -f concat -safe 0 -i video_list.txt -c copy -an .\input\video_without_audio.mp4

Get-ChildItem -Path .\input\video\* -Exclude *.jpg | Remove-Item

.\bin\ffmpeg -ss 00:00:00.000 -i .\input\video_without_audio.mp4 -t $total_audio_duration -c copy .\input\video\video_without_audio_fix_duration.mp4

Remove-Item -Path .\input\video_without_audio.mp4

# & .\split-video.ps1 $audioDuration $audioSplitDuration

# Write-Host "Start merge video and audio"
# .\bin\ffmpeg -i .\input\video_without_audio_fix_duration.mp4 -i .\input\audio.mp3 -c copy .\output\final_output.mp4

# Remove-Item -Path .\input\audio.mp3
# Remove-Item -Path .\input\video_without_audio_fix_duration.mp4
# Remove-Item -Path .\input\video_without_audio.mp4
# Remove-Item -Path .\input\video\*.ts
# Write-Host "End merge video and audio"