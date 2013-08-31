
import afsk
from bitarray import bitarray
import crc16
import struct

def test_fcs():
	fcs = afsk.ax25.FCS()
	bytes = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	bits = bitarray()
	bits.frombytes(bytes)

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

