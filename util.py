import random

import numpy as np

class DeviceShim(object):
    """Lets us interface with Robin code without making a fuss"""

    def __init__(self, rate, channels, np_format):
        self.rate = rate
        self.channels = channels
        self.np_format = np_format


def convolve_multi_channel(a, b):
    assert a.shape[1] == b.shape[1]
    num_chans = a.shape[1]
    result = np.zeros((len(a) + len(b) - 1, num_chans))
    for chan in range(num_chans):
        result[:, chan] = np.convolve(a[:, chan], b[:, chan])
    return result


def plot_scene(fs, scene):
    t_axis = robin.util.t_axis(scene, fs)
    robin.plotting.util.plot_stereo(t_axis, scene[:, 0], scene[:, 1])
