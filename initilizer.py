import os
import wget
import zipfile
import subprocess
import shutil

try:
    os.mkdir("bin", mode=777)
    os.mkdir("YT-CORPUS", mode=777)
    os.mkdir("temp_yt", mode=777)

except FileExistsError:
    pass

if os.name == 'posix':
    subprocess.call(['apt', 'install', 'ffmpeg', 'firefox', 'firefox-geckodriver', '-y'], 
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

    subprocess.call([
        'cp', '/usr/lib/geckodriver', '/usr/bin'
    ],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.STDOUT)

elif os.name == 'nt':
    filename = wget.download(
        "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
        )

    try:
        os.remove("ffmpeg.zip")
    except FileNotFoundError:
        pass
    
    os.rename(
        filename, 
        "ffmpeg.zip"
    )
    

    archive = zipfile.ZipFile('ffmpeg.zip')
    for file in archive.namelist():
        if file.startswith('ffmpeg-master-latest-win64-gpl/bin/'):
            filename = os.path.basename(file)
            source = archive.open(file)
            
            if not filename:
                continue

            target = open(os.path.join(f'bin/{filename}'), "wb")

            with source, target:
                shutil.copyfileobj(source, target)

            target.close()
            source.close()

    archive.close()

    if os.path.exists("bin/geckodriver.exe") == False:
        filename = wget.download(
            "https://github.com/mozilla/geckodriver/releases/download/v0.31.0/geckodriver-v0.31.0-win64.zip"
        )

        try:
            os.remove("gecko.zip")
        except FileNotFoundError:
            pass

        os.rename(filename, "gecko.zip")
        archive = zipfile.ZipFile('gecko.zip')
        archive.extractall('bin/')
        archive.close()

    
    os.remove("gecko.zip")
    os.remove("ffmpeg.zip")

