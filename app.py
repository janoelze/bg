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

window = Tk()

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
            redraw_tracks()

        redraw_cursor()

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

def redraw_cursor():
    if 'canvas' not in UI:
        return False

    if 'pointer' in UI:
        UI['canvas'].delete(UI['pointer'])

    # UI['canvas'].delete("all")

    width = UI['tfWidth']
    height = UI['tfHeight']

    cursorStepWidth = UI['tfWidth'] / 16
    cursorStepCurrentX = cursorStepWidth * UI['currentStep']

    # print(cursorStepCurrentX)

    UI['pointer'] = UI['canvas'].create_line(cursorStepCurrentX, 0, cursorStepCurrentX, UI['tfHeight'], fill="#000", width=2)

    # UI['canvas'].move(UI['pointer'], cursorStepCurrentX, 0)
    # UI['canvas'].move(UI['pointer'], random.randint(0,100), random.randint(0,100))

TRACKMARKER = []

def redraw_tracks():
    if 'canvas' not in UI:
        return False

    for m in TRACKMARKER:
        UI['canvas'].delete(m)

    width = UI['tfWidth']
    height = UI['tfHeight']

    cursorStepWidth = UI['tfWidth'] / 16
    cursorStepCurrentX = cursorStepWidth * UI['currentStep']

    # UI['canvas'].create_line(cursorStepCurrentX, 0, cursorStepCurrentX, UI['tfHeight'], fill="#000", width=2)

    # UI['canvas'].coords(UI['pointer'], )

    y = 0
    for TRACK in STATE['tracks']:
        for step in TRACK['grid']:
            marker_x = step * cursorStepWidth
            m = UI['canvas'].create_text(marker_x, y, text='x')
            TRACKMARKER.append(m)
        y = y + 20

    # if 'canvas' in UI:
        # 
        # UI['pointerX'] = random.randint(0,100)
        # UI['pointerY'] = random.randint(0,100)
        # UI['canvas'].update()

        # UI['bpm'].set(random.randint(0,10))
        # UI['canvas'].move(UI['pointer'], random.randint(0,100), random.randint(0,100))

if __name__ == '__main__':
    # webview.create_window('Woah dude!', html='<h1>Woah dude!<h1>')
    # webview.start()

    Thread(target = audioManager).start()

    title_frame = Frame(window).pack()
    tracks_frame = Frame(window).pack(side = "bottom")

    # canvas.create_line(15, 25, 200, 25)

    UI['canvas'] = Canvas(tracks_frame, width=UI['tfWidth'], height=UI['tfHeight'], borderwidth=2, highlightbackground='#000')
    UI['canvas'].pack()

    # UI['pointer'] = UI['canvas'].create_rectangle(UI['pointerX'], UI['pointerY'], UI['pointerX']+10, UI['pointerY']+10, fill='red')

    UI['pointer'] = UI['canvas'].create_line(0, 0, 0, UI['tfHeight'], fill="#000", width=2)

    # width = 40
    # height = 90

    # img = Image.open("waveforms/top-loop.gif")
    # img = img.resize((width, height), Image.ANTIALIAS)
    # photoImg = ImageTk.PhotoImage(img)

    # img = Image.open("waveforms/BFM_BS3_SynthLoop_09_Bbm_125bpm.gif")
    # img = img.resize((width, height), Image.ANTIALIAS)
    # photoImg2 = ImageTk.PhotoImage(img)

    # for x in range(1,10):
    #     y = 10
    #     UI['canvas'].create_image((x*42), y, image=photoImg)

    # for x in range(1,10):
    #     y = 102
    #     UI['canvas'].create_image((x*42), y, image=photoImg2)

    # img = PhotoImage(file='waveforms/top-loop.gif')
    
    # UI['canvas'].create_image(62, 30, image=photoImg)
    # UI['canvas'].create_image(104, 30, image=photoImg)


    # UI['pointer'].coords(20,30)

    # a 
    # canvas.move(a, 10, 20)

    lbl1 = Label(title_frame, text='a').pack()
    lbl2 = Label(tracks_frame, text='a').pack()


    # btn1 = Button(top_frame, text = "Button1", fg = "red").pack()# 'fg - foreground' is used to color the contents
    # btn2 = Button(top_frame, text = "Button2", fg = "green").pack()# 'text' is used to write the text on the Button
    # btn3 = Button(bottom_frame, text = "Button2", fg = "purple").pack(side = "left")# 'side' is used to align the widgets
    # btn4 = Button(bottom_frame, text = "Button2", fg = "orange").pack(side = "left")

    # mainframe = Frame(window)
    # mainframe.pack()

    # titleframe = Frame(mainframe)
    # titleframe.pack(side = BOTTOM)

    window.title("beats")

    window.mainloop()

    # while True:
        # time.sleep(1)

    # class Application(tk.Frame):
    #     def __init__(self, master=None):
    #         super().__init__(master)
    #         self.master = master
    #         self.pack()
    #         self.create_widgets()

    #         Thread(target = audioManager).start()

    #     def create_widgets(self):
    #         self.hi_there = tk.Button(self)
    #         self.hi_there["text"] = "Hello World\n(click me)"
    #         self.hi_there["command"] = self.say_hi
    #         self.hi_there.pack(side="top")

    #         self.quit = tk.Button(self, text="QUIT", fg="red",
    #                               command=self.master.destroy)
    #         self.quit.pack(side="bottom")

    #     def say_hi(self):
    #         print("hi there, everyone!")

    # root = tk.Tk()
    # app = Application(master=root)
    # app.mainloop()

    
    # Thread(target = windowManager).start()

    

