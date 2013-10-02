# coding=utf-8

# Bell 202 Audio Frequency Shift Keying
# http://n1vg.net/packet/

import logging
logger = logging.getLogger(__name__)

import math
import itertools

from bitarray import bitarray

import audiogen
from audiogen.util import multiply
from audiogen.util import constant

MARK_HZ = 1200.0
SPACE_HZ = 2200.0
BAUD_RATE = 1200.0

TWO_PI = 2.0 * math.pi

def encode(binary_data):
	'''
	Encode binary data using Bell-202 AFSK
	
	Expects a bitarray.bitarray() object of binary data as its argument.
	Returns a generator of sound samples suitable for use with the 
	audiogen module.
	'''
	framed_data = frame(binary_data)

	# set volume to 1/2, preceed packet with 1/20 s silence to allow for startup glitches
	for sample in itertools.chain(
		audiogen.silence(1.05), 
		multiply(modulate(framed_data), constant(0.5)), 
		audiogen.silence(1.05), 
	):
		yield sample


def modulate(data):
	'''
	Generate Bell 202 AFSK samples for the given symbol generator

	Consumes raw wire symbols and produces the corresponding AFSK samples. 
	'''
	seconds_per_sample = 1.0 / audiogen.sampler.FRAME_RATE
	phase, seconds, bits = 0, 0, 0

	# construct generators
	clock = (x / BAUD_RATE for x in itertools.count(1))
	tones = (MARK_HZ if bit else SPACE_HZ for bit in data)

	for boundary, frequency in itertools.izip(clock, tones):
		# frequency of current symbol is determined by how much 
		# we advance the signal's phase in each audio frame
		phase_change_per_sample = TWO_PI / (audiogen.sampler.FRAME_RATE / frequency)

		# produce samples for the current symbol 
		# until we reach the next clock boundary
		while seconds < boundary:
			yield math.sin(phase)

			seconds += seconds_per_sample
			phase += phase_change_per_sample

			if phase > TWO_PI:
				phase -= TWO_PI

		bits += 1
		logger.debug("bits = %d, time = %.7f ms, expected time = %.7f ms, error = %.7f ms, baud rate = %.6f Hz" \
			% (bits, 1000 * seconds, 1000 * bits / BAUD_RATE, 1000 * (seconds - bits / BAUD_RATE), bits / seconds))

def nrzi(data):
	'''
	Packet uses NRZI (non-return to zero inverted) encoding, which means 
	that a 0 is encoded as a change in tone, and a 1 is encoded as 
	no change in tone.
	'''
	current = True
	for bit in data:
		if not bit:
			current = not current 
		yield current

def frame(stuffed_data):
	'''
	Frame data in 01111110 flag bytes and NRZI encode.
	
	Data must be already checksummed and stuffed. Frame will be
	preceded by two bytes of all zeros (which NRZI will encode as 
	continuously altenrating tones) to assist with decoder clock 
	sync. 
	'''
	return nrzi(
		itertools.chain(
			bitarray("00000000") * 20,
			bitarray("01111110") * 100, 
			stuffed_data,
			bitarray("01111110") 
		)
	)

