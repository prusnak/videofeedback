import colormaps
import random
import struct
import threading
import time
import math

# get list with:
# pactl list | grep -A2 'Source #' | grep 'Name: ' | cut -d" " -f2

# AUDIO = 'alsa_output.pci-0000_00_1b.0.analog-stereo.monitor'
# AUDIO = 'alsa_input.pci-0000_00_1b.0.analog-stereo'
AUDIO = None

MIDI = 3
# MIDI = None

MIRRORS = ['none', 'vert', 'horiz', 'both', 'tri', 'quad', 'penta']

class AudioThread(threading.Thread):

    def __init__(self, sink):
        super(AudioThread, self).__init__()
        self.sink = sink
        self.freq = 0.0
        self.amp = 0.0
        self.active = True
        global numpy
        import numpy
        import numpy.fft

    def run(self):
        while self.active:
            buf = self.sink.emit('pull-buffer')
            raw = struct.unpack(str(len(buf)/2)+'h', buf)
#            total = 0.0
#            for i in xrange(len(raw)):
#                total += min(1.0, abs(1.0*raw[i]/4096))
#            self.amp = total/len(raw)
            raw = numpy.log(numpy.abs(numpy.fft.fft(raw))**2)
            maxi, maxv = 0, 0
            for i in xrange(128):
                if raw[i] > maxv:
                    maxv = raw[i]
                    maxi = i
            self.freq = min(1.0, 1.0*maxi/128)
            time.sleep(0.01)

    def stop(self):
        self.active = False

class Control():

    midi = None

    mirror = 'none'
    mirror_idx = 0
    paused = False
    beat = 0
    raw1 = [0] * 9
    raw2 = [0] * 9

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
                pass

        # audio device
        self.audio = None
        if AUDIO:
            try:
                import pygst
                pygst.require("0.10")
                import gst
                pipeline = gst.parse_launch('pulsesrc device=%s ! audio/x-raw-int ! appsink name=sink' % AUDIO)
                sink = pipeline.get_by_name('sink')
                sink.set_property('drop', True)
                sink.set_property('max-buffers', 1)
                pipeline.set_state(gst.STATE_PLAYING)
                self.audio = AudioThread(sink)
                self.audio.start()
            except:
                pass

    def close(self):
        if self.audio:
            self.audio.stop()

    def update(self):
        if not self.midi:
            return

        if self.audio:
#            audio = self.audio.amp
            audio = self.audio.freq
        else:
            audio = 0

        while self.midi.Poll():
            data = self.midi.Read(1)
            data = data[0][0]

            # vertical faders
            for i in xrange(9):
                if data[0] == 0xb0 and data[1] == 0x03+i and data[3] == 0x00:
                    self.raw1[i] = data[2] / 127.0

            # vertical pots
            for i in xrange(9):
                if data[0] == 0xb0 and data[1] == 0x0e+i and data[3] == 0x00:
                    self.raw2[i] = data[2] / 127.0

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

        self.noise_level      = self.raw1[0] *(1.0 - self.raw2[0]) + audio * self.raw2[0]
        self.desaturate_level = self.raw1[1] *(1.0 - self.raw2[1]) + audio * self.raw2[1]
        self.blackwhite_level = self.raw1[2] *(1.0 - self.raw2[2]) + audio * self.raw2[2]
        self.quantize_level   = self.raw1[3] *(1.0 - self.raw2[3]) + audio * self.raw2[3]
        self.emboss_level     = self.raw1[4] *(1.0 - self.raw2[4]) + audio * self.raw2[4]
        self.separation_level = self.raw1[5] *(1.0 - self.raw2[5]) + audio * self.raw2[5]
        self.pixelate_level   = self.raw1[6] *(1.0 - self.raw2[6]) + audio * self.raw2[6]
        self.hue_level        = self.raw1[7] *(1.0 - self.raw2[7]) + audio * self.raw2[7]
        self.hue_level       *= 30
        self.hue_level        = 0.5 - math.cos(self.hue_level)/2.0

        self.rotate += self.rotate_speed
        if self.beat > 0:
            self.beat -= 1

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

        elif key == '\t':
            self.beat = 3

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