exit()



# data, samplerate = soundfile.read('audio/MGF_EURO1_HIT_01.wav')

# BPM = 160
# DELTA = 60/BPM

# sound = pygame.mixer.Sound('audio/MGF_EURO1_HIT_01-16.wav')
# sound2 = pygame.mixer.Sound('audio/MGF_EURO1_HIT_01-16.wav')
# goal = time()

# while True:
#     print(time() - goal)
#     sound.play()
#     goal += DELTA
#     gc.collect()
#     sleep(goal - time())

# import pygame
# # import tempfile
# # from pydub import AudioSegment
# # from urllib.request import urlopen
# import soundfile as sf

# TRACKS = [
#     {'type': 'audio', 'src': 'audio/RK_DT4_Kick_05.wav'}
# ]

# def play(TRACK):
#     print(TRACK)
#     newfile = TRACK['src'].replace('wav', 'ogg')
#     data, samplerate = sf.read(TRACK['src'])
#     print(samplerate)
#     sf.write(newfile, data, samplerate)
#     # AudioSegment.from_mp3(TRACK['src']).export('result.ogg', format='ogg')
#     sound1 = pygame.mixer.Sound(newfile)
#     sound1.play()

# if __name__ == '__main__':
#     pygame.mixer.init()
#     play(TRACKS[0])

# while True:
#     pygame.mixer.init()
#     inpt = input('Press enter to play the sound: ')
#     sound1.play()
#     print('Playing sound')

# import pygame
# import os
# import time
# import random
# from _thread import *
# import swmixer
# import time

# swmixer.init(samplerate=44100, chunksize=1024, stereo=False)
# swmixer.start()
# snd = swmixer.Sound("test1.wav")
# snd.play()
# time.sleep(2.0) #don't quit before we hear the sound!

# _sound_library = {}

# def play_sound(path):
#   global _sound_library

#   sound = _sound_library.get(path)

#   if sound == None:
#     # canonicalized_path = os.path.abspath(path)
#     # canonicalized_path = path.replace('/', os.sep).replace('\\', os.sep)
#     # print(canonicalized_path)
#     sound = pygame.mixer.Sound(path)
#     _sound_library[path] = sound
#   sound.play()

# if __name__ == '__main__':
#     pygame.mixer.init(44100, -16, 2, 2048)
#     pygame.init()

#     # sound = pygame.mixer.Sound('Reblaus.mp3')
#     # sound.play()


#     pygame.mixer.music.load('Reblaus.mp3')
#     pygame.mixer.music.play()
#     time.sleep(2)
#     pygame.mixer.music.stop()

#     # play_sound('Reblaus.mp3')
