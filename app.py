from urllib.parse import urlencode
from urllib.request import Request, urlopen

from flask import Flask, request

import os
import json
from time import sleep
import string
import random

app = Flask(__name__)


@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()

    # Ignore messages sent by self
    if data['name'] != 'Mr. Roboto':
        if data['text'][0] == "!":
            process_command(data)       # TODO: consider starting each command process in a new thread

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


def send_message(msg):
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
