#!/usr/bin/env python

from msvg.parser import Parser
from setuptools import setup

setup(
	name = 'msvg',
	packages = ['msvg'],
	package_data = {},
	entry_points = {
		'console_scripts': ['msvg = msvg.parser:cli']
	},
	version = '0.1.0',
	description = 'A Python parsing library for http://www.openstreetmap.org/ SVG files.',
	long_description = open('README.md', 'r').read(),
	author = 'Chris Lock',
	author_email = 'chris@bright.is',
	url = 'https://github.com/chris-lock/msvg',
)