from __future__ import division

import matplotlib
matplotlib.use('TkAgg')

import scikits.audiolab
import numpy as np
import resampy
import matplotlib.pyplot as plt

import robin.pulse
import robin.plotting.util
import robin.util


SPEED_OF_SOUND = 343 # m/s


# Shhhhhh
class DeviceShim(object):
	def __init__(self, rate, channels, np_format):
		self.rate = rate
		self.channels = channels
		self.np_format = np_format


class EchoSource(object):
	def __init__(self, position, surface_area=1, refraction=1):
		self.position = position
		self.surface_area = surface_area
		self.refraction = refraction


class HeadModel(object):
	def __init__(self, ear_distance=0.1, attenutation_coeff_fn=None):
		self.ear_distance = ear_distance
		if attenutation_coeff_fn is None:
			attenutation_coeff_fn = lambda *args: [1, 1]
		self.attenutation_coeff_fn = attenutation_coeff_fn

	def ear_positions(self):
		return [
			(-self.ear_distance, 0),
			(self.ear_distance, 0)
		]


class Delayed(object):
	def __init__(self, sound, sample_delay=0, start_delay=0):
		self.sound = sound
		self.sample_delay = sample_delay
		self.start_delay = start_delay

	def render_for_scene(self, scene_duration):
		pad_left = int(self.sample_delay + self.start_delay)
		pad_right = int(scene_duration - pad_left - len(self.sound))
		res = robin.util.zero_pad(self.sound, pad_left, pad_right)
		return res


def point_distance(a, b):
	(x1, y1), (x2, y2) = a, b
	return ((x1 - x2) ** 2 + (y1 - y2) ** 2) ** 0.5


def distance_delay_in_samples(distance, fs):
	return int(2 * fs * distance / SPEED_OF_SOUND)


def simple_head_attenuation_model(position):
	def projection_to_attenuation(p):
		max_coeff = 1
		min_coeff = 0.1
		tightness = 5
		return min_coeff + (
			(max_coeff - min_coeff) * (
				1 / (1 + np.exp(-1 * tightness * p))
			)
		)
	norm_position = position / np.linalg.norm(position)
	ear_normals = [
		n / np.linalg.norm(n)
		for n in [(-1, 0), (1, 0)]
	]
	projections = [
		np.dot(norm_position, ear_normals[i])
		for i in xrange(len(ear_normals))
	]
	print "PROJECTIONS", norm_position, projections
	res = [projection_to_attenuation(p) for p in projections]
	print "ATTN", res
	return res


def simple_attenuation_coeff(distance, surface_area, air_loss_coeff=None):
	d_full_power_wavefront = 0.1
	relative_surface_area = (surface_area / d_full_power_wavefront) ** 2
	return relative_surface_area / (distance / d_full_power_wavefront) ** 4


def as_channels(left, right):
	return np.transpose(np.vstack((left, right)))


def write_scene(scene, fs):
	sf = scikits.audiolab.Sndfile(
		'output.wav',
		format=scikits.audiolab.Format(),
		channels=2,
		samplerate=fs,
		mode='w'
	)
	sf.write_frames(scene / 32768)


def plot_scene(scene, fs):
	t_axis = robin.util.t_axis(scene, fs)
	robin.plotting.util.plot_stereo(t_axis, scene[:,0], scene[:,1])


def moderate_itds_for(delays, intended_slowdown):
	[left, right] = delays
	mean = (left + right) / 2
	difference = left - right
	new_difference = difference / intended_slowdown
	return [mean + new_difference / 2, mean - new_difference / 2]


def render_scene(device, pulse, head, echo_sources, 
		us_duration, fs, intended_slowdown=20):
	rendered_pulse = 1 * pulse.render(device)
	pulse_left, pulse_right = rendered_pulse[:,0], rendered_pulse[:,1]
	sample_duration = int(us_duration * 1e-6 * fs)
	start_delay = int(sample_duration / 10)
	empty_layer = lambda: np.zeros((sample_duration, 2))
	layers = []
	# Add the initial pulse
	layers.append(
		as_channels(*[
			Delayed(
				rendered_pulse,
				start_delay=start_delay
			).render_for_scene(sample_duration)[:,0],
			Delayed(
				rendered_pulse,
				start_delay=start_delay
			).render_for_scene(sample_duration)[:,1],
		])
	)
	channels = xrange(2)
	ear_positions = head.ear_positions()
	for source in echo_sources:
		distances = [
			point_distance(
				source.position,
				ear_positions[channel]
			)
			for channel in channels
		]
		delays = moderate_itds_for([
			distance_delay_in_samples(distance, fs)
			for distance in distances
		], intended_slowdown)
		attenuations = [
			simple_attenuation_coeff(distance, source.surface_area)
			for distance in distances
		]
		attenuations = np.multiply(
			attenuations,
			head.attenutation_coeff_fn(source.position)
		)
		layers.append(
			as_channels(*[
				Delayed(
					attenuations[channel] * rendered_pulse,
					delays[channel],
					start_delay
				).render_for_scene(sample_duration)[:,channel]
				for channel in channels
			])
		)
	result = empty_layer()
	for layer in layers:
		result = result + layer
	return result


ECHO_SOURCES = [
	EchoSource((1 * (i + 1) * np.cos(a), 1 * (i + 1) * np.sin(a)), i)
	for i, a in enumerate(np.linspace(0, np.pi, 10))
]


if __name__ == "__main__":
	fs = 96000
	f0, f1, dur = 2.0e4, 3.5e4, 1e6 * 0.005
	np_format = np.int16
	device = DeviceShim(fs, 2, np_format)
	head = HeadModel(attenutation_coeff_fn=simple_head_attenuation_model)
	chirp = robin.pulse.Chirp(f0, f1, dur)
	scene = render_scene(device, chirp, head, ECHO_SOURCES, 1e5, fs, 50)
	write_scene(scene, fs)
