'''
Dts_Stream.py

Copyright (c) 2003 - 2005 James Urquhart(j_urquhart@btinternet.com)

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
'''

import struct
from struct import *
from array import *
import sys

from Torque_Util import *
from Dts_Shape import IflMaterial, dObject, DetailLevel, SubShape, Node, Trigger, ObjectState, Decal, DecalState
from Dts_Mesh import Cluster, Primitive

##############################
# Torque Game Engine
# -------------------------------
# Dts FileStream Class for Python
###############################

# Add read<type> and write<type> functions as appropriate.

# The DTSStream Class
# Writes and Reads in little endian. Buffers should be auto swapped on a different endian system

# Snagged from a mailing list
def little_endian():
    return ord(array("i",[1]).tostring()[0])

class DtsStream:
	DTSVersion = 24				# Version to read
	mExporterVersion = int(0)		# Exporter Version
	def __init__(self, fname, read=False, version=24):
		if read:
			self.fs = open(fname, "rb")
			self.DTSVersion = version	# Version to read
			self.createStreams()
			if self.flood() == None:
				self.fs.close()
				self.fs = None
				return None # Failed to read for whatever reason
		else:
			self.fs = open(fname, "wb")
			self.DTSVersion = version
			self.checkCount = 0	# Count of checkpoints read/written
			self.createStreams()
	def createStreams(self):
		self.buffer32 = array('i')	# array of long
		self.buffer16 = array('h')	# array of signed short
		self.buffer8 = array('b')	# array of signed byte. Call it a big string
		self.Allocated32 = 0		# Size buffer32 should be
		self.Allocated16 = 0		# Size buffer16 should be
		self.Allocated8  = 0		# Size buffer8 should be
	def clearStreams(self):
		del self.buffer8
		del self.buffer16
		del self.buffer32
	def __del__(self):
		self.clearStreams()
		self.fs.close()
	def storeCheck(self, checkPoint= -1):
		# Write checkpoints (unsigned presumably)
		self.writeu8(self.checkCount)
		self.writeu16(self.checkCount)
		self.writeu32(self.checkCount)
		self.checkCount += 1
	def readCheck(self):
		# Read Checkpoints (unsigned presumably)
		c8, c16, c32 = self.readu8(), self.readu16(), self.readu32()
		if c8 == c16 == c32 == self.checkCount:
			self.checkCount += 1
			return self.checkCount
		else:
			self.checkCount += 1
			print "Error! Checkpoint mismatch! (%d %d %d(8,16,32), should be %d)" % (c8, c16, c32, self.checkCount-1)
			sys.exit(1)
			#return -1
	def flush(self):
		# Get Sizes...
		sz8 = len(self.buffer8)
		sz16 = len(self.buffer16)
		sz32 = len(self.buffer32)
		if sz16 & 0x0001:
			self.write16(0)
			sz16 += 1
		while sz8 & 0x0003:
			self.write8(0)
			sz8 += 1
		# Actual Size must equal calculated size!
		offset16  = sz32
		offset8   = offset16 + (sz16/2)
		totalSize = offset8 + (sz8/4)
		# Write the resulting data to the file
		hdr = array('i')
		hdr.append(self.DTSVersion | (self.mExporterVersion<<16))
		hdr.append(totalSize)
		hdr.append(offset16)
		hdr.append(offset8)
		# Write Buffers to fs
		# ByteSwap buffers if neccesary
		
		if not little_endian():
			print "Swap"
			hdr.byteswap()
			self.buffer32.byteswap()
			self.buffer16.byteswap()
			self.buffer8.byteswap()
		# Piece of lovely cake! Yumm
		# Now comes in mac flavour!
		hdr.tofile(self.fs)
		self.buffer32.tofile(self.fs)
		self.buffer16.tofile(self.fs)
		self.buffer8.tofile(self.fs)
	def flood(self):
		# Read in File
		hdr = array('i')
		hdr.fromfile(self.fs, 4)
		# Need to swap header bytes for mac
		if not little_endian():
			hdr.byteswap()
		ver = 0
		ver, totalSize, offset16, offset8 = long(hdr[0]), long(hdr[1]), long(hdr[2]), long(hdr[3])
		
		self.mExporterVersion = ver >> 16
		ver &= 0xFF
   
		if self.DTSVersion != int(ver):
			print "Error : File Version is %d, can only read in version %d!" % (ver, self.DTSVersion)
			return None
		self.Allocated32 = offset16
		self.Allocated16 = (offset8-offset16) * 2
		self.Allocated8  = (totalSize-offset8) * 4
		# Lovely Chocolate Cake
		self.buffer32.fromfile(self.fs,self.Allocated32)
		self.buffer16.fromfile(self.fs,self.Allocated16)
		self.buffer8.fromfile(self.fs,self.Allocated8)
		# ByteSwap buffers if required...
		if not little_endian():
			self.buffer32.byteswap()
			self.buffer16.byteswap()
			self.buffer8.byteswap()
		self.checkCount = 0 
		return True
	# Quick & Easy Operators
	def write(self, value): self.write32(value) # Evil
	def write8(self, value): self.buffer8.append(value)
	def write16(self, value): self.buffer16.append(value)
	def write32(self, value): self.buffer32.append(value)
	def read(self): return self.read32()
	def read8(self): return self.buffer8.pop(0)
	def read16(self): return self.buffer16.pop(0)
	def read32(self): return self.buffer32.pop(0)
	def readbool(self):
		translate = self.read8(self)
		return translate != 0
	def writebool(self, value):
		if value: self.write8(1) # U8
		else: self.write8(0) # U8
	# >> Util Read/Write Functions we must put here <<
	
	# The Uxx and Sxx and Ux and Sx and F32 functions we need (i, h, b) - Endian should be little
	# By default stream is signed
	# To change to unsigned, If N<0 then N= N + (range/2)
	# Or use the struct.pack & struct.unpack functions
	def reads32(self):
		return self.read32()
	def readu32(self):
		# bit of a hack, but should work
		sval = self.read32()
		uval = struct.pack('i', sval)
		pval = struct.unpack('I', uval)[0]
		return pval
	def readf32(self):
		# bit of a hack, but should work
		ival = self.read32()
		pfval = struct.pack('i', ival)
		fval = struct.unpack('f', pfval)[0]
		return fval
	def writes32(self, value):
		self.write32(value)
	def writeu32(self, value):
		# Capital Letter = Unsigned
		uval = value
		puval = struct.pack('I', uval)
		ival = struct.unpack('i', puval)[0]
		self.write32(ival)
	def writef32(self, value):
		# bit of a hack, but should work
		fval = value
		pfval = struct.pack('f', fval)
		ival = struct.unpack('i', pfval)[0]
		self.write32(ival)
	def reads16(self):
		return self.read16()
	def readu16(self):
		# bit of a hack, but should work
		sval = self.read16()
		uval = struct.pack('h', sval)
		pval = struct.unpack('H', uval)[0]
		return pval
	def writes16(self, value):
		self.write16(value)
	def writeu16(self, value):
		# Capital Letter = Unsigned
		uval = value
		puval = struct.pack('H', uval)
		ival = struct.unpack('h', puval)[0]
		self.write16(ival)
	def reads8(self):
		return self.read8()
	def readu8(self):
		# bit of a hack, but should work
		sval = self.read8()
		uval = struct.pack('b', sval)
		pval = struct.unpack('B', uval)[0]
		return pval
	def writes8(self, value):
		self.write8(value)
	def writeu8(self, value):
		# Capital Letter = Unsigned
		uval = value
		puval = struct.pack('B', uval)
		ival = struct.unpack('b', puval)[0]
		self.write8(ival)
	# End ?x* functions
	def readBox(self):
		v1 = self.readPoint3F()
		v2 = self.readPoint3F()
		return Box(v1, v2)
	def writeBox(self, value):
		self.writePoint3F(value.min)
		self.writePoint3F(value.max)
	def readPrimitive(self):
		v1 = self.reads16()
		v2 = self.reads16()
		v3 = self.reads32()
		return Primitive(v1, v2, v3)
	def writePrimitive(self, value):
		self.writes16(value.firstElement)
		self.writes16(value.numElements)
		self.writes32(value.matindex)
	def readPoint2F(self):
		# X, Y
		x, y = self.readf32(), self.readf32()
		return Vector2(x, y)
	def writePoint2F(self, value):
		self.writef32(value.members[0])
		self.writef32(value.members[1])
	def readPoint3F(self):
		# X, Y, Z
		x, y, z = self.readf32(), self.readf32(), self.readf32()
		return Vector(x, y, z)
	def writePoint3F(self, value):
		self.writef32(value[0])
		self.writef32(value[1])
		self.writef32(value[2])
	def readPoint4F(self):
		# X, Y, Z, W
		x, y, z, w = self.readf32(), self.readf32(), self.readf32(), self.readf32()
		return Vector(x, y, z, w)
	def writePoint4F(self, value):
		self.writef32(value[0])
		self.writef32(value[1])
		self.writef32(value[2])
		self.writef32(value[3])
	def writeMatrixF(self, value):
		# We assume its a 4*4 matrix. Silly us.
		for r in range(0, 4):
			for c in range(0, 4):
				self.writef32(value.get(r, c))
	def readMatrixF(self):
		mat = []
		# We assume its a 4*4 matrix. Silly us.
		for r in range(0, 4):
			for c in range(0, 4):
				mat.append(self.readf32())
		return MatrixF(mat)
	def readQuat(self):
		# Read a 32bit Quaternion (eek! space!)
		# X, Y, Z, W
		x, y, z, w = self.readf32(), self.readf32(), self.readf32(), self.readf32()
		return Quaternion(x, y, z, w)
	def saveQuat(self, value):
		# Write a 32bit Quaternion (eek! space!)
		# X, Y, Z, W
		self.writePoint4F(value) # Same as Quat
	def readQuat16(self):
		# Reads in quat16 and returns quat
		# X, Y, Z, W
		q16 = Quat16()
		q16.x, q16.y, q16.z, q16.w = self.reads16(), self.reads16(), self.reads16(), self.reads16()
		return q16.toQuat()
	def writeQuat16(self, value):
		# Converts quat to quat16 and writes
		# X, Y, Z, W
		q16 = value.toQuat16()
		# HACK : Clip some of these values if they are too big or too small
		# (-32,768 to +32,767)
		if q16.x > 32767: q16.x = 32767
		elif q16.x < -32768: q16.x = -32768
		elif q16.y > 32767: q16.y = 32767
		elif q16.y < -32768: q16.y = -32768
		elif q16.z > 32767: q16.z = 32767
		elif q16.z < -32768: q16.z = -32768
		elif q16.w > 32767: q16.w = 32767
		elif q16.w < -32768: q16.w = -32768
		self.writes16(q16.x)
		self.writes16(q16.y)
		self.writes16(q16.z)
		self.writes16(q16.w)
	def readCluster(self):
		v1 = self.reads32()
		v2 = self.reads32()
		v3 = self.readPoint3F()
		v4 = self.readf32()
		v5 = self.reads32()
		v6 = self.reads32()
		return Cluster(v1, v2, v3, v4, v5, v6)
	def writeCluster(self, value):
		self.writes32(value.startPrimitive)
		self.writes32(value.endPrimitive)
		self.writePoint3F(value.normal)
		self.writef32(value.k)
		self.writes32(value.frontCluster)
		self.writes32(value.backCluster)
	def readNode(self):
		v1 = self.reads32()
		v2 = self.reads32()
		v3 = self.reads32() # Computed at Runtime
		v4 = self.reads32() # Computed at Runtime
		v5 = self.reads32() # Computed at Runtime
		no = Node(v1, v2) # Better set these in case...
		no.firstObject = v3
		no.firstChild  = v4
		no.nextSibling = v5
		return Node(v1, v2)
	def writeNode(self, value):
		self.writes32(value.name)
		self.writes32(value.parent)
		self.writes32(value.firstObject) # Computed at Runtime
		self.writes32(value.firstChild)  # Computed at Runtime
		self.writes32(value.nextSibling) # Computed at Runtime
	def readObjectState(self):
		v1 = self.readf32()
		v2 = self.reads32()
		v3 = self.reads32()
		return ObjectState(v1, v2, v3)
	def writeObjectState(self, value):
		self.writef32(value.vis)
		self.writes32(value.frame)
		self.writes32(value.matFrame)
	def readObject(self):
		v1 = self.reads32()
		v2 = self.reads32()
		v3 = self.reads32()
		v4 = self.reads32()
		v5 = self.reads32()
		v6 = self.reads32()
		ob = dObject(v1, v2, v3, v4)
		ob.sibling = v5
		ob.firstDecal = v6
		return ob
	def writeObject(self, value):
		self.writes32(value.name)
		self.writes32(value.numMeshes)
		self.writes32(value.firstMesh)
		self.writes32(value.node)
		self.writes32(value.sibling)
		self.writes32(value.firstDecal)
	def readDecalState(self):
		v1 = self.reads32()
		return DecalState(v1)
	def writeDecalState(self, value):
		self.writes32(value.frame)
	def readDecal(self):
		v1 = self.reads32()
		v2 = self.reads32()
		v3 = self.reads32()
		v4 = self.reads32()
		v5 = self.reads32()
		return Decal(v1, v2, v3, v4, v5)
	def writeDecal(self, value):
		self.writes32(value.name)
		self.writes32(value.numMeshes)
		self.writes32(value.firstMesh)
		self.writes32(value.object)
		self.writes32(value.sibling)
	def readTrigger(self):
		v1 = self.reads32()
		v2 = self.readf32()
		return Trigger(v1, v2)
	def writeTrigger(self, value):
		self.writes32(value.state)
		self.writef32(value.pos)
	def readDetailLevel(self):
		v1 = self.reads32()
		v2 = self.reads32()
		v3 = self.reads32()
		v4 = self.readf32()
		v5 = self.readf32()
		v6 = self.readf32()
		v7 = self.reads32()
		return DetailLevel(v1, v2, v3, v4, v5, v6, v7)
	def writeDetailLevel(self, value):
		self.writes32(value.name)
		self.writes32(value.subshape)
		self.writes32(value.objectDetail)
		self.writef32(value.size)
		self.writef32(value.avgError)
		self.writef32(value.maxError)
		self.writes32(value.polyCount)
	def readString(self):
		# Read in string... from Dts Stream
		slen = self.read8()
		if slen == 0:
			return None
		mystr = array('B')
		for ln in range(0, slen):
			mystr.append(self.readu8()) # May not work
		return mystr.tostring()
	def writeString(self, value):
		# Write string... in Dts Stream
		mystr = array('B')
		mystr.fromstring(value)
		self.write8(len(mystr))
		for ln in range(0, len(value)):
			self.writeu8(mystr[ln])
	def readStringt(self):
		# Read in string...(terminated) from Dts Stream
		end = 0
		mystr = array('B')
		while end != 1:
			val = self.readu8()
			if val != 0x00:
				mystr.append(val)
			else:
				end = 1
		return mystr.tostring()
	def writeStringt(self, value):
		# Write string... in Dts Stream
		# Quick fix : If we are None, or length 0, then just terminate
		if value == None:
			self.writeu8(0x00)
			return
		elif len(value) == 0:
			self.writeu8(0x00)
			return

		# Else just do the normal way
		mystr = array('B')
		mystr.fromstring(value)
		if mystr[len(mystr)-1] != 0x00:
			mystr.append(0x00)
		for ln in range(0, len(mystr)):
			self.writeu8(mystr[ln])
	def readIflMaterial(self):
		v1 = self.reads32()
		v2 = self.reads32()
		v3 = self.reads32()
		v4 = self.reads32()
		v5 = self.reads32()
		return IflMaterial(v1, v2, v3, v4, v5)
	def writeIflMaterial(self, value):
		self.writes32(value.name)
		self.writes32(value.slot)
		self.writes32(value.firstFrame)
		self.writes32(value.time)
		self.writes32(value.numFrames)

# End of file
