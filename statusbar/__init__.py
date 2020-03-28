import sys
import click
import requests
import os
import datetime
import sys
import json
import re
import random
import subprocess
import traceback

class SkipItemException(Exception):
    pass

def load_config(section):
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "conf.json")
    return json.load(open(config_file, "r"))[section]

def get_battery():
    command = ['acpitool', '-B']

    try:
        process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError as e:
        raise SkipItemException("acpitool is not installed") from e

    output = process.stdout.decode('utf-8')

    marker = 'Remaining capacity'

    for line in output:
        if marker in line:
            percentage = round(float(line.split(' ')[-1][:-1]))
            return f'{percentage}%'

    raise ValueError(f'Marker "{marker}" not found')

def get_date():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

def get_weather():
    conf = load_config("weather")
    location = conf["location"]
    api_key = conf["api_key"]

    r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&APPID={api_key}&units=metric")

    r.raise_for_status()

    data = json.loads(r.text)

    temp = int(data["main"]["temp"])
    weather = list([item["main"] for item in data["weather"]])[0]

    return f'{temp}°C {weather}'

def get_spotify_song():

    command = [
        'dbus-send',
        '--print-reply',
        '--dest=org.mpris.MediaPlayer2.spotify',
        '/org/mpris/MediaPlayer2',
        'org.freedesktop.DBus.Properties.Get',
        'string:org.mpris.MediaPlayer2.Player',
        'string:Metadata'
    ]
    process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if process.returncode != 0:
        raise SkipItemException

    output = process.stdout.decode('utf-8').replace('\n', '')

    artist = re.search('string "xesam:artist".*?string "(.*?)"', output).group(1)
    title = re.search('string "xesam:title".*?string "(.*?)"', output).group(1)

    return "{} / {}".format(artist, title)

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

    statusbar = []
    for i, item in enumerate(items):
        header = color_headers[len(statusbar)%len(color_headers)]

        try:
            item_text = item()
        except SkipItemException as e:
            print(str(e), file=sys.stderr)
            continue
        except Exception:
            traceback.print_exc(file=sys.stderr)
            continue

        statusbar.append(f'{header} {item_text} ')

    print(''.join(statusbar), end='')


