# Dindo Bot

import random
import numpy as np
import time
import gi
import cv2
import imutils
gi.require_version('Gtk', '3.0')
from gi.repository import GObject
from lib.shared import LogType, DebugLevel
from lib import data, tools, imgcompare, accounts
from .game import GameThread
import pyscreenshot as ImageGrab
from PIL import Image

class FightingThread(GameThread):

    def __init__(self, parent, game_location):
        GameThread.__init__(self, parent, game_location)
        self.save_screenshots = parent.settings['Fighting']['SaveScreenshots']
        if self.save_screenshots:
            self.index = 0

    def my_turn_to_play(self):
        return True

    def fight_still_on(self):
        if self.has_box_appeared('Victory') or self.has_box_appeared('Defeat') or self.has_box_appeared('NewVictory'):
            return False
        return True

    def handle_fight(self):
        '''
        This fight handler requires the character to have an arakne and to
        have mapped the arakne shortcut in dofus to the one in data.py
        The bot will invoke the arakne and pass its turn until it is over or
        another arakne needs to be invoked.
        '''
        self.log('Fight detected.', LogType.Info)
        self.sleep(2.0)
        # Accept position and start fight
        self.press_key(data.KeyboardShortcuts['EndTurn'])
        self.sleep(6.0)
        # Pass our first turn because the arakne isn't ready yet
        self.press_key(data.KeyboardShortcuts['EndTurn'])

        still_in_fight = True
        while still_in_fight:
            if self.my_turn_to_play():
                self.log("Playing ...", LogType.Info)
                # Wait a couple seconds before playing
                self.sleep(5.0)

                # check for pause or suspend
                self.pause_event.wait()
                if self.suspend: return

                # To establish where to invoke the arakne, we do an image comparison
                # between before and after clicking on the arakne spell. We then
                # identify squares where the arakne can be invoke. This is robust to
                # being anywhere on the screen. It will fail if the character has no
                # space around.
                x, y, width, height = self.game_location
                before = ImageGrab.grab(bbox=(x,y, x+width, y+height), backend='pygdk3')
                screen_initial = np.array(before)
                self.press_key(data.KeyboardShortcuts['arakne'])
                self.sleep(3.0)
                after = ImageGrab.grab(bbox=(x,y, x+width, y+height), backend='pygdk3')
                screen_spell = np.array(after)
                self.sleep(1.0)
                difference_screen = screen_initial - screen_spell

                im = Image.fromarray(difference_screen)
                if self.save_screenshots:
                    im.save(f"screenshots/difference-{self.index}.jpeg")

                image = difference_screen
                resized = imutils.resize(image, width=300)
                ratio = image.shape[0] / float(resized.shape[0])

                # check for pause or suspend
                self.pause_event.wait()
                if self.suspend: return

                # convert the resized image to grayscale, blur it slightly,
                # and threshold it
                gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
                blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                thresh = cv2.threshold(blurred, 60, 255, cv2.THRESH_BINARY)[1]

                # find contours in the thresholded image and initialize the
                # shape detector
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                    cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)

                cX = []
                cY = []
                # loop over the contours
                for c in cnts:
                    # compute the center of the contour, then detect the name of the
                    # shape using only the contour
                    dx = np.max(c, axis=0)[0][0] - np.min(c, axis=0)[0][0]
                    if dx < 12 or dx > 14:
                        continue

                    M = cv2.moments(c)
                    if not M["m00"]:
                        continue
                    cX.append(int((M["m10"] / M["m00"]) * ratio))
                    cY.append(int((M["m01"] / M["m00"]) * ratio))

                    # shape += str(cX * cY)
                    # multiply the contour (x, y)-coordinates by the resize ratio,
                    # then draw the contours and the name of the shape on the image
                    c = c.astype("float")
                    c *= ratio
                    c = c.astype("int")
                    cv2.drawContours(image, [c], -1, (0, 255, 0), 2)
                    # cv2.putText(image, shape, (cX, cY), cv2.FONT_HERSHEY_SIMPLEX,
                    # 	0.5, (255, 255, 255), 2)
                    cv2.circle(image, (cX[-1],cY[-1]), 1, (255,0,0))

                    im = Image.fromarray(image)
                    if self.save_screenshots:
                        im.save(f"screenshots/processed-{self.index}.jpeg")
                        self.index += 1
                if not len(cX):
                    self.debug("No contours found. Can\'t invoke the arakne", DebugLevel.High)
                elif self.fight_still_on():
                    blue_box = {}
                    i = random.randint(0,len(cX)-1)
                    blue_box['x'] = cX[i]
                    blue_box['y'] = cY[i]
                    blue_box['width'] = width
                    blue_box['height'] = height
                    self.click(blue_box)
                    self.debug(f"Invoked Spider on {blue_box['x']}, {blue_box['y']}", DebugLevel.High)

                self.sleep(2.0)
                self.debug("End Turn .. ", DebugLevel.High)
                self.press_key(data.KeyboardShortcuts['EndTurn'])
            else:
                self.sleep(2.0)
                self.log("Waiting for our turn to play", LogType.Info)
            # check for pause or suspend
            self.pause_event.wait()
            if self.suspend: return
            # We check whether the fight has ended or not
            still_in_fight = self.fight_still_on()

        self.log("Game Finished", LogType.Info)
        self.press_key('esc')
        self.sleep(3.0)
