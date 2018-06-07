import numpy as np

import geom

triangle = (
    np.array([5, 0, 0]),
    np.array([5, 5, 0]),
    np.array([5, 5, 5]),
)

face = geom.Face(triangle)
ray = geom.Ray(np.array([0, 0, 0]), np.array([0.5, 0.2, 0.1]))

print face.intersect_ray(ray)
