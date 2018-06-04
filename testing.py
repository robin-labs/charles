from __future__ import division

import math

import charles.head_model
import charles.raycast
import charles.scene
import hrtf
import numpy as np
import robin.pulse
import robin.plotting.util

from scene import EchoSource, HeadModel
from render import EchoLayer, Layer, Timeline, render_scene
from util import DeviceShim, write_scene
from thaler_click import ExpertClick

fs = 96000
f0, f1, dur = 1.0e4, 2.2e4, 1e6 * 0.001
np_format = np.float64
device = DeviceShim(fs, 2, np_format)
pulse = robin.pulse.Chirp(f0, f1, dur)
head = HeadModel(hrtf.make_hrtf_data_getter(fs)[0])

wall = charles.scene.Wall((-1, 2), (1, 2), 3)
wall2 = charles.scene.Wall((1, 1), (1, -1), 3)
echo_sources = []
for (position, coeff) in charles.raycast.cast_lambertian(
    charles.head_model.HeadModel(), [wall, wall2]
):
    echo_sources.append(EchoSource(position[0:2], 1, coeff))

scene = render_scene(fs, device, pulse, head, echo_sources, 1)
write_scene(fs, scene, "output/test_charles_chirp.wav")
