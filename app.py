# pip3 install pygame==2.0.0.dev6
# buttons https://stackoverflow.com/questions/10990137/pygame-mouse-clicking-detection
# trigger https://github.com/akjmicro/pystepseq/blob/master/pystepseq/tempotrigger.py
# https://github.com/arosspope/pi-thrum/blob/master/step.py

from clockblocks import Clock
import time, math
from threading import Thread
from math import floor
import contextlib
import sounddevice as sd

with contextlib.redirect_stdout(None):
    import pygame

import json
import os.path
import glob
import random
import soundfile as sf
from waveform import Waveform, draw_waveform_array, draw_waveform_cell, get_waveform_data
from os import path
# from time import time, sleep
from datetime import datetime

from gabber import Gabber
from state import get_state, set_state, persist_state, recover_state, get_state_all, set_state_all

RUN = True

# ram stores

_sound_library = {}
_image_library = {}

# config

CONFIG = {
    'app_name': 'bg @ 0.1',
    'fps': 20,
    'window_width': 600,
    'window_height': 400,
    'channel_num': 4,
    'bars': 1,
    'pulse_file': 'modular-pulse.wav',
    'store_dir': 'data/',
    'waveforms_dir': 'waveforms/',
    'samples_dir': 'samples/',
    'library_dir': 'library/'
}

# setup pulse

i = 0
for device in sd.query_devices():
    if 'C-Media' in device['name'] and device['max_output_channels'] > 0:
        set_state('pulse_device', i)
    i = i + 1

pulse_data, pulse_fs = sf.read(CONFIG['pulse_file'], dtype='float32')

# helper

def log(msg):
    print('%s: %s' % (datetime.utcnow().strftime('%M:%S.%f')[:-4], msg))

# def get_state():
#     if path.exists(CONFIG['store_dir'] + '/state.json'):
#         with open(CONFIG['store_dir'] + '/state.json') as json_file:
#             return json.load(json_file)
#     else:
#         return {
#             'bpm': 120,
#             'bars': CONFIG['bars']
#         }

def play(channel, sample_id):
    if sample_id in _sound_library:
        channel.play(_sound_library[sample_id])

# def set_state(state):
#     with open(CONFIG['store_dir'] + '/state.json', 'w') as outfile:
#         return json.dump(state, outfile)

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

        # get_waveform_array(filename, 100)

        # exit()

        if not path.exists(wv_filename):
            log('creating waveform for %s' % filename)

            waveform = Waveform(filename)
            waveform.save(wv_filename)

        _image_library[os.path.basename(wv_filename)] = pygame.image.load(wv_filename)

# audio channel init

with contextlib.redirect_stdout(None):
    pygame.mixer.pre_init(44100, -16, 2, 256)
    pygame.mixer.init()
    pygame.init()

CHANNELS = []

for i in range(0, CONFIG['channel_num']):
    CHANNELS.append(pygame.mixer.Channel(i))

# recover state

# STATE = get_state_all()

recover_state()

set_state('app_run', True)
set_state('volume', 0.3)
set_state('tempo', 120)

set_state('tracks', [
    # {'channel': 0, 'locked': False, 'stutter': False, 'volume': 1, 'sample_id': 'PRCT_123_E_Synth_Loop_4_Wet copy 4.wav', 'grid': [0,2]},
    # {'channel': 1, 'locked': False, 'stutter': True, 'volume': 1, 'sample_id': 'Ensemble [120] F AgingGold 1.wav', 'grid': [0,4,6]},
    {'channel': 2, 'locked': True, 'stutter': True, 'volume': 1, 'sample_id': 'kick.wav', 'grid': [0,8]},
    # {'channel': 3, 'locked': False, 'stutter': False, 'volume': 1, 'sample_id': 'hat-3.wav', 'grid': [2,6,10,14]},
])

# set_state_all(STATE)

load_samples()

