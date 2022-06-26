from pytube import YouTube
import os
from pydub import AudioSegment

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
    startTime = startSec*1000
    endTime = endSec*1000

    song = AudioSegment.from_file(f"{FileName}.mp3")
    song = song[startTime:endTime]

    song.export(f"{outFile}.mp3", format='mp3')



