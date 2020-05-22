# pip3 install pygame==2.0.0.dev6

import clockblocks
import time, math
from threading import Thread
from math import floor
import contextlib

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
            'bars': CONFIG['bars']
        }

def play(channel, sample_id):
    if sample_id in _sound_library:
        channel.play(_sound_library[sample_id])

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

STATE = get_state()

STATE['current_step'] = 0
STATE['max_steps'] = 0
STATE['bpm'] = 120
STATE['volume'] = 0.3

STATE['tracks'] = [
    # {'channel': 0, 'locked': False, 'stutter': False, 'volume': 1, 'sample_id': 'PRCT_123_E_Synth_Loop_4_Wet copy 4.wav', 'grid': [0,2]},
    {'channel': 1, 'locked': False, 'stutter': True, 'volume': 1, 'sample_id': 'Ensemble [120] F AgingGold 1.wav', 'grid': [0,4,6]},
    {'channel': 2, 'locked': False, 'stutter': True, 'volume': 1, 'sample_id': 'kick.wav', 'grid': [0,4,8,12]},
    # {'channel': 3, 'locked': False, 'stutter': False, 'volume': 1, 'sample_id': 'hat-3.wav', 'grid': [2,6,10,14]},
]

# print(CHANNELS[0])

set_state(STATE)

load_samples()

