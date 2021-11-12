import requests
from pathlib import Path
from environs import Env

env = Env()
env.read_env()

NASA_TOKEN = env('NASA_TOKEN')


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix[1:]


def get_image(url: str, file_path: str) -> None:
    response = requests.get(url)
    response.raise_for_status()

    with open(file_path, 'wb') as file:
        file.write(response.content)


def get_photos_by_flight(flight_id: int, dir_path: str) -> None:
    flight_url = f'https://api.spacexdata.com/v3/launches/{flight_id}'
    response = requests.get(flight_url)
    response.raise_for_status()

    launch = response.json()
    image_url: str
    for image_url in launch['links']['flickr_images']:
        image_name = Path(image_url).name
        filename = f'{dir_path}/{image_name}'
        get_image(image_url, filename)


def get_apod_images(dir_path: str, image_count: int = 2) -> None:
    apod_url = 'https://api.nasa.gov/planetary/apod'
    params = {
        'api_key': NASA_TOKEN,
        'count': image_count
    }
    dir_path += '/apod'
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


def get_last_epic(nasa_token: str) -> None:
    pass


if __name__ == '__main__':
    image_dir = 'images'
    Path(image_dir).mkdir(exist_ok=True)
    img_url = 'https://upload.wikimedia.org/wikipedia/commons/3/3f/HST-SM4.jpeg'
    # get_photos_by_flight(108, image_dir)
    get_apod_images(image_dir)
