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
    EchoSource((1 * (i + 1) * np.cos(a), 1 * (i + 1) * np.sin(a)), i ** 0.75)
    for i, a in enumerate(np.linspace(0, np.pi, 10))
]

ECHO_SOURCES = [
    EchoSource((0, 3), 1),
    EchoSource((3, 3), 3),
]


fs = 96000
f0, f1, dur = 1.0e4, 2.2e4, 1e6 * 0.005
np_format = np.int16
device = DeviceShim(fs, 2, np_format)
chirp = robin.pulse.Chirp(f0, f1, dur).render(device)
head = HeadModel(hrtf.make_hrtf_data_getter(fs)[0])
echo_sources = CIRCULAR_ECHO_SOURCES


def write_differential_scenes():
    normalized = render_scene(fs, device, chirp, head, echo_sources, 20)
    unnormalized = render_scene(fs, device, chirp, head, echo_sources, 1)
    write_scene(fs, normalized  / 32768, "output/diff/normalized.wav")
    write_scene(fs, unnormalized / 32768, "output/diff/unnormalized.wav")


if __name__ == "__main__":
    write_differential_scenes()