class Gabber(object):
    def __init__(self):
        super(Gabber, self).__init__()

        self.bars = 1
        self.bpb = 4
        self.max_steps = (4 * self.bpb) * self.bars
        self.current_step = 0

        STATE['max_steps'] = self.max_steps

        Thread(target = self.run).start()

    def shuffle_track(self):
        # track = random.choice(STATE['tracks'])
        # print('shuffle')
        random_track = False

        ctracks_cop = STATE['tracks'].copy()
        random.shuffle(ctracks_cop)

        for track in ctracks_cop:
            if 'locked' not in track or not track['locked']:
                random_track = track
                break

        if random_track:
            inc = random.randint(1,8)
            new_grid = []
            s = 0

            while s <= self.max_steps:
                new_grid.append(s)
                s = s + inc

            random_track['grid'] = new_grid

    def run(self):
        global RUN

        clock = clockblocks.Clock()
        start = time.time()

        while RUN:
            if STATE['current_step'] >= STATE['max_steps']:
                STATE['current_step'] = 0

            # update_window()

            # STATE['current_step'] = self.current_step

            play_output = []

            if 'do_quit' in STATE and STATE['do_quit']:
                exit()

            for TRACK in STATE['tracks']:
                channel = CHANNELS[TRACK['channel']]
                sample_id = TRACK['sample_id']

                if 'volume' in TRACK:
                    channel.set_volume(TRACK['volume'] * STATE['volume'])

                if 'stutter' in TRACK and TRACK['stutter']:
                    channel.set_volume((TRACK['volume'] * STATE['volume']) * random.randint(70,100)/100)

                if 'sample_id' in TRACK and 'grid' in TRACK and TRACK['sample_id']:
                    if STATE['current_step'] in TRACK['grid']:
                        if channel.get_busy():
                            channel.stop()

                        play(channel, TRACK['sample_id'])
                        play_output.append('[%s]' % TRACK['sample_id'][0:6])

            log('playing %s' % (' '.join(play_output)))

            # print('%s/%s %s' % (step, max_steps, ))

            if random.randint(0,100) > 90:
                self.shuffle_track()

            # self.current_step = self.current_step + 1
            # STATE['current_step'] = self.current_step

            STATE['current_step'] = STATE['current_step'] + 1

            clock.wait((60/STATE['bpm'])/4)

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
    ), 0, 32)
    
    # screen.fill((0,0,0))

    # pygame.display.update()

    # creates a clock
    clock = pygame.time.Clock()

    font = pygame.font.SysFont('arial', 16)

    RED = (255, 0, 0)
    GRAY = (150, 150, 150)

    def draw():
        TOTAL_STEPS = 16 * STATE['bars']

        screen.fill((0,0,0))

        txt_time = font.render(
            datetime.utcnow().strftime('%M:%S.%f')[:-4],
            True,
            (255,255,255)
        )

        txt_step = font.render(
            str('%s/%s' % (STATE['current_step'], TOTAL_STEPS)),
            True,
            (255,255,255)
        )

        # print(STATE['current_step'])

        screen.blit(txt_time,(0, 0))
        screen.blit(txt_step,(0, 20))

        # draw tracks

        tracks_padding_left = 40
        tracks_padding_right = 20

        tracks_width = CONFIG['window_width']

        track_cell_height = 70
        track_cell_width = tracks_width / TOTAL_STEPS

        grid_left = 0
        beat = 0

        for x in range(0, TOTAL_STEPS):
            if grid_left > 0:
                if beat >= 4:
                    pygame.draw.line(screen, (50,50,50), (grid_left,0),(grid_left, CONFIG['window_height']), 1)
                    beat = 0
                else:
                    pygame.draw.line(screen, (30,30,30), (grid_left,0),(grid_left, CONFIG['window_height']), 1)

            beat = beat + 1
            grid_left = grid_left + track_cell_width

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

        posy = 0

        for track in STATE['tracks']:
            sample_filename ='%s/%s' % (CONFIG['samples_dir'], track['sample_id'])
            wv_data = get_waveform_data(sample_filename)

            sorted_hits = sorted(track['grid'])

            def draw_hit(wv_data, sorted_hits, posx):
                length = 1

                for s in range(0, TOTAL_STEPS):
                    has_next = ((hit+s) not in sorted_hits)
                    if not has_next:
                        length = length + 1
                    else:
                        break

                for bar_num in range(1, int((track_cell_width*length))+1):
                    value = 0

                    try:
                        if bar_num <= len(wv_data):
                            value = wv_data[bar_num]
                    except Exception as e:
                        value = 0

                    # curr_y = posy + ((track_cell_height - item_height)/2)

                    item_height = (value*1.5) + random.randint(-2,2)
                    curr_y = posy + ((track_cell_height - item_height)/2)

                    if posx < (CONFIG['window_width']-4):
                        pygame.draw.line(
                            screen,
                            (255,255,255),
                            (posx, curr_y),
                            (posx, curr_y + item_height),
                            1
                        )

                    posx = posx + 2

            first_hit = False

            for hit in range(0, TOTAL_STEPS):
                posx = track_cell_width * hit
                if hit in sorted_hits:
                    draw_hit(wv_data, sorted_hits, posx)
                else:
                    pass
                    # if not first_hit:
                    #     draw_hit([], sorted_hits, posx, first_hit)


            posy = posy + track_cell_height


            # print(wv_data)

            # draw_step = 0
            # draw_x = 0
            BARS = []

            # current_bars = []
            # total_steps = int(CONFIG['window_width'] / 2)

            # print(int(CONFIG['window_width'] / 16))
            # exit()

            bars_count = int(CONFIG['window_width'] / 2)
            step_bar_count = int(bars_count / 16)
            current_step = 0
            segment_counter = 0
            data_index = 0

            bar_counter = 0

            # print(bars_count)
            # print(step_bar_count)
            # print(current_step)
            # print(data_index)

            # print(track['grid'])

            sorted_hits = sorted(track['grid'])

            for bar_num in range(0, bars_count):
                if bar_counter > step_bar_count:
                    bar_counter = 0
                    current_step = current_step + 1

                    if current_step in track['grid']:
                        data_index = 0

                try:
                    BARS.append(wv_data[data_index])
                except Exception as e:
                    BARS.append(0)

                bar_counter = bar_counter + 1

                # if segment_counter > step_bar_count:
                #     segments_progressed = segments_progressed + 1
                #     segment_counter = 0

                # if data_index <= len(wv_data):
                #     print(wv_data[data_index])
                #     BARS.append(wv_data[data_index])
                # else:
                #     BARS.append(0)

                data_index=data_index+1
                # segment_counter=segment_counter+1

            posx = 0

            # print(BARS)

            # for column in BARS:
            #     item_height = (column*1.5) + random.randint(-1,1)

            #     curr_y = posy + ((track_cell_height - item_height)/2)
            #     # curr_x = posx + x_left 

            #     # if x_left <= int(track_cell_width):
            #     line_color = (255,255,255)

            #     #     if x_left==0:
            #     # line_color = (255,0,0)

            #     pygame.draw.line(
            #         screen,
            #         line_color,
            #         (posx, curr_y),
            #         (posx, curr_y + item_height),
            #         1
            #     )

            #     # x_left = x_left + 4

            #     posx = posx + 2

            # posy = posy + track_cell_height



                # if draw_step in track['grid']:
                #     array_index = 0


                    # print(draw_step)
                    # for rms in wv_data:


                    # for bar_count in range(0, steps_per_bar):
                    #     print(bar_count)

                #     if bar_count <= len(wv_data):
                #         current_bars.append(wv_data[bar_count])
                #     else:
                #         current_bars.append(0)
                # if draw_step in track['grid']:
                #     current_bars = get_waveform_data(sample_filename)
                # else:

            # 

        # draw cursor

        # for i in range(0,steps+1):
        #     pygame.draw.line(screen, (90,90,90), ((track_cell_width*i)+1,0),((track_cell_width*i)+1,CONFIG['window_height']), 1)

        # x = (tracks_width/steps) * 
        cursor_x = (track_cell_width * (STATE['current_step']-1))

        print(cursor_x)

        pygame.draw.line(screen, (255,255,255), (cursor_x,0),(cursor_x,CONFIG['window_height']), 1)

        pygame.display.update()

    while RUN:
        draw()

        # screen.fill((0,0,0))
        # screen.blit(time,(0, 0))#

        # screen.fill((0,0,255))
        # pygame.draw.rect(screen,(78,203,245),(0,0,250,500),5)

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

