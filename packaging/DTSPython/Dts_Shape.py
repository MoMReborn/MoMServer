'''
Dts_Shape.py

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

from Torque_Util import *
from Dts_Mesh import Primitive, Cluster, DtsMesh
from Dts_Stream import *

###############################
# Torque Game Engine
# -------------------------------
# Dts Shape Class(es) for Python
###############################

# Node class - DTS tree node
class Node:
	def __init__(self, na=0, pa=-1):
		self.name = na		# index of its name in the DTS string table
		self.parent = pa	# number of the parent node; -1 if root
		self.firstObject = -1	# deprecated; set to -1
		self.firstChild  = -1	# deprecated; set to -1
		self.nextSibling = -1	# deprecated; set to -1

# dObject class - DTS object
class dObject:
	def __init__(self, na=0, nm=0, fm=0, no=-1):
		self.name = na		# index of its name in the DTS string table
		self.numMeshes = nm	# number of meshes (only one for detail level)
		self.firstMesh = fm	# number of the first mesh (meshes must be consecutive)
		self.node = no		# number of the node where the object is stored
		self.sibling = -1	# deprecated; set to -1
		self.firstDecal = -1	# deprecated; set to -1
	def duplicate(self):
		clone = dObject(self.name, self.numMeshes, self.firstMesh, self.node)
		clone.sibling = self.sibling
		clone.firstDecal = self.firstDecal

# dMaterial class - DTS material
class dMaterial:
	# Material flags
	SWrap             = 0x00000001
	TWrap             = 0x00000002
	Translucent       = 0x00000004
	Additive          = 0x00000008
	Subtractive       = 0x00000010
	SelfIlluminating  = 0x00000020
	NeverEnvMap       = 0x00000040
	NoMipMap          = 0x00000080
	MipMapZeroBorder  = 0x00000100
	IFLMaterial       = 0x00000000
	IFLFrame          = 0x10000000
	DetailMap         = 0x20000000
	BumpMap           = 0x40000000
	ReflectanceMap    = 0x80000000
	AuxiliaryMask     = 0xF0000000
	def __init__(self, na=0, fl=0, refl=-1, bum=-1, det=-1, dets=1.0, reflc=0):
		self.name = na		# texture name; materials don't use the DTS string table
		self.flags = fl		# material flags
		self.reflectance = refl	# index of reflectance map
		self.bump = bum		# index of bump map
		self.detail = det	# index of detail map
		self.detailScale = dets	# Scale of detail map
		self.reflection = reflc	# Amount of reflectance

# Decal Class	
class Decal:
	def __init__(self, na, nm, fm, ob=-1, sb=-1):
		self.name = na
		self.numMeshes = nm
		self.firstMesh = fm
		self.object = ob
		self.sibling = sb

# MaterialList class
class MaterialList:
	version = 1	# Version of the dts material list
	def __init__(self):
		self.materials = []
	
	def __del__(self):
		while len(self.materials) != 0:
			del self.materials[0]
		del self.materials
	
	def materialExists(self, name):
		for m in self.materials:
			if m.name == name:
				return True
		return False
	
	def findMaterial(self, name):
		for m in range(0, len(self.materials)):
			if self.materials[m].name == name:
				return m
		return None
	
	def get(self, no):
		if no >= len(self.materials): return None
		return self.materials[no]
	
	def add(self, mt):
		self.materials.append(mt)
		return len(self.materials)-1
	
	def size(self):
		return len(self.materials)
	
	def printInfo(self):
		print "Material List, Version %d" % (self.version)
		print "Contains : %d Materials" % (len(self.materials))
		for m in self.materials:
			print "Material : %s" % (m.name)
			print "-Flags : %d" % (m.flags)
			print "-Reflectance : %d" % (m.reflectance)
			print "-Bump : %d" % (m.bump)
			print "-Detail : %d" % (m.detail)
			print "-detailScale : %f" % (m.detailScale)
			print "-reflection : %f" % (m.reflection)
	
	def read(self, fs):
		ver = struct.unpack('<b', fs.read(calcsize('<b')))[0] #U8
		if self.version == ver:
			sz = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
			# Read strings, adding a material for each one
			for cnt in range(0, sz):
				st = array('c') 
				# Read in string..
				ss = struct.unpack('<b', fs.read(calcsize('<b')))[0] #U8
				st.fromfile(fs, ss)
				self.materials.append(dMaterial(st.tostring()))
			# Read the rest of the Material properties (ref and ds is F32, rest is U32)
			for mat in self.materials:
				mat.flags = struct.unpack('<I', fs.read(calcsize('<I')))[0] # U32
			for mat in self.materials:
				mat.reflectance = struct.unpack('<I', fs.read(calcsize('<I')))[0] # U32
			for mat in self.materials:
				mat.bump = struct.unpack('<I', fs.read(calcsize('<I')))[0] # U32
			for mat in self.materials:
				mat.detail = struct.unpack('<I', fs.read(calcsize('<I')))[0] # U32
			for mat in self.materials:
				mat.detailScale = struct.unpack('<f', fs.read(calcsize('<f')))[0] # F32
			for mat in self.materials:
				mat.reflection = struct.unpack('<f', fs.read(calcsize('<f')))[0] # F32
		else:
			print "Error! Version mismatch (%d, should be %d)" % (ver, self.version)
	
	def write(self, fs):
		fs.write(struct.pack('<b', self.version)) # Version
		# name, flags, refl, bump, det, detsca, reflecion (in seperate arrays)
		# Names
		fs.write(struct.pack('<i', len(self.materials))) #S32
		for mat in self.materials:
			fs.write(struct.pack('<b', len(mat.name))) # Length of Name
			st = array('c')
			st.fromstring(mat.name)
			st.tofile(fs)
		for mat in self.materials:
			fs.write(struct.pack('<I', mat.flags))
		for mat in self.materials:
			fs.write(struct.pack('<I', mat.reflectance))
		for mat in self.materials:
			fs.write(struct.pack('<I', mat.bump))
		for mat in self.materials:
			fs.write(struct.pack('<I', mat.detail))
		for mat in self.materials:
			fs.write(struct.pack('<f', mat.detailScale))
		for mat in self.materials:
			fs.write(struct.pack('<f', mat.reflection))


# IFLMaterial class
class IflMaterial:
	def __init__(self, na=0, sl=0, ff=0, ti=0, nf=0):
		self.name = na		# index of its name in the DTS string table
		self.slot = sl		# Slot of IFL Material
		self.firstFrame = ff	# First IFL Frame
		self.time = ti		# Time for sequence
		self.numFrames = nf	# Number of frames in material

# DetailLevel class
class DetailLevel:
	def __init__(self, na=0, ss=0, od=0, sz=0.0, ae=-1, me=-1, pc=0):
		self.name = na		# index of the name in the DTS string table
		self.subshape = ss	# number of the subshape it belongs to
		self.objectDetail = od	# number of object mesh to draw for each object
		self.size = sz		# minimum pixel size (F32)
		self.avgError = ae	# Average error (alternate detail scheme)
		self.maxError = me	# Maximum error (alternate detail scheme)
		self.polyCount = pc	# Polygon count (of all meshes in detail level)

# Encodes billboard data
def encodeBillBoard(equator, polar, polarangle, dl, dim, includepoles):
	val = 0

	# dim is width + height

	# 2, 2, 45, 0, 256, 0

	# equator - Number of Equator Steps
	# polar - Number of Polar Steps
	# polarangle(radians) - Threshhold before showing the polar view on the billboard
	# dl - Detail level to take picture of (typically 0)
	# dim - image dimensions (max 128)
	# includepoles - Take shots of top and bottom?

	val |= (equator & 0x7F)			# bits 0..6
	val |= (val & 0x3F) << 7		# bits 7..12

	# polarAngle max is 1.57079632679  0.785398163397
	# polarAngle max in degrees is 45.0
	# (int value unpacked is 32)

	# Convert to radians
	polarAngle = (float(polarangle) * 3.14159265358979323846) / 180.0
	# Compress the value using some division
	polarAngle = int( round( ((polarAngle) / (1.0/64.0) / 3.14159265358979323846 / 0.5)) )
	if polarAngle > 32: polarAngle = 32 # cannot be higher than 32

	val |= (polarAngle & 0x3F) << 13	# bits 13..18
	val |= (dl & 0x0F) << 19		# 19..22
	val |= (dim & 0xFF) << 23		# 23..30

	if includepoles:
		val |= 1 << 31 # true
	else:
		val |= 0 << 31 # false

	return val

# Subshape class - DTS subshape 
class SubShape:
	def __init__(self, fn=0, fo=0, fd=0, nn=0, no=0, nd=0):
		self.firstNode = fn	# Index of first node in subshape
		self.firstObject = fo	# Index of first object in subshape
		self.firstDecal = fd	# Index of first decal in subshape
		self.numNodes = nn	# Number of nodes in subshape
		self.numObjects = no	# Number of objects in subshape
		self.numDecals = nd	# Number of decals in the subshape
		self.firstTranslucent=0	# N/A
		
# ObjectState class
class ObjectState:
	def __init__(self, vs=1.0, fr=0, mf=0):
		self.vis = vs		# Alpha of object (0..1.0f)
		self.frame = fr		# Frame each mesh of the object should be on ([(vertsPerFrame*frame)..((vertsPerFrame*frame)+vertsPerFrame)])
		self.matFrame = mf	# IFL Material frame

# Trigger class (used for footsteps, etc)
class Trigger:
	StateOn = 1 << 31
	InvertOnReverse = 1 << 30
	StateMask = 1 << (30)-1
	
	def __init__(self, st=0, ps=0.0, revert=False):
		self.pos = ps
		
		if (st == 0) or (st < -30) or (st > 30):
			print "Warning : Invalid Trigger state (%d)" % (st)
		if st < 0:
			val = -st - 1
			on = False
		else:
			val = st - 1
			on = True
		
		if on:
			self.state = 1 << val
			self.state |= self.StateOn
		else:
			self.state = 1 << val
		
		if revert:
			self.state |= self.InvertOnReverse

# Get the highest number from an array (unsigned)
def highest(arr):
	lasthighest = 0
	for a in arr:
		if a > lasthighest: lasthighest = a
	return lasthighest

# Sequence class
class Sequence:
	# flags
	UniformScale    = 0x0001
	AlignedScale    = 0x0002
	ArbitraryScale  = 0x0004
	Blend           = 0x0008
	Cyclic          = 0x0010
	MakePath        = 0x0020
	IFLInit         = 0x0040
	HasTranslucency = 0x0080
	def __init__(self, na=0, fl=0, nk=0, du=0.0, pri=0, fg=-1, ng=0, br=-1, bt=-1, bs=-1, bos=-1, bds=-1, ft=-1, nt=0, tb=0):
		self.nameIndex = na		# index of the name in the DTS string table
		self.flags = fl			# Flags of sequence
		self.numKeyFrames = nk		# Number of keyframes in sequence
		self.duration = du		# Duratuion of the sequence in seconds
		self.priority = pri		# Priority of sequence
		self.firstGroundFrame = fg	# Index of first ground frame
		self.numGroundFrames = ng	# Number of ground frames
		self.baseRotation = br		# Index of first rotation frame
		self.baseTranslation = bt	# Index of first translation frame
		self.baseScale = bs		# Index of first scale frame
		self.baseObjectState = bos	# Index of first object state
		self.baseDecalState = bds	# Index of first decal state
		self.firstTrigger = ft		# Index of first trigger
		self.numTriggers = nt		# Number of triggers
		self.toolBegin=tb		# ToolBegin
		self.matters_rotation = []	# Boolean list of nodes used in sequence with rotation frames
		self.matters_translation = []	# Boolean list of nodes used in sequence with translation frames
		self.matters_scale = []		# Boolean list of nodes used in sequence with scale frames
		self.matters_decal = []		# Boolean list of decals used in sequence
		self.matters_ifl = []		# Boolean list of IFL materials used in sequence
		self.matters_vis = []		# Boolean list of object states.visibility used in sequence
		self.matters_frame = []		# Boolean list of object states.frame used in sequence
		self.matters_matframe = []	# Boolean list of object states.matframe used in sequence
	def __del__(self):
		del self.matters_rotation
		del self.matters_translation
		del self.matters_scale
		del self.matters_decal
		del self.matters_ifl
		del self.matters_vis
		del self.matters_frame
		del self.matters_matframe
	def read(self, fs):
		self.nameIndex = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.flags = struct.unpack('<I', fs.read(calcsize('<I')))[0] #U32
		self.numKeyFrames = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.duration = struct.unpack('<f', fs.read(calcsize('<f')))[0] #F32
		self.priority = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.firstGroundFrame = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.numGroundFrames = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.baseRotation = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.baseTranslation = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.baseScale = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.baseObjectState = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.baseDecalState = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.firstTrigger = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.numTriggers = struct.unpack('<i', fs.read(calcsize('<i')))[0] #S32
		self.toolBegin = struct.unpack('<f', fs.read(calcsize('<f')))[0] #F32
		
		# Read integer sets
		self.matters_rotation = readIntegerSet(fs)
		self.matters_translation = readIntegerSet(fs)
		self.matters_scale = readIntegerSet(fs)
		self.matters_decal = readIntegerSet(fs)
		self.matters_ifl = readIntegerSet(fs)
		self.matters_vis = readIntegerSet(fs)
		self.matters_frame = readIntegerSet(fs)
		self.matters_matframe = readIntegerSet(fs)
	
	def write(self, fs, noIndex=False):
		# Write Struct...
		if noIndex == False: # Write Index
			fs.write(struct.pack('<i',self.nameIndex))
		fs.write(struct.pack('<I',self.flags))
		fs.write(struct.pack('<i',self.numKeyFrames))
		fs.write(struct.pack('<f',self.duration))
		fs.write(struct.pack('<i',self.priority))
		fs.write(struct.pack('<i',self.firstGroundFrame))
		fs.write(struct.pack('<i',self.numGroundFrames))
		fs.write(struct.pack('<i',self.baseRotation))
		fs.write(struct.pack('<i',self.baseTranslation))
		fs.write(struct.pack('<i',self.baseScale))
		fs.write(struct.pack('<i',self.baseObjectState))
		fs.write(struct.pack('<i',self.baseDecalState))
		fs.write(struct.pack('<i',self.firstTrigger))
		fs.write(struct.pack('<i',self.numTriggers))
		fs.write(struct.pack('<f',self.toolBegin))
		
		# Write integer sets
		writeIntegerSet(fs, self.matters_rotation)
		writeIntegerSet(fs, self.matters_translation)
		writeIntegerSet(fs, self.matters_scale)
		writeIntegerSet(fs, self.matters_decal)
		writeIntegerSet(fs, self.matters_ifl)
		writeIntegerSet(fs, self.matters_vis)
		writeIntegerSet(fs, self.matters_frame)
		writeIntegerSet(fs, self.matters_matframe)

	# Resizes the matters array, removing 0's
	def clearMatters(self, matter):
		count = 0
		# Count number of 0's
		for m in matter:
			if not m:
				count += 1
		del matter[:count]
		# Make sure everything is 1
		for m in range(0, len(matter)):
			matter[m] = True

	# Counts nodes used in sequence
	def countNodes(self, countMode = -1):
		global_count = 0
		translation_count = 0
		rotation_count = 0
		scale_count = 0
		# NOTE: assumes matters_rotation is the size of the shape's nodes and the other matters_*
		for n in range(0, len(self.matters_rotation)):
			if (countMode == 0) and self.matters_rotation[n]: rotation_count += 1
			elif (countMode == 1) and self.matters_translation[n]: translation_count += 1
			elif (countMode == 2) and self.matters_scale[n]: scale_count += 1
			elif self.matters_rotation[n] or self.matters_translation[n] or self.matters_scale[n]:
				global_count += 1
		
		if countMode == 0: return rotation_count
		elif countMode == 1: return translation_count
		elif countMode == 2: return scale_count
		else: return global_count

	# Returns indexes of nodes used in sequence
	def getNodes(self, countMode = -1):
		nodes = []
		for n in range(0, len(self.matters_rotation)):
			if self.matters_rotation[n]: 
				if not nodes.__contains__(n): nodes.append(n)
		if countMode == 0: return nodes
		elif countMode != -1: nodes = []
		
		for n in range(0, len(self.matters_translation)):
			if self.matters_translation[n]:
				if not nodes.__contains__(n): nodes.append(n)
		if countMode == 1: return nodes
		elif countMode != -1: nodes = []
		
		for n in range(0, len(self.matters_scale)):
			if self.matters_scale[n]:
				if not nodes.__contains__(n): nodes.append(n)
		if countMode == 2: return nodes
		return nodes

# The rather pointless DecalState class
class DecalState:
	def __init__(self, fr=0):
		self.frame = fr

# Main Shape Class
class DtsShape:
	smNumSkipLoadDetails = False

	def getNode(self, name):
		for n in self.nodes:
			if n.name == -1:
				continue
			if name == self.sTable.get(n.name):
				return n
		return None
	
	def getNodeIndex(self, name):
		for n in range(0, len(self.nodes)):
			if self.nodes[n].name == -1:
				continue
			if name == self.sTable.get(self.nodes[n].name):
				return n
		return None
	
	def getSequence(self, name):
		for s in self.sequences:
			if s.nameIndex == -1:
				continue
			if name == self.sTable.get(s.nameIndex):
				return s
		return None
	
	def __init__(self):
		self.bounds = Box()		# Bounds of shape
		self.center = Vector(0,0,0)	# Center
		self.tubeRadius = 0		# Shape tube radius (all meshes)
		self.radius = 0.0		# Shape radius (all meshes)
		self.meshes = []		# Meshes
		self.nodes = []			# Nodes (bones)
		self.sequences = []		# Sequences
		self.triggers = []		# Triggers
		self.objects = []		# Objects
		self.objectstates = []		# Object States
		self.iflmaterials = []		# IFL Materials
		self.subshapes = []		# Subshapes
		self.detaillevels = []		# Detail Levels
		self.decals = []		# Decals
		self.decalstates = []		# Decal States
		self.materials = MaterialList()	# Material List
		self.sTable = StringTable()	# String Table
		self.defaultRotations = []	# Default node rotations
		self.defaultTranslations = []	# Default node translations
		self.nodeTranslations = []	# Node translations
		self.nodeRotations = []		# Node rotations
		self.nodeUniformScales = array('f') # Node scales (uniform)
		self.nodeAlignedScales = []	# Node scales (aligned)
		self.nodeAbitraryScaleFactors = []# Node scale factors
		self.nodeAbitraryScaleRots = []	# Node scale quats
		
		self.groundTranslations = []	# Ground translation frames
		self.groundRotations = []	# Ground rotation frames
		
		self.alphain = array('f')	# Used for detail blending
		self.alphaout = array('f')	# Used for detail blending
		self.mPreviousMerge = []
		self.mExportMerge = False
		self.mSmallestVisibleSize = 0	# Smallest visible size (approximation)
		self.mSmallestVisibleDL = 0
	
	def __del__(self):
		clearArray(self.meshes)
		del self.nodes
		clearArray(self.sequences)
		del self.triggers
		del self.objects
		del self.objectstates
		del self.iflmaterials
		del self.subshapes
		del self.detaillevels
		del self.decals
		del self.decalstates
		del self.materials
		del self.defaultRotations
		del self.defaultTranslations
		del self.nodeTranslations 
		del self.nodeRotations
		del self.nodeUniformScales
		del self.nodeAlignedScales
		del self.nodeAbitraryScaleFactors
		del self.nodeAbitraryScaleRots
		del self.groundTranslations
		del self.groundRotations
		del self.alphain 
		del self.alphaout
		del self.mPreviousMerge
		del self.sTable
	
	def checkSkip(self, meshNum, curObject, curDecal, skipDL):
		# More or less a translation of the C++ code
		# 0 = false, 1 = true
		if skipDL==0:
			return False # easy out...
		# Skip detail level exists on this subshape
		skipSS = self.detaillevels[skipDL].subshape
		
		if curObject < len(self.objects):
			start = self.objects[curObject].firstMesh
			if meshNum >= start:
				# We are either from this object, the next object, or a decal
				if meshNum < start + self.objects[curObject].numMeshes:
					# This Object...
					if self.subshapes[skipSS].firstObject > curObject:
						# Haven't reached this subshape yet
						return True
					if (len(self.subshapes) == skipSS+1) or (curObject < self.subshapes[skipSS+1].firstObject):
						# curObject is on the subshape of a skip detail...make sure it's after skipDL
						if meshNum-start < self.detaillevels[skipDL].objectDetail:
							return True
						else:
							return False
					# if we get here, then curObject occurs on a subShape after skip detail (so keep it)
					return False
				else:
					return self.checkSkip(meshNum, curObject + 1, curDecal, skipDL)

		if curDecal < len(self.decals):
			start = self.decals[curDecal].firstMesh
			if meshNum >= start:
				# we are either from this decal, the next decal, or error
				if meshNum < start + self.decals[curDecal].numMeshes:
					# this object...
					if self.subshapes[skipSS].firstDecal > curDecal:
						# haven't reached this subshape yet
						return True
					if (len(self.subshapes) == skipSS+1) or (curDecal < self.subshapes[skipSS+1].firstDecal):
						# curDecal is on subshape of skip detail...make sure it's after skipDL
						if meshNum-start<self.detaillevels[skipDL].objectDetail:
							return True
						else:
							return False
					else:
						# if we get here, then curDecal ocurrs on subShape after skip detail (so keep it)
						return False
			else:
				# advance decal, try again
				return self.checkSkip(meshNum, curObject, curDecal+1, skipDL)
		return False
	
	def write(self, dstream):
		# In this function, we write to the dstream, flush it, then write_end
		# Write Counts...
		dstream.writes32(len(self.nodes))
		dstream.writes32(len(self.objects))
		dstream.writes32(len(self.decals))
		dstream.writes32(len(self.subshapes))
		dstream.writes32(len(self.iflmaterials))
		dstream.writes32(len(self.nodeRotations))
		dstream.writes32(len(self.nodeTranslations))
		dstream.writes32(len(self.nodeUniformScales))
		dstream.writes32(len(self.nodeAlignedScales))
		dstream.writes32(len(self.nodeAbitraryScaleFactors)) # Both scale's must be same length
		
		dstream.writes32(len(self.groundRotations))
		dstream.writes32(len(self.objectstates))
		dstream.writes32(len(self.decalstates))
		dstream.writes32(len(self.triggers))
		dstream.writes32(len(self.detaillevels))
		dstream.writeu32(len(self.meshes))

		dstream.writes32(len(self.sTable.strings))

		dstream.writes32(self.mSmallestVisibleSize) # This is typecasted to F32, but isn't a float when stored
		dstream.writes32(self.mSmallestVisibleDL)

		dstream.storeCheck()

		# Write Bounds...
		dstream.writef32(self.radius)
		dstream.writef32(self.tubeRadius)
		dstream.writePoint3F(self.center)
		dstream.writeBox(self.bounds)
		
		dstream.storeCheck()
		
		# Write Various Vectors...
		# Write Nodes
		for cnt in self.nodes:
			dstream.writeNode(cnt)
		
		dstream.storeCheck()
		
		# Write Objects
		for cnt in self.objects:
			dstream.writeObject(cnt)
		
		dstream.storeCheck()
		
		# Write Decals
		for cnt in self.decals:
			dstream.writeDecal(cnt)
		
		dstream.storeCheck()
		
		# Write Ifl Materials
		for cnt in self.iflmaterials:
			dstream.writeIflMaterial(cnt)
		
		dstream.storeCheck()
		
		# Write SubShapes
		for shape in self.subshapes:
		# first* and num*
			dstream.writes32(shape.firstNode)
		for shape in self.subshapes:
			dstream.writes32(shape.firstObject)
		for shape in self.subshapes:
			dstream.writes32(shape.firstDecal)
			
		dstream.storeCheck()
		
		for shape in self.subshapes:
			dstream.writes32(shape.numNodes)
		for shape in self.subshapes:
			dstream.writes32(shape.numObjects)
		for shape in self.subshapes:
			dstream.writes32(shape.numDecals)
			
		dstream.storeCheck()
		
		# Get default translation and rotation...
		for cnt in range(0, len(self.defaultRotations)): # Same length as default translations
			dstream.writeQuat16(self.defaultRotations[cnt])
			dstream.writePoint3F(self.defaultTranslations[cnt])
			
		# Get any node sequence data stored in shape
		for cnt in self.nodeTranslations:
			dstream.writePoint3F(cnt)
		for cnt in self.nodeRotations:
			dstream.writeQuat16(cnt)
			
		dstream.storeCheck()
		
		# More node sequence data...scale
		for cnt in self.nodeUniformScales:
			dstream.writef32(cnt)
		for cnt in self.nodeAlignedScales:
			dstream.writePoint3F(cnt)
		for cnt in self.nodeAbitraryScaleFactors:
			dstream.writePoint3F(cnt)
		for cnt in self.nodeAbitraryScaleRots:
			dstream.writeQuat16(cnt)
			
		dstream.storeCheck()
		
		for cnt in self.groundTranslations:
			dstream.writePoint3F(cnt)
		for cnt in self.groundRotations:
			dstream.writeQuat16(cnt)
			
		dstream.storeCheck()
		
		# Object States
		for cnt in self.objectstates:
			dstream.writeObjectState(cnt)
			
		dstream.storeCheck()
		
		# Decal States
		
		for cnt in self.decalstates:
			dstream.writeDecalState(cnt)
		
		dstream.storeCheck()
		
		# Frame Triggers
		
		for cnt in self.triggers:
			dstream.writeTrigger(cnt)
		
		dstream.storeCheck()
		
		# Details
		
		for cnt in self.detaillevels:
			dstream.writeDetailLevel(cnt)
		
		dstream.storeCheck()
		
		# Meshes
		for msh in self.meshes:
			dstream.writeu32(int(msh.mtype)) # Write Mesh Type
			msh.write(dstream)
		
		dstream.storeCheck()
		
		# Names
		for cnt in self.sTable.strings:
			dstream.writeStringt(cnt)
		dstream.storeCheck()
		# ...
		
		# Flush. Needed here
		dstream.flush()
		self.write_end(dstream) # And write the rest of the story
	
	def write_end(self, dstream):
		# Write Sequences and Materials HERE
		dstream.fs.write(struct.pack('<i', len(self.sequences))) #S32
		for seq in self.sequences:
			seq.write(dstream.fs)
		
		# Write Material List
		self.materials.write(dstream.fs)
	
	def read(self, dstream):
		# Read in a shape. Calls the mesh read, and soforth
		#print "Reading in Sequences and Materials"
		# First, we need to read in sequences (not in memory buffers, is at end of the file)...
		numSequences = struct.unpack('<i', dstream.fs.read(calcsize('<i')))[0] #S32
		for seq in range(0, numSequences): # ^^ as usual, this spits out an annoying array
			sq = Sequence()
			sq.read(dstream.fs)
			self.sequences.append(sq)
		
		# Read Material List
		self.materials.read(dstream.fs)
		
		#JMR (only interested in materials)
		return
		
        #print "Reading in from streams..."
		## >> End of normal file reading <<##
		# Get Counts...
		numNodes = dstream.reads32()       # S32 numNodes = alloc.get32();
		numObjects = dstream.reads32()     # S32 numObjects = alloc.get32();
		numDecals = dstream.reads32()      # S32 numDecals = alloc.get32();
		numSubShapes = dstream.reads32()   # S32 numSubShapes = alloc.get32();
		numIflMaterials = dstream.reads32()# S32 numIflMaterials = alloc.get32();
		numNodeRots = dstream.reads32()    # S32 numNodeRots = alloc.get32();
		numNodeTrans = dstream.reads32()   # S32 numNodeTrans = alloc.get32();
		numNodeUniformScales = dstream.reads32() # S32 numNodeUniformScales = alloc.get32();
		numNodeAlignedScales = dstream.reads32() # S32 numNodeAlignedScales = alloc.get32();
		numNodeArbitraryScales = dstream.reads32() # S32 numNodeArbitraryScales = alloc.get32();
		
		numGroundFrames = dstream.reads32() # S32 numGroundFrames = alloc.get32();
		numObjectStates = dstream.reads32() # S32 numObjectStates = alloc.get32();
		numDecalStates = dstream.reads32() # S32 numDecalStates = alloc.get32();
		numTriggers = dstream.reads32() # S32 numTriggers = alloc.get32();
		numDetails = dstream.reads32() # S32 numDetails = alloc.get32();
		numMeshes = dstream.reads32() # S32 numMeshes = alloc.get32();
		numNames = dstream.reads32()

		self.mSmallestVisibleSize = dstream.reads32() # Not a float
		self.mSmallestVisibleDL = dstream.reads32()
		skipDL = min(self.mSmallestVisibleDL,self.smNumSkipLoadDetails)
		
		dstream.readCheck() # Fails on 8bit buffer
			
		# get bounds
		self.radius = dstream.readf32()
		self.tubeRadius = dstream.readf32()
		self.center = dstream.readPoint3F()
		self.bounds = dstream.readBox()
		
		dstream.readCheck()
		
		# Copy Various Vectors...
		# Read in Nodes
		for cnt in range(0, numNodes):
			self.nodes.append(dstream.readNode())
		
		dstream.readCheck()
		
		# Read in Objects
		for cnt in range(0, numObjects):
			self.objects.append(dstream.readObject())
		
		dstream.readCheck()

		# Read in Decals
		for cnt in range(0, numDecals):
			self.decals.append(dstream.readDecal())
		
		dstream.readCheck()
		
		# Read in Ifl Materials
		for cnt in range(0, numIflMaterials):
			self.iflmaterials.append(dstream.readIflMaterial())
		
		dstream.readCheck()
		
		# Read in subShapes
		# A tad more complex since the file stores everything seperatly
		afirstNode = []
		afirstObject = []
		afirstDecal = []
		anumNodes = []
		anumObjects = []
		anumDecals = []
		for cnt in range(0, numSubShapes):
			afirstNode.append(dstream.reads32())
		for cnt in range(0, numSubShapes):
			afirstObject.append(dstream.reads32())
		for cnt in range(0, numSubShapes):
			afirstDecal.append(dstream.reads32())

		dstream.readCheck()
		
		for cnt in range(0, numSubShapes):
			anumNodes.append(dstream.reads32())
		for cnt in range(0, numSubShapes):
			anumObjects.append(dstream.reads32())
		for cnt in range(0, numSubShapes):
			anumDecals.append(dstream.reads32())
		for cnt in range(0, numSubShapes):
			# Finally, add the subshapes
			self.subshapes.append(SubShape(afirstNode[cnt], afirstObject[cnt], afirstDecal[cnt], anumNodes[cnt], anumObjects[cnt], anumDecals[cnt]))
		
		dstream.readCheck()
		# Cleanup
		del afirstNode
		del afirstObject
		del afirstDecal
		del anumNodes
		del anumObjects
		del anumDecals
		
		# No need to read meshIndexList

		# Get default translation and rotation...
		for cnt in range(0, numNodes):
			self.defaultRotations.append(dstream.readQuat16())
			self.defaultTranslations.append(dstream.readPoint3F())
			
		# Get any node sequence data stored in shape
		for cnt in range(0, numNodeTrans):
			self.nodeTranslations.append(dstream.readPoint3F())
		for cnt in range(0, numNodeRots):
			self.nodeRotations.append(dstream.readQuat16())
			
		dstream.readCheck()
		
		# More node sequence data...scale
		for cnt in range(0, numNodeUniformScales):
			self.nodeUniformScales.append(dstream.readf32()) #F32
		for cnt in range(0, numNodeAlignedScales):
			self.nodeAlignedScales.append(dstream.readPoint3F())
		for cnt in range(0, numNodeArbitraryScales):
			self.nodeArbitraryScaleFactors.append(dstream.readPoint3F())
		for cnt in range(0, numNodeArbitraryScales):
			self.nodeArbitraryScaleRots.append(dstream.readQuat16())
			
		dstream.readCheck()
		
		# version 22 & 23 shapes accidentally had no ground transforms, and ground for
		# earlier shapes is handled just above, so...
		
		for cnt in range(0, numGroundFrames):
			self.groundTranslations.append(dstream.readPoint3F())
		for cnt in range(0, numGroundFrames):
			self.groundRotations.append(dstream.readQuat16())
			
		dstream.readCheck()
		
		# Object States
		for cnt in range(0, numObjectStates):
			self.objectstates.append(dstream.readObjectState())
			
		dstream.readCheck()
		
		# Decal States
		
		for cnt in range(0, numDecalStates):
			self.decalstates.append(dstream.readDecalState())
		
		dstream.readCheck()
		
		# Frame Triggers
		
		for cnt in range(0, numTriggers):
			self.triggers.append(dstream.readTrigger())
		
		dstream.readCheck()
		
		# Details
		
		for cnt in range(0, numDetails):
			self.detaillevels.append(dstream.readDetailLevel())
		
		dstream.readCheck()
		
		# Meshes
		# about to read in the meshes...first must allocate some scratch space
		# ^^ We are not doing it in python though
		#print "Reading in Meshes..."
		# Read in Meshes (sans skins)...
		# Straight forward read one at a time
		
		curObject, curDecal= 0, 0 # For tracking skipped meshes
		for cnt in range(0, numMeshes):
			skip = False#self.checkSkip(cnt, curObject, curDecal, skipDL)
			mesh = DtsMesh()
			mesh.mtype = dstream.readu32() #U32 Type of Mesh
			#print "Found Mesh"
			if not skip:
				#print "Reading..."
				val = mesh.read(dstream, self)
				if (val != 1) and (mesh.mtype != 4):
					print "Error Reading Mesh!"
					return None
				self.meshes.append(mesh)

		dstream.readCheck()
		#print "Finished Reading Meshes"
		
		# Read in names to our private string table...
		for cnt in range(0, numNames):
			self.sTable.addString(dstream.readStringt())

		dstream.readCheck()
   
		# allocate storage space for some arrays (filled in during Shape::init)...
		#for cnt in range(0, numDetails):
		#	self.alphain.append(dstream.readf32())
		#for cnt in range(0, numDetails):
		#	self.alphaout.append(dstream.readf32())
	
		for cnt in range(0, numObjects):
			self.mPreviousMerge.append(-1)

		self.mExportMerge = dstream.DTSVersion >= 23;
		
	def getBounds(self):
		return self.bounds
	
	def getRadius(self):
		return self.radius
	
	def getTubeRadius(self):
		return self.tubeRadius
	
	def addName(self, s):
		return self.sTable.addString(s)
	
	def calculateBounds(self):
		if len(self.objects) == 0:
			return
		self.bounds.max = Vector(-10e30, -10e30, -10e30)
		self.bounds.min = Vector(10e30, 10e30, 10e30)

		# Iterate through the objects instead of the meshes
		# so we can easily get the default transforms.
		
		for ob in range(0, len(self.objects)):
			object = self.objects[ob]
			trans = Vector()
			rot = Quaternion()
			trans, rot = self.getNodeWorldPosRot(object.node)
			for j in range(0, object.numMeshes):
				bounds2 = self.meshes[object.firstMesh + j].getBounds(trans,rot) ;
				self.bounds.min[0] = min(self.bounds.min.x(), bounds2.min.x())
				self.bounds.min[1] = min(self.bounds.min.y(), bounds2.min.y())
				self.bounds.min[2] = min(self.bounds.min.z(), bounds2.min.z())
				self.bounds.max[0] = max(self.bounds.max.x(), bounds2.max.x())
				self.bounds.max[1] = max(self.bounds.max.y(), bounds2.max.y())
				self.bounds.max[2] = max(self.bounds.max.z(), bounds2.max.z())
	
	def calculateRadius(self):
		maxRadius = float(0.0)
		for i in range(0, len(self.objects)):
			object = self.objects[i]
			trans = Vector()
			rot = Quaternion()
			trans, rot = self.getNodeWorldPosRot(object.node)
			for j in range(0, object.numMeshes):
				mesh = self.meshes[object.firstMesh + j]
				meshRadius = mesh.getRadiusFrom(trans, rot, self.center)
				if meshRadius > maxRadius: # stupid typo. Fixed!
					maxRadius = meshRadius
			
		self.radius = maxRadius
	
	def calculateTubeRadius(self):
		maxRadius = float(0.0)
		for ob in self.objects:
			trans = Vector2()
			rot = Quaternion()
			trans, rot = self.getNodeWorldPosRot(ob.node)
			for j in range(0, ob.numMeshes):
				mesh = self.meshes[ob.firstMesh + j]
				meshRadius = mesh.getTubeRadiusFrom(trans, rot, self.center)
				if meshRadius > maxRadius:
					maxRadius = meshRadius
		self.tubeRadius = maxRadius
	
	def calculateCenter(self):
		self.center = self.bounds.max.midpoint(self.bounds.min)
	
	def setSmallestSize(self, i):
		# Assumes detail levels are going from biggest -> smallest
		if i < 1.0: i = 1.0
		self.mSmallestVisibleSize = i
		self.mSmallestVisibleDL = -1
		foundSmallest = 9999
		for det in range(0, len(self.detaillevels)):
			# Select a detail level that is smaller than the current, yet bigger than the absolute smallest.
			# Also make sure we don't select billboard details.
			if (self.detaillevels[det].size >= self.mSmallestVisibleSize) and (self.detaillevels[det].size < foundSmallest):
				foundSmallest = self.detaillevels[det].size
				self.mSmallestVisibleDL = det
		# Fix any bad values
		if self.mSmallestVisibleDL < 0: self.mSmallestVisibleDL = 0 # Must at least be 0
	
	def calcSmallestSize(self):
		# Assumes detail levels are going from biggest -> smallest
		self.mSmallestVisibleDL = -1
		self.mSmallestVisibleSize = 9999
		for det in range(0, len(self.detaillevels)):
			# Select a detail level that is smaller than the current, yet bigger than the absolute smallest.
			# Also make sure we don't select billboard details.
			if (self.detaillevels[det].size >= 0) and (self.detaillevels[det].size < self.mSmallestVisibleSize):
				self.mSmallestVisibleDL = det
				self.mSmallestVisibleSize = int(self.detaillevels[det].size)
		# Fix any bad values
		if self.mSmallestVisibleDL < 0: self.mSmallestVisibleDL = 0 # Must at least be 0
		if self.mSmallestVisibleSize == 9999: self.mSmallestVisibleSize = 0
	
	def setCenter(self, p):
		self.center = p
	
	def getNodeWorldPosRot(self, n):
		# Build total translation & rotation for this node
		nidx = []
		nidx.append(n)
		nid = n
		while ((self.nodes[nid].parent) >= 0):
			nid = self.nodes[nid].parent
			nidx.insert(0,nid)
		trans = Vector(0,0,0)
		rot = Quaternion(0,0,0,1)
		for nod in nidx:
			trans += rot.apply(self.defaultTranslations[nod])
			rot = self.defaultRotations[nod] * rot
		return trans, rot
	
	def materialExists(self, name):
		return self.materials.materialExists(name)
	
	def printInfo(self):
		print "Stats for Shape"
		print "***************"
		print "nodes : %d" % (len(self.nodes))
		print "objects : %d" % (len(self.objects))
		print "decals : %d" % (len(self.decals))
		print "subshapes : %d" % (len(self.subshapes))
		print "ifl materials : %d" % (len(self.iflmaterials))
		print "node rotations : %d" % (len(self.nodeRotations))
		print "node translations : %d" % (len(self.nodeTranslations))
		print "node uniform scales : %d" % (len(self.nodeUniformScales))
		print "node aligned scales : %d" % (len(self.nodeAlignedScales))
		print "node abitrary scales : %d" % (len(self.nodeAbitraryScaleFactors))
		
		print "ground frames : %d" % (len(self.groundTranslations))
		print "object states : %d" % (len(self.objectstates))
		print "decal states : %d" % (len(self.decalstates))
		print "triggers : %d" % (len(self.triggers))
		print "detail levels : %d" % (len(self.detaillevels))
		print "meshes : %d" % (len(self.meshes))
		print "names : %d" % (len(self.sTable.strings))
		for n in self.sTable.strings:
			print "  %s" % (n.tostring())
		print "smallest visible size : %d" % (self.mSmallestVisibleSize)
		print "smallest visible DL : %d" % (self.mSmallestVisibleDL)
		
		print "radius : %f" % (self.radius)
		print "tube radius : %f" % (self.tubeRadius)
		print "center : (%f %f %f)" % (self.center[0], self.center[1], self.center[2])
		print "bounds : (%f %f %f) (%f %f %f)" % (self.bounds.min[0], self.bounds.min[1], self.bounds.min[2],self.bounds.max[0], self.bounds.max[1], self.bounds.max[2])

		print "End Stats"
	
	def clearDynamicData(self):
		pass
	
	def init(self):	
		self.clearDynamicData()
		
		# Clear any bogus node info
		for i in self.nodes:
			i.firstObject = i.firstChild = i.nextSibling = -1
			
		# Fill in node info :
		for i in range(0, len(self.nodes)):
			parentId = self.nodes[i].parent
			if parent >= 0:
				if self.nodes[parentId].firstChild<0:
					self.nodes[parentId].firstChild=i
				else:
					child = self.nodes[parentId].firstChild
					while self.nodes[child].nextSibling >= 0:
						child = self.nodes[child].nextSibling
					self.nodes[child].nextSibling = i
		# Fill in object info :
		for i in range(0, len(self.objects)):
			self.objects[i].sibling = -1
			self.objects[i].firstDecal = -1
			
			nodeIndex = self.objects[i].node
			if nodeIndex >= 0:
				if self.nodes[nodeIndex].firstObject<0:
					self.nodes[nodeIndex].firstObject = i
				else:
					objectIndex = self.nodes[nodeIndex].firstObject
					while self.objects[objectIndex].nextSibling >= 0:
						objectIndex = self.objects[objectIndex].nextSibling
					self.objects[objectIndex].sibling = i
		# Fill in decal info :
		for i in range(0, len(self.decals)):
			self.decals[i].sibling = -1
			objectIndex = self.decals[i].object
			if self.objects[objectIndex].firstDecal < 0: # must set objects decal to this
				self.objects[objectIndex].firstDecal = i
			else:
				decalIndex = self.objects[objectIndex].firstDecal
				while self.decals[decalIndex].sibling >= 0:
					decalIndex = self.decals[decalIndex].sibling
				self.decals[decalIndex].sibling = i
		# Fill in sequence data :
		mFlags = 0
		'''
		for in in range(0, len(self.sequences)):
			if not self.sequences[i].animatesScale:
				continue
			
			curVal = mFlags & AnyScale
			newVal = self.sequences[i].flags & AnyScale
			mFlags &= ~(AnyScale)
			mFlags |= max(curVal, NewVal)
		'''
		for i in range(0, len(self.detaillevels)):
			if self.detaillevels[i].size < 0:
				print "TODO 1" # Not implemented creation of these lists yet!!
				#self.alphaIn[i] = 0.0
				#self.alphaOut[i] = 0.0
			elif i+1 == len(self.detaillevels) or self.detaillevels[i+1].size < 0:
				print "TODO 2"
				#self.alphaIn[i] = 0.0
				#self.alphaOut[i] = smAlphaOutLastDetail
			else:
				if self.detaillevels[i+1].subshape < 0:
					print "TODO 3" 
					# billboard detail special
					#self.alphaIn[i] = smAlphaInBillboard
					#self.alphaOut[i] = smAlphaOutBillboard
				else:
					print "TODO 4"
					# Normal detail next
					#self.alphaIn[i] = smAlphaInDefault
					#self.alphaOut[i] = smAlphaOutDefault
			
		# Fixes up subshape # and object detail #
		for i in range(0, self.mSmallestVisibleDL-1):
			if i < self.smNumSkipLoadDetails:
				# detail levels renders when pixel size > cap
				# zap meshes + decals associated with it and
				# use next detail level instead
				ss = self.detaillevels[i].subshape
				od = self.detaillevels[i].objectDetail
				
				if ss == self.detaillevels[i+1].subshape and od == self.detaillevels[i+1].objectDetail:
					# already done? (init supposedly called multiple times??)
					continue
				self.detaillevels[i].subshape = self.detaillevels[i+1].subshape
				self.detaillevels[i].objectDetail = self.detaillevels[i+1].objectDetail
		
		# Calculates polycount on detail levels
		for i in range(0, len(self.detaillevels)):
			count = 0
			ss = self.detaillevels[i].subshape
			od = self.detaillevels[i].objectDetail
			if ss < 0:
				# billboard
				count += 2
				continue
			start = self.subshapes[ss].firstObject
			end = start + self.subshapes[ss].numObjects
			for j in range(start, end):
				object = self.objects[j]
				if od < object.numMeshes:
					mesh = self.meshes[object.firstMesh+od]
					count += mesh.getPolyCount()
			self.detaillevels[i].polyCount = count
			
		#Init the collision accelerator array << Probably don't need this for what we're doing!!
		# for dca in range(0, len(self.detailCollisionAccelerators):
		#	print "BOO"
		
		# Here we calculate a merge buffer size... probably don't need this anyway
		mMergeBufferSize = 0
		for i in range(0, len(self.meshes)):
			object = self.objects[i]
			maxSize = 0
			for dl in range(0, object.numMeshes):
				mesh = self.meshes[object.firstMesh + dl]
				maxSize = getMax(maxSize, len(mesh.mindices)) # mindices = MERGE indices?
			mMergeBufferSize += maxSize
		
		self.initMaterialList()
		# Now that was exciting
	
	def initMaterialList(self):
		# loops through subshapes finding translucent objects...
		pass

	# Following functions for DSQ Support
	def writeDSQSequence(self, fs, sequence):
		fs.write(struct.pack('<i', 24)) # S32, version 24 currently

		nodes_used = sequence.getNodes()
		node_rots = sequence.countNodes(0)
		node_locs = sequence.countNodes(1)
		node_scales = sequence.countNodes(2)
		
		new_rot_matters = []
		new_loc_matters = []
		new_scale_matters = []
		
		# Write node names
		# -- this is how we will map imported sequence nodes to shape nodes
		# Do not write node names not affected by animation
		fs.write(struct.pack('<i', len(nodes_used)))
		cur_writ = 0
		for n in nodes_used:
			# Write the node, since its a part of the sequence
			if self.nodes[n].name != -1:
				fs.write(struct.pack('<i', len(self.sTable.strings[self.nodes[n].name])))
				self.sTable.strings[self.nodes[n].name].tofile(fs)
			else:
				fs.write(struct.pack('<i', 0)) # No length, -1 index!
				# Warning : do not name more than 1 node -1 index!
			
			# Add to the new matters list
			new_rot_matters.append(sequence.matters_rotation[n])
			new_loc_matters.append(sequence.matters_translation[n])
			new_scale_matters.append(sequence.matters_scale[n])
			cur_writ  += 1
		
		if len(nodes_used) != sequence.countNodes():
			# This should never happen
			print "Warning : node list size mismatch! Expecting %d nodes, but got %d. Sequence may not load." % (sequence.countNodes(),len(nodes_used))
		
		sequence.matters_rotation = new_rot_matters
		sequence.matters_translation = new_loc_matters
		sequence.matters_scale = new_scale_matters

		# legacy write -- write zero objects, don't pretend to support object export anymore
		fs.write(struct.pack('<i', 1337)) # S32

		# On import, we will need to adjust keyframe data based on number of
		# nodes/objects in this shape...number of nodes can be inferred from
		# above, but number of objects cannot be. Write that quantity here:
		fs.write(struct.pack('<i', len(self.objects))) # S32
		
		# Calculate bases
		# (All need to start from 0)
		if sequence.baseRotation < 0: baseRotation = 0
		else: baseRotation = sequence.baseRotation
		
		if sequence.baseTranslation < 0: baseTranslation = 0
		else: baseTranslation = sequence.baseTranslation
		
		if sequence.baseScale < 0: baseScale = 0
		else: baseScale = sequence.baseScale
		
		if sequence.firstGroundFrame < 0: baseGround = 0
		else: baseGround = sequence.firstGroundFrame
		
		baseTrigger = sequence.firstTrigger
		
		# Write node states -- skip default node states
		fs.write(struct.pack('<i', node_rots*sequence.numKeyFrames)) # S32
		for n in self.nodeRotations[baseRotation:baseRotation+(node_rots*sequence.numKeyFrames)]:
			q16 = n.toQuat16() # << Remember its Quat16's!
			# Check if we are out of bounds
			if q16.x > 32767: q16.x = 32767
			elif q16.x < -32768: q16.x = -32768
			elif q16.y > 32767: q16.y = 32767
			elif q16.y < -32768: q16.y = -32768
			elif q16.z > 32767: q16.z = 32767
			elif q16.z < -32768: q16.z = -32768
			elif q16.w > 32767: q16.w = 32767
			elif q16.w < -32768: q16.w = -32768
			fs.write(struct.pack('<h', q16[0])) # F32 x
			fs.write(struct.pack('<h', q16[1])) # F32 y
			fs.write(struct.pack('<h', q16[2])) # F32 z
			fs.write(struct.pack('<h', q16[3])) # F32 w
		
		fs.write(struct.pack('<i', node_locs*sequence.numKeyFrames)) # S32
		for n in self.nodeTranslations[baseTranslation:baseTranslation+(node_locs*sequence.numKeyFrames)]:
			fs.write(struct.pack('<f', n[0])) # F32 x
			fs.write(struct.pack('<f', n[1])) # F32 y
			fs.write(struct.pack('<f', n[2])) # F32 z

		if sequence.flags & Sequence.UniformScale:
			fs.write(struct.pack('<i', node_scales*sequence.numKeyFrames)) # S32
			for n in self.nodeUniformScales[baseScale:baseScale+(node_scales*sequence.numKeyFrames)]:
				fs.write(struct.pack('<f', self.nodeUniformScales))
		else: fs.write(struct.pack('<i',0))
		
		if sequence.flags & Sequence.AlignedScale:
			fs.write(struct.pack('<i', node_scales*sequence.numKeyFrames)) # S32
			for n in self.nodeAlignedScales[baseScale:baseScale+(node_scales*sequence.numKeyFrames)]:
				fs.write(struct.pack('<f', n[0])) # X
				fs.write(struct.pack('<f', n[1])) # Y
				fs.write(struct.pack('<f', n[2])) # Z
		else: fs.write(struct.pack('<i',0))
		
		if sequence.flags & Sequence.ArbitraryScale:
			fs.write(struct.pack('<i', node_scales*sequence.numKeyFrames)) # S32
			for n in self.nodeAbitraryScaleRots[baseScale:baseScale+(node_scales*sequence.numKeyFrames)]:
				q16 = Quat16(n)
				fs.write(struct.pack('<h', q16[0])) # X
				fs.write(struct.pack('<h', q16[1])) # Y
				fs.write(struct.pack('<h', q16[2])) # Z
				fs.write(struct.pack('<h', q16[3])) # W
			for n in self.nodeAbitraryScaleFactors[baseScale:baseScale+(node_scales*sequence.numKeyFrames)]:
				fs.write(struct.pack('<f', n[0])) # X
				fs.write(struct.pack('<f', n[1])) # Y
				fs.write(struct.pack('<f', n[2])) # Z
		else: fs.write(struct.pack('<i',0))
		
		fs.write(struct.pack('<i', sequence.numGroundFrames)) # S32
		for n in self.groundTranslations[baseGround:baseGround+sequence.numGroundFrames]:
			fs.write(struct.pack('<f', n[0])) # X
			fs.write(struct.pack('<f', n[1])) # Y
			fs.write(struct.pack('<f', n[2])) # Z
		for n in self.groundRotations[baseGround:baseGround+sequence.numGroundFrames]:
			q16 = Quat16(n)
			fs.write(struct.pack('<h', q16[0])) # X
			fs.write(struct.pack('<h', q16[1])) # Y
			fs.write(struct.pack('<h', q16[2])) # Z
			fs.write(struct.pack('<h', q16[3])) # W

		# write object states -- legacy..no object states
		fs.write(struct.pack('<i', 0))
		
		# Also set the bases accordingly
		if sequence.baseRotation > 0: sequence.baseRotation = 0
		if sequence.baseTranslation > 0: sequence.baseTranslation = 0
		if sequence.baseScale > 0: sequence.baseScale = 0
		if sequence.firstGroundFrame > 0: sequence.firstGroundFrame = 0
		if sequence.firstTrigger > 0: sequence.firstTrigger = 0
		
		# Write Sequence
		fs.write(struct.pack('<i', 1))

		if sequence.nameIndex != -1:
			fs.write(struct.pack('<i', len(self.sTable.strings[sequence.nameIndex])))
			self.sTable.strings[sequence.nameIndex].tofile(fs)
		else:
			fs.write(0x00)

		# Now write the sequence itself
		sequence.write(fs, True)

		# write out all the triggers...
		if baseTrigger > -1:
			fs.write(struct.pack('<i', sequence.numTriggers))
			for t in self.triggers[baseTrigger:baseTrigger+sequence.numTriggers]:
				fs.write(struct.pack('<I', t.state))	# U32
				fs.write(struct.pack('<f', t.pos))	# F32
		else:
			fs.write(struct.pack('<i', 0)) # S32

	def readDSQSequences(self):
		print "TODO: Shape.readDSQSequences"
		# We do not need to implement this for the exporter
