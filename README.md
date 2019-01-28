# Dindo Bot

[![Python](https://img.shields.io/badge/python%20%3E%3D-3.0-blue.svg)](#)
[![GTK](https://img.shields.io/badge/gtk-3.0-brightgreen.svg)](#)
[![OS](https://img.shields.io/badge/os-Linux-orange.svg)](#)

Farming bot for Dofus game.

![screenshot](screenshot.png)

## Installation

First, you need to install some dependencies using one of the following commands:

**Debian & derivatives:**
```bash
sudo apt install python3-gi gir1.2-gtk-3.0 gir1.2-wnck-3.0 python3-xlib python3-pil
```

**Arch Linux & derivatives:**
```bash
sudo pacman -S python-gobject python-xlib python-pillow
```

Then, clone this repository using git or just [download](https://github.com/AXeL-dev/Dindo-Bot/archive/master.zip) & unzip it:
```bash
git clone https://github.com/AXeL-dev/Dindo-Bot.git
```

To run the bot:
```bash
cd /path/to/bot
python3 bot.py
```

You could even run the bot in developer mode (brings some additional features):
```bash
python3 bot.py --dev
```

**Note:** the [desktop file](dindo-bot.desktop) can also be used to run the bot.

## To Know

- Dindo bot use screen pixels to interact with the game client, so you cannot use your PC for something else while using the bot.
- Is it detectable by the Anti-bot?
> It shouldn't be, because it imitates exactly the human behaviour, but as a conclusion, nothing is 100% safe.
- The main goal of this bot is to simplify repetitive tasks and reduce boredom during your game play.
- Also, the bot does not encourage multi-boting and does not support it anyway.
