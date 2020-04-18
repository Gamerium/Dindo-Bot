#!/bin/bash

if [ "$(id -u)" != "0" ]; then
echo “This script must be run as root” 2>&1
exit 1
fi

# remove symlink
rm -f /usr/local/bin/dindo-bot

# remove desktop files
rm -f /usr/share/applications/dindo-bot.desktop
rm -f /usr/share/applications/dindo-bot-dev.desktop

# remove icons
rm -f /usr/share/icons/hicolor/128x128/apps/dindo-bot.png
