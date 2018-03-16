from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

import os
import json
from time import sleep
import string
import random
import datetime
try:
    from bs4 import BeautifulSoup as bs
except Exception as e:
    print(e)


app = Flask(__name__)

cursed = []


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # Ignore messages sent by self
    if data['name'] != 'Mr. Roboto':
        # send_message(str(data))
        if data['text'][0] == "!":
            process_command(data)       # TODO: consider starting each command process in a new thread

        if data['name'] in cursed:
            send_message('May your soul burn forever in fiery torment!')
        
        if 'club today?' in data['text']:
            today = datetime.datetime.today()
            if today.weekday() == 4:
                timeuntil = today.time() - datetime.time(14, 15)
                send_message('Yes! Coding Club starts in {} hours, {} minutes, {} seconds!'.format(timeuntil.hour, timeuntil.minute, timeuntil.second))
            else:
                send_message('No!!!!!!!!!!!!!!!!!!!')

    return "ok", 200


def process_command(data):
    command = data['text'][1:].split(' ')[0]
    body = data['text'][1+len(command):].strip()

    print(command, body)

    if command == 'joke':
        # send_message('Where did Tigger look for Pooh?')
        # sleep(2)
        # send_message('In the toilet!')
        send_message(
            '\"You should make !repeat allow arbitrary string echoing, and !exec allow arbitrary code execution. :-)\"')

    elif command == 'randimg':
        max_images = 5
        num_images = int(body) if body.isdigit() else 1
        if num_images > max_images:
            send_message('You may not request more than {} images at a time.'.format(max_images))
            num_images = max_images

        for _ in range(num_images):
            image_url = random_imgur_url()
            send_message(image_url)
            
    elif command == 'echo':
        send_message(body)

    elif command == 'eval':
        try:
            msg = str(eval(body))
        except Exception as e:
            msg = 'Error: {}'.format(e)
        send_message(msg)

    elif command == 'define':
        word = body
        url = "http://www.dictionary.com/browse/{0}?s=t".format(word)
        print("url: " + url)
        html = urlopen(url)
        soup = bs(html, "html.parser")
        definitions = soup.findAll("div", {"class": "def-content"})
        msg = definitions[0].text
        send_message(msg)

    # elif initial.lower().startswith("urban definition of"):
    #     word = initial[len("urban definition of") + 1:].replace(" ", "+")
    #     url = "http://www.urbandictionary.com/define.php?term={0}".format(word)
    #     print("url: " + url)
    #     html = urllib.request.urlopen(url)
    #     soup = bs(html, "html.parser")
    #     definitions = soup.findAll("div", {"class": "meaning"})
    #     for d in definitions:
    #         say(d.text + " Would you like to hear another definition?")
    #         answer = get_speech_google()
    #         if not any(a in answer.lower() for a in affirmatives):
    #             break

    elif command == 'curse':
        target = body
        cursed.append(target)
        send_message('{} has been cursed!'.format(target))

    elif command == 'repent':
        target = data['name']
        if target in cursed:
            cursed.remove(target)
        send_message('You have been forgiven.')



def send_message(msg):
    if len(msg) > 1000:
        msg = msg[:997] + '...'

    url = 'https://api.groupme.com/v3/bots/post'
    data = {
        'bot_id': os.getenv('GROUPME_BOT_ID'),
        'text': msg,
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()


def send_image(image):
    image_url = upload_image(image)['url']
    print(image_url)


def upload_image(image):
    url = 'https://image.groupme.com/pictures'
    data = {
        'file': image
    }
    request = Request(url, urlencode(data).encode())
    json = urlopen(request).read().decode()
    image_urls = json['payload']
    print(image_urls)
    return image_urls


def random_imgur_url():
    base_url = 'http://i.imgur.com'
    extensions = ['jpg', 'png', 'gif']
    id_symbols = string.digits + string.ascii_letters

    max_attempts = 100

    for _ in range(max_attempts):
        image_id = ''.join(random.choice(id_symbols) for _ in range(5))
        image_extension = random.choice(extensions)
        image_url = '{}/{}.{}'.format(base_url, image_id, image_extension)
        # Test if valid image url
        img = urlopen(image_url).read()
        if len(img) != 503:     # length of 'removed.png'
            return image_url
