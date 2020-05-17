import sys, time, random
from time import sleep, perf_counter
import json
import os.path
import gc
import glob
import random
import soundfile as sf
import contextlib

with contextlib.redirect_stdout(None):
    import pygame

from time import time, sleep
from datetime import datetime
from os import path

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtCore import Qt

from waveform import Waveform

from threading import Thread

# ram stores

_sound_library = {}

# config

CONFIG = {
    'app_name': 'bg @ 0.1',
    'window_width': 500,
    'window_height': 400,
    'channel_num': 4,
    'store_dir': 'data/',
    'waveforms_dir': 'waveforms/',
    'samples_dir': 'samples/',
    'library_dir': 'library/'
}

# helper

def log(msg):
    print('%s: %s' % (datetime.utcnow().strftime('%M:%S.%f')[:-4], msg))

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

def quit_app():
    print('quit')

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

with contextlib.redirect_stdout(None):
    pygame.mixer.pre_init(44100, -16, 2, 256)
    pygame.mixer.init()
    pygame.init()

CHANNELS = []

for i in range(0, CONFIG['channel_num']):
    CHANNELS.append(pygame.mixer.Channel(i))

# recover state

STATE = get_state()

STATE['current_step'] = 0
STATE['bpm'] = 122

STATE['tracks'] = [
    {'channel': 0, 'stutter': False, 'volume': 1, 'sample_id': 'dt_synth_122_sing_G#m.wav', 'grid': [0]},
    {'channel': 1, 'stutter': True, 'volume': 1, 'sample_id': 'kick.wav', 'grid': [0,4,8,12]},
    {'channel': 2, 'stutter': True, 'volume': 1, 'sample_id': 'hat-2.wav', 'grid': [0,2,4,8,10,11,12]},
    {'channel': 3, 'stutter': True, 'volume': 1, 'sample_id': 'hat-3.wav', 'grid': [0,2,4,8,10,11,12]},
]

# print(CHANNELS[0])

set_state(STATE)

# hey!

window = {}

log('hey!')

# load library

load_samples()

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # self.actionExit.setShortcutContext(QtCore.Qt.ApplicationShortcut)
        self.shortcut = QShortcut(QKeySequence("ESCAPE"), self)
        self.shortcut.activated.connect(self.on_quit)

        self.shortcut = QShortcut(QKeySequence("Ctrl+Q"), self)
        self.shortcut.activated.connect(self.on_quit)

        self.window_width = CONFIG['window_width']
        self.window_height = CONFIG['window_height']

        self.tracks_padding_left = 20
        self.tracks_padding_right = 20

        self.label = QtWidgets.QLabel()
        canvas = QtGui.QPixmap(self.window_width, self.window_height)

        self.setWindowTitle(CONFIG['app_name'])
        self.setFixedSize(self.window_width, self.window_height)

        self.label.setPixmap(canvas)
        self.setCentralWidget(self.label)
        self.draw()

        self.btn = QPushButton("play", self)
        # self.btn.clicked.connect(self.draw())
        self.btn.move(10, 10)

        # self.timer = QtCore.QTimer()
        # self.timer.timeout.connect(self.draw)
        # self.timer.start(70)

    def on_quit(self):
        STATE['do_quit'] = True
        exit()

    def draw(self):
        p = QtGui.QPainter(self.label.pixmap())

        p.fillRect(self.rect(), QColor(0, 0, 0, 190))

        def draw_tracks(p):
            tracks_width = (self.window_width - (self.tracks_padding_left + self.tracks_padding_right))

            steps = 16 * STATE['bars']

            track_cell_height = 90
            track_cell_width = tracks_width / steps

            y = 0
            for track in STATE['tracks']:
                for step in range(0, (16 * STATE['bars'])):
                    # p.setBrush(QBrush(Qt.green, Qt.DiagCrossPattern))
                    # p.drawRect(self.tracks_padding_left+(step*track_cell_width), y*track_cell_height, track_cell_width,track_cell_height)

                    # waveform_path = track['sample_id'].replace(
                    #     CONFIG['samples_dir'],
                    #     CONFIG['waveforms_dir']
                    # ).replace('.wav', '.gif')

                    # print(waveform_path)

                    ahead = 0

                    for n in range(step, (16 * STATE['bars'])):
                        if n not in track['grid']:
                            ahead = ahead + 1
                        else:
                            break

                    if step in track['grid']:
                        p.drawImage(
                            QtCore.QRect(
                                self.tracks_padding_left+((step+ahead)*track_cell_width),
                                y*track_cell_height,
                                track_cell_height,
                                track_cell_width
                            ),
                            QtGui.QImage('%s/%s' % (CONFIG['waveforms_dir'], track['sample_id'].replace('.wav', '.gif')))
                        )
                y = y + 1

            # y = 0
            # for n in range(0,4):
            #     for x in range(0,8):
            #         p.drawRect(y, st, 400,200)
                    # p.drawImage(
                    #     QtCore.QRect(x*width, y, width, width),
                    #     QtGui.QImage("waveforms/Abletunes TSD Snare 27.gif")
                    # )
            #     y = y + width

        def draw_cursor(p):
            pen = QPen(Qt.white, 3)
            p.setPen(pen)

            steps = 16 * STATE['bars']
            
            tracks_width = (self.window_width - (self.tracks_padding_left + self.tracks_padding_right))

            x = (tracks_width/steps) * STATE['current_step']

            p.drawLine(
                x,
                0,
                x,
                self.window_height
                )

        def draw_text(p):
            p.drawText(
                random.randint(0,100),
                random.randint(0,100),
                str(STATE['bpm'])
                )

        draw_tracks(p)
        draw_cursor(p)
        draw_text(p)

        p.end()

        self.update()

def update_window():
    if window:
        window.draw()

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

    delay = d = 60 / 120
    print(60 / delay, 'bpm')
    prev = perf_counter()

    # for i in range(20):
        

    DELTA = (60/(STATE['bpm'] * 4))
    GOAL = time()

    max_steps = 16 * STATE['bars']
    step = STATE['current_step']

    while True:
        if step >= max_steps:
            step = 0

        update_window()

        STATE['current_step'] = step

        play_output = []

        if 'do_quit' in STATE and STATE['do_quit']:
            exit()

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
                    play_output.append('[%s]' % TRACK['sample_id'][0:6])

        log('playing %s' % (' '.join(play_output)))

        # print('%s/%s %s' % (step, max_steps, ))

        if step % 8 == 0 and random.randint(0,100) > 40:
            random_track = random.choice(STATE['tracks'])
            shuffle_track(random_track)

        step = step + 1

        sleep(d)
        t = perf_counter()
        delta = t - prev - delay
        print('{:+.9f}'.format(delta))
        d -= delta
        prev = t

        # GOAL += DELTA

        # gc.collect()

        # sleepInterval = GOAL - time()

        # if sleepInterval >= 0:
        #     sleep(sleepInterval)
        # else:
        #     sleep(0)

if __name__ == '__main__':
    Thread(target = audioManager).start()

    # app = QtWidgets.QApplication(sys.argv)
    
    # window = MainWindow()
    # window.show()
    # app.exec_()


