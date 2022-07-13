from fileinput import filename
from pytube import YouTube
import os
import subprocess


Path = os.path.join(
    os.getcwd(),
    "bin"
)

os.environ["PATH"] += os.pathsep + Path

def DownloadAudio(url:str, saveFileName: str):

    yt = YouTube(url)
    video = yt.streams.filter(only_audio=True).first()
    out_file = video.download(output_path=os.path.dirname(saveFileName))

    try:
        os.rename(out_file, f"{saveFileName}.mp3")

    except FileExistsError:
        os.remove(f"{saveFileName}.mp3")
        os.rename(out_file, f"{saveFileName}.mp3")

def cutAudio(FileName: str, outFile: str, startSec: int, endSec: int):
    with open("ffmpeg.log", "a") as f:
        subprocess.call(
            ['ffmpeg', '-i', FileName+".mp3", '-s', str(startSec), '-t', str(endSec-startSec), outFile+".mp3"]
        , stdout=f,
        stderr=subprocess.STDOUT)


