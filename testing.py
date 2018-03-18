from __future__ import division

import math
import random

import numpy as np
import robin.pulse
import robin.plotting.util
import hrtf

from render import EchoSource, HeadModel, Layer, EchoLayer, Timeline
from util import DeviceShim, write_scene


def render_scene(device, rnd_pulse, head_model, echo_sources, 
		us_duration, fs, itd_compress=20):
	return Timeline([Layer(rnd_pulse)] + [
		EchoLayer(rnd_pulse, echo_source, head_model, itd_compress)
		for echo_source in echo_sources
	]).render(fs)


CIRCULAR_ECHO_SOURCES = [
	EchoSource((1 * (i + 1) * np.cos(a), 1 * (i + 1) * np.sin(a)), i ** 0.75)
	for i, a in enumerate(np.linspace(0, np.pi, 10))
]

ECHO_SOURCES = [
	EchoSource((0, 3), 1),
	EchoSource((3, 3), 3),
]

def generate_random_echo_sources(n=5, dist_bounds=(2,3), sa_bounds=(0.5, 0.5)):
	for i in xrange(n):
		azm = random.random() * 180
		dist = dist_bounds[0] + random.random() * dist_bounds[1]
		pos = (dist * np.cos(azm), dist * np.sin(azm))
		sa = sa_bounds[0] + random.random() * sa_bounds[1]
		yield EchoSource(pos, sa)


if __name__ == "__main__":
	fs = 96000
	f0, f1, dur = 1.0e4, 2.2e4, 1e6 * 0.005
	np_format = np.int16
	device = DeviceShim(fs, 2, np_format)
	chirp = robin.pulse.Chirp(f0, f1, dur).render(device)
	head = HeadModel(hrtf.make_hrtf_data_getter(fs)[0])
	echo_sources = CIRCULAR_ECHO_SOURCES
	scene = render_scene(device, chirp, head, echo_sources, 1e5, fs, 20)
	write_scene(fs, scene  / 32768, "circular.wav")
