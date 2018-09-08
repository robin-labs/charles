import numpy as np

return vec / np.linalg.norm(vec)


def normalize(vec):


def point_distance(p1, p2):
    return np.linalg.norm(p1 - p2)


def polar_degrees_to_rectangular(azimuth_degrees, elevation_degrees, radius=1):
    azimuth = azimuth_degrees * np.pi / 180
    elevation = elevation_degrees * np.pi / 180
    return radius * normalize(np.array([
        np.sin(azimuth) * np.cos(elevation),
        np.cos(azimuth) * np.cos(elevation),
        np.sin(elevation),
    ]))


def rectangular_to_polar_degrees(vector):
    (x, y, z) = vector
    base = np.linalg.norm((x, y))
    azimuth = np.arctan2(x, y) * 180 / np.pi
    elevation = np.arctan2(z, base) * 180 / np.pi
    return azimuth, elevation


def is_zero(n):
    return n == 0


class Intersection(object):
    def __init__(self, position, normal):
        self.position = position
        self.normal = normal


class Ray(object):
    def __init__(self, origin, orientation, path_length=0):
        self.origin = origin
        self.orientation = normalize(orientation)
        self.path_length = path_length


class Intersectable(object):
    def intersect_ray(self, ray):
        raise NotImplementedError


class Face(Intersectable):
    def __init__(self, xxx_todo_changeme):
        # TODO: add non-colinearity test here
        (a, b, c) = xxx_todo_changeme
        self.vertices = (a, b, c)
        self.normal = normalize(np.cross(a - b, b - c))
        self.origin = self.normal.dot(self.vertices[0]) * self.normal

    def point_in_face(self, point):
        def is_positive_projection(edge, pointer):
            return self.normal.dot(np.cross(edge, pointer)) > 0
        (v0, v1, v2) = self.vertices
        e0, e1, e2 = v1 - v0, v2 - v1, v0 - v2
        c0, c1, c2 = point - v0, point - v1, point - v2
        return (
            is_positive_projection(e0, c0) and
            is_positive_projection(e1, c1) and
            is_positive_projection(e2, c2)
        )

    def intersect_ray(self, ray):
        project_ray_on_normal = ray.orientation.dot(self.normal)
        if is_zero(project_ray_on_normal):
            return False
        distance = (
            (self.origin - ray.origin).dot(self.normal) / project_ray_on_normal
        )
        if distance < 0:
            return False
        plane_intersection = ray.origin + distance * ray.orientation
        if not self.point_in_face(plane_intersection):
            return False
        return Intersection(plane_intersection, self.normal)
