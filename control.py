import colormaps
import random
import struct
import threading
import time
import math

class Control():

    def __init__(self, app):
        self.app = app
        self.reset()

    def reset(self):
        self.paused = False
        self.mirror = None
        self.rotate = 0
        self.rotate_speed = 0
        self.negative = False
        self.modeselektor = None
        self.threshold_level = None
        self.quantize_level = None
        self.emboss_level = None
        self.noise_level = None
        self.desaturate_level = None
        self.separation_level = None
        self.pixelate_level = None
        self.hue_level = None
        self.zoom_freq = None

    def close(self):
        pass

    def update(self):
        self.rotate += self.rotate_speed

    def update_key(self, key):

        # pause
        if key == ' ':
            self.paused = not self.paused
            return

        # reset all effects
        if key == '\x7F':
            self.app.setColormap(None)
            self.reset()
            return

        # tab - negative
        if key == '\t':
            self.negative = not self.negative
            return

        # rotation
        if key == '[':
            self.rotate_speed -= 0.5
            return
        if key == ']':
            self.rotate_speed += 0.5
            return
        if key == '\x0d':
            self.rotate_speed = -self.rotate_speed
        if key == '\x08':
            if self.rotate_speed == 0:
                self.rotate = 0
            else:
                self.rotate_speed = 0
            return

        # effects
        if key in 'mctqendsphz':
            self.modeselektor = key
            return

        # effect amount
        if self.modeselektor is not None and key in '`1234567890':

            if key == '`':
                value = None
            elif key == '0':
                value = 10
            else:
                value = ord(key) - 48

            # mirror
            if self.modeselektor == 'm':
                if value <= 7:
                    self.mirror = value

            # colormap
            if self.modeselektor == 'c':
                if value is None:
                    self.app.setColormap(None)
                elif value == 1:
                    self.app.setColormap(colormaps.sepia)
                elif value == 2:
                    self.app.setColormap(colormaps.heat)
                elif value == 3:
                    self.app.setColormap(colormaps.xray)
                elif value == 4:
                    self.app.setColormap(colormaps.xpro)
                elif value == 5:
                    self.app.setColormap(colormaps.yellowblue)
                elif value == 6:
                    self.app.setColormap(colormaps.fire)
                elif value == 7:
                    self.app.setColormap(colormaps.sea)

            # threshold
            if self.modeselektor == 't':
                self.threshold_level = 0.1 * value if value is not None else None

            # quantize
            if self.modeselektor == 'q':
                self.quantize_level = 0.1 * value if value is not None else None

            # emboss
            if self.modeselektor == 'e':
                self.emboss_level = 0.1 * value if value is not None else None

            # noise
            if self.modeselektor == 'n':
                self.noise_level = 0.1 * value if value is not None else None

            # desaturate
            if self.modeselektor == 'd':
                self.desaturate_level = 0.1 * value if value is not None else None

            # separation
            if self.modeselektor == 's':
                self.separation_level = 0.1 * value if value is not None else None

            # pixelate
            if self.modeselektor == 'p':
                self.pixelate_level = 0.1 * value if value is not None else None

            # hue
            if self.modeselektor == 'h':
                self.hue_level = (0.2 * value - 1.0) if value is not None else None

            if self.modeselektor == 'z':
                if value:
                    self.zoom_freq = (80 + value * 10) / 60.0 / 4.0
                else:
                    self.zoom_freq = None

            self.modeselektor = None
            return
