#!/bin/bash

which pyenv 2>&1 >/dev/null || {
    echo "Please install pyenv, see https://github.com/pyenv/pyenv#installation"
    exit 1
}

cd $HOME/.dotfiles || {
    echo "$HOME/.dotfiles does not exist"
    exit 1
}

pyenv install --skip-existing 3.7.6
pyenv local 3.7.6

pip install --upgrade pip

virtualenv -p `which python` venv
. ./venv/bin/activate
pip install -r requirements.txt
