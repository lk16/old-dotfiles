#!/bin/bash
title=$(dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 \
    org.freedesktop.DBus.Properties.Get string:org.mpris.MediaPlayer2.Player string:Metadata 2>&1 \
    | sed -n '/title/{n;p}' \
    | cut -d '"' -f 2)

if [[ $title == *"Error org.freedesktop.DBus.Error"* ]]; then
    exit 0
fi

artist=$(dbus-send --print-reply --dest=org.mpris.MediaPlayer2.spotify /org/mpris/MediaPlayer2 \
    org.freedesktop.DBus.Properties.Get string:org.mpris.MediaPlayer2.Player string:Metadata  2>&1 \
    | sed -n '/xesam:artist/{n;n;p}' \
    | cut -d '"' -f 2
)

echo "$artist / $title"