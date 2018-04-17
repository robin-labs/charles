from __future__ import division

import math

import numpy as np
import robin.pulse
import robin.plotting.util
import hrtf

from scene import EchoSource, HeadModel
from render import EchoLayer, Layer, Timeline, render_scene
from util import DeviceShim, write_scene


CIRCULAR_ECHO_SOURCES = [
    EchoSource((1 * math.sqrt(i + 1) * np.cos(a), 1 * math.sqrt(i + 1) * np.sin(a)), 1)
    for i, a in enumerate(np.linspace(0, np.pi, 10))
]

REVERSE_CIRCULAR_ECHO_SOURCES = [
    EchoSource((-1 * math.sqrt(i + 1) * np.cos(a), 1 * math.sqrt(i + 1) * np.sin(a)), 1)
    for i, a in enumerate(np.linspace(0, np.pi, 10))
]

print [s.position for s in CIRCULAR_ECHO_SOURCES]
print [s.position for s in REVERSE_CIRCULAR_ECHO_SOURCES]

ECHO_SOURCES = [
    EchoSource((0, 3), 4),
    EchoSource((3, 3), 8),
    EchoSource((1, 1.5), 4),
    EchoSource((-1.5, 1.5), 4),
]


fs = 96000
f0, f1, dur = 1.0e4, 2.2e4, 1e6 * 0.001
np_format = np.float64
device = DeviceShim(fs, 2, np_format)
pulse = robin.pulse.Chirp(f0, f1, dur).render(device)
head = HeadModel(hrtf.make_hrtf_data_getter(fs)[0])
echo_sources = REVERSE_CIRCULAR_ECHO_SOURCES


def write_differential_scenes(name):
    normalized = render_scene(fs, device, pulse, head, echo_sources, 1 / 0.03)
    unnormalized = render_scene(fs, device, pulse, head, echo_sources, 1)
    write_scene(fs, normalized, "output/{0}-normalized.wav".format(name))
    write_scene(fs, unnormalized, "output/{0}-unnormalized.wav".format(name))


if __name__ == "__main__":
    write_differential_scenes("chirp-short-reverse-circular")
