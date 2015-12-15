import colormaps
import random
import struct
import threading
import time
import math

class Mirror:

    def __init__(self, t):
        self.t = t

    def dec(self):
        if self.t > 0:
            self.t -= 1

    def inc(self):
        if self.t < 7:
            self.t += 1

    def __eq__(self, a):
        return self.t == a

class Control():

    midi = None

    mirror = Mirror(0)
    paused = False
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
        try:
            import pypm
            pypm.Initialize()
            for i in xrange(pypm.CountDevices()):
                di = pypm.GetDeviceInfo(i)
                if di[1].startswith('WORLDE') and di[2]:
                    self.midi = pypm.Input(i)
                    print 'MIDI Controller found as MIDI device #%d' % i
                    break
            else:
                raise Exception()
        except:
            self.midi = None
            print 'MIDI Controller not found'

    def close(self):
        pass

    def update(self):

        self.rotate += self.rotate_speed

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
                self.mirror.dec()
            if data[0] == 176 and data[1] == 64 and data[2] == 127 and data[3] == 0:
                self.mirror.inc()

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
            self.mirror = Mirror(0)
            self.negative = False
            self.blackwhite = False
            self.quantize = False
            self.emboss = False

        elif key == '\t': # tab
            self.negative = not self.negative

        # mirrors
        elif key == '1':
            self.mirror = Mirror(1)
        elif key == '2':
            self.mirror = Mirror(2)
        elif key == '3':
            self.mirror = Mirror(3)
        elif key == '4':
            self.mirror = Mirror(4)
        elif key == '5':
            self.mirror = Mirror(5)
        elif key == '6':
            self.mirror = Mirror(6)
        elif key == '7':
            self.mirror = Mirror(7)

        # filters
        elif key == 'z':
            self.blackwhite = not self.blackwhite
        elif key == 'x':
            self.quantize = not self.quantize
        elif key == 'c':
            self.emboss = not self.emboss

        # colormaps
        elif key == 'q':
            self.app.setColormap(None)
        elif key == 'w':
            self.app.setColormap(colormaps.sepia)
        elif key == 'e':
            self.app.setColormap(colormaps.heat)
        elif key == 'r':
            self.app.setColormap(colormaps.xray)
        elif key == 't':
            self.app.setColormap(colormaps.xpro)
        elif key == 'y':
            self.app.setColormap(colormaps.fire)
        elif key == 'u':
            self.app.setColormap(colormaps.sea)

        # rotation
        elif key == '[':
            self.rotate_speed -= 0.5
        elif key == ']':
            self.rotate_speed += 0.5
        elif key == '\x08':
            if self.rotate_speed == 0:
                self.rotate = 0
            else:
                self.rotate_speed = 0
