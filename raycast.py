from __future__ import division

import numpy as np

import geom


def cast_all_rays_for_echolocator(echolocator):
    pairs = echolocator.hrtf.azimuth_elevation_pairs
    power_per_ray = 1 / len(pairs)
    for (azimuth, inclination) in pairs:
        power = power_per_ray * echolocator.gain_at_azimuth(azimuth)
        yield power, geom.Ray(
            echolocator.origin,
            geom.polar_degrees_to_rectangular(azimuth, inclination)
        )


def cast_lambertian(echolocator, scene_objects, max_distance=float('inf')):
    """Performs a simple raycast using a Lambertian scene model: we assume all
    objects in the scene scatter echoes in a perfectly diffuse way, and we
    totally ignore echoes of echoes. Rather than casting from a virtual sound
    emitter, we cast rays from the head model at evenly spaced angles, and
    intersect them with objects in the scene; the returned "echo" at every
    angle thus comes the first object intersected by the ray at that angle, and
    is described by an intersection and a coefficient of reflected power, which
    is just the dot product of the surface normal and the ray attenuated by the
    absorption of the surface. For now, I'm consuming this simple model using 
    the echogen repository, which uses a similar abstraction to actually
    generate audio.

    Args:
        head_model: a HeadModel object that tells us which rays to cast
        scene_objects: a list of SceneObject instances
        max_distance: how far to cast (we probably don't care)

    Returns:
        An array of (intersection, reflection) tuples where...
            intersection: np.array([x, y, z])
            reflection: a reflection coefficient on [0, 1] representing the
                fraction of incident power returned to the receiver.
    """
    echoes = []
    for ray_coeff, ray in cast_all_rays_for_echolocator(echolocator):
        intersected_point = None
        intersected_coefficient = None
        min_distance = max_distance
        for scene_object in scene_objects:
            for intersectable in scene_object.get_intersectables():
                intersection = intersectable.intersect_ray(ray)
                if intersection:
                    distance = geom.point_distance(
                        echolocator.origin,
                        intersection.position
                    )
                    if distance < min_distance:
                        min_distance = distance
                        intersected_point = intersection.position
                    intersected_coefficient = abs(intersection.normal.dot(
                        ray.orientation
                    )) * scene_object.get_reflectivity() * ray_coeff
        if intersected_point is not None:
            echoes.append((intersected_point, intersected_coefficient))
    return echoes
