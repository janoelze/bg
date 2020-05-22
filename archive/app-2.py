import sys, time, random
import json, pygame
import os.path
import gc
import glob
import random
import soundfile as sf

from time import time, sleep
from datetime import datetime
from os import path

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from waveform import Waveform

from threading import Thread#

# ram stores

_sound_library = {}

# config

CONFIG = {
    'store_dir': 'data/',
    'waveforms_dir': 'waveforms/',
    'samples_dir': 'samples/',
    'library_dir': 'library/'
}

# helper

def log(msg):
    now = datetime.now()
    print('%s: %s' % (now.strftime("%H:%M:%S"), msg))

def get_state():
    if path.exists(CONFIG['store_dir'] + '/state.json'):
        with open(CONFIG['store_dir'] + '/state.json') as json_file:
            return json.load(json_file)
    else:
        return {
            'bpm': 120,
            'bars': 1
        }

def set_state(state):
    with open(CONFIG['store_dir'] + '/state.json', 'w') as outfile:
        return json.dump(state, outfile)

def load_samples():
    count = len(glob.glob(CONFIG['samples_dir'] + '/*.wav'))

    log('loading %s samples' % count)

    for filename in glob.glob(CONFIG['samples_dir'] + '/*.wav'):
        log('loading %s' % filename)

        lib_filename = filename.replace(CONFIG['samples_dir'], CONFIG['library_dir'])

        if not path.exists(lib_filename):
            log('converting %s' % filename)

            data, samplerate = sf.read(filename)
            sf.write(lib_filename, data, 44100, subtype='PCM_16')

    for filename in glob.glob(CONFIG['library_dir'] + '/*.wav'):
        sound = pygame.mixer.Sound(filename)
        _sound_library[os.path.basename(filename)] = sound

        wv_filename = filename.replace(
            CONFIG['library_dir'],
            CONFIG['waveforms_dir']
            ).replace('.wav', '.gif')

        if not path.exists(wv_filename):
            log('creating waveform for %s' % filename)

            waveform = Waveform(filename)
            waveform.save(wv_filename)

# audio channel init

pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.mixer.init()
pygame.init()

CHANNELS = []

for i in range(0,4):
    CHANNELS.append(pygame.mixer.Channel(i))

print(CHANNELS)

# recover state

STATE = get_state()

STATE['current_step'] = 0

STATE['tracks'] = [
    {'channel': 0, 'stutter': False, 'volume': 1, 'sample_id': 'hat-loop.wav', 'grid': [0]},
    {'channel': 1, 'stutter': True, 'volume': 1, 'sample_id': 'kick.wav', 'grid': [0]},
]

# print(CHANNELS[0])

set_state(STATE)

# load library

load_samples()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(400, 300)

        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.draw_something()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.draw_something)
        self.timer.start(50)

    def draw_something(self):
        painter = QtGui.QPainter(self.label.pixmap())

        def drawTracks(painter):
            x = random.randint(0,100)
            y = random.randint(0,100)

            width = 40
            y = 0
            for n in range(0,4):
                for x in range(0,8):
                    painter.drawImage(
                        QtCore.QRect(x*width, y, width, width),
                        QtGui.QImage("waveforms/Abletunes TSD Snare 27.gif")
                    )
                y = y + width

        def drawCursor(painter):
            pen = QPen(Qt.white, 3)
            painter.setPen(pen)
            painter.drawLine(random.randint(0,100), random.randint(0,100), random.randint(0,100), random.randint(0,100))

        def drawText(painter):
            # bpm
            painter.drawText(random.randint(0,100), random.randint(0,100), str(STATE['bpm']))

        drawTracks(painter)
        drawCursor(painter)
        drawText(painter)

        painter.end()

        self.update()

def audioManager():
    def shuffle_track(TRACK):
        inc = random.randint(1,8)
        grid = []
        step = 0

        while step <= max_steps:
            grid.append(step)
            step = step + inc

        TRACK['grid'] = grid

    def play(channel, sample_id):
        if sample_id in _sound_library:
            channel.play(_sound_library[sample_id])

    DELTA = (60/(STATE['bpm'] * 4))
    GOAL = time()

    max_steps = 16 * STATE['bars']
    step = STATE['current_step']

    while True:
        if step >= max_steps:
            step = 0

        STATE['current_step'] = step

        play_output = []

        for TRACK in STATE['tracks']:
            channel = CHANNELS[TRACK['channel']]
            sample_id = TRACK['sample_id']

            if 'volume' in TRACK:
                channel.set_volume(TRACK['volume'])

            if 'stutter' in TRACK and TRACK['stutter']:
                channel.set_volume(random.randint(80,100)/100)

            if 'sample_id' in TRACK and 'grid' in TRACK and TRACK['sample_id']:
                if step in TRACK['grid']:
                    if channel.get_busy():
                        channel.stop()

                    play(channel, TRACK['sample_id'])
                    play_output.append('[%s]' % TRACK['sample_id'][0:5])

        log('playing %s' % (' '.join(play_output)))

        # print('%s/%s %s' % (step, max_steps, ))

        if step % 8 == 0 and random.randint(0,100) > 40:
            random_track = random.choice(STATE['tracks'])
            shuffle_track(random_track)

        step = step + 1

        GOAL += DELTA

        gc.collect()

        sleepInterval = GOAL - time()

        if sleepInterval >= 0:
            sleep(sleepInterval)
        else:
            sleep(0)

if __name__ == '__main__':
    Thread(target = audioManager).start()

    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()