if __name__ == '__main__':
    g = Gabber()
    main()


# # -*- coding: utf-8 -*-
# """
# Created on Thu May  4 22:08:22 2017

# @author: comcast_wizard
# """
# #KeyBand
# '''
# Drum samples downladed from here: http://www.soundsinhd.com/45-free-sp1200-acoustic-drum-samples-sounds-in-hd/
# TF2 sound effects downloaded from the TF2 wiki
# Drum image downloaded from Derpo's Magnificent Sprites:
# https://forums.terraria.org/index.php?threads/derpos-magnificent-sprites.9091/page-46 
# '''
# import pygame, sys
# from pygame.locals import *
# import time

# pygame.init()
# pygame.font.init()
# font = pygame.font.SysFont('Arial', 12)

# '''
# songlist = font.render('List of songs:', False, (0,0,0))
# (Songs were removed on the published version)
# '''

# drumlist = font.render('List of drum effects:',False,(0,0,0))
# snare_ = font.render('W: Snare',False,(0,0,0)) 
# clap_ = font.render('A: Clap',False,(0,0,0))
# tom_ = font.render('S: Tom',False,(0,0,0))
# hat_ = font.render('D: Hat',False,(0,0,0))
# basedrum_ = font.render('Q: Basedrum1',False,(0,0,0))
# basedrum2_ = font.render('E: Basedrum2',False,(0,0,0))
# crash_ = font.render('R: Crash',False,(0,0,0))
# snareroll_ = font.render('F: Snare roll',False,(0,0,0))

# effectslist = font.render('List of special effects:',False,(0,0,0))
# badum_ = font.render('Y: Badum tss',False,(0,0,0))
# scream_ = font.render('U: Wilhelm scream',False,(0,0,0))
# gong_ = font.render('I: Gong',False,(0,0,0)) 
# yeah_ = font.render('H: Yeah',False,(0,0,0))
# nope_ = font.render('J: Nope',False,(0,0,0))
# nom_ = font.render('K: Nom nom',False,(0,0,0))
# down_ = font.render('L: It goes down!',False,(0,0,0))

# stopmusic = font.render('P: Stop all sounds',False,(0,0,0))
# pausemusic = font.render('0: Pause all sounds',False,(0,0,0))
# unpausemusic = font.render('9: Unpause all sounds',False,(0,0,0))

# # #Code for making it display in a window
# # display = pygame.display.set_mode((600, 500))
# # pygame.display.set_caption('bg @ 0.2')

# # white = (255, 255, 255)
# # black = (0, 0, 0)

# # display.fill((black))
# # display.blit(drumlist,(10,230))
# # pygame.display.update()

# # while True:
# #     time.sleep(0.1)

# # import pygame
# from sys import exit as sysExit

# pygame.init()
# screen = pygame.display.set_mode((512,512))
# screen.fill((255,255,255))

# pygame.display.update()

# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.KEYUP:
#             if event.mod & pygame.KMOD_CTRL and pygame.key.key_code("q"):
#                 print(pygame.KMOD_CTRL)

#         if event.type == pygame.QUIT:
#             pygame.display.update()
#             pygame.display.quit()
#             pygame.quit()
#             exit(0)
#             sysExit(0)

# # while True: 
# #     #Background
# #     display.fill((black))
# #     # display.blit(bg,(125,0))
    
    
# #     #Text display:
# #     '''
# #     display.blit(songlist,(10,100))
# #     display.blit(weez01,(10,120))
# #     display.blit(weez02,(10,135))
# #     display.blit(weez03,(10,150))
# #     display.blit(weez04,(10,165))
# #     display.blit(gday01,(10,180))
# #     display.blit(gday02,(10,195))
# #     display.blit(oasis01,(10,210))
# #     '''
# #     display.blit(drumlist,(10,230))
# #     # display.blit(snare_,(10,245))
# #     # display.blit(clap_,(10,260))
# #     # display.blit(tom_,(10,275))
# #     # display.blit(hat_,(10,290))
# #     # display.blit(basedrum_,(10,305))
# #     # display.blit(basedrum2_,(10,320))
# #     # display.blit(crash_,(10,335))
# #     # display.blit(snareroll_,(10,350))
# #     # display.blit(effectslist,(10,370))
# #     # display.blit(badum_,(10,385))
# #     # display.blit(scream_,(10,400))
# #     # display.blit(gong_,(10,415))
# #     # display.blit(yeah_,(10,430))
# #     # display.blit(nope_,(10,445))
# #     # display.blit(nom_,(10,460))
# #     # display.blit(down_,(10,475))
# #     # display.blit(stopmusic, (10,550))
# #     # display.blit(pausemusic,(10,565))
# #     # display.blit(unpausemusic,(10,580))
    
