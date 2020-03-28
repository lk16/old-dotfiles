import click
import requests
import os
import datetime
import sys
import json
import re
import random
import subprocess

def load_config(section):
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "conf.json")
    return json.load(open(config_file, "r"))[section]


def get_battery():
    return 'TODO'

def get_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def get_weather():
    conf = load_config("weather")
    location = conf["location"]
    api_key = conf["api_key"]

    url = "https://api.openweathermap.org/data/2.5/weather?q={}&APPID={}&units=metric".format(location, api_key)

    r = requests.get(url)
    data = json.loads(r.text)

    temp = int(data["main"]["temp"])
    weather_group = list([item["main"] for item in data["weather"]])[0]

    weather_chars = {
        "Thunderstorm": "🌩 ",
        "Drizzle": "🌧 ",
        "Rain": "🌧 🌧 ",
        "Snow": "🌨 ",
        "Clear": "☼ ",
        "Clouds": "🌥️ "
    }

    try:
        weather = weather_chars[weather_group]
    except KeyError:
        weather = weather_group

    return str(temp) + "°C " + weather

def get_statusbar():

    items = [
        get_spotify_song,
        get_weather,
        get_battery,
        get_date,
    ]

    color_headers = [
        '#[bg=colour238]#[fg=colour11]',
        '#[bg=colour233]#[fg=colour11]'
    ]

    statusbar = ""
    for i, item in enumerate(items):
        statusbar += color_headers[i%len(color_headers)] + ' ' + item() + ' '

    print(statusbar, end='')



def get_spotify_song():
    command = ['dbus-send', '--print-reply', '--dest=org.mpris.MediaPlayer2.spotify',  '/org/mpris/MediaPlayer2',
        'org.freedesktop.DBus.Properties.Get', 'string:org.mpris.MediaPlayer2.Player', 'string:Metadata']
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    output = process.stdout.decode('utf-8')
    output = output.replace('\n', '')

    try:
        artist = re.search('string "xesam:artist".*?string "(.*?)"', output).group(1)
        title = re.search('string "xesam:title".*?string "(.*?)"', output).group(1)
    except Exception:
        artist = ""
        title = ""

    return "{} / {}".format(artist, title)