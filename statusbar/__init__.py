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
import slack

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

class Slack(StatusBarItem):

    def expiry(self):
        return 60

    def get_text(self):
        conf = load_config("slack")

        rtm_client = slack.RTMClient(
        token=conf['token'],
        connect_method='rtm.start'
        )

        @rtm_client.run_on(event="open")
        def on_open(**payload):
            rtm_client.slack_state = payload['data']
            payload['rtm_client'].stop()

        rtm_client.start()

        slack_state = rtm_client.slack_state

        muted_channel_ids = set(slack_state['self']['prefs']['muted_channels'].split(','))

        id_to_username = {}
        for user in slack_state["users"]:
            id_to_username[user["id"]] = user.get("real_name") or user.get("name") or "???"

        output = []

        def get_rating(channel, conf, muted_channel_ids):

            if channel['id'] in muted_channel_ids:
                return 'muted'

            if channel['is_im'] or channel['is_mpim']:
                return 'direct'

            for rating, channels in conf['channel_ratings'].items():
                if rating not in ['good', 'medium', 'bad']:
                    # TODO print warning
                    continue

                if channel['name'] in channels:
                    return rating

            return 'unrated'

        for channel in slack_state['channels'] + slack_state['groups'] + slack_state['ims']:

            if not channel.get('is_member', True) or channel['is_archived']:
                continue

            human_readable_name = channel.get("name")

            if not human_readable_name:
                human_readable_name = id_to_username[channel["user"]]

            rating = get_rating(channel, conf, muted_channel_ids)

            row = (channel["id"], rating, channel["unread_count_display"], human_readable_name)
            output.append(row)

        unreads_by_rating = {}

        for row in sorted(output, key = lambda x: (x[1], -x[2])):
            print(f"{row[0]: >11} {row[1]: >9} {row[2]: >6} unreads   {row[3]}", file=sys.stderr)

            rating = row[1]
            unreads = row[2]

            if rating not in unreads_by_rating:
                unreads_by_rating[rating] = 0
            unreads_by_rating[rating] += unreads


        colors = [
            ("direct", "#ffffff"),
            ("good", "#39e600"),
            ("medium", "#ffe970"),
            ("bad", "#ff6f69"),
            ("unrated", "#96897f"),
        ]

        output = ""

        for rating, color in colors:
            unreads = unreads_by_rating.get(rating, 0)
            if unreads > 0:
                output += f"#[fg={color}]{unreads} "
        return output.strip()

statusbar_classes = {
    "battery": Battery,
    "date": Date,
    "reddit": Reddit,
    "spotify": Spotify,
    "weather": Weather,
    "slack": Slack,
}

def get_statusbar(run_item, enable_cache):

    conf = load_config('statusbar')

    if enable_cache:
        cache = load_cache()
    else:
        cache = {}

    if run_item:
        items = [run_item]
    else:
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

            if 'error' in cache_item:
                print(f'Found error marker in cache for {item}', file=sys.stderr)
                raise SkipItemException()


            if (not cache_item) or (now > cache_item['expiry']):

                item_text = statusbar_item.get_text()
                print(f'Running {item}', file=sys.stderr)
                expiry = statusbar_item.expiry()

                if expiry != -1:
                    cache[item] = {
                        'expiry': now + expiry,
                        'text': item_text
                    }

            else:
                print(f'Loaded {item} from cache', file=sys.stderr)
                item_text = cache_item['text']

            header = color_headers[len(statusbar)%len(color_headers)]

            statusbar.append(f'{header} {item_text} ')

        except SkipItemException as e:
            print(f'Skipping {item}', file=sys.stderr)
        except Exception:
            traceback.print_exc(file=sys.stderr)

            statusbar_item = statusbar_classes[item]()
            expiry = statusbar_item.expiry()

            if expiry != -1:
                cache[item] = {
                    'expiry': now + expiry,
                    'text': '',
                    'error': True
                }

    write_cache(cache)
    print(''.join(statusbar))


