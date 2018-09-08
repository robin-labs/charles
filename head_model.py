import numpy as np

from . import geom


class HeadModel(object):
    """Models the head as a source of rays to cast"""

    def __init__(
        self,
        max_azimuth_degrees=90,
        max_inclination_degrees=50,
        resolution_degrees=5,
        radius_meters=0.1,
        height_meters=1.7  # One of me
    ):
        self.origin = np.array([0, 0, height_meters])
        self.max_azimuth_degrees = max_azimuth_degrees
        self.max_inclination_degrees = max_inclination_degrees
        self.resolution_degrees = resolution_degrees
        self.radius_meters = radius_meters

    def cast_all_rays(self):
        azimuth_range_radians = np.arange(
            start=-self.max_azimuth_degrees,
            stop=self.max_azimuth_degrees,
            step=self.resolution_degrees
        ) * (np.pi / 180)
        inclination_range_radians = np.arange(
            start=-self.max_inclination_degrees,
            stop=self.max_inclination_degrees,
            step=self.resolution_degrees
        ) * (np.pi / 180)
        power_per_ray = 1 / (len(azimuth_range_radians) *
                             len(inclination_range_radians))
        for azimuth in azimuth_range_radians:
            for inclination in inclination_range_radians:
                yield power_per_ray, geom.Ray(
                    self.origin,
                    geom.normalize(np.array([
                        np.sin(azimuth) * np.cos(inclination),
                        np.cos(azimuth) * np.cos(inclination),
                        np.sin(inclination),
                    ]))
                )
