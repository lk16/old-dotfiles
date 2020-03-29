
# Dotfiles

These are my dotfiles. Feel free to use them on your machine!

## Installing

* Backup or remove any existing `$HOME/.bashrc`, `$HOME/.bash_aliases` and `$HOME/.tmux.conf`
* Clone this repo into `HOME/.dotfiles`
* Symlink all dotfiles to the files in the repo:
```sh
ln -s $HOME/.dotfiles/.bashrc $HOME/.bashrc
ln -s $HOME/.dotfiles/.bash_aliases $HOME/.bash_aliases
ln -s $HOME/.dotfiles/.tmux.conf $HOME/.tmux.conf
```
* Install [pyenv](https://github.com/pyenv/pyenv#installation). Note the pyenv `PATH` value is already in `$HOME/.bashrc`
* Install python 3.7.6 and python dependencies:
```sh
cd $HOME/.dotfiles
pyenv install --skip-existing 3.7.6
pyenv local 3.7.6

virtualenv -p `which python` venv
. ./venv/bin/activate
pip install -r requirements.txt

```
* Modify `$HOME/.dotfiles/conf.json` to your taste. You can use the sample file `conf.json.example`.





## TODO
- [ ] general
    - [ ] create install guide
    - [x] use virtualenv to not depend on click being globally installed
    - [ ] lint code
    - [ ] use type annotations
    - [ ] test everything


- [ ] tmux statusbar
    - [ ] customize statusbar items
        - [x] allow customizing order in config file
        - [ ] update interval
        - [ ] colours
    - [ ] warnings
        - [ ] full disk
        - [ ] high cpu usage
    - [x] weather
    - [x] spotify
    - [ ] battery
        - [ ] show percentage
        - [ ] show symbol if charching
    - [x] current date and time
    - [ ] updates
        - [x] reddit
            - [x] karma
            - [x] unread replies
        - [ ] slack
            - [ ] unread mentions
            - [ ] allow blacklisting channels
        - [ ] gmail unread mails
        - [ ] bitbucket
            - [ ] unapproved PRs to review
        - [ ] google calendar next meeting

- [ ] tools
    - [ ] csvcut
    - [ ] jsonschema validator
    - [x] confirm for dangerous commands
    - [ ] highlight stdin
        - [x] by string
        - [ ] by regex


### References
- https://peterforgacs.github.io/2017/04/25/Tmux/
- https://github.com/sbernheim4/dotfiles
- https://github.com/ahf/dotfiles
