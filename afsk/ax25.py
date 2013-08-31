# coding=utf8

import logging
logging.basicConfig(level=logging.INFO)

import struct

from bitarray import bitarray
import audiogen

from . import afsk

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
			logging.debug("Stuffing bit")
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
	def __init__(
		self,
		destination=b"APRS", 
		source=b"", 
		digipeaters=(b"RELAY", b"WIDE2-1"), 
		info=b"\""
	):
		self.flag = b"\x7e"

		self.destination = destination
		self.source = source
		self.digipeaters = digipeaters

		self.info = info
	
	@classmethod
	def callsign_encode(self, callsign):
		callsign = callsign.upper()
		if callsign.find(b"-") > 0:
			callsign, ssid = callsign.split(b"-")
		else:
			ssid = b"0"

		assert(len(ssid) == 1)
		assert(len(callsign) <= 6)

		callsign = b"{callsign:6s}{ssid}".format(callsign=callsign, ssid=ssid)

		# now shift left one bit, argh
		return b"".join([chr(ord(char) << 1) for char in callsign])

	def encoded_addresses(self):
		address_bytes = bytearray(b"{destination}{source}{digis}".format(
			destination = AX25.callsign_encode(self.destination),
			source = AX25.callsign_encode(self.source),
			digis = b"".join([AX25.callsign_encode(digi) for digi in self.digipeaters])
		))

		# set the low order (first, with eventual little bit endian encoding) bit
		# in order to flag the end of the address string
		address_bytes[-1] |= 0x01

		return address_bytes

	def header(self):
		return b"{addresses}{control}{protocol}".format(
			addresses = self.encoded_addresses(),
			control = self.control_field, # * 8,
			protocol = self.protocol_id,
		)
	def packet(self):
		return b"{header}{info}{fcs}".format(
			flag = self.flag,
			header = self.header(),
			info = self.info,
			fcs = self.fcs()
		)
	def unparse(self):
		flag = bitarray(endian="little")
		flag.frombytes(self.flag)

		bits = bitarray(endian="little")
		bits.frombytes("".join([self.header(), self.info, self.fcs()]))

		return flag + bit_stuff(bits) + flag
	
	def __repr__(self):
		return self.__str__()
	def __str__(self):
		return b"{source}>{destination},{digis}:{info}".format(
			destination = self.destination,
			source = self.source,
			digis = b",".join(self.digipeaters),
			info = self.info
		)

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
		content.frombytes("".join([self.header(), self.info]))

		fcs = FCS()
		for bit in content:
			fcs.update_bit(bit)
#		fcs.update(self.header())
#		fcs.update(self.info)
		return fcs.digest()

class UI(AX25):
	def __init__(
		self,
		destination=b"APRS", 
		source=b"", 
		digipeaters=(b"WIDE1-1", b"WIDE2-1"),
		info=b""
	):
		AX25.__init__(
			self, 
			destination, 
			source, 
			digipeaters,
			info
		)
		self.control_field = b"\x03"
		self.protocol_id = b"\xf0"
			
def main():
	import sys
	callsign = sys.argv[1] if len(sys.argv) > 1 else "DUMMY"
	data = sys.argv[2] if len(sys.argv) > 2 else ":Test"

	packet = UI("APRS", callsign, info=data)

	print("Sending packet: '{}'".format(packet))
	logging.debug(r"Packet bits:\n{!r}".format(packet.unparse()))

	audiogen.sampler.play(afsk.encode(packet.unparse()), blocking=True)

	## file output
	#with open("test.wav", "wb") as f:
	#	audiogen.write_wav(f, afsk(packet.unparse()))
	#audiogen.util.play("test.wav")

if __name__ == "__main__":
	main()

