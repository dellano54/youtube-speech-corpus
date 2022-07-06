'''
Author: Dellano Samuel Fernandez
Date: 2.07.2022
Name: yt-speech-Corpus
Desc: For generating speech to text data from youtube using youtube's auto speech-text
      AI to train a much powerful AI capable of generating correct speech-to-text predictions
      with reduction in WER (Word Error Rate) and low time complexity curently the 
      speech-2-text-medium transformer model takes about 0.6 sec for the transcription of 12 sec audio
      Currently i dont have enough computational power to run this but i hope someday i will run this 
      and train a open source model which can perform or even out perform commercial google 
      speech-to-text model

'''

import srt_utils
import video_utils
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from argparse import ArgumentParser
from requests.utils import unquote
import os
from tqdm import tqdm
from multiprocessing import Pool

parser = ArgumentParser()

parser.add_argument("LinkFile", type=str, help="file which contains the links")

args = parser.parse_args()

print(colored(
    "[info] completed imports",
    color='green'
))

class SubTitles():
    def __init__(self, datasetFolder: str):
        self.datasetFolder = datasetFolder
        self.temp_yt = "temp_yt"

        #initilize web driver firefox headless
        print(
            colored(
                "[info] initilizing program...",
                color='yellow'
            )
        )

        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(options=options, service_log_path="log.tmp")

        #get the youtube links from the file
        with open(args.LinkFile, "r") as f:
            self.links = f.read().split("\n")


        #get the ids and URL encoded links in a deque format. Format of the output [{url: 'url', id: 'youtube id'}, {url: 'url', id: 'youtube id'}]
        self.links = srt_utils.encodeLinks(self.links)

        print(
            colored(
                "[info] completed initilizing sequence",
                color='green'
            )
        )

    @staticmethod
    def _cutAudios(DownPath, AudioPath, data, idx):

        try:
            os.mkdir(
                os.path.join(
                    AudioPath,
                    "Audio"
                )
            )
        except FileExistsError:
            pass

        with tqdm(total=len(data), position=idx, desc=f"Cutting Files From {idx}") as pbar:
            for i in data:
                Audid, startTime, endTime, _ = i.values()

                outFileName = os.path.join(
                    AudioPath,
                    "Audio",
                    str(Audid)
                )

                video_utils.cutAudio(
                    DownPath,
                    outFileName,
                    startTime,
                    endTime
                )

                pbar.update(1)



    def __len__(self):
        return len(self.links)

    def __getitem__(self, idx):
        data = self.links[idx]
        
        #get the url and id
        url, id = data.values()
        url = unquote(url)

        #download the subtitles
        data = srt_utils.SerializeSRT(
            srt_utils.getSRT(
                data,
                self.driver
            )
        )

        print(
            colored(
                f"\n[info] [{idx}] Downloaded Subtitles successfully",
                color='green'
            )
        )

        #make the dirs required
        Downpath = os.path.join(
            os.getcwd(),
            self.temp_yt,
            id
        )

        path = os.path.join(
            os.getcwd(),
            self.datasetFolder,
            id
        )

        try:
            os.mkdir(path, mode=777)
        except FileExistsError:
            pass

        
        #download the youtube audio
        video_utils.DownloadAudio(
            url,
            Downpath
        )

        '''

        print(
            colored(
                f"\n[info] [{idx}] completed downloading video Files",
                color='green'
            )
        )
        '''

        self._cutAudios(Downpath,
                        path,
                        data,
                        idx)

        

        srt_utils.save(
            data,
            os.path.join(
                path,
                "meta"
            )
        )

        '''

        print(
            colored(
                f'\n[info] completed processing {idx} batch',
                color='green'
            )
        )

        '''


def get_values(idx):
    sub[idx]


#initilizing class
sub = SubTitles("YT-CORPUS")

#using threading for multithread processing
with Pool(5) as p:
    p.map(get_values, range(len(sub)))
    p.close()
    p.join()