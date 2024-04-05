$audioSplitDuration = $args[1]

# $audioSplitDuration = "8"

$VideoPath = (Get-ChildItem .\input\video *.mp4).FullName

Write-Output "-> Video input name: $VideoPath"

# [string]$audioSplitDuration =  [int]$audioSplitDuration*3600

if ($audioSplitDuration -eq "-1") {
    Exit 0
}

.\bin\ffmpeg -i $VideoPath -f segment -segment_time $audioSplitDuration -c copy $VideoPath%03d.mp4

Remove-Item $VideoPath