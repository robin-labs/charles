from __future__ import division

import numpy as np

import hrtf
from render import Layer, Timeline
from util import DeviceShim, convolve_multi_channel, plot_scene


def render_pulse_with_distribution(fs, pulse, dist):
	data_getter, get_possible_azimuths = (
		hrtf.make_hrtf_data_getter(fs, dtype=np.float32)
	)
	rnd_pulse = pulse.render(DeviceShim(fs, 2, np.float32))
	all_pulses = []
	for azimuth in get_possible_azimuths(elevation=0):
		ir = data_getter(0, azimuth) / 32768
		convolved = convolve_multi_channel(rnd_pulse, ir)
		all_pulses.append(dist(azimuth) * convolved)
	scale = (
		sum([np.sum(p[:, 0] ** 2) / len(p[:, 0]) for p in all_pulses]) / 
		(np.sum(rnd_pulse[:, 0] ** 2) / len(rnd_pulse[:, 0]))
	)
	return reduce(lambda a, b: a + b, all_pulses)