def main():
    global RUN

    # initializes Pygame
    pygame.init()

    # sets the window title
    pygame.display.set_caption(CONFIG['app_name'])

    # sets the window size
    screen = pygame.display.set_mode((
        CONFIG['window_width'],
        CONFIG['window_height']
    ), pygame.RESIZABLE)
    
    # screen.fill((0,0,0))

    # pygame.display.update()

    # creates a clock
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('arial', 16)

    RED = (255, 0, 0)
    GRAY = (150, 150, 150)

    def draw():
        # TOTAL_STEPS = 16 * get_state('bars')

        screen.fill((0,0,0))

        txt_time = font.render(
            datetime.utcnow().strftime('%M:%S.%f')[:-4],
            True,
            (255,255,255)
        )

        txt_step = font.render(
            str('%s/%s' % (get_state('ticks'), get_state('total_ticks'))),
            True,
            (255,255,255)
        )

        # print(STATE['current_step'])

        screen.blit(txt_time,(0, 0))
        screen.blit(txt_step,(0, 20))

        # draw tracks

        # tracks_padding_left = 40
        # tracks_padding_right = 20

        # tracks_width = CONFIG['window_width']

        # track_cell_height = 70
        # track_cell_width = tracks_width / TOTAL_STEPS

        # grid_left = 0
        # beat = 0

        # for x in range(0, TOTAL_STEPS):
        #     if grid_left > 0:
        #         if beat >= 4:
        #             pygame.draw.line(screen, (50,50,50), (grid_left,0),(grid_left, CONFIG['window_height']), 1)
        #             beat = 0
        #         else:
        #             pygame.draw.line(screen, (30,30,30), (grid_left,0),(grid_left, CONFIG['window_height']), 1)

        #     beat = beat + 1
        #     grid_left = grid_left + track_cell_width

        # print(track_cell_width)

        # y = 0

        # for track in STATE['tracks']:
        #     sample_filename ='%s/%s' % (CONFIG['samples_dir'], track['sample_id'])
        #     for x in range(0, steps+1):
        #         if x in track['grid']:
        #             multiplier = 0

        #             for lookahead in range(0,16):
        #                 if (x + lookahead) not in track['grid']:
        #                     multiplier = multiplier + 1
        #                 else:
        #                     break

        #             draw_waveform_cell(screen, sample_filename, x * track_cell_width, y*track_cell_height, track_cell_height, track_cell_width)
        #         else:
        #             draw_waveform_cell(screen, 'n/a', x * track_cell_width, y*track_cell_height, track_cell_height, track_cell_width)
        #     # draw_waveform_array(screen, '%s/%s' % (CONFIG['samples_dir'], track['sample_id']), floor(CONFIG['window_width']/4), y*track_cell_height, track_cell_height, STATE['bpm'])
        #     y = y + 1

        # draw cursor

        pygame.draw.rect(screen,(255,255,255),(20,20,CONFIG['window_width']-20,CONFIG['window_height']-90),1)

        TOTAL_STEPS = 16 * CONFIG['bars']
        CHANNEL_HEIGHT = 80
        TOTAL_LINES = int((CONFIG['window_width']-25)/2)
        LINES_PER_BAR = int(TOTAL_LINES / 16)

        # print('TOTAL_STEPS', TOTAL_STEPS)
        # print('CHANNEL_HEIGHT', CHANNEL_HEIGHT)
        # print('LINE_SLOTS', LINE_SLOTS)
        # print('TOTAL_LINES', TOTAL_LINES)
        # print('LINES_PER_BAR', LINES_PER_BAR)

        CURSOR_TO_DRAW = []
        GRID_TO_DRAW = []
        # BGRID_TO_DRAW = []
        LINES_TO_DRAW = []

        # BARS_PROGRESSED = 0

        # for n in range(0, TOTAL_LINES):
        #     GRID_TO_DRAW

        # counter = LINES_PER_BAR
        # step_counter = 4

        # for n in range(0, TOTAL_LINES):
        #     counter = counter - 1

        #     if counter <= 0:
        #         step_counter = step_counter - 1

        #         line_color = (30,30,30)

        #         if step_counter <= 0:
        #             line_color = (60,60,60)
        #             step_counter = 4

        #         if len(GRID_TO_DRAW) == STATE['current_step']:
        #             line_color = (255,255,255)

        #         GRID_TO_DRAW.append([
        #             n*2,
        #             0,
        #             n*2,
        #             CONFIG['window_height'],
        #             line_color
        #         ])

        #         counter = LINES_PER_BAR

        # posx = 0
        # counter = (LINES_PER_BAR*4)
        # for n in range(0, TOTAL_LINES):
        #     counter = counter - 1

        #     if counter <= 0:
        #         # BGRID_TO_DRAW.append([
        #         #     n,
        #         #     0,
        #         #     n,
        #         #     CONFIG['window_height']
        #         # ])
        #         counter = TOTAL_STEPS
        #     posx = posx + 2

        posy = 0
        # counter = LINES_PER_BAR*4
        # hits = 0

        for track in get_state('tracks'):
            sample_filename ='%s/%s' % (CONFIG['samples_dir'], track['sample_id'])
            wv_data = get_waveform_data(sample_filename)
            sorted_hits = sorted(track['grid'])

            LINE_BUFFER = []

            current_wv_buffer = []
            current_step = 0
            current_step_counter = LINES_PER_BAR

            if 0 in track['grid']:
                current_wv_buffer = wv_data.copy()

            for n in range(0, TOTAL_LINES):
                current_step_counter = current_step_counter - 1

                if current_step_counter <= 0:
                    current_step = current_step + 1
                    current_step_counter = LINES_PER_BAR

                    if current_step in track['grid']:
                        current_wv_buffer = wv_data.copy()

                if len(current_wv_buffer):
                    LINE_BUFFER.append(current_wv_buffer[0])
                    current_wv_buffer.pop(0)
                else:
                    LINE_BUFFER.append(0)


            for n in range(0, TOTAL_LINES):
                LINE_BUFFER.append(0)

            for step in range(0, TOTAL_STEPS):
                if step in track['grid']:
                    # print(step*LINES_PER_BAR)
                    # print(len(LINE_BUFFER))
                    # exit()

                    value_i = 0
                    for value in wv_data[0:1]:
                        try:
                            LINE_BUFFER[(LINES_PER_BAR * step) + value_i] = value
                        except Exception as e:
                            pass
                        value_i = value_i + 1

            steps_counter = 0
            bars_counter = 0
            posx = 20
            for VALUE in LINE_BUFFER:
                steps_counter = steps_counter - 1

                if steps_counter <= 0:
                    
                    steps_counter = LINES_PER_BAR

                    line_color = (30,30,30)

                    if bars_counter <= 0:
                        bars_counter = 4
                        line_color = (50,50,50)

                    bars_counter = bars_counter - 1

                    GRID_TO_DRAW.append([
                        posx,
                        0,
                        posx,
                        CONFIG['window_height'],
                        line_color
                    ])

                LINE_HEIGHT = (VALUE*1.5) + random.randint(-2,2)
                curr_y = posy + ((CHANNEL_HEIGHT - LINE_HEIGHT)/2)

                LINES_TO_DRAW.append([
                    posx,
                    curr_y,
                    posx,
                    curr_y + LINE_HEIGHT
                ])

                posx = posx + 1

            posy = posy + CHANNEL_HEIGHT

        for LINE in GRID_TO_DRAW:
            # if LINE[0] < (CONFIG['window_width']):
            pygame.draw.line(
                screen,
                LINE[4],
                (LINE[0], LINE[1]),
                (LINE[2], LINE[3]),
                1
            )

        # i = 0
        for LINE in LINES_TO_DRAW:
            # if LINE[0] < (CONFIG['window_width']):
            pygame.draw.line(
                screen,
                (255,255,255),
                (LINE[0], LINE[1]),
                (LINE[2], LINE[3]),
                1
            )
            # i = i + 1

        # for LINE in CURSOR_TO_DRAW:
        #     pygame.draw.line(
        #         screen,
        #         (255,255,255),
        #         (LINE[0], LINE[1]),
        #         (LINE[2], LINE[3]),
        #         1
        #     )

        # for LINE in BGRID_TO_DRAW:
        #     pygame.draw.line(
        #         screen,
        #         (255,255,255),
        #         (LINE[0], LINE[1]),
        #         (LINE[2], LINE[3]),
        #         1
        #     )


        # exit()

        # posy = 0

        # for track in STATE['tracks']:
        #     sample_filename ='%s/%s' % (CONFIG['samples_dir'], track['sample_id'])
        #     wv_data = get_waveform_data(sample_filename)

        #     sorted_hits = sorted(track['grid'])

        #     def draw_hit(wv_data, sorted_hits, posx):
        #         length = 1

        #         for s in range(0, TOTAL_STEPS):
        #             has_next = ((hit+s) not in sorted_hits)
        #             if not has_next:
        #                 length = length + 1
        #             else:
        #                 break

        #         for bar_num in range(1, int((track_cell_width*length))+1):
        #             value = 0

        #             try:
        #                 if bar_num <= len(wv_data):
        #                     value = wv_data[bar_num]
        #             except Exception as e:
        #                 value = 0

        #             # curr_y = posy + ((track_cell_height - item_height)/2)

        #             item_height = (value*1.5) + random.randint(-2,2)
        #             curr_y = posy + ((track_cell_height - item_height)/2)

        #             if posx < (CONFIG['window_width']-4):
        #                 pygame.draw.line(
        #                     screen,
        #                     (255,255,255),
        #                     (posx, curr_y),
        #                     (posx, curr_y + item_height),
        #                     1
        #                 )

        #             posx = posx + 2

        #     first_hit = False

        #     for hit in range(0, TOTAL_STEPS):
        #         posx = track_cell_width * hit
        #         if hit in sorted_hits:
        #             draw_hit(wv_data, sorted_hits, posx)
        #         else:
        #             pass
        #             # if not first_hit:
        #             #     draw_hit([], sorted_hits, posx, first_hit)


        #     posy = posy + track_cell_height


        #     # print(wv_data)

        #     # draw_step = 0
        #     # draw_x = 0
        #     BARS = []

        #     # current_bars = []
        #     # total_steps = int(CONFIG['window_width'] / 2)

        #     # print(int(CONFIG['window_width'] / 16))
        #     # exit()

        #     bars_count = int(CONFIG['window_width'] / 2)
        #     step_bar_count = int(bars_count / 16)
        #     current_step = 0
        #     segment_counter = 0
        #     data_index = 0

        #     bar_counter = 0

        #     # print(bars_count)
        #     # print(step_bar_count)
        #     # print(current_step)
        #     # print(data_index)

        #     # print(track['grid'])

        #     sorted_hits = sorted(track['grid'])

        #     for bar_num in range(0, bars_count):
        #         if bar_counter > step_bar_count:
        #             bar_counter = 0
        #             current_step = current_step + 1

        #             if current_step in track['grid']:
        #                 data_index = 0

        #         try:
        #             BARS.append(wv_data[data_index])
        #         except Exception as e:
        #             BARS.append(0)

        #         bar_counter = bar_counter + 1

        #         # if segment_counter > step_bar_count:
        #         #     segments_progressed = segments_progressed + 1
        #         #     segment_counter = 0

        #         # if data_index <= len(wv_data):
        #         #     print(wv_data[data_index])
        #         #     BARS.append(wv_data[data_index])
        #         # else:
        #         #     BARS.append(0)

        #         data_index=data_index+1
        #         # segment_counter=segment_counter+1

        #     posx = 0

        #     # print(BARS)

        #     # for column in BARS:
        #     #     item_height = (column*1.5) + random.randint(-1,1)

        #     #     curr_y = posy + ((track_cell_height - item_height)/2)
        #     #     # curr_x = posx + x_left 

        #     #     # if x_left <= int(track_cell_width):
        #     #     line_color = (255,255,255)

        #     #     #     if x_left==0:
        #     #     # line_color = (255,0,0)

        #     #     pygame.draw.line(
        #     #         screen,
        #     #         line_color,
        #     #         (posx, curr_y),
        #     #         (posx, curr_y + item_height),
        #     #         1
        #     #     )

        #     #     # x_left = x_left + 4

        #     #     posx = posx + 2

        #     # posy = posy + track_cell_height



        #         # if draw_step in track['grid']:
        #         #     array_index = 0


        #             # print(draw_step)
        #             # for rms in wv_data:


        #             # for bar_count in range(0, steps_per_bar):
        #             #     print(bar_count)

        #         #     if bar_count <= len(wv_data):
        #         #         current_bars.append(wv_data[bar_count])
        #         #     else:
        #         #         current_bars.append(0)
        #         # if draw_step in track['grid']:
        #         #     current_bars = get_waveform_data(sample_filename)
        #         # else:

        #     # 

        # draw cursor

        # for i in range(0,steps+1):
        #     pygame.draw.line(screen, (90,90,90), ((track_cell_width*i)+1,0),((track_cell_width*i)+1,CONFIG['window_height']), 1)

        # x = (tracks_width/steps) * 
        # cursor_x = (track_cell_width * (STATE['current_step']-1))

        # print(cursor_x)

        # pygame.draw.line(screen, (255,255,255), (cursor_x,0),(cursor_x,CONFIG['window_height']), 1)

        pygame.display.update()

    while RUN:
        draw()

        # screen.fill((0,0,0))
        # screen.blit(time,(0, 0))#

        # screen.fill((0,0,255))

        # gets the state of all keyboard modifiers
        mod_bitmask = pygame.key.get_mods()

        # gets events from the event queue
        for event in pygame.event.get():
            # if the 'close' button of the window is pressed
            if event.type == pygame.KEYUP and (mod_bitmask & pygame.KMOD_META):
                if event.key == pygame.K_q:
                    is_running = False
                    RUN = False

            if event.type == pygame.QUIT:
                # stops the application
                is_running = False
                RUN = False

            if event.type == pygame.VIDEORESIZE:
                # There's some code to add back window content here.
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)

        # captures the activated modifiers
        # if mod_bitmask & pygame.KMOD_NONE:
        #     print('"pygame.KMOD_NONE" modifier activated')
        # if mod_bitmask & pygame.KMOD_LSHIFT:
        #     print('"pygame.KMOD_LSHIFT" modifier activated')
        # if mod_bitmask & pygame.KMOD_RSHIFT:
        #     print('"pygame.KMOD_RSHIFT" modifier activated')
        # if mod_bitmask & pygame.KMOD_SHIFT:
        #     print('"pygame.KMOD_SHIFT" modifier activated')
        # if mod_bitmask & pygame.KMOD_LCTRL:
        #     print('"pygame.KMOD_LCTRL" modifier activated')
        # if mod_bitmask & pygame.KMOD_RCTRL:
        #     print('"pygame.KMOD_RCTRL" modifier activated')
        # if mod_bitmask & pygame.KMOD_CTRL:
        #     print('"pygame.KMOD_CTRL" modifier activated')
        # if mod_bitmask & pygame.KMOD_LALT:
        #     print('"pygame.KMOD_LALT" modifier activated')
        # if mod_bitmask & pygame.KMOD_RALT:
        #     print('"pygame.KMOD_RALT" modifier activated')
        # if mod_bitmask & pygame.KMOD_ALT:
        #     print('"pygame.KMOD_ALT" modifier activated')
        # if mod_bitmask & pygame.KMOD_LMETA:
        #     print('"pygame.KMOD_LMETA" modifier activated')
        # if mod_bitmask & pygame.KMOD_RMETA:
        #     print('"pygame.KMOD_RMETA" modifier activated')
        # if mod_bitmask & pygame.KMOD_META:
        #     print('"pygame.KMOD_META" modifier activated')
        # if mod_bitmask & pygame.KMOD_NUM:
        #     print('"pygame.KMOD_NUM" modifier activated')
        # if mod_bitmask & pygame.KMOD_CAPS:
        #     print('"pygame.KMOD_CAPS" modifier activated')
        # if mod_bitmask & pygame.KMOD_MODE:
        #     print('"pygame.KMOD_MODE" modifier activated')

        # limits updates to 5 frames per second (FPS)
        clock.tick(CONFIG['fps'])

    # finalizes Pygame
    pygame.quit()

def play_samples():
    print('p')

def play_pulse():
    pulse_device = get_state('pulse_device')

    if pulse_device:
        sd.play(pulse_data, pulse_fs, device=pulse_device)

if __name__ == '__main__':
    def on_beat(g, tick, total_ticks):
        set_state('tick', tick)
        set_state('total_ticks', total_ticks)

        play_pulse()
        play_samples()

        print(tick, total_ticks)

    g = Gabber(on_beat)

    print(get_state('tempo'))

    g.set_tempo(get_state('tempo'))

    main()
