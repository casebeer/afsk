# coding=utf8

import logging
logger = logging.getLogger(__name__)

import struct
import sys
import argparse

from bitarray import bitarray
import audiogen

import afsk

def bit_stuff(data):
	count = 0
	for bit in data:
		if bit:
			count += 1
		else:
			count = 0
		yield bit
		# todo: do we stuff *after* fifth '1' or *before* sixth '1?'
		if count == 5:
			logger.debug("Stuffing bit")
			yield False
			count = 0

def bit_unstuff(data):
	pass

class FCS(object):
	def __init__(self):
		self.fcs = 0xffff
	def update_bit(self, bit):
		check = (self.fcs & 0x1 == 1)
		self.fcs >>= 1
		if check != bit:
			self.fcs ^= 0x8408
	def update(self, bytes):
		for byte in (ord(b) for b in bytes):
			for i in range(7,-1,-1):
				self.update_bit((byte >> i) & 0x01 == 1)
	def digest(self):
#		print ~self.fcs
#		print "%r" % struct.pack("<H", ~self.fcs % 2**16)
#		print "%r" % "".join([chr((~self.fcs & 0xff) % 256), chr((~self.fcs >> 8) % 256)])
		# digest is two bytes, little endian
		return struct.pack("<H", ~self.fcs % 2**16)
		
def fcs(bits):
	'''
	Append running bitwise FCS CRC checksum to end of generator
	'''
	fcs = FCS()
	for bit in bits:
		yield bit
		fcs.update_bit(bit)

#	test = bitarray()
#	for byte in (digest & 0xff, digest >> 8):
#		print byte
#		for i in range(8):
#			b = (byte >> i) & 1 == 1
#			test.append(b)
#			yield b

	# append fcs digest to bit stream

	# n.b. wire format is little-bit-endianness in addition to little-endian
	digest = bitarray(endian="little")
	digest.frombytes(fcs.digest())
	for bit in digest:
		yield bit

def fcs_validate(bits):
	buffer = bitarray()
	fcs = FCS()

	for bit in bits:
		buffer.append(bit)
		if len(buffer) > 16:
			bit = buffer.pop(0)
			fcs.update(bit)
			yield bit
	
	if buffer.tobytes() != fcs.digest():
		raise Exception("FCS checksum invalid.")

class AX25(object):
	def __init__(self, destination="APRS", source="", digipeaters=("RELAY", "WIDE2-1"), info="\"" ):
		self.flag = b"\x7e"
		self.destination = destination
		self.source = source
		self.digipeaters = digipeaters
		self.info = info
	
	@classmethod
	def callsign_encode(self, callsign):
		callsign = callsign.upper()
		if callsign.find("-") > 0:
			callsign, ssid = callsign.split("-")
		else:
			ssid = "0"

		assert(len(ssid) == 1)
		assert(len(callsign) <= 6)

		callsign = "{callsign:6s}{ssid}".format(callsign=callsign, ssid=ssid)
		# now shift left one bit, argh
		return b"".join([bytes([char << 1]) for char in callsign.encode('utf-8')])

	def encoded_addresses(self):
		address = b"".join([AX25.callsign_encode(self.destination),AX25.callsign_encode(self.source), b"".join([AX25.callsign_encode(digi) for digi in self.digipeaters])])
		address_bytes = bytearray(address)

		# set the low order (first, with eventual little bit endian encoding) bit
		# in order to flag the end of the address string
		address_bytes[-1] |= 0x01

		return address_bytes

	def header(self):
		return b"".join([self.encoded_addresses(), self.control_field, self.protocol_id])		

	def packet(self):
		return b"".join([self.flag,self.header(),self.info.encode('utf-8'),self.fcs()])

	def unparse(self):
		flag = bitarray(endian="little")
		flag.frombytes(self.flag)

		bits = bitarray(endian="little")
		bits.frombytes(b"".join([self.header(), self.info.encode('utf-8'), self.fcs()]))
		return flag + bit_stuff(bits) + flag
	
	def __repr__(self):
		return self.__str__()

	def __str__(self):
		__str__ = "{source}>{destination},{digis}:{info}".format(
			destination = self.destination,
			source = self.source,
			digis = ",".join(self.digipeaters),
			info = self.info
		)
		return __str__

	@classmethod
	def parse(cls, bits):
		# todo
		raise Exception("Not implemented")
		return cls(
			destination=None,
			source=None,
			digipeaters=None,
			info=None
		)
	
	def fcs(self):
		content = bitarray(endian="little")
		content.frombytes(b"".join([self.header(), self.info.encode('utf-8')]))

		fcs = FCS()
		for bit in content:
			fcs.update_bit(bit)
#		fcs.update(self.header())
#		fcs.update(self.info)
		return fcs.digest()

class UI(AX25):
	def __init__(self, destination="APRS", source="", digipeaters=("WIDE1-1", "WIDE2-1"), info=""):
		AX25.__init__(self, destination, source, digipeaters, info)
		self.control_field = b"\x03"
		self.protocol_id = b"\xf0"
			
def main(arguments=None):
	parser = argparse.ArgumentParser(description='')
	parser.add_argument(
		'-c',
		'--callsign', 
		required=True,
		help='Your ham callsign. REQUIRED.'
	)
	parser.add_argument(
		'info', 
		metavar='INFO',
		help='APRS message body'
	)
	parser.add_argument(
		'--destination',
		default='APRS',
		help='AX.25 destination address. See http://www.aprs.org/aprs11/tocalls.txt'
	)
	parser.add_argument(
		'-d',
		'--digipeaters',
		'--path',
		default=b'WIDE1-1,WIDE2-1',
		help='Digipeater path to use. "New Paradigm" recommendations are "WIDE1-1,WIDE2-1" for mobile and "WIDE2-1" for fixed stations. Defaults to "WIDE1-1,WIDE2-1."'
	)
	parser.add_argument(
		'-o',
		'--output', 
		default=None,
		help='Write audio to wav file. Use \'-\' for stdout.'
	)
	parser.add_argument(
		'-v',
		'--verbose',
		action='count',
		help='Print more debugging output.'
	)
	args = parser.parse_args(args=arguments)

	if args.verbose == 0:
		logging.basicConfig(level=logging.INFO)
	elif args.verbose >=1:
		logging.basicConfig(level=logging.DEBUG)

	packet = UI(
		destination=args.destination,
		source=args.callsign, 
		info=args.info,
		digipeaters=args.digipeaters.split(b','),
	)

	logger.info(r"Sending packet: '{0}'".format(packet))
	logger.debug(r"Packet bits:\n{0!r}".format(packet.unparse()))

	audio = afsk.encode(packet.unparse())

	if args.output == '-':
		audiogen.sampler.write_wav(sys.stdout, audio)
	elif args.output is not None:
		with open(args.output, 'wb') as f:
			audiogen.sampler.write_wav(f, audio)
	else:
		audiogen.sampler.play(audio, blocking=True)

if __name__ == "__main__":
	main()