# #     pygame.display.update()
    
    
# #     for event in pygame.event.get():
# #         if event.type == QUIT:
# #             pygame.quit()
# #             sys.exit()
        
# #         #Event to check for pressed keys
# #         if event.type == pygame.KEYDOWN:
# #             #Choose background music
# #             #Choose a song (as background music), and then drum along.
# #             #Songs were removed on the published version
            
# #             #Play sound effects
# #             #creates sound objects and assigns them into different channels so they can be played simultaneously
# #             if event.key == pygame.K_w:
# #             #snare
# #                 snare = pygame.mixer.Sound('snare.wav')
# #                 snare.set_volume(0.4)
# #                 pygame.mixer.Channel(1).play(snare)
                
# #             if event.key == pygame.K_a:
# #             #clap
# #                 clap = pygame.mixer.Sound('clap.wav')
# #                 clap.set_volume(0.4)
# #                 pygame.mixer.Channel(7).play(clap)
                
# #             if event.key == pygame.K_s:
# #             #tom
# #                 tom = pygame.mixer.Sound('tom.wav')
# #                 tom.set_volume(0.4)
# #                 pygame.mixer.Channel(2).play(tom)

# #             if event.key == pygame.K_d:
# #             #hat
# #                 hat = pygame.mixer.Sound('hat.wav')
# #                 tom.set_volume(0.4)
# #                 pygame.mixer.Channel(4).play(hat)
                
# #             if event.key == pygame.K_q:
# #             #basedrum1
# #                 basedrum = pygame.mixer.Sound('basedrum.wav')
# #                 basedrum.set_volume(0.4)
# #                 pygame.mixer.Channel(5).play(basedrum)
                
# #             if event.key == pygame.K_e:
# #             #basedrum2
# #                 basedrum2 = pygame.mixer.Sound('basedrum2.wav')
# #                 basedrum2.set_volume(0.4)
# #                 pygame.mixer.Channel(6).play(basedrum2)
                
# #             if event.key == pygame.K_r:
# #             #crash
# #                 crash = pygame.mixer.Sound('crash.wav')
# #                 crash.set_volume(0.4)
# #                 pygame.mixer.Channel(3).play(crash)
                
# #             if event.key == pygame.K_f:
# #             #snare roll
# #                 snareroll = pygame.mixer.Sound('snareroll.wav')
# #                 snareroll.set_volume(0.4)
# #                 pygame.mixer.Channel(4).play(snareroll)
            
# #             #Play special effects:
# #             if event.key == pygame.K_y:
# #             #badum tss
# #                 badum = pygame.mixer.Sound('badumtss.wav')
# #                 badum.set_volume(0.5)
# #                 pygame.mixer.Channel(1).play(badum)
                
# #             if event.key == pygame.K_u:
# #             #wilhelm scream
# #                 scream = pygame.mixer.Sound('willscream.wav')
# #                 scream.set_volume(0.5)
# #                 pygame.mixer.Channel(3).play(scream)
                
# #             if event.key == pygame.K_i:
# #             #gong
# #                 gong = pygame.mixer.Sound('gong.wav')
# #                 gong.set_volume(0.45)
# #                 pygame.mixer.Channel(2).play(gong)
                
# #             if event.key == pygame.K_h:
# #             #yeah
# #                 yeah = pygame.mixer.Sound('yeah.wav')
# #                 yeah.set_volume(0.6)
# #                 pygame.mixer.Channel(4).play(yeah)
                
# #             if event.key == pygame.K_j:
# #             #nope
# #                 nope = pygame.mixer.Sound('nope.wav')
# #                 nope.set_volume(0.6)
# #                 pygame.mixer.Channel(5).play(nope)
                
# #             if event.key == pygame.K_k:
# #             #nom nom
# #                 nom = pygame.mixer.Sound('nom.wav')
# #                 nom.set_volume(0.6)
# #                 pygame.mixer.Channel(6).play(nom)
                
# #             if event.key == pygame.K_l:
# #                 down = pygame.mixer.Sound('down.wav')
# #                 pygame.mixer.Channel(7).play(down)
            
                
# #             #Stop all sounds:
# #             if event.key == pygame.K_p:
# #                 pygame.mixer.stop()
# #             if event.key == pygame.K_0:
# #                 pygame.mixer.pause()
# #             if event.key == pygame.K_9:
# #                 pygame.mixer.unpause()
 
# #     time.sleep(1)
