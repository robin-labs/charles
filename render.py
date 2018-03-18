from __future__ import division

import math

import numpy as np
import robin.util

SPEED_OF_SOUND = 343 # m/s


def render_scene(fs, device, rnd_pulse, head_model, sources, itd_compress):
    return Timeline([Layer(rnd_pulse)] + [
        EchoLayer(rnd_pulse, echo_source, head_model, itd_compress)
        for echo_source in sources
    ]).render(fs)


def distance_delay_in_samples(fs, distance):
    return int(2 * fs * distance / SPEED_OF_SOUND)


def simple_attenuation_coeff(distance, surface_area, air_loss_coeff=None):
    d_full_power_wavefront = 0.1
    relative_surface_area = (surface_area / d_full_power_wavefront) ** 2
    return relative_surface_area / (distance / d_full_power_wavefront) ** 4


def moderate_itds_for(delays, itd_compress):
    [left, right] = delays
    mean = (left + right) / 2
    difference = left - right
    new_difference = difference / itd_compress
    return map(int, [mean + new_difference / 2, mean - new_difference / 2])


class Layer(object):
    def __init__(self, rnd_pulse, delays=(0, 0)):
        self.rnd_pulse = rnd_pulse
        self.delays = delays
        self.CHANNELS = xrange(2)

    def render(self, fs):
        for i in self.CHANNELS:
            yield self.rnd_pulse[:, i], self.delays[i]


class EchoLayer(object):
    def __init__(self, rnd_pulse, echo_source, head_model, itd_compress=1):
        self.rnd_pulse = rnd_pulse
        self.echo_source = echo_source
        self.head_model = head_model
        self.itd_compress = itd_compress
        self.CHANNELS = xrange(2)

    def render(self, fs):
        channel_delays = []
        samples = []
        for channel in self.CHANNELS:
            distance = self.echo_source.distance_to_point(
                self.head_model.ear_position_of_channel(channel)
            )
            delay = distance_delay_in_samples(fs, distance)
            attenuation = simple_attenuation_coeff(
                distance,
                self.echo_source.surface_area
            )
            channel_delays.append(delay)
            samples.append(
                self.head_model.apply_hrtf(
                    attenuation * self.rnd_pulse,
                    self.echo_source,
                    channel
                )
            )
        channel_delays = moderate_itds_for(channel_delays, self.itd_compress)
        for i in self.CHANNELS:
            yield samples[i], channel_delays[i]


class Timeline(object):
    def __init__(self, layers=None):
        self.layers = layers or []

    def add_layer(self, layer):
        self.layers.append(layer)

    def render(self, fs):
        scene = np.zeros((1, 2))
        for layer in self.layers:
            for channel, (chan_sample, delay) in enumerate(layer.render(fs)):
                end_sample = len(chan_sample) + delay - 1
                if len(scene) < end_sample:
                    scene = robin.util.zero_pad(scene, right_length=end_sample)
                scene[:, channel] += robin.util.zero_pad(
                    chan_sample,
                    left_length=delay,
                    right_length=(len(scene) - len(chan_sample) - delay)
                )
        return scene
