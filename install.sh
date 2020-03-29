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

virtualenv -p `which python` venv
. ./venv/bin/activate
pip install -r requirements.txt

ln -s $HOME/.dotfiles/.bashrc ~/.bashrc || echo "please backup your $HOME/.bashrc file, so we can simlink it from the repo"
ln -s $HOME/.dotfiles/.bash_aliases ~/.bash_aliases || echo "please backup your $HOME/.bash_aliases file, so we can simlink it from the repo"
ln -s $HOME/.dotfiles/.tmux.conf ~/.tmux.conf || echo "please backup your $HOME/.tmux file, so we can simlink it from the repo"