import srt_utils
import video_utils
from termcolor import colored
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from argparse import ArgumentParser
from requests.utils import unquote
import os
from tqdm import tqdm
import threading
from collections import deque

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
        self.driver = webdriver.Firefox(options=options, executable_path=r'geckodriver.exe', service_log_path="log.tmp")

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


        for i in tqdm(data, desc=f"Cutting Files From {idx}"):
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

        print(
            colored(
                f"\n[info] [{idx}] completed downloading video Files",
                color='green'
            )
        )

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

        print(
            colored(
                f'\n[info] completed processing {idx} batch',
                color='green'
            )
        )

class Workers():
    def __init__(self, sub):
        self.sub = sub
        self.threads = self._CreateProcesses()

    def _getValue(self, idx):
        self.sub[idx]

    def _CreateProcesses(self):
        threads = deque([])

        for i in range(len(self.sub)):

            process = threading.Thread(
                target=self._getValue,
                args=(i, ),
                name=str(i),
                daemon=True
            )

            threads.append(
                process
            )

        return threads

    def run(self):
        #start the threads
        for thread in self.threads:
            thread.start()

        #wait till all the threads are completed
        for thread in self.threads:
            thread.join()


#initilizing class
sub = SubTitles("YT-CORPUS")

#using threading for multiprocesses
threadWorker = Workers(sub)
threadWorker.run()