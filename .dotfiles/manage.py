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

    url = f"https://api.openweathermap.org/data/2.5/weather?q={location}&APPID={api_key}&units=metric"

    r = requests.get(url)
    data = json.loads(r.text)

    temp = int(data["main"]["temp"])
    weather = list([item["main"] for item in data["weather"]])[0]

    print(str(temp) + "°C " + weather)


@cli.command()
@click.argument("cmd", nargs=-1)
def confirm(cmd):
    print(f'You are about to run this command: {" ".join(cmd)}')
    number = random.randint(100, 1000)
    print(f"To confirm type this number: {number}")
    if input("> ") == str(number):
        subprocess.call(cmd)


if __name__ == "__main__":
    cli()
