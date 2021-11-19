from datetime import datetime, date
from os import walk
from time import sleep

import requests
from pathlib import Path
from environs import Env
import telegram


def download_image(url: str, file_path: str, params=None) -> None:
    response = requests.get(url, params=params)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_photos_by_flight(flight_id: int, images_dir: str) -> None:
    flight_url = f'https://api.spacexdata.com/v3/launches/{flight_id}'
    response = requests.get(flight_url)
    response.raise_for_status()

    dir_path = f'{images_dir}/spacex'
    Path(dir_path).mkdir(parents=True, exist_ok=True)

    launch = response.json()
    for image_url in launch['links']['flickr_images']:
        image_name = Path(image_url).name
        filename = f'{dir_path}/{image_name}'
        download_image(image_url, filename)


def get_apod_images(nasa_token: str, images_dir: str, image_count: int = 10) -> None:
    apod_url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': nasa_token,
        'count': image_count
    }
    dir_path = f'{images_dir}/apod'
    Path(dir_path).mkdir(parents=True, exist_ok=True)
    response = requests.get(apod_url, params=params)
    response.raise_for_status()
    apod_heap = response.json()
    for apod_element in apod_heap:
        if 'url' not in apod_element:
            continue
        image_url = apod_element['url']
        image_name = Path(image_url).name
        filename = f'{dir_path}/{image_name}'
        download_image(image_url, filename)


def generate_epic_link(image_date: date, image_name: str) -> str:
    url = f'https://api.nasa.gov/EPIC/archive/natural/{image_date.year}/{image_date.month:02d}/{image_date.day:02d}' \
          f'/png/{image_name}.png'
    return url


def get_last_epic(nasa_token: str, images_dir: str) -> None:
    url = 'https://api.nasa.gov/EPIC/api/natural'
    params = {
        'api_key': nasa_token
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    for epic_data in response.json():
        epic_date = datetime.fromisoformat(epic_data['date']).date()
        image_url = generate_epic_link(epic_date, epic_data['image'])

        dir_path = f'{images_dir}/epic'
        Path(dir_path).mkdir(parents=True, exist_ok=True)
        filename = f'{dir_path}/{epic_data["image"]}.png'
        download_image(image_url, filename, params=params)


def give_images_paths(images_dir: str):
    for (dir_path, dir_names, filenames) in walk(images_dir):
        for filename in filenames:
            yield Path(dir_path) / filename


def send_images(bot_token: str, chat_id: str, timeout: int, images_dir: str):
    bot = telegram.Bot(token=bot_token)

    image_path = give_images_paths(images_dir)
    while True:
        with open(next(image_path), 'rb') as image_file:
            bot.send_photo(chat_id=chat_id, photo=image_file)
        sleep(timeout)


if __name__ == '__main__':
    env = Env()
    env.read_env()

    get_photos_by_flight(108, env('IMAGES_DIR'))
    get_apod_images(env('NASA_TOKEN'), env('IMAGES_DIR'))
    get_last_epic(env('NASA_TOKEN'), env('IMAGES_DIR'))

    send_images(env('BOT_TOKEN'), env('CHAT_ID'), env.int('TIMEOUT', 60 * 60 * 24), env('IMAGES_DIR'))
