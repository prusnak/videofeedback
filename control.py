import colormaps
import random
import struct
import threading
import time
import math

MIDI = 3

MIRRORS = ['none', 'vert', 'horiz', 'both', 'tri', 'quad', 'penta']

class Control():

    midi = None

    mirror = 'none'
    mirror_idx = 0
    paused = False
    beat = 0
    fader = [0] * 9
    pot = [0] * 9
    btn = [False] * 9

    negative = False
    blackwhite = False
    quantize = False
    emboss = False

    rotate = 0
    rotate_speed = 0

    noise_level = 0.0
    desaturate_level = 0.0
    blackwhite_level = 0.5
    quantize_level = 0.5
    emboss_level = 0.5
    separation_level = 0.0
    pixelate_level = 0.0
    hue_level = 0.0

    def __init__(self, app):
        self.app = app

        # midi device
        self.midi = None
        if MIDI:
            try:
                import pypm
                pypm.Initialize()
                self.midi = pypm.Input(MIDI)
            except:
                self.midi = None

    def close(self):
        pass

    def update(self):

        self.rotate += self.rotate_speed
        if self.beat > 0:
            self.beat -= 1

        if not self.midi:
            return

        while self.midi.Poll():
            data = self.midi.Read(1)
            data = data[0][0]

            # vertical faders
            for i in xrange(9):
                if data[0] == 0xb0 and data[1] == 0x03+i and data[3] == 0x00:
                    self.fader[i] = data[2] / 127.0

            # vertical pots
            for i in xrange(9):
                if data[0] == 0xb0 and data[1] == 0x0e+i and data[3] == 0x00:
                    self.pot[i] = data[2] / 127.0

            # buttons under faders
            for i in xrange(9):
                if data[0] == 176 and data[1] == 23 + i and data[2] == 127 and data[3] == 0:
                    self.btn[i] = True

            # buttons near big wheel
            if data[0] == 176 and data[1] == 67 and data[2] == 127 and data[3] == 0:
                if self.mirror_idx > 0:
                    self.mirror_idx -= 1
                    self.mirror = MIRRORS[self.mirror_idx]
            if data[0] == 176 and data[1] == 64 and data[2] == 127 and data[3] == 0:
                if self.mirror_idx < len(MIRRORS) - 1:
                    self.mirror_idx += 1
                    self.mirror = MIRRORS[self.mirror_idx]

            # big wheel
#            if data[0] == 0xc0 and data[2] == 0x00 and data[3] == 0x00:
#                pass

            # horizontal fader
            if data[0] == 0x01 and data[1] == 0x00 and data[3] == 0xf7:
                d = (data[2] / 127.0 - 0.5)
                self.rotate_speed = d * d * d * 32.0

        self.noise_level      = self.fader[0]
        self.desaturate_level = self.fader[1]
        self.blackwhite_level = self.fader[2]
        self.quantize_level   = self.fader[3]
        self.emboss_level     = self.fader[4]
        self.separation_level = self.fader[5]
        self.pixelate_level   = self.fader[6]
        self.hue_level        = self.fader[7]
        self.hue_level        = self.hue_level * 2 - 1

        if self.btn[2]:
            self.blackwhite = not self.blackwhite
        if self.btn[3]:
            self.quantize = not self.quantize
        if self.btn[4]:
            self.emboss = not self.emboss
        self.btn = [False] * 9


    def update_kbd(self, key):

        # pause
        if key == ' ':
            self.paused = not self.paused

        # reset all effects
        elif key == '`':
            self.app.setColormap(None)
            self.mirror = 'none'
            self.mirror_idx = 0
            self.negative = False
            self.blackwhite = False
            self.quantize = False
            self.emboss = False

        # beat
        elif key == '\t': # tab
            self.beat = 3

        # mirrors
        elif key == '1':
            self.mirror_idx = 1
            self.mirror = MIRRORS[1]
        elif key == '2':
            self.mirror_idx = 2
            self.mirror = MIRRORS[2]
        elif key == '3':
            self.mirror_idx = 3
            self.mirror = MIRRORS[3]
        elif key == '4':
            self.mirror_idx = 4
            self.mirror = MIRRORS[4]
        elif key == '5':
            self.mirror_idx = 5
            self.mirror = MIRRORS[5]
        elif key == '6':
            self.mirror_idx = 6
            self.mirror = MIRRORS[6]

        # filters
        elif key == 'q':
            self.negative = not self.negative
        elif key == 'w':
            self.blackwhite = not self.blackwhite
        elif key == 'e':
            self.quantize = not self.quantize
        elif key == 'r':
            self.emboss = not self.emboss

        # colormaps
        elif key == 'a':
            self.app.setColormap(None)
        elif key == 's':
            self.app.setColormap(colormaps.sepia)
        elif key == 'd':
            self.app.setColormap(colormaps.heat)
        elif key == 'f':
            self.app.setColormap(colormaps.xray)
        elif key == 'g':
            self.app.setColormap(colormaps.xpro)
        elif key == 'h':
            self.app.setColormap(colormaps.fire)
        elif key == 'j':
            self.app.setColormap(colormaps.sea)
