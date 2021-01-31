'''
Decimate_VTK.py

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
import math
import copy
import Dts_Decimate

# Try getting VTK
try:
	import vtkpython
	vtk = vtkpython # code expects module "vtk"
except:
	vtk = None

'''
	VTK Decimate Interface
'''

class VTKDecimate(Dts_Decimate.Decimate):
	def __init__(self):
		global vtk
		if vtk == None: return None
		Dts_Decimate.Decimate.__init__(self)
	def process(self,target=0.5):
		global vtk
		newfaces = []
		
		# Firstly, import verts
		self.points = vtk.vtkPoints()
		for vert in self.verts:
			self.points.InsertNextPoint(vert[0], vert[1], vert[2])
		
		# Build up lists of faces to seperatly decimate
		flags = self.calcFlags()
		faceList = []
		for i in range(0, len(flags)): faceList.append([])

		for f in self.faces:
			idx = -1
			for i in range(0, len(flags)):
				if flags[i] == f[1]:
					idx = i
					break
			if idx != -1: faceList[idx].append(f[0])

		# Strip faces
		count = 0
		for face_l in faceList:
			newFaces = self.vtkDecimateFaces(face_l, target)
			for newFace in newFaces:
				newfaces.append([newStrip, flags[count]])

			count += 1
		
		self.faces = newfaces

	# Determines how many strips we need minimum (aka for each material)
	def calcFlags(self):
		flist = []
		found = False
		# Returns a list of all flags used in primitives
		for f in self.faces:
			found = False 
			for i in range(0, len(flist)):
				if f[1] == flist[i]:
					found = True # We found it in the list already!
					break
			# Couldn't find entry in flist, or its length is 0
			if not found:
				flist.append(f[1]) # Add primitive matindex to list
		return flist

	def vtkstripFaces(self, facelist, target):
		global vtk
		# primlist is array of triangle indices, points is a vtk point array
		faces = vtk.vtkCellArray()
		nsfaces = [] # List of faces and indices

		# Insert polygon indices
		for face in facelist:
			faces.InsertNextCell(len(face))
			# This maps from strip indices -> mesh indices (into mesh points list)
			for ind in face: faces.InsertCellPoint(ind)

		newmesh = None
		mesh = vtk.vtkPolyData()
		mesh.SetPoints(self.points)
		mesh.SetPolys(faces)

		if mesh.GetNumberOfPolys() > 0:
			# We need to decimate mesh, but ideally not modify points
			decimate = vtk.vtkDecimatePro()
			decimate.SetInput(mesh)
			decimate.SetPreserveTopology(True)
			decimate.SetTargetReduction(target)
			decimate.SetSplitting(False)
			decimate.Update()
			# Calculate max length of indices
			newmesh = decimate.GetOutput()
			del strip # clear stripper
		else:
			print "   Oddity: Mesh has no polygons!"

		# Import data we got back from stripper.
		if newmesh != None:
			vtkNewFaces = newmesh.GetFaces()
			print newmesh

			# We should be able to import the strip data easily
			# Values appear like : <Strip Length> <Strip Indices> ...etc
			faceData = vtkNewFaces.GetData()

			stripCount = 0
			maxStrip = 0
			inds = [] # Temporary indices list

			for ind in range(0, faceData.GetSize()):
				if maxStrip == stripCount:
					if stripCount > 0: # add inds if we have added any
						nstrips.append(inds)
						inds = [] # stop catcher from catching these inds again
						stripCount = 0
					maxStrip = faceData.GetValue(ind)
				else:
					inds.append(faceData.GetValue(ind))
					stripCount += 1
				# Catch any strip we forgot to enter since the array abruptly ended
			if len(inds) > 0:
				nstrips.append(inds)
		else:
			print "   Oddity: Mesh did not return from operation."

		# Cleanup
		del faces
		del newmesh
		del mesh

		# Return
		return nfaces