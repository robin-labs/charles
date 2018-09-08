

import os
import re

import numpy as np
import samplerate


def read_hrtf_elevations():
    extractor = re.compile("^elev(?P<elevation>-?[0-9]+)$")
    for file in os.listdir("hrtf"):
        matched = extractor.match(file)
        if matched:
            yield int(matched.group("elevation"))


def read_hrtf_azimuths_from_directory(elevation):
    extractor = re.compile("^H(?:-?[0-9]+)e(?P<azimuth>[0-9]+)a.dat$")
    for file in os.listdir(os.path.join(
        "hrtf",
        "elev{0}".format(str(elevation)),
    )):
        matched = extractor.match(file)
        if matched:
            yield int(matched.group("azimuth"))
        else:
            raise Exception("Your regex doesn't work, dummy!")


def read_hrtf_filter(elevation, azimuth, fs=44100, dtype=np.float64):
    path = os.path.join(
        "hrtf",
        "elev{0}".format(str(elevation)),
        "H{0}e{1}a.dat".format(str(elevation), str(azimuth).zfill(3))
    )
    data = np.fromfile(file(path, "rb"), np.dtype(">i2"), 256) / 16384
    data.shape = (128, 2)
    return samplerate.resample(data, fs / 44100, "sinc_best").astype(dtype)


class HRTF(object):
    def __init__(self, fs, dtype=None):
        self.azimuth_elevation_pairs = []
        self.filters = {}
        for elevation in read_hrtf_elevations():
            self.filters[elevation] = {}
            azimuths = read_hrtf_azimuths_from_directory(elevation)
            for azimuth in azimuths:
                filter = read_hrtf_filter(elevation, azimuth, fs, dtype)
                self.filters[elevation][azimuth] = filter
                self.azimuth_elevation_pairs.append(
                    (azimuth, elevation)
                )
                self.filters[elevation][-azimuth] = filter[:, [1, 0]]
                self.azimuth_elevation_pairs.append(
                    (-azimuth, elevation)
                )

    def get_at_angle(self, azimuth, elevation, channel):
        possible_elevations = list(self.filters.keys())
        closest_elevation = sorted(
            possible_elevations,
            key=lambda p: abs(p - elevation)
        )[0]
        possible_azimuths = list(self.filters[closest_elevation].keys())
        closest_azimuth = sorted(
            possible_azimuths,
            key=lambda p: abs(p - azimuth)
        )[0]
        filter = self.filters[closest_elevation][closest_azimuth]
        return filter[:, channel]
