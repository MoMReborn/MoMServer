'''
Dts_Mesh.py

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
from Dts_Stream import *
from Torque_Util import *
import Dts_Stripper
import Dts_Decimate
import math
import copy

#############################
# Torque Game Engine
# -------------------------------
# Dts Mesh Class(es) for Python
#############################

'''
- Reads and Writes DTS Meshes
'''

# The Primitive Class
class Primitive:
	# types
	Triangles    = 0x00000000
	Strip        = 0x40000000
	Fan          = 0x80000000	# may not be supported in the engine?
	TypeMask     = 0xC0000000
	Indexed      = 0x20000000	# All primitives must be indexed
	NoMaterial   = 0x10000000	# Set if face has no material assigned, else things may screw up
	MaterialMask = 0x0FFFFFFF
	def __init__(self, fe=0, ne=0, ty=0):
		self.firstElement = fe	# First indicie used by primitive
		self.numElements = ne	# Number of elements in primitive (> 3 usually is a STRIP / FAN)
		self.matindex = ty		# |'d Value of types + index of material used

# The Cluster Class for clustered meshes
class Cluster:
	def __init__(self, sp=0, ep=0, nrm=None, kn=0.0, fc=0, bc=0):
		self.startPrimitive = sp# Start primitive index
		self.endPrimitive = ep	# End primitive index
		self.normal = nrm			# Normal of cluster
		self.k = kn					# The "D" in the plane equation
		self.frontCluster = fc	# Front cluster index
		self.backCluster = bc	# Back cluster index

# The Main Mesh Class
class DtsMesh:
	# Class Constants
	smUseEncodedNormals = False	# Read in encoded normals for standard meshes. We just ignore this
	smUseTriangles = False
	smUseOneStrip = False
	smMaxStripSize = 7

	# Mesh types
	T_Standard  = 0			# Standard meshes can be moved by bones, but not be deformed by them
	T_Skin         = 1		# Skin meshes can be deformed by bones
	T_Decal       = 2		# Decal meshes are a bit obsolete. They were used to plonk bullet holes, etc on shapes
	T_Sorted      = 3		# Sorted meshes are extended Standard meshes which allow transparent surfaces to be drawn correctly
	T_Null          = 4		# No mesh. Purpose of this is unknown.
	
	# Mesh Flags
	Billboard = 0x80000000		# Mesh always faces player
	HasDetail = 0x40000000		# Mesh has other versions in other detail levels
	BillboardZ = 0x20000000		# Mesh always faces player on the Z axis (up)
	EncodedNormals = 0x10000000	# Mesh has encoded normals

	def __init__(self, t=4):
		self.radius = float(0.0)	# Radius of mesh
		self.numFrames = 1		# Number of frames in mesh
		self.matFrames = 1		# Number of IFL material frames in mesh
		self.vertsPerFrame = 0		# Vertexes per frame (vertex animation)
		self.parent = -1		# Parent mesh (used to share data)
		self.flags = 0			# Mesh Flags
		self.mtype = t			# Type of mesh
		self.alwaysWriteDepth = False	# Always write depth?
		
		self.verts = []			# Vertexes
		self.tverts = []		# Texture verts
		self.normals = []		# Normals
		self.enormals = array('B')	# Encoded normals
		self.primitives = []		# Primitives (makes faces from indices)
		self.indices = array('H')	# Indices for primitives
		self.mindices = array('H')	# Indices for primitives
		self.vindex = array('i')	# Vertex indexes for bone influences
		self.bindex = array('i')	# Bone indexes for influences
		self.vweight = array('f')	# Vertex weights
		self.nodeIndex = array('i')	# Node indexes for node transforms (skin mesh)
		self.nodeTransforms = []	# Node transforms
		self.texgenS = []		# TexGen (U)  (decals)
		self.texgenT = [] 		# TexGen (V)  (decals)
		self.materialIndex = 0		# Material index (decals)
		self.clusters = []		# Clusters (bsp for sorted meshes)
		self.startCluster = array('i')	# Starting cluster
		self.startPrimitive = []	# Start primitive in cluster
		self.firstVerts = array('i')	# First vert index of cluster
		self.numVerts = array('i')	# Number of verts in cluster
		self.firstTVerts = array('i')	# First texture verts in cluster
		self.bounds = Box()		# Bounds of shape
		self.center = Vector()		# Center of shape
	
	def __del__(self):
		del self.verts
		del self.tverts
		del self.normals
		del self.enormals
		del self.primitives
		del self.indices
		del self.mindices
		del self.vindex
		del self.bindex
		del self.vweight
		del self.nodeIndex
		del self.nodeTransforms
		del self.texgenS
		del self.texgenT
		del self.clusters
		del self.startCluster
		del self.startPrimitive
		del self.firstVerts
		del self.numVerts
		del self.firstTVerts
		del self.bounds
		del self.center
		
	def getType(self):
		return self.mtype
	
	def setType(self, t):
		self.mtype = t
	
	def setFlag(self, f):
		self.flags |= f
	
	def getPolyCount(self):
		count = 0
		for p in range(len(self.primitives)):
			if (self.primitives[p].matindex & Primitive().Strip):
				count += self.primitives[p].numElements - 2
			else:
				count += self.primitives[p].numElements / 3
		return(count)
	
	def getRadius(self):
		return(self.radius)
	
	def getRadiusFrom(self, trans, rot, center):
		radius = float(0.0)

		for vert in self.verts:
			tv = rot.apply(vert) + trans
			distance = (tv - center).length()
			if distance > radius:
				radius = distance
		return radius
	
	def getTubeRadiusFrom(self, trans, rot, center):
		radius = float(0.0)

		for vert in self.verts:
			tv = rot.apply(vert) + trans
			distance = (tv - center)
			distance2 = Vector2(distance[0], distance[1]).length() 
			if distance2 > radius:
				radius = distance2
		return radius
	
	def getCenter(self):
		return(self.center)
	
	def getBounds(self, trans, rot):
		# Compute the bounding box using the given transform
		bounds2 = Box()
		bounds2.max = Vector(-10e30, -10e30, -10e30)
		bounds2.min = Vector(10e30, 10e30, 10e30)

		for vert in self.verts:
			tv = rot.apply(vert) + trans
			if tv[0] < bounds2.min[0]:
				bounds2.min[0] = tv[0]
			if tv[1] < bounds2.min[1]:
				bounds2.min[1] = tv[1]
			if tv[2] < bounds2.min[2]:
				bounds2.min[2] = tv[2]
			if tv[0] > bounds2.max[0]:
				bounds2.max[0] = tv[0]
			if tv[1] > bounds2.max[1]:
				bounds2.max[1] = tv[1]
			if tv[2] > bounds2.max[2]:
				bounds2.max[2] = tv[2]
		return(bounds2)
	
	def setMaterial(self, n):
		for p in self.primitives:
			p.matindex = (p.matindex & ~Primitive().MaterialMask) | (n & Primitive().MaterialMask)
	
	def getNodeIndexCount(self):
		return(len(self.nodeIndex))
	
	def getNodeIndex(self, node):
		if (node >= 0) and (node < len(self.nodeIndex)):
				return self.nodeIndex[node]
		return None
	
	def setNodeTransform(self, node, t, q):
		# Build inverse transform, the mesh wants to be able to
		# transform the vertices into node space.
		t = q.inverse().apply(-t)
		row = []
		row.append(t.x())
		row.append(t.y())
		row.append(t.z())
		row.append(1)
		
		# point * translation * transform (+ a bit of weights) = position
		# The toMatrix builds a transposed transform from what we
		# want, so we need to pass the original quaternion to get
		# the inverse.
		self.nodeTransforms[node] = q.toMatrix()
		self.nodeTransforms[node].setCol(3,row)
	
	def translate(self, tra):
		for v in range(0,len(self.verts)):
			self.verts[v] += tra
		self.calculateBounds()
		self.calculateCenter()
		self.calculateRadius()
	
	def rotate(self, rot):
		for v in range(0,len(self.verts)):
			self.verts[v] = rot.apply(self.verts[v])
		self.calculateBounds()
		self.calculateCenter()
		self.calculateRadius()
	
	def setCenter(self, c):
		self.center = c
	
	def setBounds(self, b):
		self.bounds = b
	
	def setRadius(self, r):
		self.radius = r
	
	def setFrames(self, n):
		self.numFrames = n
		self.vertsPerFrame = len(self.verts)/n
	
	def setParent(self, n):
		self.parent = n
	
	def calculateBounds(self):
		self.bounds.max = Vector(-10e30, -10e30, -10e30)
		self.bounds.min = Vector(10e30, 10e30, 10e30)

		for vertex in self.verts:
			if vertex[0] < self.bounds.min[0]:
				self.bounds.min[0] = vertex[0]
			if vertex[1] < self.bounds.min[1]:
				self.bounds.min[1] = vertex[1]
			if vertex[2] < self.bounds.min[2]:
				self.bounds.min[2] = vertex[2]
			if vertex[0] > self.bounds.max[0]:
				self.bounds.max[0] = vertex[0]
			if vertex[1] > self.bounds.max[1]:
				self.bounds.max[1] = vertex[1]
			if vertex[2] > self.bounds.max[2]:
				self.bounds.max[2] = vertex[2]
	
	def calculateCenter(self):
		for v in range(len(self.bounds.max.members)):
			self.center[v] = ((self.bounds.min.members[v] - self.bounds.max.members[v])/2) + self.bounds.max.members[v]
	
	def calculateRadius(self):
		self.radius = float(0.0)
			
		for vertex in self.verts:
			tV = vertex - self.center
			result = 0
			for n in range(len(tV.members)):
				result += tV.members[n] * tV.members[n]
			distance = math.sqrt(result)
			if distance > self.radius:
				self.radius = distance
	
	def getVertexBone(self, node):
		# Finds the bone index in the table, or adds it if it's
		# not there.  The vertex bone & nodeIndex list are here to
		# track which bones are used by this mesh.
		b = 0
		while b < len(self.nodeIndex):
			if self.nodeIndex[b] == node:
				return b
			b += 1
		self.nodeIndex.append(node)
		self.nodeTransforms.append(MatrixF().identity())
		return b
	
	def encodeNormal(self, p):
		return 0 # disable
		global normalTable
		bestIndex = 0
		x, y, z = p
		bestDot = -10E30
		for i in range(0,256):
			dot = x * normalTable[i][0] + y * normalTable[i][1] + z * normalTable[i][2]
			if dot > bestDot:
				bestIndex = i
				bestDot = dot
		return bestIndex
	
	def read(self, dstream, shape):
		# Header and Bounds
		if (self.mtype == self.T_Null) or not (self.T_Standard or self.T_Decal or self.T_Skin or self.T_Sorted):
			return None # Null mesh, no data!
		# Decal Meshes are an exception; They do not use regular mesh assemble!
		if self.mtype != self.T_Decal:
			dstream.readCheck()
			self.numFrames = dstream.reads32() #S32
			self.matFrames = dstream.reads32() #S32
			self.parent    = dstream.reads32() #S32
			self.bounds    = dstream.readBox() #Box
			self.center    = dstream.readPoint3F() #Vector
			self.radius    = dstream.readf32() # Float (32bit)

			# If we have a parent, don't read some of this stuff in

			# Vertexes
			# (Should be 0 if skin mesh)
			if self.parent < 0:
				for cnt in range(0, dstream.reads32()):
					self.verts.append(dstream.readPoint3F())
			else:
				dstream.reads32()
				self.verts = shape.meshes[self.parent].verts

			# Texture Coordinates
			if self.parent < 0:
				for cnt in range(0, dstream.reads32()):
					self.tverts.append(dstream.readPoint2F())
			else:
				dstream.reads32()
				self.tverts = shape.meshes[self.parent].tverts

			# Normals
			# Real in normals and enormals regardless of if we have them or not
			if self.parent < 0:
				for cnt in range(0, len(self.verts)):
					self.normals.append(dstream.readPoint3F())
				for cnt in range(0, len(self.verts)):
					dstream.readu8() # dummy read of enormals
			else:
				self.normals = shape.meshes[self.parent].normals
				self.enormals = shape.meshes[self.parent].enormals

			# Primitives and other stuff
			for cnt in range(0, dstream.reads32()):
				self.primitives.append(dstream.readPrimitive())
			for cnt in range(0, dstream.reads32()):
				self.indices.append(dstream.readu16()) # U16
			for cnt in range(0, dstream.reads32()):
				self.mindices.append(dstream.readu16()) # U16
			self.vertsPerFrame = dstream.reads32()
			self.flags = dstream.readu32()

			dstream.readCheck()

			# Woohoo!! Done Reading Mesh Bit...
			self.calculateBounds()
			# End Standard Mesh Read
		# Now for other mesh types
		if self.mtype == self.T_Skin:
			# Skin Mesh

			# If we have a parent, don't read some of this stuff in

			if self.parent < 0:
				# Read Initial Verts... (plonked into verts array really)
				for cnt in range(0, dstream.reads32()):
					self.verts.append(dstream.readPoint3F())
			else:
				dstream.reads32()
				# Following already done before!
				#self.verts = shape.meshes[self.parent].verts

			# Normals...
			# (note : encoded normals not read)
			if self.parent <0:
				# Advance past norms.don't use
				for u in self.verts:
					dstream.read8()# Skip

				# Read in normals
				for n in self.verts:
					self.normals.append(dstream.readPoint3F())
			else:
				self.normals, self.enormals = shape.meshes[self.parent].normals, shape.meshes[self.parent].enormals

			if self.parent < 0:
				# Read Initial Transforms...
				for cnt in range(0, dstream.reads32()):
					self.nodeTransforms.append(dstream.readMatrixF())

				sz = dstream.reads32()
				# Read Vertex Indexes...
				for cnt in range(0, sz):
					self.vindex.append(dstream.reads32())

				# Read Bone Indexes...
				for cnt in range(0, sz):
					self.bindex.append(dstream.reads32())

				# Read Vertex Weights...
				for cnt in range(0, sz):
					self.vweight.append(dstream.readf32())

				# Read Node Indexes...
				for cnt in range(0, dstream.reads32()):
					self.nodeIndex.append(dstream.reads32())
			else:
				for i in range(0, 3):
					dstream.reads32() # read in sizes
				self.nodeTransforms = shape.meshes[self.parent].nodeTransforms
				self.vindex = shape.meshes[self.parent].vindex
				self.bindex = shape.meshes[self.parent].bindex
				self.vweight = shape.meshes[self.parent].vweight
				self.nodeIndex = shape.meshes[self.parent].nodeIndex

			# And finally, checkpoint =)
			dstream.readCheck()
		elif self.mtype == self.T_Decal:
			# Decal Mesh
			# Read Primitives...
			nprims = dstream.reads32()
			for cnt in range(0, nprims):
				self.primitives.append(dstream.readPrimitive())
			# Read Indicies...
			ninds = dstream.reads32()
			for cnt in range(0, ninds):
				self.indices.append(dstream.readu16()) #U16
			nsps = dstream.reads32()
			# Read Start Primitives...
			for cnt in range(0, nsps):
				self.startPrimitive.append(dstream.reads32()) #S32
			# Read in TexGen's
			for cnt in range(0, nsps):
				self.texgenS.append(dstream.readPoint4F())
			for cnt in range(0, nsps):
				self.texgenT.append(dstream.readPoint4F())
			# Material Index
			self.materialIndex = dstream.reads32()
			dstream.readCheck()
		elif self.mtype == self.T_Sorted:
			# Sorted Mesh
			# Read Clusters (e.g helmet visor is cluster)
			sz = dstream.reads32()
			for cnt in range(0, sz):
				self.clusters.append(dstream.readCluster())
			# Read Start Cluster
			sz = dstream.reads32()
			for cnt in range(0, sz):
				self.startCluster.append(dstream.reads32())
			# Read first Verts
			nfv = dstream.reads32()
			for cnt in range(0, sz):
				self.firstVerts.append(dstream.reads32())
			# Read num Verts
			sz = dstream.reads32()
			for cnt in range(0, sz):
				self.numVerts.append(dstream.reads32())
			sz = dstream.reads32()
			for cnt in range(0, sz):
				self.firstTVerts.append(dstream.reads32())
			self.alwaysWriteDepth = dstream.readu32()
			dstream.readCheck()
		else:
			# Null or Standard or Unknown Mesh
			if self.mtype != self.T_Standard:
				print "Error : Cannot read mesh type %d" % (self.mtype)
		return True # We are ok

	# Write!!
	def write(self, dstream):
		if self.mtype == self.T_Null:
			return None
		# Decal Meshes are an exception; They do not use regular mesh assemble!
		if self.mtype == self.T_Decal:
			# Write Primitives...
			dstream.writes32(len(self.primitives))
			for cnt in self.primitives:
				dstream.writePrimitive(cnt)
			# Write Indicies...
			dstream.writes32(len(self.indices))
			for cnt in self.indices:
				dstream.writeu16(cnt) #U16
			# Write Start Primitives...
			dstream.writes32(len(self.startPrimitive))
			for cnt in self.startPrimitive:
				dstream.writes32(cnt) #S32
			# Read in TexGen's
			for cnt in self.texgenS:
				dstream.writePoint4F(cnt)
			for cnt in self.texgenT:
				dstream.writePoint4F(cnt)
			# Material Index
			dstream.writes32(self.materialIndex)
			dstream.storeCheck()
		else:
			# Note : we only need to write
			# some things IF we don't have a parent
			dstream.storeCheck()
			dstream.writes32(self.numFrames) #S32
			dstream.writes32(self.matFrames) #S32
			dstream.writes32(self.parent) #S32
			dstream.writeBox(self.bounds) #Box
			dstream.writePoint3F(self.center) #Vector
			dstream.writef32(self.radius) # Float (32bit)

			# Vertexes
			# Some things should definatly not be written if we are a skin mesh
			# (e.g verts should only be written once in the SkinMesh iverts)
			if self.mtype == self.T_Skin:
				dstream.writes32(0) # 0 verts, but many iverts
			else:
				dstream.writes32(len(self.verts))
				if self.parent < 0:
					for v in self.verts:
						dstream.writePoint3F(v)

			# Texture Coordinates
			dstream.writes32(len(self.tverts))
			if self.parent < 0:
				for v in self.tverts:
					dstream.writePoint2F(v)

			# Normals
			# Write normals and enormals regardless of if we have them or not
			# Forget it if we are a skin mesh. (since stored elsewhere)
			if self.parent < 0:
				if self.mtype != self.T_Skin:
					for n in self.normals:
						dstream.writePoint3F(n)
					for n in self.normals: # enormals dummy write
						dstream.writeu8(0)

			# Primitives and other stuff
			dstream.writes32(len(self.primitives))
			for p in self.primitives:
				dstream.writePrimitive(p)
			dstream.writes32(len(self.indices))
			for p in self.indices:
				dstream.writeu16(p) # U16
			dstream.writes32(len(self.mindices))
			for p in self.mindices:
				dstream.writeu16(p) # U16
			dstream.writes32(self.vertsPerFrame)
			dstream.writeu32(self.flags)

			dstream.storeCheck()

			# Now write Other mesh type data
			if self.mtype == self.T_Skin: 
				dstream.writes32(len(self.verts))

				if self.parent < 0:
					for vert in self.verts:
						dstream.writePoint3F(vert)
					
				# Write normals and encoded normals
				# NOTE: removed encoded normals write
				if self.parent < 0:
					for u in self.normals:
						dstream.write8(0) # Skip enormals
					for n in self.normals:
						dstream.writePoint3F(n)
				
				# Write Initial Transforms...
				dstream.writes32(len(self.nodeTransforms))
				if self.parent < 0:
					for vert in self.nodeTransforms:
						dstream.writeMatrixF(vert)

				# Vertex Indexes...
				dstream.writes32(len(self.vindex))
				if self.parent < 0:
					for vert in self.vindex:
						dstream.writes32(vert)
				
					# Bone Indexes...
					for vert in self.bindex:
						dstream.writes32(vert)

					# Vertex Weights...
					for vert in self.vweight:
						dstream.writef32(vert)
				
				# Node Indexes...
				dstream.writes32(len(self.nodeIndex))
				if self.parent < 0:
					for vert in self.nodeIndex:
						dstream.writes32(vert)
					
				dstream.storeCheck()
			elif self.mtype == self.T_Sorted:
				# Clusters...
				dstream.writes32(len(self.clusters))
				for c in self.clusters:
					dstream.writeCluster(c)
				
				# Start Cluster...
				dstream.writes32(len(self.startCluster))
				for c in self.startCluster:
					dstream.writes32(c)
				
				# First Verts
				dstream.writes32(len(self.firstVerts))
				for c in self.firstVerts:
					dstream.writes32(c)
				
				# Num Verts
				dstream.writes32(len(self.numVerts))
				for c in self.numVerts:
					dstream.writes32(c)
				
				# First Tex Verts
				dstream.writes32(len(self.firstTVerts))
				for c in self.firstTVerts:
					dstream.writes32(c)

				dstream.writeu32(self.alwaysWriteDepth)

				dstream.storeCheck()
	def convertToTris(self, quads=False):
		# Converts stuff to regular triangles primitives
		# NOTE: Face order *seems* to be slightly off
		newinds = array('H')
		newprims = []
		numStrips = 0
		print "Converting Triangle Strip -> Triangles"
		for p in self.primitives:
			if p.matindex & p.Strip:
				if quads and p.numElements == 4:
					# Same as lone triangle, but extra vertex
					newprims.append(Primitive(len(newinds), 4, p.matindex))
					newinds.append(self.indices[p.firstElement])
					newinds.append(self.indices[p.firstElement+1])
					newinds.append(self.indices[p.firstElement+2])
					newinds.append(self.indices[p.firstElement+3])
				elif p.numElements > 3:
					numStrips += 1
					if quads:
						addinds, addprims = self.unwindQuadStrip(p, len(newinds))
					else:
						addinds, addprims = self.unwindStrip(p, len(newinds))
					for inds in addinds: newinds.append(inds)
					for prim in addprims: newprims.append(prim)
					del addinds
					del addprims
				else: # Its a lone triangle
					newprims.append(Primitive(len(newinds), 3, p.matindex))
					newinds.append(self.indices[p.firstElement])
					newinds.append(self.indices[p.firstElement+1])
					newinds.append(self.indices[p.firstElement+2])
			#else TODO: Support Fan, etc
		print "Converted %d strips" % numStrips
		# Finally we have our new primitives
		self.indices, self.primitives = newinds, newprims

	def unwindQuadStrip(self, strip, offset):
		# First, unwind to tris
		newinds, newprims = self.unwindStrip(strip, offset)

		# TODO
		quadinds = newinds
		quadprims = newprims
		
		return quadinds, newprims
		
	def unwindStrip(self, strip, offset):
		# The purpose of this function is to convert a triangle strip, strip into primitives
		newinds = array('H') # New Indices, adds on top of everything else
		newprims = [] # New primitives

		front = True
		# 01234 -> 012 321 234
		ind = strip.firstElement+2
		while ind < (strip.firstElement+strip.numElements):
			newprims.append(Primitive(len(newinds) + offset,3,strip.matindex))
			if front:
				newinds.append(self.indices[ind-2])
				newinds.append(self.indices[ind-1])
				newinds.append(self.indices[ind])
			else:
				newinds.append(self.indices[ind])
				newinds.append(self.indices[ind-1])
				newinds.append(self.indices[ind-2])
			front = not front
			ind += 1

		return newinds, newprims

	'''
	Triangle Strip Code
	'''

	def windStrip(self, max_stripsize):
		Dts_Stripper.Stripper.maxStripSize = max_stripsize
		stripper = Dts_Stripper.chooseStripper()
		if not stripper: 
			print "     Stripping Mesh : Disabled (No Stripper Found)"
			return
		else:
			print "     Stripping Mesh : ..."
		stripper.verts = self.verts

		# Convert primitives in different batches if we are a cluster, else, do it normally
		if self.mtype == self.T_Sorted:
			newPrimitives = []
			newIndices = []
			for c in self.clusters:
				# We need to update offsets for primitives when we strip (since there will be less of them)
				c.startPrimitive = len(newPrimitives)
				for p in self.primitives[c.startPrimitive:c.endPrimitive]:
					stripper.faces.append([self.indices[p.firstElement:p.firstElement+p.numElements], p.matindex])
				# Ready, Steady, Strip!
				stripper.strip()
				for strip in stripper.strips:
					self.primitives.append(Primitive(len(newIndices),len(strip[0]),strip[1]))
					for ind in strip[0]:
						newIndices.append(ind)
				c.endPrimitive = len(newPrimitives)
				stripper.clear()
			self.indices = newIndices
			self.primitives = newPrimitives
		else:
			# All we need to do is convert the whole set of primitives
			for p in self.primitives:
				stripper.faces.append([self.indices[p.firstElement:p.firstElement+p.numElements], p.matindex])
			stripper.strip()
			
			self.indices = []
			self.primitives = []
			for strip in stripper.strips:
				self.primitives.append(Primitive(len(self.indices),len(strip[0]),strip[1]))
				#print "STRIP:",strip[0]
				for ind in strip[0]:
					self.indices.append(ind)
		del stripper

	def passMatrix(self, matrix):
		# Applies a matrix to all the verts in the mesh
		for v in self.verts:
			v = matrix.passPoint(v)
	
	'''
	Decimation code
	'''
	# Makes primitives less
	def collapsePrims(self, target=0.5):
		# If we do not have VTK, we cannot use this code
		
		if self.mtype == self.T_Sorted:
			print "     Decimate : Disabled (Sorted Mesh)"
			return

		decimate = Dts_Decimate.chooseDecimator()
		if not decimate:
			print "     Decimate : Disabled (Not Decimator found)"
			return
		else:
			print "     Decimate : ..."
		
		# All we need to do is convert the whole set of primitives
		for p in self.primitives:
			decimate.faces.append([self.indices[p.firstElement:p.firstElement+p.numElements], p.matindex])
		
		decimate.process(target)
		
		self.indices = []
		self.primitives = []
		for face in decimate.faces:
			self.primitives.append(Primitive(len(self.indices),len(face[0]),face[1]))
			for ind in face[0]:
				self.indices.append(ind)
				
		del decimate
		
	# Duplicates mesh
	def duplicate(self):
		# Arrays and class objects are the major concern
		d = DtsMesh()
		d.mtype = self.mtype
		d.numFrames = self.numFrames
		d.matFrames = self.matFrames
		d.parent = self.parent

		for v in self.verts:
			d.verts.append(Vector(v[0], v[1], v[2]))
		for t in self.tverts:
			d.tverts.append(Vector2(t[0], t[1]))
		for n in self.normals:
			d.normals.append(Vector(n[0], n[1], n[2]))
		for e in self.enormals:
			d.enormals.append(e)
		for p in self.primitives:
			d.primitives.append(Primitive(p.firstElement,p.numElements, p.matindex))
		for i in self.indices:
			d.indices.append(i)
		for m in self.mindices:
			d.mindices.append(m)

		d.bounds = Box(Vector(self.bounds.min[0],self.bounds.min[1],self.bounds.min[2]),
                               Vector(self.bounds.max[0],self.bounds.max[1],self.bounds.max[2]))
		d.center = Vector(self.center[0], self.center[1], self.center[2])
		d.radius = self.radius
		d.vertsPerFrame = self.vertsPerFrame
		d.flags = self.flags

		for i in self.vindex:
			d.vindex.append(i)
		for b in self.bindex:
			d.bindex.append(b)
		for v in self.vweight:
			d.vweight.append(v)
		for n in self.nodeIndex:
			d.nodeIndex.append(n)
		for n in self.nodeTransforms:
			d.nodeTransforms.append(MatrixF(copy.deepcopy(n.members)))

		for p in self.startPrimitive:
			d.startPrimitive.append(p)
		for ts in self.texgenS:
			d.texgenS.append(Vector4(ts[0], ts[1], ts[2], ts[3]))
		for tt in self.texgenT:
			d.texgenT.append(Vector4(tt[0], tt[1], tt[2], tt[3]))
		d.materialIndex = self.materialIndex

		for c in self.clusters:
			d.clusters.append(Cluster(c.startPrimitive, c.endPrimitive, c.normal, c.k, c.frontCluster, c.backCluster))
		for c in self.startCluster:
			d.startCluster.append(c)
		for v in self.firstVerts:
			d.firstVerts.append(v)
		for v in self.numVerts:
			d.numVerts.append(v)
		for t in self.firstTVerts:
			d.firstTVerts.append(t)

		return d

	'''
	Sorted Mesh Routines
	'''

	def generateClusters(self, numBigFaces, maxDepth, zLayerUp, zLayerDown):
		'''
			on entry, mesh is organized like a standard mesh...
			numFrames, numMatFrames, & vertsPerFrame describe what
			is held in verts, norms, and tverts arrays
			primitives and indices vectors describe the faces (same
			faces on each frame/matFrame)
			
			we want to convert this over to the structure that will be
			used by TSSortedMesh...we also want to sort the faces, of course...
		'''
		
		meshFaces = []
		meshIndices = []
		meshVerts = []
		meshNorms = []
		meshTVerts = []
		meshClusters = []
		
		for i in range(0,self.numFrames):
			for j in range(0, self.matFrames):
				faces = self.primitives
				indices = self.indices
				clusters = []
				verts = copy.deepcopy(self.verts)
				norms = copy.deepcopy(self.normals)
				tverts = copy.deepcopy(self.tverts)
				
				sort = Dts_TranslucentSort.TranslucentSort(faces,indices,verts,norms,tverts,numBigFaces,maxDepth,zLayerUp,zLayerDown)
				sort.sort()
				newFaces = []
				newIndices = []
				sort.generateClusters(clusters,newFaces,newIndices)
				
				k = 0
				while k < len(clusters):
					if (clusters[k].startPrimitive==clusters[k].endPrimitive and clusters[k].frontCluster==clusters[k].backCluster):
						# this cluster serves no purpose...get rid of it
						for l in range(0, len(clusters)):
							if l==k:
								continue
							if clusters[l].frontCluster == k:
								clusters[l].frontCluster = clusters[k].frontCluster
							if clusters[l].frontCluster > k:
								clusters[l].frontCluster -= 1
							if clusters[l].backCluster == k:
								clusters[l].backCluster = clusters[k].backCluster
							if clusters[l].backCluster > k:
								clusters[l].backCluster -= 1
						
						del clusters[k]
						k = -1 # start over, our parent may now be useless...
					k += 1
				
				if j==0:
					self.startCluster.append(len(meshClusters))
					self.firstVerts.append(len(meshVerts))
					self.numVerts.append(len(verts))
				
				# TODO: if tverts same as some previous frame, use that frame number
				# o.w.
				self.firstTVerts.append(len(meshTVerts))
	
				# adjust startPrimitive, endPrimitive, frontCluster, & backCluster on list of clusters just generated
				for k in range(0, len(clusters)):
					cluster = clusters[k]
					cluster.startPrimitive += len(meshFaces)
					cluster.endPrimitive += len(meshFaces)
					cluster.frontCluster += len(meshClusters)
					cluster.backCluster += len(meshClusters)
				
				# now merge in just computed verts, tverts, indices, primitives, and clusters...
				meshVerts += verts
				if self.firstTVerts[-1] == len(meshTVerts):
					meshTVerts += tverts
				meshNorms += norms
				meshIndices += newIndices
				meshFaces += newFaces
				meshClusters += clusters 
		
		self.clusters = meshClusters
		self.primitives = meshFaces
		self.indices = meshIndices
		self.verts = meshVerts
		self.normals = meshNorms
		self.tverts = meshTVerts

	def sortMesh(self, alwaysWriteDepth=False, maxDepth=2, numBigFaces=0, zLayerUp=True, zLayerDown=True):
		'''
		All we need to do is turn control over to generateClusters.
		generateClusters() will construct the BSP tree, and roll any
		new primitives / clusters / vertexes into the mesh data
		'''
		self.alwaysWriteDepth = alwaysWriteDepth
		print "      Sorting : WD(%d) NB(%d) MD(%d) ZU(%d), ZD(%d)" % (alwaysWriteDepth, numBigFaces, maxDepth, zLayerUp, zLayerDown)
		self.generateClusters(numBigFaces, maxDepth, zLayerUp, zLayerDown)
		print "      Sorting : Done, Generated %d clusters" % len(self.clusters)


import Dts_TranslucentSort
# End of file
