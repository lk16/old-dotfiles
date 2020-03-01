#!/usr/bin/env python3

import click
import requests
import os
import sys
import json
import re
import random
import subprocess


def load_config(section):
    config_file = os.path.join(os.path.dirname(os.path.realpath(__file__)), "conf.json")
    return json.load(open(config_file, "r"))[section]


@click.group()
def cli():
    pass


@cli.command()
def weather():
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

    print(str(temp) + "°C " + weather)

@cli.command()
@click.argument("cmd", nargs=-1)
def confirm(cmd):
    print('You are about to run this command: {}'.format(colorize_text(" ".join(cmd), "cyan")))
    number = random.randint(100, 1000)
    print("To confirm type this number: {}".format(number))
    if input("> ") == str(number):
        subprocess.call(cmd)


@cli.command()
def spotify_song():
    command = ['dbus-send', '--print-reply', '--dest=org.mpris.MediaPlayer2.spotify',  '/org/mpris/MediaPlayer2', 
        'org.freedesktop.DBus.Properties.Get', 'string:org.mpris.MediaPlayer2.Player', 'string:Metadata']
    process = subprocess.run(command, stdout=subprocess.PIPE)
 
    output = process.stdout.decode('utf-8')
    output = output.replace('\n', '')

    try:
        artist = re.search('string "xesam:artist".*?string "(.*?)"', output).group(1)
        title = re.search('string "xesam:title".*?string "(.*?)"', output).group(1)    
    except Exception:
        artist = ""
        title = ""

    print("{} / {}".format(artist, title))

def colorize_text(text, color):
    markers = {
        "red": "\033[1;31m",
        "green": "\033[1;32m",
        "yellow": "\033[1;33m",
        "blue": "\033[1;34m",
        "purple": "\033[1;35m",
        "cyan": "\033[1;36m",
        "white": "\033[1;37m",
        "reset": '\033[0m', 
    }

    return "{}{}{}".format(markers[color], text, markers["reset"])

@cli.command()
@click.option('-r', '--red', type=str)
@click.option('-g', '--green', type=str)
@click.option('-y', '--yellow', type=str)
@click.option('-b', '--blue', type=str)
@click.option('-p', '--purple', type=str)
@click.option('-c', '--cyan', type=str)
@click.option('-w', '--white', type=str)
def highlight(**kwargs):
    for line in sys.stdin:
        for color, text in kwargs.items():
            if text:
                line = line.replace(text, colorize_text(text, color))
        print(line, end='')


if __name__ == "__main__":
    cli()
