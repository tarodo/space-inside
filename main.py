from datetime import datetime, date
from os import walk
from time import sleep

import requests
from pathlib import Path
from environs import Env
import telegram

env = Env()
env.read_env()

NASA_TOKEN = env('NASA_TOKEN')
IMAGES_DIR = env('IMAGES_DIR')
BOT_TOKEN = env('BOT_TOKEN')
CHAT_ID = env('CHAT_ID')
TIMEOUT = env.int('TIMEOUT', 60*60*24)


def get_image(url: str, file_path: str, params=None) -> None:
    response = requests.get(url, params=params)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_photos_by_flight(flight_id: int) -> None:
    flight_url = f'https://api.spacexdata.com/v3/launches/{flight_id}'
    response = requests.get(flight_url)
    response.raise_for_status()

    dir_path = f'{IMAGES_DIR}/spacex'
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    launch = response.json()
    image_url: str
    for image_url in launch['links']['flickr_images']:
        image_name = Path(image_url).name
        filename = f'{dir_path}/{image_name}'
        get_image(image_url, filename)


def get_apod_images(image_count: int = 10) -> None:
    apod_url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': NASA_TOKEN,
        'count': image_count
    }
    dir_path = f'{IMAGES_DIR}/apod'
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    response = requests.get(apod_url, params=params)
    response.raise_for_status()
    apod_heap = response.json()
    image_url: str
    for apod_element in apod_heap:
        if 'url' not in apod_element:
            continue
        image_url = apod_element['url']
        image_name = Path(image_url).name
        filename = f'{dir_path}/{image_name}'
        get_image(image_url, filename)


def generate_epic_link(image_date: date, image_name: str) -> str:
    url = f'https://api.nasa.gov/EPIC/archive/natural/{image_date.year}/{image_date.month:02d}/{image_date.day:02d}' \
          f'/png/{image_name}.png'
    return url


def get_last_epic() -> None:
    url = 'https://api.nasa.gov/EPIC/api/natural'
    params = {
        'api_key': NASA_TOKEN
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    for epic_data in response.json():
        epic_date = datetime.fromisoformat(epic_data['date']).date()
        image_url = generate_epic_link(epic_date, epic_data['image'])

        dir_path = f'{IMAGES_DIR}/epic'
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        filename = f'{dir_path}/{epic_data["image"]}.png'
        get_image(image_url, filename, params=params)


def give_image():
    for (dir_path, dir_names, filenames) in walk(IMAGES_DIR):
        for filename in filenames:
            yield f'{dir_path}\\{filename}'


def send_it_all():
    bot = telegram.Bot(token=BOT_TOKEN)

    images = give_image()
    while True:
        bot.send_photo(chat_id=CHAT_ID, photo=open(next(images), 'rb'))
        sleep(TIMEOUT)


if __name__ == '__main__':
    get_photos_by_flight(108)
    get_apod_images()
    get_last_epic()

    send_it_all()
