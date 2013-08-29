#!/usr/bin/env python
# coding=utf8

from setuptools import setup, find_packages

required_modules = [
	'audiogen',
	'bitarray',
	]

with open("README.rst", "rb") as f:
	readme = f.read()

setup(
	name="afsk",
	version="0.0.1",
	description="AFSK – Bell 202 Audio Frequency Shift Keying encoder",
	author="Christopher H. Casebeer",
	author_email="",
	url="",

	packages=find_packages(exclude='tests'),
	install_requires=required_modules,

	tests_require=["nose", "crc16"],
	test_suite="nose.collector",

	entry_points={
		"console_scripts": [
			"afsk = afsk.afsk:main"
		]
	},

	long_description=readme,
	classifiers=[
		"Environment :: Console",
		"License :: OSI Approved :: BSD License",
		"Intended Audience :: Developers",
		"Topic :: Multimedia :: Sound/Audio",
		"Topic :: Communications :: Ham Radio",
	]
)

