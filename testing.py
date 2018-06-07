from __future__ import division

import math

import charles.head_model
import charles.raycast
import charles.scene
import hrtf
import numpy as np
import robin.plotting.util

from scene import EchoSource, HeadModel
from render import EchoLayer, Layer, Timeline, render_scene
from util import DeviceShim, write_scene
from thaler_click import ExampleEcholocator

fs = 96000
f0, f1, dur = 1.0e4, 2.2e4, 1e6 * 0.001
np_format = np.float64
device = DeviceShim(fs, 2, np_format)
echolocator = ExampleEcholocator()
scene = [
    charles.scene.Wall((-1, 2), (1, 2), 3),
    charles.scene.Wall((1, 1), (1, -1), 3)
]

rendered = render_scene(fs, device, echolocator, scene)
write_scene(fs, rendered, "output/test_charles_chirp.wav")
