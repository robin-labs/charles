from __future__ import division

import math
import random

import numpy as np
from robin.plotting.util import plot_samples

from util import plot_scene 


class EchoSource(object):
    def __init__(self, position, surface_area=1, refraction=1):
        self.position = position
        self.surface_area = surface_area
        self.refraction = refraction

    def azimuth(self):
        return (-180 / math.pi) * (
            math.atan2(self.position[1], self.position[0]) - 
            math.pi / 2
        )

    def distance_to_point(self, point):
        (x1, y1), (x2, y2) = self.position, point
        return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5	


class HeadModel(object):
    def __init__(self, hrtf_data_getter, ear_distance=0.0):
        self.hrtf_data_getter = hrtf_data_getter
        self.ear_distance = ear_distance

    def ear_position_of_channel(self, channel):
        return [
            (-self.ear_distance, 0),
            (self.ear_distance, 0)
        ][channel]

    def apply_hrtf(self, sample, source, channel):
        sample_at_channel = sample[:, channel]
        azimuth = source.azimuth()
        abs_azimuth = abs(azimuth)
        select_channel = channel if azimuth == abs_azimuth else (1 - channel)
        impulse_response = (
            self.hrtf_data_getter(0, abs_azimuth)[:, select_channel]
        )
        output = np.convolve(sample_at_channel, impulse_response)
        return output


def generate_random_echo_sources(n=5, dist_bounds=(2,3), sa_bounds=(0.5, 0.5)):
    for _ in xrange(n):
        azm = random.random() * 180
        dist = dist_bounds[0] + random.random() * dist_bounds[1]
        pos = (dist * np.cos(azm), dist * np.sin(azm))
        sa = sa_bounds[0] + random.random() * sa_bounds[1]
        yield EchoSource(pos, sa)
