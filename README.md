# Space inside us
The service for sending in Telegram channel photos from api of SpaceX and NASA.

It downloads: 
1. images from Spacex flight #108.
1. 10 random images from NASA APOD.
1. images from NASA EPIC for the last day.

Then sends images to a Telegram group with a timeout in 1 day. User can change this parametr int the `.env` file

## Install
Python3 should be already installed. Then use pip (or pip3, if there is a conflict with Python2) to install dependencies:
```
pip install -r requirements.txt
```
## Env Settings
Create `.env` from `.env.Example`
1. NASA_TOKEN - str, your toke from NASA api. Create it your own [here](https://api.nasa.gov/)
1. IMAGES_DIR - str, dir path for images
1. BOT_TOKEN - str, your Telegram bot token. Use [BotFather](https://t.me/BotFather) to generate it.
1. CHAT_ID - str, name of your group with a bot. Example `@myGroupForSpace`
1. TIMEOUT_SEC - Optional(str), timeout for sending images in seconds, default: 1 day

## Start
```
python main.py
```