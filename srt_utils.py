import requests
from collections import deque
import json
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
import time

#check status
def check_status(response, url):
    if response.status_code != 200:
        time.sleep(2)
        response = requests.get(url)
        if response.status_code != 200:
            raise requests.exceptions.RequestException(response.text)

#encode the links
def encodeLinks(urls: list):
    out = deque([])
    for i in urls:
        out.append(
            {
                "url": requests.utils.quote(i, safe=''),
                "id": i.split("=")[1]
            }
        )

    return out

#get the subtitles
def getSRT(link: dict, driver):
    url = f"https://www.downloadyoutubesubtitles.com/?u={link['url']}"
    
    driver.get(url)

    try:
        WebDriverWait(driver, 5
            ).until_not(EC.presence_of_element_located((By.ID, "loader-ani")))

    except exceptions.TimeoutException:
        pass
    
    url = f"https://www.downloadyoutubesubtitles.com/get2.php?i={link['id']}&format=srt&hl=a.en&a=&removeTags=1"
    response = requests.get(url)
    check_status(response, url)

    content = response.text.replace("\n\n\n", "@@@").replace("\n", "").replace("@@@", "\n").replace("\r", "\n").rstrip().split("\n\n")

    return content

#get the timestamps
def getTimeStamp(inputs1: str,
                 inputs2: str,
                 second_id=False):

    inputs1 = inputs1.split(" --> ")[0]
    inputs1 = inputs1.split(",")[0].split(":")

    hrs1 = int(inputs1[0])*(60*60)
    min1 = int(inputs1[1])*60
    sec1 = int(inputs1[2])

    inputs2 = inputs2.split(" --> ")[1 if second_id else 0]
    inputs2 = inputs2.split(",")[0].split(":")

    hrs2 = int(inputs2[0])*(60*60)
    min2 = int(inputs2[1])*60
    sec2 = int(inputs2[2])

    return hrs1+min1+sec1, hrs2+min2+sec2

#serialize and ordinate it
def SerializeSRT(content):
    out = deque([])

    for i in range(len(content)):
        id = content[i].split("\n")[0]

        if i+1 == len(content):
            startTime, endTime = getTimeStamp(
                content[i].split("\n")[1],
                content[i].split("\n")[1],
                second_id=True
            )

        else:
            startTime, endTime = getTimeStamp(
                content[i].split("\n")[1],
                content[i+1].split("\n")[1]
            )

        transcription = content[i].split("\n")[2]

        out.append(
            {
                "id": int(id),
                "startTime": startTime,
                "endTime": endTime,
                "transcription": transcription
            }
        )
    
    return list(out)

#save subtitles in a json file
def save(dict: list, id: str):
    final = json.dumps(dict, indent=2)

    with open(f"{id}.json", "w") as f:
        f.write(final)

