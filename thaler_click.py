from __future__ import absolute_import

import robin.pulse
import numpy as np


def subclick(t, (a, b, c), (freq, magnitude, phase)):
    heaviside = 0.5 * (1 + np.sign(t - c))
    center = magnitude * np.cos(2 * np.pi * freq * t + phase)
    envelope = a * np.exp(-b * t - c)
    return heaviside * envelope * center


class ThalerClick(robin.pulse.Pulse):
    def __init__(self, envelope, peaks, gain_pattern):
        """You're gonna love this terrible API, I guarantee it

        envelope: tuple (a, b, c) representing envelope of click
            a: rise magnitude (unitless)
            b: decay rate (1 / seconds)
            c: onset time (seconds)
        
        peaks: array of tuples [(freq, magnitude, phase)] representing the peak
                frequencies that are decomposable from an echolocator's click:
            freq: a peak frequency (Hz)
            magnitude: magnitude of that frequency (unitless)
            phase: phase of that frequency (radians)

        gain_pattern: tuple (alpha, beta) representing cardioid gain pattern
        """
        self.envelope = envelope
        self.peaks = peaks
        self.gain_pattern = gain_pattern
        # Determine how long the pulse should be from its decay rate -- we'll
        # call it done when it reaches 1/1000 of its peak magnitude (a)
        (_, b, c) = self.envelope
        us_duration = (c - (np.log(1e-3) / b)) * 1e6
        super(ThalerClick, self).__init__(us_duration)

    def _render(self, device):
        """Renders the click.

        Note that we don't make use of gain_pattern here -- this is exposed to
        the caller by the gain_at_azimuth function, but we otherwise assume
        that the click characteristics are azimuth-independent.

        device: an object implementing the Robin device API, meaning that it
            provides us rate, channels, and np_format members.
        """
        t_axis = self.t_axis(device)
        return sum([
            subclick(t_axis, self.envelope, peak)
            for peak in self.peaks
        ])


class ExpertClick(ThalerClick):
    """Uses parameters from EE1 in the Thaler paper"""

    def __init__(self):
        super(ExpertClick, self).__init__(
            (0.388, 1.57e3, 1.10 * 1e-3),
            [
                (3.54 * 1e3, 6.58, 1.59),
                (5.30 * 1e3, 2.68, 1.60),
                (6.93 * 1e3, 2.49, 1.65),
                (9.97 * 1e3, 0.868, 1.72),
                (11.88 * 1e3, 1.00, 1.39),
            ],
            (0.130, 0.282)
        )
