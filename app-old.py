# http://echonest.github.io/remix/

import pygame
from time import time, sleep
import gc
import glob
import random
import soundfile as sf
import os.path
import webview
from threading import Thread

from tkinter import *
from PIL import Image
from PIL import ImageTk

# from ui import UIManager
from waveform import Waveform

# ui = UIManager()

# window = Tk()

pygame.mixer.pre_init(44100, -16, 2, 256)
pygame.mixer.init()
pygame.init()

ch1 = pygame.mixer.Channel(0)
ch2 = pygame.mixer.Channel(1)
ch3 = pygame.mixer.Channel(2)
ch4 = pygame.mixer.Channel(3)

_sound_library = {}

for file in glob.glob('sources/*.wav'):
    newFile = file.replace('sources/', 'processed/')
    data, samplerate = sf.read(file)
    sf.write(newFile, data, 44100, subtype='PCM_16')

for file in glob.glob('processed/*.wav'):
    sound = pygame.mixer.Sound(file)
    _sound_library[os.path.basename(file)] = sound

    wv_file = file.replace('processed/', 'waveforms/').replace('.wav', '.gif')
    waveform = Waveform(file)
    waveform.save(wv_file)

def play(channel, audio_id):
    if audio_id in _sound_library:
        channel.play(_sound_library[audio_id])

UI = {
    'pointerX': 0,
    'pointerY': 0,
    'tfWidth': 300,
    'tfHeight': 200
}

STATE = {
    'conf': {
        'bpm': 125
    },
    'tracks': [
        {'channel': ch1, 'stutter': True, 'volume': 1, 'audio_id': 'dt_kick_big.wav', 'grid': [0,4,8,12]},
        {'channel': ch2, 'stutter': False, 'volume': 1, 'audio_id': 'dt_hat_bart.wav', 'grid': [0]},
        {'channel': ch3, 'stutter': True, 'volume': 1, 'audio_id': 'dt_fxloop_120_below.wav', 'grid': [0]},
        {'channel': ch4, 'stutter': True, 'volume': 1, 'audio_id': 'HiHat 17.wav', 'grid': [1,2,3,4,6,8,10,14]},
        # {'channel': ch1, 'stutter': False, 'volume': 1, 'audio_id': 'RK_DT4_Beat_Loop_09_124bpm.wav', 'grid': [0,4,8,12]},
        # {'channel': ch2, 'stutter': False, 'volume': 1, 'audio_id': 'RK_DT4_Bass_Loop_24_125bpm_C.wav', 'grid': [0]},
        # {'channel': ch3, 'stutter': False, 'volume': 1, 'audio_id': 'Echo Noise Burst 01.wav', 'grid': [0]},
        # {'channel': ch4, 'stutter': True, 'volume': 1, 'audio_id': 'HiHat 17.wav', 'grid': [1,2,3,4,6,8,10,14]},
    ]
}

def audioManager():
    GLOBAL_BARS = 1
    GLOBAL_STEPS = 16 * GLOBAL_BARS
    BPM = 125*4
    DELTA = 60/BPM
    goal = time()
    i = 0

    TRACKS = []

    def shuffle_track(TRACK):
        inc = random.randint(1,8)
        grid = []

        step = 0
        while step <= GLOBAL_STEPS:
            grid.append(step)
            step = step + inc

        TRACK['grid'] = grid

    for TRACK in STATE['tracks']:
        shuffle_track(TRACK)

    while True:
        if i >= GLOBAL_STEPS:
            i = 0

        UI['currentStep'] = i

        played = []

        for TRACK in STATE['tracks']:
            TRACK['channel'].set_volume(TRACK['volume'])

            if TRACK['stutter']:
                TRACK['channel'].set_volume(random.randint(80,100)/100)

            if i in TRACK['grid']:
                if TRACK['channel'].get_busy():
                    TRACK['channel'].stop()

                play(TRACK['channel'], TRACK['audio_id'])
                played.append(TRACK['audio_id'])

        print('%s/%s %s' % (i, GLOBAL_STEPS, ', '.join(played)))

        if i % 8 == 0 and random.randint(0,100) > 40:
            random_track = random.choice(STATE['tracks'])
            shuffle_track(random_track)

        i = i + 1

        goal += DELTA
        gc.collect()

        sleepInterval = goal - time()

        if sleepInterval >= 0:
            sleep(sleepInterval)
        else:
            sleep(0)


        # ui.update({})
# def windowManager():

# def redraw_cursor():
#     if 'canvas' not in UI:
#         return False

#     if 'pointer' in UI:
#         UI['canvas'].delete(UI['pointer'])

#     # UI['canvas'].delete("all")

#     width = UI['tfWidth']
#     height = UI['tfHeight']

#     cursorStepWidth = UI['tfWidth'] / 16
#     cursorStepCurrentX = cursorStepWidth * UI['currentStep']

#     UI['pointer'] = UI['canvas'].create_line(cursorStepCurrentX, 0, cursorStepCurrentX, UI['tfHeight'], fill="#000", width=2)

if __name__ == '__main__':
    Thread(target = audioManager).start()
