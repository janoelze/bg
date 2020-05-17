import sys

import contextlib
with contextlib.redirect_stdout(None):
    import pygame

from pydub import AudioSegment
from PIL import Image, ImageDraw
import numpy as np

_wv_store = {}

def draw_waveform_array(screen, src, bars, y_offset, bar_height, bpm):
    BARS = bars
    BAR_HEIGHT = bar_height
    LINE_WIDTH = 5
    db_ceiling = 60

    if src not in _wv_store or _wv_store[src]['bars'] != bars:
        _wv_store[src] = {
            'obj': AudioSegment.from_file(src),
            'bars': bars,
        }

        audio_file = _wv_store[src]['obj']

        chunk_length = len(audio_file) / BARS

        loudness_of_chunks = [
            audio_file[i * chunk_length: (i + 1) * chunk_length].rms
            for i in range(BARS)]

        max_rms = max(loudness_of_chunks) * 1.00

        _wv_store[src]['max_array'] = [int((loudness / max_rms) * db_ceiling)
                for loudness in loudness_of_chunks]

        # STATE['bpm']

        # print(audio.duration_seconds)

        # data = np.fromstring(audio._data, np.int16)
        # fs = audio.frame_rate

        # length = len(data)
        # RATIO = length/BARS

        # count = 0
        # maximum_item = 0
        # _wv_store[src]['max_array'] = []
        # highest_line = 0

        # for d in data:
        #     if count < RATIO:
        #         count = count + 1

        #         if abs(d) > maximum_item:
        #             maximum_item = abs(d)
        #     else:
        #         _wv_store[src]['max_array'].append(maximum_item)

        #         if maximum_item > highest_line:
        #             highest_line = maximum_item

        #         maximum_item = 0
        #         count = 1

        # _wv_store[src]['line_ratio'] = highest_line/BAR_HEIGHT

        # print(_wv_store[src]['max_array'])

    current_x = 1

    for item in _wv_store[src]['max_array']:
        item_height = item
        current_y = (BAR_HEIGHT - item_height)/2

        # print('draw', current_y)

        pygame.draw.line(screen, (255,255,255), (current_x,current_y+y_offset),(current_x,current_y + item_height+y_offset), 2)

        current_x = current_x + 4


class Waveform(object):
    bar_count = 107
    db_ceiling = 60

    def __init__(self, filename):
        self.filename = filename

        audio_file = AudioSegment.from_file(
            self.filename, self.filename.split('.')[-1])

        self.peaks = self._calculate_peaks(audio_file)

    def _calculate_peaks(self, audio_file):
        """ Returns a list of audio level peaks """
        chunk_length = len(audio_file) / self.bar_count

        loudness_of_chunks = [
            audio_file[i * chunk_length: (i + 1) * chunk_length].rms
            for i in range(self.bar_count)]

        max_rms = max(loudness_of_chunks) * 1.00

        return [int((loudness / max_rms) * self.db_ceiling)
                for loudness in loudness_of_chunks]

    def _get_bar_image(self, size, fill):
        """ Returns an image of a bar. """
        width, height = size
        bar = Image.new('RGBA', size, fill)

        end = Image.new('RGBA', (width, 2), fill)
        draw = ImageDraw.Draw(end)
        draw.point([(0, 0), (3, 0)], fill='#000')
        draw.point([(0, 1), (3, 1), (1, 0), (2, 0)], fill='#000')

        bar.paste(end, (0, 0))
        bar.paste(end.rotate(180), (0, height - 2))
        return bar

    def _generate_waveform_image(self):
        """ Returns the full waveform image """
        im = Image.new('RGB', (840, 128), 'rgba(0,0,0,0)')
        for index, value in enumerate(self.peaks, start=0):
            column = index * 5 + 2
            upper_endpoint = 64 - value

            im.paste(self._get_bar_image((4, value * 2), '#fff'),
                     (column, upper_endpoint))

        return im

    def save(self, wv_file):
        """ Save the waveform as an image """
        # png_filename = self.filename.replace(
        #     self.filename.split('.')[-1], 'png')
        with open(wv_file, 'wb') as imfile:
            self._generate_waveform_image().save(imfile, 'GIF')
