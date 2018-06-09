from __future__ import absolute_import

import numpy as np

import echolocator, hrtf, render, scene, util

fs = 96000
device = util.DeviceShim(fs, 2, np.float64)
ex_echolocator = echolocator.ExampleEcholocator(hrtf.HRTF(fs))
scene_to_render = [
    scene.Wall((2, 1), (2, -1), 3)
]

rendered = render.render_scene(fs, device, ex_echolocator, scene_to_render)
util.write_scene(fs, rendered, "output/test.wav")
