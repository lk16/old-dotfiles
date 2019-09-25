#!/usr/bin/env python3

import click
import requests
import json


@click.group()
def cli():
    pass


@cli.command()
def weather():
    r = requests.get(
        "https://api.openweathermap.org/data/2.5/weather?q=London,uk&APPID=d9a557c2687e36ed1ea2f2d1cac38cb7&units=metric"
    )
    data = json.loads(r.text)

    temp = int(data["main"]["temp"])
    weather = "/".join([item["main"] for item in data["weather"]])

    print(str(temp) + "°C " + weather)


if __name__ == "__main__":
    cli()
