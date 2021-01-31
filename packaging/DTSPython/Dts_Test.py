'''
Dts_Test.py

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
from Dts_Stream import *
from Dts_Mesh import *
from Dts_Shape import *

import string
import sys

#############################
# Torque Game Engine
# -------------------------------
# Test for Dts Classes for Python
#############################

# NOTE : Test 4 is slightly ok but doesn't like lots of meshes (skipping probably not right?)
# Uncomment the tests below if you wish to test the shape reading / writing

# Filenames for tests
file1 = "tree2.dts"
file2 = "treeclone.dts"
file3 = "anotherfile.dts"

def test1():
	# Test 1. Ok
	print "Test 1. Basic Stream i/o"
	print "================="
	Stream = DtsStream("stream_test")
	# Write some stuff...
	
	Stream.writeu8(72) #H
	Stream.writeu8(73) #I
	Stream.storeCheck()
	Stream.writes32(2000)
	Stream.writeu32(1000)
	Stream.storeCheck()
	Stream.writes16(657)
	Stream.writeu16(666)
	Stream.storeCheck()
	Stream.storeCheck()
	Stream.flush()
	print "Buffers : "
	print Stream.buffer8
	print Stream.buffer16
	print Stream.buffer32
	print "==========="
	del Stream

	Stream = DtsStream("stream_test", 1)
	print "Buffers : "
	print Stream.buffer8
	print Stream.buffer16
	print Stream.buffer32
	print "==========="
	# Now Read it back in
	print "Byte : ", str(Stream.readu8())
	print "Byte : ", str(Stream.readu8())
	Stream.readCheck()
	print "Int : ", Stream.reads32()
	print "Int : ", Stream.readu32()
	Stream.readCheck()
	print "Short : ", Stream.reads16()
	print "Short : ", Stream.readu16()
	Stream.readCheck()
	Stream.readCheck()
	del Stream

	print "Test Finished."
	print "=============="

def test2():
	# Test 2. Ok
	print "Test 2. Writing Semi Interesting data"
	print "================="
	Stream = DtsStream("stream_test")
	# Write some stuff...
	
	Stream.writeStringt("Hello There")
	Stream.storeCheck()
	Stream.writeStringt("And another hello here")
	Stream.storeCheck()
	Stream.storeCheck()
	Stream.storeCheck()
	Stream.writeu32(888)
	Stream.writes32(-888)
	Stream.writeu32(-888)
	Stream.storeCheck()
	Stream.storeCheck()
	Stream.flush()
	del Stream

	Stream = DtsStream("stream_test", 1)
	strn = Stream.readStringt()
	print strn
	Stream.readCheck()
	strn = Stream.readStringt()
	print strn
	Stream.readCheck()
	Stream.readCheck()
	Stream.readCheck()
	print "Int's : %d %d %d" % (Stream.readu32(), Stream.reads32(), Stream.readu32())
	Stream.readCheck()
	Stream.readCheck()
	del Stream

	print "Test Finished."
	print "=============="

def test3():
	# Test 3. Ok
	print "Test 3. Writing floats"
	print "================="
	Stream = DtsStream("stream_test")
	# Write some stuff...
	Stream.storeCheck()
	Stream.storeCheck()
	Stream.storeCheck()
	Stream.storeCheck()
	Stream.writef32(34.67)
	Stream.writef32(99.45)
	Stream.storeCheck()
	Stream.writef32(-22.86)
	Stream.writef32(0.00)
	Stream.storeCheck()
	Stream.writef32(1.34)
	Stream.storeCheck()
	Stream.storeCheck()
	Stream.flush()
	del Stream

	Stream = DtsStream("stream_test", 1)
	Stream.readCheck()
	Stream.readCheck()
	Stream.readCheck()
	Stream.readCheck()
	print Stream.readf32(), "(34.67)"
	print Stream.readf32(), "(99.45)"
	Stream.readCheck()
	print Stream.readf32(), "(-22.86)"
	print Stream.readf32(), "(0.00)"
	Stream.readCheck()
	print Stream.readf32(), "(-1.34)"
	Stream.readCheck()
	Stream.readCheck()
	del Stream

	print "Test Finished."
	print "=============="
	
def test4():
	# Test 4. Should be ok
	print "Test 4. Shape Reading"
	print "====================="
	# Create the stream
	global file1
	Stream = DtsStream(file1,1)
	if Stream.fs != None:
		# Create the shape
		Shape = DtsShape()
		# Read from the stream
		Shape.read(Stream)
		Shape.printInfo()

		print "Default Node Stuff (%d nodes) : " % (len(Shape.nodes))

		print "node Transforms on each mesh : "

		for m in Shape.meshes:
			print "--mesh"
			for n in m.nodeTransforms:
				print "Transform : "
				for x in range(0, 4):
					for y in range(0, 4):
						print "%f," % (n.get(x, y)),
					print " "
				print "**"
			print "--"
		for m in Shape.meshes:
			triStrips = 0
			if triStrips == 1:
				break
			for m in m.primitives:
				if m.numElements > 3:
					print "Shape Contains Triangle Strips"
					triStrips = 1
					break			
		for n in range(0, len(Shape.nodes)):
			tra = Shape.defaultTranslations[n]
			rot = Shape.defaultRotations[n]
			print "Node Default Translation : %f %f %f" % (tra[0], tra[1], tra[2])
			print "Node Default Quaternion  : %f %f %f %f"  % (rot[0], rot[1], rot[2], rot[3])
	
		# Finish
		del Stream
	else:
		print "Error! Stream failed to load!"
		del Stream

	print "Test Finished."
	print "=============="

def printBuffer(buf, fs):
	col = 0
	for b in buf:
		if col != 15:
			fs.write("%s," % (b))
			col += 1
		else:
			fs.write("\n")
			fs.write("%s" % (b))
			col = 0
def dump_Buffers(dstream, fname):
	dump = open("%s_8"  % (fname), "w")
	printBuffer(dstream.buffer8, dump)
	dump.close()
	dump = open("%s_16"  % (fname), "w")
	printBuffer(dstream.buffer16, dump)
	dump.close()
	dump = open("%s_32" % (fname), "w")
	printBuffer(dstream.buffer32, dump)
	dump.close()

def test5():
	# Test 5. Should produce nearly identical, or even better identical files.
	print "Test 5. Identical Test Reading and Saving"
	print "====================="
	# Create the stream
	global file1
	global file2
	Stream = DtsStream(file1,1)
	OtherStream = DtsStream(file2)
	if Stream.fs != None:
		
		print "Loading shape..."
		# Create the shape
		Shape = DtsShape()
		# Read from the stream
		Shape.read(Stream)
		Shape.write(OtherStream)
		Shape.printInfo()
		for n in range(0, len(Shape.nodes)):
			tra = Shape.defaultTranslations[n]
			rot = Shape.defaultRotations[n]
			print "Node Default Translation : %f %f %f" % (tra[0], tra[1], tra[2])
			print "Node Default Quaternion  : %f %f %f %f"  % (rot[0], rot[1], rot[2], rot[3])
		print "Shape Saved, reading back in..."
		del Shape
		del Stream
		del OtherStream
		
		Stream = DtsStream(file1,1)
		Other_Shape = DtsShape()
		Other_Shape.read(Stream)
		Other_Shape.printInfo()
		for n in range(0, len(Other_Shape.nodes)):
			tra = Other_Shape.defaultTranslations[n]
			rot = Other_Shape.defaultRotations[n]
			print "Node Default Translation : %f %f %f" % (tra[0], tra[1], tra[2])
			print "Node Default Quaternion  : %f %f %f %f"  % (rot[0], rot[1], rot[2], rot[3])
		print "Done"
		# Finish
		del Other_Shape
		del Stream
	else:
		print "Error! Stream failed to load!"
		del Stream
		del OtherStream

	print "Test Finished."
	print "=============="
	
def test6(): # Plonks one mesh from a shape into another
	global file1
	global file2
	global file3
	Stream = DtsStream(file1, 1)
	OtherStream = DtsStream(file2, 1)
	SaveStream = DtsStream(file3)
	Shape = DtsShape()
	Shape.read(Stream) # Read in file
	OtherShape = DtsShape()
	OtherShape.read(OtherStream) # Read in triangle

	OtherShape.meshes[0] = Shape.meshes[3]
	OtherShape.write(SaveStream) # Save

	del Shape
	del OtherShape
	del Stream
	del SaveStream
	del OtherStream

	print "Test Finished."
	print "=============="

def test7(): # Makes a test dts
	global file1
	Stream = DtsStream(file1)
	Shape = DtsShape()
	msh = DtsMesh(0)

	# Lets Have some Dummy Data
	msh.verts=[Vector(0.0, 1.0, 0.0), Vector(1.0, 0.0, 0.0), Vector(1.0, 1.0, 0.0), # A
	           Vector(1.0, 2.0, 0.0), # B
		   Vector(2.0, 1.0, 0.0), # C
		   Vector(0.0, 2.0, 0.0), # D
		   Vector(2.0, 2.0, 0.0), # E
		   Vector(0.0, 3.0, 0.0), # F
		   Vector(1.0, 3.0, 0.0), # G
	]
	for t in msh.verts:
		msh.tverts.append(Vector2(0,0))
	for n in msh.verts:
		msh.normals.append(Vector(0.0,0.0,1.0)) # UP
	msh.indices=[0,1,2, # A
	             0,1,3, # B
	             1,4,3, # C
	             0,3,5, # D
	             3,4,6, # E
	             5,3,7, # F
	             3,8,7] # G

	for i in range(0, len(msh.indices) / 3):
		msh.primitives.append(Primitive(i*3, 3, Primitive().Strip | Primitive().Indexed | Primitive().NoMaterial))

	msh.vertsPerFrame = len(msh.verts)
	msh.calculateBounds()
	msh.calculateCenter()
	msh.calculateRadius()

	msh.maxStripSize = 7
	msh.windStrip() # Make the strip

	# Crash course in making a shape
	Shape.meshes.append(msh)
	Shape.objects.append(dObject(Shape.addName("Object"), 1, 0, 0))
	Shape.objectstates.append(ObjectState(1.0, 0, 0))
	Shape.subshapes.append(SubShape(0, 0, 0, 1, 1, 0))
	Shape.detaillevels.append(DetailLevel(Shape.addName("Detail-1"), 0, 0, 10.0, -1, -1, 7))

	n = Node(Shape.addName("Root"), -1)
	# Add default translations and rotations for this bone
	Shape.defaultTranslations.append(Vector(0,0,0))
	Shape.defaultRotations.append(Quaternion(0,0,0,1))
	Shape.nodes.append(n)

	o = Shape.objects[-1]
	world_trans, world_rot = Shape.getNodeWorldPosRot(o.node)
	msh.translate(-world_trans)
	msh.rotate(world_rot.inverse())

	Shape.calculateBounds()
	Shape.calculateCenter()
	Shape.calculateRadius()
	Shape.calculateTubeRadius()
	Shape.setSmallestSize(1)

	Shape.write(Stream)

	del Shape
	del Stream

	print "Test Finished."
	print "=============="

def replace_billboard(Shape,detail,equator, polar, polarangle, dim, includepoles):
	print "Replacing Detail %d with billboard" % detail
	Shape.detaillevels[detail].objectDetail = encodeBillBoard(equator, polar, polarangle, 0, dim, includepoles)
	
def add_billboard(Shape,detail_size,equator, polar, polarangle, dim, includepoles):
	print "Inserting Detail Level (size: %d)" % detail_size
	bbOb = encodeBillBoard(equator, polar, polarangle, 0, dim, includepoles)
	detail = DetailLevel(Shape.addName("BILLBOARD"), -1, bbOb, detail_size, -1, -1, 0)
	Shape.detaillevels.insert(colStart+1,detail)

def insert_billboard(): # Inserts a billboard deail into an existing shape
	# Billboard constants
	equator, polar, polarangle, dim, includepoles
	
	print "Billboard inserter"
	if sys.argc < 2:
		print "Parameters : <dts file>"
		return
	file_in = sys.argv[1]
	print "Reading.... %s" % file_in
	Stream = DtsStream(file_in, 1)
	Shape = DtsShape()
	Shape.read(Stream) # Read in file
	del Stream

	# Loop through billboards, find detail before collision meshes start
	colStart = -1
	for d in range(0, len(Shape.detaillevels)):
		if Shape.detaillevels[d].size == -1:
			colStart = d
	if colStart == -1: # didn't find collision meshes, so use detail count
		colStart = len(Shape.detaillevels)

	# Ask the user either to :
	#	A) Replace the last detail level (only if we have >1 detail)
	# OR	B) Add a new detail level
	# Resize detail levels
	
	print "Detail Levels in shape :"
	for detail in range(0, colStart):
		print "Detail %s (size : %d)" % (detail, Shape.detaillevels[detail].size)
	
	if colStart == 1:
		print "Shape only has one regular detail level, inserting new detail."
		add_billboard(Shape, Shape.detaillevels[0].size / 2,equator, polar, polarangle, dim, includepoles)
	else:
		print "Select an option [1-2]"
		print "1) Replace the last detail level"
		print "2) Add a new detail level"
		selection = input()
		if selection == 1:
			
			print "Detail Level %d replaced." % (colStart)
		elif selection == 2:
			print "Inserting new detail."
			add_billboard(Shape, Shape.detaillevels[colStart-1].size / 2,equator, polar, polarangle, dim, includepoles)
		else:
			print "Error : Invalid Option"
			del Shape
			return
	
	print "Writing file..."
	SaveStream = DtsStream(fileout)
	Shape.write(SaveStream) # Save
	del SaveStream
	del Shape
	print "Done"

def test_plane():
	print "Testing Ray Plane Intersection..."
	pl = PlaneF(Vector(0,0,1), Vector(0,1,1), Vector(1,1,1))
	# Ray intersect
	foo = pl.intersectRay(Vector(0,0,-10), Vector(0, 0, -20))
	if foo != None:
		print "Intersection is : ", foo[0], foo[1], foo[2]
	else:
		print "Error: Failed to get intersection!"
	# Ray distance
	foo = pl.intersect(Vector(0,0,-10), Vector(0, 0, -20))
	if foo != None:
		print "Intersection distance is : ", foo
	else:
		print "Error: Failed to get intersection distance!"
	print "Test Finished."
	print "=============="


if __name__ == "__main__":
	print "Performing Selected Tests :"
	#test1()
	#test2()
	#test3()
	#test4()	# Uncomment if you have a dts to test against
	test5()	# Uncomment if you have a dts to test against
	#test6()	# uncomment if you have a dts to test against
	#test7()	# uncomment if you have a obj to test against
	#insert_billboard("player.dts", "player_billboard.dts",6, 6, 45.0, 64, 1)
	#test_plane()
	print "** Finished Tests **"
