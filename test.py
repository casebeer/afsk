import logging
logging.basicConfig(level=logging.DEBUG)

from afsk.ax25 import FCS
from bitarray import bitarray

import crc16
import struct

bs_header = '\x82\xa0\xa4\xa6@@`\x88\xaa\x9a\x9a\xb2@`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0'
bs_packet = '\x82\xa0\xa4\xa6@@`\x88\xaa\x9a\x9a\xb2@`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0:Test\xf5g'

unstuffed_body = '01000001000001010010010101100101000000100000001000000110000100010101010101011001010110010100110100000010000001100111010101001001000100010101000101000110000000100100011001110101010010010001000101010001001001100000001011000110110000000000111101011100001010101010011011001110001011101111101111110011'
stuffed_body = '0100000100000101001001010110010100000010000000100000011000010001010101010101100101011001010011010000001000000110011101010100100100010001010100010100011000000010010001100111010101001001000100010101000100100110000000101100011011000000000011110101110000101010101001101100111000101110111110011111010011'


def test_packet():
	packet = ax25.UI("APRS", "DUMMY", info=":Test")
	generated_bits = packet.unparse()
	generated_bytes = generated_bits.tobytes()
	expected_bytes = '~\x82\xa0\xa4\xa6@@`\x88\xaa\x9a\x9a\xb2@`\xae\x92\x88\x8ab@b\xae\x92\x88\x8ad@c\x03\xf0:Test\x9f/\xfb\x01'
	#expected_bits = bitarray.bitarray('01111110010000010000010100100101011001010000001000000010000001100001000101010101010110010101100101001101000000100000011001110101010010010001000101010001010001100000001001000110011101010100100100010001010100010010011000000010110001101100000000001111010111000010101010100110110011100010111011111001111101001101111110')

	print ("Unstuffed body BA:\n%s" % unstuffed_body)

	print ("checksummed_content_bits:\n%r %r" % (packet.header(), packet.info))

	print ("BS PACKET:\n%r" % (bs_packet))
	print ("Packet:\n%s\n%r\nHeader:\n%r" % (packet, packet.packet(), packet.header()))
	print ("BS HEADER:\n%r" % (bs_header))
	print ("Generated:\n%r\nExpected:\n%r" % (generated_bytes, expected_bytes))

	#assert generated_bits == expected_bits
	assert generated_bytes == expected_bytes

def test_fcs():
	fcs = FCS()
	str_bytes = b'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'
	bits = bitarray()
	bits.frombytes(str_bytes)

	for bit in bits:
		fcs.update_bit(bit)

	#-63653
	assert fcs.digest() == '[\x07'

#	print "calcbytes"
#	print "%r" % fcs2.digest()

	digest = bitarray(endian="little")
	digest.frombytes(fcs.digest())
	assert digest == bitarray('1101101011100000')

test_fcs()

