from __future__ import division

import math

import matplotlib.pyplot as plt
import numpy as np
import robin.util

import geom
import raycast

SPEED_OF_SOUND = 343  # m/s


def render_scene(fs, device, echolocator, scene):
    rendered_pulse = echolocator.pulse.render(device)
    return Timeline([Layer(rendered_pulse)] + [
        EchoLayer(rendered_pulse, position_meters, power_watts)
        for position_meters, power_watts
        in raycast.cast_lambertian(echolocator, scene)
    ]).render(fs, echolocator)


def distance_delay_in_samples(fs, distance):
    return int(2 * fs * distance / SPEED_OF_SOUND)


def apply_hrtf(hrtf, position, sample, channel):
    azimuth, elevation = geom.rectangular_to_polar_degrees(position)
    return np.convolve(
        sample[:, channel],
        hrtf.get_at_angle(azimuth, elevation, channel)
    )


class Layer(object):
    def __init__(self, rnd_pulse, delays=(0, 0)):
        self.rnd_pulse = rnd_pulse
        self.delays = delays
        self.CHANNELS = xrange(2)

    def render(self, fs, _):
        for i in self.CHANNELS:
            yield i, self.rnd_pulse[:, i], self.delays[i]


class EchoLayer(object):
    def __init__(self, sample, position_meters, power_watts):
        self.sample = sample
        self.position_meters = position_meters
        self.power_watts = power_watts
        self.CHANNELS = xrange(2)

    def render(self, fs, echolocator):
        distance_meters = np.linalg.norm(self.position_meters)
        delay = distance_delay_in_samples(fs, distance_meters)
        for channel in self.CHANNELS:
            sample = np.sqrt(self.power_watts) * apply_hrtf(
                echolocator.hrtf,
                self.position_meters,
                self.sample,
                channel
            )
            yield channel, sample, delay


class Timeline(object):
    def __init__(self, layers):
        self.layers = layers

    def render(self, fs, echolocator):
        scene = np.zeros((1, 2))
        for layer in self.layers:
            for channel, sample, delay in layer.render(fs, echolocator):
                end_sample = len(sample) + delay - 1
                if len(scene) < end_sample:
                    scene = robin.util.zero_pad(scene, right_length=end_sample)
                scene[:, channel] += robin.util.zero_pad(
                    sample,
                    left_length=delay,
                    right_length=(len(scene) - len(sample) - delay)
                )
        return scene
