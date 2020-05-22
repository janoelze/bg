import struct
import threading
import time
import sounddevice as sd
import soundfile as sf
import clockblocks

class Tempotrigger:
    def __init__(self, num_triggers_per_qn=24, cycle_len=24 * 8):
        self.runstate = 0
        self.num_triggers_per_qn = num_triggers_per_qn
        self.cycle_len = cycle_len
        self.cycle_len_flag = self.cycle_len - 1
        self.tempo = 120
        self.sleep_time = 60.0 / (self.tempo * self.num_triggers_per_qn)
        # mcast sender stuff (for sending sync timestamps):
        # self.MYPORT = constants.DEFAULT_MULTICAST_PORT
        # self.MYGROUP = "225.0.0.250"
        # self.sender = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # self.mygroup = self.MYGROUP
        # self.ttl = struct.pack("b", 1)  # Time-to-live
        # self.sender.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, self.ttl)
        self.callback = False

    def set_num_triggers(self, numtriggers):
        self.num_triggers_per_qn = numtriggers
        self.sleep_time = 60.0 / float(self.tempo * self.num_triggers_per_qn)

    def set_tempo(self, tempo):
        self.tempo = tempo
        self.sleep_time = 60.0 / float(tempo * self.num_triggers_per_qn)

    def set_cycle_len(self, cycle_len):
        self.cycle_len = cycle_len
        self.cycle_len_flag = self.cycle_len - 1

    def trigger(self):
        self.cycle_idx = self.cycle_len_flag  # just before 0
        while self.runstate == 1:
            self.target = time.time() + self.sleep_time
            self.cycle_idx = (self.cycle_idx + 1) % self.cycle_len
            # self.sender.sendto(
            #     bytes(
            #         "".join(
            #             [repr(self.cycle_idx).zfill(4), "|", repr(self.cycle_len)]
            #         ).zfill(4),
            #         "ascii",
            #     ),
            #     (self.mygroup, self.MYPORT),
            # )
            self.callback(self.cycle_idx)
            time.sleep(self.sleep_time - 0.006)
            # accuracy tweak loop:
            nowtime = time.time()  # starting point
            while nowtime < self.target:  # while not within 1ms
                time.sleep(0.0001)
                nowtime = time.time()  # get new moving point

    def run(self, callback):
        self.callback = callback

        if self.runstate == 0:
            self.runstate = 1
            threading.Thread(target=self.trigger).start()
            # _thread.start_new_thread(self.trigger, ())

    def stop(self):
        if self.runstate == 1:
            self.runstate = 0

if __name__ == '__main__':
    clock = clockblocks.Clock()
    # t = Tempotrigger(1)

    # t.set_tempo(120)

    pulse_device = False

    i = 0
    for device in sd.query_devices():
        print(device)
        if 'C-Media' in device['name'] and device['max_output_channels'] > 0:
            pulse_device = i
        i = i + 1

    pulse_data, pulse_fs = sf.read('modular-pulse.wav', dtype='float32')

    def on_beat():
        if pulse_device:
            sd.stop()
            sd.play(pulse_data, pulse_fs, device=pulse_device)

    # i = 0
    # while True:
    #     clock.wait((60/120)/4)
    #     t = threading.Thread(target=on_beat, args=()).start()
    #     i = i + 1

    # t.run(on_beat)

    from clockblocks import Clock

    clock = Clock(initial_tempo=200)

    clock.set_tempo_target(200,0)

    while clock.beat() < 90:
        on_beat()
        clock.wait(1)
