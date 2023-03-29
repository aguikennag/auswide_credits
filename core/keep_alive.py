import requests
import time
import random

while True :
    requests.get("https://www.google.com")

    print('pinged..')
    time.sleep(random.randrange(30,60))