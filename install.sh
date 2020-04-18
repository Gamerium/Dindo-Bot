#!/bin/bash

# root detection
if [ "$(id -u)" != "0" ]; then
echo “This script must be run as root” 2>&1
exit 1
fi

# run uninstall script first
sh uninstall.sh

# package manager detection
APT_CMD=$(which apt)
PACMAN_CMD=$(which pacman)

# install dependencies
if [[ ! -z $APT_CMD ]]; then
  sudo apt -y install python-gi gir1.2-gtk-3.0 gir1.2-wnck-3.0 python-xlib python3-xlib python-pil python3-pil scrot
elif [[ ! -z $PACMAN_CMD ]]; then
  sudo pacman -S python-gobject gtk3 libwnck3 python-xlib python-pillow scrot
else
  echo "error can't install dependencies"
  exit 1
fi

# get script path
SCRIPT_PATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# create symlink
ln -s $SCRIPT_PATH/bot.py /usr/local/bin/dindo-bot
chmod 755 /usr/local/bin/dindo-bot

# copy & update desktop files
cp dindo-bot.desktop /usr/share/applications/dindo-bot.desktop
sed -i 's/^Exec=.*$/Exec=dindo-bot/g' /usr/share/applications/dindo-bot.desktop
chmod 755 /usr/share/applications/dindo-bot.desktop

cp dindo-bot-dev.desktop /usr/share/applications/dindo-bot-dev.desktop
sed -i 's/^Exec=.*$/Exec=dindo-bot --dev/g' /usr/share/applications/dindo-bot-dev.desktop
chmod 755 /usr/share/applications/dindo-bot-dev.desktop

# copy icons
cp icons/logo.png /usr/share/icons/hicolor/128x128/apps/dindo-bot.png
chmod 644 /usr/share/icons/hicolor/128x128/apps/dindo-bot.png

# refresh icons cache
gtk-update-icon-cache
