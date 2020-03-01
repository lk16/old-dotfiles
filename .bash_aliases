alias config='/usr/bin/git --git-dir=$HOME/.dotfiles/.git/ --work-tree=$HOME'

alias brc='source $HOME/.bashrc'

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
    alias cg='grep --color=always'
fi

alias ccat='pygmentize -g'
alias lcat='pygmentize -g -O style=colorful,linenos=1'

# cut and paste
alias c='xclip -in -selection clipboard'
alias p='xclip -out -selection clipboard'

alias ll='ls -l'
alias la="ls -la"
alias l='ls -CF'


alias gig='git'

alias gg="git log --graph --oneline --decorate --all"
alias ggs="git push"
alias ggs="git status"
alias ggsi="git status --ignored"
alias ggc="git checkout"
alias ggr="git rebase"
alias ggrc="git rebase --continue"
alias gitroot='git rev-parse --show-toplevel 2>/dev/null'
alias gv="git rev-parse HEAD | cut -c -8"
alias ggpf="git push --force-with-lease"

alias edit="code"
alias json="python3 -m json.tool"

function goo() {
    brave-browser --new-tab "https://google.com/search?q=$*" 2>&1 >/dev/null
}

function gocover() {
    covername=$(basename $(gitroot))
    coverfile="/tmp/$covername.cover"
    go test -coverprofile="$coverfile" ./... >/dev/null
    go tool cover -html="$coverfile" 2>&1 >/dev/null
}

function bright() {
    for output in $(xrandr | grep ' connected ' | cut -d ' ' -f 1); do
        xrandr --output "$output" --brightness $1 2>/dev/null
    done
}

function confirm() {
    $HOME/.dotfiles/manage.py confirm -- $@
}
