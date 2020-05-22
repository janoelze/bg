from state import get_state, set_state, persist_state, recover_state, get_state_all, set_state_all
from threading import Thread
from clockblocks import Clock

class Gabber(object):
    def __init__(self, callback):
        super(Gabber, self).__init__()

        # self.bars = 1
        # self.bpb = 4
        # self.max_steps = (4 * self.bpb) * self.bars
        # self.current_step = 0

        # STATE['max_steps'] = self.max_steps

        self.total_ticks = 0
        self.ticks_per_bar = 4
        self.tick = 0

        self.oldTempo = 120
        self.newTempo = self.oldTempo

        self.callback = callback
        self.clock = Clock(initial_tempo=self.oldTempo)

        Thread(target = self.run).start()

    # def shuffle_track(self):
    #     random_track = False

    #     tracks = get_state('tracks')
    #     tracks_c = tracks.copy()

    #     random.shuffle(tracks_c)

    #     for track in ctracks_cop:
    #         if 'locked' not in track or not track['locked']:
    #             random_track = track
    #             break

    #     if random_track:
    #         inc = random.randint(1,8)
    #         new_grid = []
    #         s = 0

    #         while s <= self.max_steps:
    #             new_grid.append(s)
    #             s = s + inc

    #         random_track['grid'] = new_grid

    def set_tempo(self, bpm):
        self.newTempo = bpm

    def run(self):
        if self.newTempo != self.oldTempo:
            print('transition bpm: %s => %s' % (self.oldTempo, self.newTempo))

            self.clock.set_tempo_target(self.newTempo,0)
            self.oldTempo = self.newTempo

        while self.clock.beat() < 90:
            if self.tick >= self.ticks_per_bar:
                self.tick = 0

            self.callback(self, self.tick, self.total_ticks)

            self.tick = self.tick + 1
            self.total_ticks = self.total_ticks + 1

            if get_state('app_run'):
                self.clock.wait(1)

        # clock = clockblocks.Clock()
        # start = time.time()

        # while RUN:
        #     if STATE['current_step'] >= STATE['max_steps']:
        #         STATE['current_step'] = 0

        #     play_pulse()

        #     # update_window()

        #     # STATE['current_step'] = self.current_step

        #     play_output = []

        #     if 'do_quit' in STATE and STATE['do_quit']:
        #         exit()

        #     for TRACK in STATE['tracks']:
        #         channel = CHANNELS[TRACK['channel']]
        #         sample_id = TRACK['sample_id']

        #         if 'volume' in TRACK:
        #             channel.set_volume(TRACK['volume'] * STATE['volume'])

        #         if 'stutter' in TRACK and TRACK['stutter']:
        #             channel.set_volume((TRACK['volume'] * STATE['volume']) * random.randint(70,100)/100)

        #         if 'sample_id' in TRACK and 'grid' in TRACK and TRACK['sample_id']:
        #             if STATE['current_step'] in TRACK['grid']:
        #                 if channel.get_busy():
        #                     channel.stop()

        #                 play(channel, TRACK['sample_id'])
        #                 play_output.append('[%s]' % TRACK['sample_id'][0:6])

        #     log('playing %s' % (' '.join(play_output)))

        #     # print('%s/%s %s' % (step, max_steps, ))

        #     if random.randint(0,100) > 90:
        #         self.shuffle_track()

        #     # self.current_step = self.current_step + 1
        #     # STATE['current_step'] = self.current_step

        #     STATE['current_step'] = STATE['current_step'] + 1

        #     clock.wait((60/STATE['bpm'])/4)
