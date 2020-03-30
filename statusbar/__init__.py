import time
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
import praw

class SkipItemException(Exception):
    pass

config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..", "conf.json")
cache_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), ".cache.json")

def load_config(section):
    return json.load(open(config_file, "r"))[section]

def load_cache():
    try:
        return json.load(open(cache_file, "r"))
    except FileNotFoundError:
        return {}

def write_cache(cache):
    json.dump(cache, open(cache_file, "w"))



class StatusBarItem(object):
    def expiry(self):
        return -1


class Battery(StatusBarItem):
    def get_text(self):
        command = ['acpitool', '-B']

        try:
            process = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as e:
            raise SkipItemException("acpitool is not installed") from e

        output = process.stdout.decode('utf-8').split('\n')

        marker = 'Remaining capacity'

        for line in output:
            if marker in line:
                percentage = round(float(line.split(' ')[-1][:-1]))
                return f'{percentage}%'

        raise ValueError(f'Marker "{marker}" not found')


class Date(StatusBarItem):
    def get_text(self):
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M')

class Weather(StatusBarItem):

    def expiry(self):
        return 60

    def get_text(self):
        conf = load_config("weather")
        location = conf["location"]
        api_key = conf["api_key"]

        r = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&APPID={api_key}&units=metric")

        r.raise_for_status()

        data = json.loads(r.text)

        temp = int(data["main"]["temp"])
        weather = list([item["main"] for item in data["weather"]])[0]

        return f'{temp}°C {weather}'

class Spotify(StatusBarItem):

    def get_text(self):
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

class Reddit(StatusBarItem):

    def expiry(self):
        return 60

    def get_text(self):
        # See https://praw.readthedocs.io/en/latest/getting_started/authentication.html#obtain-the-authorization-url
        # and check "using a saved refresh token" to get below credentials

        conf = load_config("reddit")

        reddit = praw.Reddit(
            client_id=conf['client_id'],
            client_secret=conf['client_secret'],
            refresh_token=conf['refresh_token'],
            user_agent='linux:dotfiles:v0.0.0')


        me = reddit.user.me()
        karma = me.link_karma + me.comment_karma
        unread = len(list(reddit.inbox.unread(limit=None)))

        text = str(karma)

        if unread > 0:
            text += f' ({unread})'

        return text

statusbar_classes = {
    "battery": Battery,
    "date": Date,
    "reddit": Reddit,
    "spotify": Spotify,
    "weather": Weather,
}

def get_statusbar():

    conf = load_config('statusbar')
    cache = load_cache()

    items = conf["items"]

    color_headers = [
        '#[bg=colour238]#[fg=colour11]',
        '#[bg=colour233]#[fg=colour11]'
    ]

    statusbar = []

    for item in items:

        try:
            statusbar_item = statusbar_classes[item]()
            now = int(time.time())

            cache_item = cache.get(item, {})

            if (not cache_item) or (now > cache_item['expiry']):
                item_text = statusbar_item.get_text()
                expiry = statusbar_item.expiry()

                if expiry != -1:
                    cache[item] = {
                        'expiry': now + expiry,
                        'text': item_text
                    }

            else:
                item_text = cache_item['text']

            header = color_headers[len(statusbar)%len(color_headers)]
            print(f'Running {item}', file=sys.stderr)

        except SkipItemException as e:
            print(f'Skipping {item}', file=sys.stderr)
            continue
        except Exception:
            traceback.print_exc(file=sys.stderr)
            continue

        statusbar.append(f'{header} {item_text} ')

    write_cache(cache)
    print(''.join(statusbar), end='')


