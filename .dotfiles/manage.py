#!/usr/bin/env python3

import click
import requests
import os
import json
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
    weather = list([item["main"] for item in data["weather"]])[0]

    print(str(temp) + "°C " + weather)


@cli.command()
@click.argument("cmd", nargs=-1)
def confirm(cmd):
    print('You are about to run this command: {}'.format(" ".join(cmd)))
    number = random.randint(100, 1000)
    print("To confirm type this number: {}".format(number))
    if input("> ") == str(number):
        subprocess.call(cmd)


if __name__ == "__main__":
    cli()
