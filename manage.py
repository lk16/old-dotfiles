#!/usr/bin/env python

import click
import requests
import os
import datetime
import sys
import json
import re
import random
import subprocess

import statusbar


@click.group()
def cli():
    pass

@cli.command()
@click.argument("cmd", nargs=-1)
def confirm(cmd):
    print('You are about to run this command: {}'.format(colorize_text(" ".join(cmd), "cyan")))
    number = random.randint(100, 1000)
    print("To confirm type this number: {}".format(number))
    if input("> ") == str(number):
        subprocess.call(cmd)

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


@click.option('-i', '--item', type=str)
@click.option('--cache/--no-cache', default=True)
@cli.command()
def get_statusbar(item, cache):
    return statusbar.get_statusbar(run_item=item, enable_cache=cache)

if __name__ == "__main__":
    cli()
