import numpy as np

import geom


class SceneObject(object):
    def get_reflectivity(self):
        raise NotImplementedError

    def get_intersectables(self):
        raise NotImplementedError


class Wall(SceneObject):
    """Represents a flat surface standing perpendicular to the xy plane and
    extending a certain height into the z-dimension. You know, a wall.
    """

    def __init__(self, start_point_meters, end_point_meters, height_meters):
        self.start_point_meters = start_point_meters
        self.end_point_meters = end_point_meters
        self.height_meters = height_meters

    def get_reflectivity(self):
        return 1

    def get_intersectables(self):
        # A wall is just two triangular faces!
        (x1, y1) = self.start_point_meters
        (x2, y2) = self.end_point_meters
        # Two bottom points
        b1, b2 = np.array([x1, y1, 0]), np.array([x2, y2, 0])
        # Two top points
        t1, t2 = np.array([x1, y1, self.height_meters]), np.array(
            [x2, y2, self.height_meters])
        return (
            geom.Face((b1, b2, t1)),
            geom.Face((t1, t2, b2)),
        )
