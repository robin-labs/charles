from __future__ import division

import math

import numpy as np
import robin.pulse
import robin.plotting.util
import hrtf

from scene import EchoSource, HeadModel
from render import EchoLayer, Layer, Timeline, render_scene
from util import DeviceShim, write_scene
from thaler_click import ExpertClick


CIRCULAR_ECHO_SOURCES = [
    EchoSource((1 * math.sqrt(i + 1) * np.cos(a), 1 * math.sqrt(i + 1) * np.sin(a)), 1)
    for i, a in enumerate(np.linspace(0, np.pi, 10))
]

REVERSE_CIRCULAR_ECHO_SOURCES = [
    EchoSource((-1 * math.sqrt(i + 1) * np.cos(a), 1 * math.sqrt(i + 1) * np.sin(a)), 1)
    for i, a in enumerate(np.linspace(0, np.pi, 10))
]

ECHO_SOURCES = [
    EchoSource((0, 3), 4),
    EchoSource((3, 3), 8),
    EchoSource((1, 1.5), 4),
    EchoSource((-1.5, 1.5), 4),
]

def single_echo_source(dist, az, area=1):
    return [EchoSource((-dist * np.cos(az), dist * np.sin(az)), area)]

fs = 96000
f0, f1, dur = 1.0e4, 2.2e4, 1e6 * 0.001
np_format = np.float64
device = DeviceShim(fs, 2, np_format)
pulse = ExpertClick()
head = HeadModel(hrtf.make_hrtf_data_getter(fs)[0])

print pulse

def write_scenes(name):
    for az in np.linspace(0, 180, 19):
        az_rad = az * np.pi / 180
        az_disp = az - 90
        for dist in (1.5, 2, 3):
            echo_sources = single_echo_source(dist, az_rad)
            scene = render_scene(fs, device, pulse, head, echo_sources, 1)
            write_scene(fs, scene, "output/{0}_{1}m_{2}.wav".format(
                name, dist, az_disp
            ))


if __name__ == "__main__":
    write_scenes("ee1")
