'''
Dts_TranslucentSort.py

Portions Copyright (c) 2004 - 2005 James Urquhart(j_urquhart@btinternet.com)

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

Original Code Copyright (C) GarageGames.com, Inc.
'''

# hold indices and sizes of biggest faces...these are marked as higher priority for splitting with
bigFaces = []
bigFaceSizes = []

# planes in this list are hidden because we are on the other side of them at the time...
noAddNormals = []

def getMinMaxExtents(x, v0, v1, v2):
	xmin = xmax = x.dot(v0)
	dot = x.dot(v1)
	if xmin>dot:
		xmin=dot
	elif xmax<dot:
		xmax=dot
	dot = x.dot(v2)
	if xmin>dot:
		xmin=dot
	elif xmax<dot:
		xmax=dot
	
	return xmin, xmax

class FaceInfo:
	def __init__(self):
		self.used = False
		self.priority = -1
		self.parentFace = 0
		self.childFace1 = 0
		self.childFace2 = 0
		self.childFace3 = 0
		self.normal = Vector()
		self.k = .0
		self.isInFrontOfMe = []
		self.isBehindMe = []
		self.isCutByMe = []
		self.isCoPlanarWithMe = []
	
	def __del__(self):
		del self.isInFrontOfMe
		del self.isBehindMe
		del self.isCutByMe
		del self.isCoPlanarWithMe
	
	def __str__(self):
		if not self.used:
			retStr = "Face (Unused)"
		else:
			retStr = "Face (Used)"
		
		retStr += "Priority: %d\n \
		parentFace: %d\n \
		Child Faces: %d %d %d\n \
		Plane : (%f %f %f)/%f \n \
		Front Faces: %s\n \
		Back Faces : %s\n \
		Cut Faces : %s\n \
		Co Faces : %s" % (self.priority,self.parentFace,self.childFace1,self.childFace2,self.childFace3,self.normal[0],self.normal[1],self.normal[2],self.k,self.isInFrontOfMe,self.isBehindMe,self.isCutByMe,self.isCoPlanarWithMe)
		return retStr

class TranslucentSort:
	def __init__(self, faces=[], indices=[], verts=[], norms=[], tverts=[], numBigFaces=0, maxDepth=1, zLayerUp=False, zLayerDown=False):
		global bigFaces, bigFaceSizes
		self.frontClusters = []
		self.backClusters = []
		self.middleCluster = []
		
		self.splitNormal = Vector()
		self.splitK = .0
		
		self.mNumBigFaces = numBigFaces
		self.mMaxDepth = maxDepth
		self.mZLayerUp = zLayerUp
		self.mZLayerDown = zLayerDown
		
		self.currentDepth = 0
		
		self.frontSort = None
		self.backSort = None
		
		self.faceInfoList = []
		self.saveFaceInfoList = []
		
		self.mFaces = faces
		self.mIndices = indices
		self.mVerts = verts
		self.mNorms = norms
		self.mTVerts = tverts
		
		self.initFaces()
	
	def makefrom(self):
		newSort = TranslucentSort(self.mFaces,self.mIndices,self.mVerts,self.mNorms,self.mTVerts)
		# ^^ NOTE: Not sure if the above is safe
		
		newSort.faceInfoList = [None]*len(self.faceInfoList)
		for i in range(0, len(newSort.faceInfoList)):
			newSort.faceInfoList[i] = copy.copy(self.faceInfoList[i])
		
		newSort.currentDepth = self.currentDepth + 1
		newSort.mMaxDepth = self.mMaxDepth
		newSort.mZLayerUp = self.mZLayerUp
		newSort.mZLayerDown = self.mZLayerDown
		newSort.mNumBigFaces = 0 # never used...
		return newSort
	
	def __del__(self):
		del self.frontSort
		del self.backSort
		
		clearArray(self.faceInfoList)
		clearArray(self.saveFaceInfoList)
		clearArray(self.frontClusters)
		clearArray(self.backClusters)
		
	def initFaces(self):
		self.faceInfoList = [None]*len(self.mFaces)
		for i in range(0, len(self.faceInfoList)):
			self.faceInfoList[i] = FaceInfo()
			self.faceInfoList[i].used = False
		
		for i in range(0, len(self.mFaces)):
			self.initFaceInfo(self.mFaces[i], self.faceInfoList[i])
			self.setFaceInfo(self.mFaces[i], self.faceInfoList[i])
	
	def initFaceInfo(self, face, faceInfo, setPriority=True):
		global bigFaces, bigFaceSizes
		faceInfo.used = False
		faceInfo.parentFace = -1
		faceInfo.childFace1 = -1
		faceInfo.childFace2 = -1
		faceInfo.childFace3 = -1

		# get normal and plane constant
		idx0 = self.mIndices[face.firstElement + 0]
		idx1 = self.mIndices[face.firstElement + 1]
		idx2 = self.mIndices[face.firstElement + 2]
		vert0 = self.mVerts[idx0]
		vert1 = self.mVerts[idx1]
		vert2 = self.mVerts[idx2]
		# compute normal using largest gap...
		edge01 = vert1-vert0
		edge12 = vert2-vert1
		edge20 = vert0-vert2
		if edge01.dot(edge01)>=edge12.dot(edge12) and edge01.dot(edge01)>=edge20.dot(edge20):
			# edge01 biggest gap
			faceInfo.normal = edge12.cross(edge20) * -1.0
		elif edge12.dot(edge12)>=edge20.dot(edge20) and edge12.dot(edge12)>=edge01.dot(edge01):
			# edge12 biggest gap
			faceInfo.normal = edge20.cross(edge01) * -1.0
		else:
			# edge20 biggest gap
			faceInfo.normal = edge01.cross(edge12) * -1.0
		faceInfo.normal = faceInfo.normal.normalize()
		faceInfo.k = faceInfo.normal.dot(vert0)
		
		if setPriority:
			faceInfo.priority = 0
			maxExtent = edge01.dot(edge01)
			if maxExtent<edge12.dot(edge12):
				maxExtent = edge12.dot(edge12)
			if maxExtent<edge20.dot(edge20):
				maxExtent = edge20.dot(edge20)
			
			for i in range(0, self.mNumBigFaces):
				if i == len(bigFaceSizes) or maxExtent > bigFaceSizes[i]:
					bigFaceSizes.insert(i, maxExtent)
					count = 0
					for f in self.mFaces:
						if f == face:
							faceIdx = count
							break
						count += 1
					bigFaces.insert(i, faceIdx)
					
					while i < len(bigFaceSizes):
						if i < self.mNumBigFaces:
							self.faceInfoList[bigFaces[i]].priority = self.mNumBigFaces-i
						else:
							self.faceInfoList[bigFaces[i]].priority = 0
						i += 1
					while len(bigFaceSizes) > self.mNumBigFaces:
						del bigFaceSizes[-1]
						del bigFaces[-1]
					break
	
	def setFaceInfo(self, face, faceInfo):
		faceInfo.isInFrontOfMe = [False]*len(self.mFaces)
		faceInfo.isBehindMe = [False]*len(self.mFaces)
		faceInfo.isCutByMe = [False]*len(self.mFaces)
		faceInfo.isCoPlanarWithMe = [False]*len(self.mFaces)
		
		normal = faceInfo.normal
		k = faceInfo.k
		
		count = 0
		for f in self.mFaces:
			if f == face:
				myIndex = count
				break
			count += 1
		
		for i in range(0, len(self.mFaces)):
			if i == myIndex or self.faceInfoList[i].used:
				continue
			
			otherFace = self.mFaces[i]
			
			idx0 = self.mIndices[otherFace.firstElement + 0]
			idx1 = self.mIndices[otherFace.firstElement + 1]
			idx2 = self.mIndices[otherFace.firstElement + 2]
			v0 = self.mVerts[idx0]
			v1 = self.mVerts[idx1]
			v2 = self.mVerts[idx2]
			hasFrontVert, hasBackVert = False, False
			if normal.dot(v0) > k + PlaneF.EPSILON:
				hasFrontVert = True
			elif normal.dot(v0) < k - PlaneF.EPSILON:
				hasBackVert = True
			if normal.dot(v1) > k + PlaneF.EPSILON:
				hasFrontVert = True
			elif normal.dot(v1) < k - PlaneF.EPSILON:
				hasBackVert = True
			if normal.dot(v2) > k + PlaneF.EPSILON:
				hasFrontVert = True
			elif normal.dot(v2) < k - PlaneF.EPSILON:
				hasBackVert = True
			
			if hasFrontVert and not hasBackVert:
				faceInfo.isInFrontOfMe[i] = True
			elif not hasFrontVert and hasBackVert:
				faceInfo.isBehindMe[i] = True
			elif hasFrontVert and hasBackVert:
				faceInfo.isCutByMe[i] = True
			elif not hasFrontVert and not hasBackVert:
				faceInfo.isCoPlanarWithMe[i] = True
	
	def clearFaces(self, removeThese):
		i = 0
		for faceInfo in self.faceInfoList:
			faceInfo.isInFrontOfMe = subtractSet(faceInfo.isInFrontOfMe, removeThese)
			faceInfo.isBehindMe = subtractSet(faceInfo.isBehindMe, removeThese)
			faceInfo.isCutByMe = subtractSet(faceInfo.isCutByMe, removeThese)
			faceInfo.isCoPlanarWithMe = subtractSet(faceInfo.isCoPlanarWithMe, removeThese)
			if removeThese[i]:
				faceInfo.used = True
			i += 1
	
	def saveFaceInfo(self):
		while len(self.saveFaceInfoList) != 0:
			del self.saveFaceInfoList[0]
		self.saveFaceInfoList = [None]*len(self.faceInfoList)
		
		for i in range(0, len(self.saveFaceInfoList)):
			self.saveFaceInfoList[i] = copy.copy(self.faceInfoList[i])
	
	def restoreFaceInfo(self):
		for i in range(0, len(saveFaceInfo)):
			self.faceInfoList[i] = self.saveFaceInfoList[i]
	
	def addFaces(self, addClusters, faces, indices, continueLast = False):
		global noAddNormals
		startFaces = len(faces)
		for c in addClusters:
			if type(c) == list:
				if startFaces != len(faces): nVal = False
				else: nVal = continueLast
				changedFaces = self.addFaces(c, faces, indices, nVal)
			else:
				toAdd = addClusters
				startNewFace = not continueLast or len(faces) == 0
				while allSet(toAdd):
					for i in range(0, len(self.mFaces)):
						if not startNewFace and faces[-1].matindex != self.mFaces[i].matindex:
							continue
						if not toAdd[i]:
							continue
						for k in range(0, len(noAddNormals)):
							if noAddNormals[k].dot(self.faceInfoList[i].normal) > .99:
								toAdd[i] = False
						if not toAdd[i]:
							continue
						# add this face...
						if startNewFace:
							faces.append(Primitive(len(indices),0,self.mFaces[i].matindex))
							startNewFace = False
						faces[-1].numElements += 3
						indices.append(self.mIndices[self.mFaces[i].firstElement+0])
						indices.append(self.mIndices[self.mFaces[i].firstElement+1])
						indices.append(self.mIndices[self.mFaces[i].firstElement+2])
						toAdd[i] = False
					startNewFace = True
	
	def addOrderedFaces(self, orderedCluster, faces, indices, continueLast = False):
		global noAddNormals
		toAdd = orderedCluster
		startNewFace = not continueLast or len(faces) == 0
		while len(toAdd) != 0:
			i = 0
			while i < len(toAdd):
				k = 0
				while k < len(noAddNormals):
					if noAddNormals[k].dot(self.faceInfoList[toAdd[i]].normal) > .99:
						del toAdd[i]
						i -= 1
						break
					k += 1
				if k != len(noAddNormals):
					continue
				if not startNewFace and self.mFaces[toAdd[i]].matindex != faces[-1].matindex:
					continue
				if startNewFace:
					faces.append(Primitive(len(indices), 0, self.mFaces[toAdd[i]].matindex))
					startNewFace = False
				faces[-1].numElements += 3
				indices.append(self.mIndices[self.mFaces[toAdd[i]].firstElement+0])
				indices.append(self.mIndices[self.mFaces[toAdd[i]].firstElement+1])
				indices.append(self.mIndices[self.mFaces[toAdd[i]].firstElement+2])
				del toAdd[i]
				i -= 1
			startNewFace = True
	
	def splitFace(self, faceIndex, normal, k):
		idx0 = self.mIndices[self.mFaces[faceIndex].firstElement + 0]
		idx1 = self.mIndices[self.mFaces[faceIndex].firstElement + 1]
		idx2 = self.mIndices[self.mFaces[faceIndex].firstElement + 2]
	
		v0 = self.mVerts[idx0]
		v1 = self.mVerts[idx1]
		v2 = self.mVerts[idx2]
	
		k0 = normal.dot(v0)
		k1 = normal.dot(v1)
		k2 = normal.dot(v2)
		
		# if v0, v1, or v2 is on the plane defined by normal and k, call special case routine
		if math.fabs(k0-k) < epsilon or math.fabs(k1-k) < epsilon or math.fabs(k2-k) < epsilon:
			self.splitFace2(faceIndex,normal,k)
			return
	
		# find the odd man out (the vertex alone on his side of the plane)
		code, rogue = 0,0
		if k0 < k:
			code |= 1
		if k1 < k:
			code |= 2
		if k2 < k:
			code |= 4
		if code == 1 or code == 6:
			rogue = 0
		elif code == 2 or code == 5:
			rogue = 1
		elif code == 4 or code == 3:
			rogue = 2
		elif code == 0 or code == 7:
			return # shouldn't happen...
	
		# re-order verts so that rogue vert is first vert
		idx0 = self.mIndices[self.mFaces[faceIndex].firstElement + ((rogue+0)%3)]
		idx1 = self.mIndices[self.mFaces[faceIndex].firstElement + ((rogue+1)%3)]
		idx2 = self.mIndices[self.mFaces[faceIndex].firstElement + ((rogue+2)%3)]
		v0 = self.mVerts[idx0]
		v1 = self.mVerts[idx1]
		v2 = self.mVerts[idx2]
		k0 = normal.dot(v0)
		k1 = normal.dot(v1)
		k2 = normal.dot(v2)
		tv0 = self.mTVerts[idx0]
		tv1 = self.mTVerts[idx1]
		tv2 = self.mTVerts[idx2]
		n0 = self.mNorms[idx0]
		n1 = self.mNorms[idx1]
		n2 = self.mNorms[idx2]
	
		# find intersection of edges and plane
		a01 = (k-k0)/(k1-k0)
		a02 = (k-k0)/(k2-k0)
		v01 = v1-v0
		v01 *= a01
		v01 += v0
		tv01 = tv1-tv0
		tv01 *= a01
		tv01 += tv0
		v02 = v2-v0
		v02 *= a02
		v02 += v0
		tv02 = tv2-tv0
		tv02 *= a02
		tv02 += tv0
	
		# interpolate the normals too (we'll just linearly interpolate...perhaps slerp if later)
		n01 = n1-n0
		n01 *= a01
		n01 += n0
		n01.normalize()
		n02 = n2-n0
		n02 *= a02
		n02 += n0
		n02.normalize()
	
		# add two new verst
		idx01 = len(self.mVerts)
		self.mVerts.append(v01)
		self.mNorms.append(n01)
		self.mTVerts.append(tv01)
		idx02 = len(self.mVerts)
		self.mVerts.append(v02)
		self.mNorms.append(n02)
		self.mTVerts.append(tv02)
	
		# add three faces :
		# add "rogue" face
		self.mFaces.append(Primitive(len(self.mIndices), 3, self.mFaces[faceIndex].matindex))
		self.mIndices.append(idx0)
		self.mIndices.append(idx01)
		self.mIndices.append(idx02)
		# add idx01, idx1, idx02
		self.mFaces.append(Primitive(len(self.mIndices), 3, self.mFaces[faceIndex].matindex))
		self.mIndices.append(idx01)
		self.mIndices.append(idx1)
		self.mIndices.append(idx02)
		# add idx2, idx02, idx01
		self.mFaces.append(Primitive(len(self.mIndices), 3, self.mFaces[faceIndex].matindex))
		self.mIndices.append(idx2)
		self.mIndices.append(idx02)
		self.mIndices.append(idx1)
	
		# finally, set faceInfo
		numFaces = len(self.mFaces)
		self.faceInfoList.append(FaceInfo())
		self.faceInfoList.append(FaceInfo())
		self.faceInfoList.append(FaceInfo())
	
		self.faceInfoList[faceIndex].used = True
		self.faceInfoList[faceIndex].childFace1 = nuself.mFaces-3
		self.faceInfoList[faceIndex].childFace2 = nuself.mFaces-2
		self.faceInfoList[faceIndex].childFace3 = nuself.mFaces-1
	
		self.initFaceInfo(self.mFaces[numFaces-3],self.faceInfoList[numFaces-3],False)
		self.initFaceInfo(self.mFaces[numFaces-2],self.faceInfoList[numFaces-2],False)
		self.initFaceInfo(self.mFaces[numFaces-1],self.faceInfoList[numFaces-1],False)
	
		self.faceInfoList[numFaces-3].priority = self.faceInfoList[faceIndex].priority
		self.faceInfoList[numFaces-2].priority = self.faceInfoList[faceIndex].priority
		self.faceInfoList[numFaces-1].priority = self.faceInfoList[faceIndex].priority
		self.faceInfoList[numFaces-3].parentFace = faceIndex
		self.faceInfoList[numFaces-2].parentFace = faceIndex
		self.faceInfoList[numFaces-1].parentFace = faceIndex
	
	def splitFace2(self, faceIndex, normal, k):
		idx0 = self.mIndices[self.mFaces[faceIndex].firstElement + 0]
		idx1 = self.mIndices[self.mFaces[faceIndex].firstElement + 1]
		idx2 = self.mIndices[self.mFaces[faceIndex].firstElement + 2]
	
		v0 = self.mVerts[idx0]
		v1 = self.mVerts[idx1]
		v2 = self.mVerts[idx2]
	
		k0 = normal.dot(v0)
		k1 = normal.dot(v1)
		k2 = normal.dot(v2)
	
		# make sure we got here legitimately
		if math.fabs(k0-k) >= PlaneF.EPSILON and math.fabs(k1-k) >= PlaneF.EPSILON and math.fabs(k2-k) >= PlaneF.EPSILON:
			print "TODO: ASSERT"
	
		# find the odd man out (the vertex that is on the plane)
		rogue
		if math.fabs(k0-k) < PlaneF.EPSILON:
			rogue = 0
		elif math.fabs(k1-k) < PlaneF.EPSILON:
			rogue = 1
		elif math.fabs(k2-k) < PlaneF.EPSILON:
			rogue = 2
		else:
			print "TODO: ASSERT"
	
		# re-order verts so that rogue vert is first vert
		idx0 = self.mIndices[self.mFaces[faceIndex].firstElement + ((rogue+0)%3)]
		idx1 = self.mIndices[self.mFaces[faceIndex].firstElement + ((rogue+1)%3)]
		idx2 = self.mIndices[self.mFaces[faceIndex].firstElement + ((rogue+2)%3)]
		v0 = self.mVerts[idx0]
		v1 = self.mVerts[idx1]
		v2 = self.mVerts[idx2]
		k0 = normal.dot(v0)
		k1 = normal.dot(v1)
		k2 = normal.dot(v2)
		tv0 = self.mTVerts[idx0]
		tv1 = self.mTVerts[idx1]
		tv2 = self.mTVerts[idx2]
		n0 = self.mNorms[idx0]
		n1 = self.mNorms[idx1]
		n2 = self.mNorms[idx2]
	
		# find intersection of edges and plane
		a12 = (k-k1)/(k2-k1)
		v12 = v2-v1
		v12 *= a12
		v12 += v1
		tv12 = tv2-tv1
		tv12 *= a12
		tv12 += tv1
	
		# interpolate the normals too (we'll just linearly interpolate..perhaps slerp if later)
		n12 = n2-n1
		n12 *= a12
		n12 += n1
		n12.normalize()
	
		# add new vert
		idx12 = len(self.mVerts)
		self.mVerts.append(v12)
		self.mNorms.append(n12)
		self.mTVerts.append(tv12)
	
		# add two faces:
		self.mFaces.append(Primitive(len(self.mIndices),3,self.mFaces[faceIndex].matindex))
		# add idx0, idx2, idx12
		self.mIndices.append(idx0)
		self.mIndices.append(idx2)
		self.mIndices.append(idx12)
		self.mFaces.append(Primitive(len(self.mIndices),3,self.mFaces[faceIndex].matindex))
		# add idx0, idx12, idx1
		self.mIndices.append(idx0)
		self.mIndices.append(idx12)
		self.mIndices.append(idx1)
		
		# finally, set faceInfo
		numFaces = len(self.mFaces)
		self.faceInfoList.append(FaceInfo())
		self.faceInfoList.append(FaceInfo())
	
		self.faceInfoList[faceIndex].used = True
		self.faceInfoList[faceIndex].childFace1 = numFaces-2
		self.faceInfoList[faceIndex].childFace2 = numFaces-1
		self.faceInfoList[faceIndex].childFace3 = -1
	
		self.initFaceInfo(self.mFaces[numFaces-2],self.faceInfoList[numFaces-2],False)
		self.initFaceInfo(self.mFaces[numFaces-1],self.faceInfoList[numFaces-1],False)
	
		self.faceInfoList[numFaces-2].priority = self.faceInfoList[faceIndex].priority
		self.faceInfoList[numFaces-1].priority = self.faceInfoList[faceIndex].priority
		self.faceInfoList[numFaces-2].parentFace = faceIndex
		self.faceInfoList[numFaces-1].parentFace = faceIndex
	
	def sort(self):
		i = 0
		while i != len(self.faceInfoList):
			if not self.faceInfoList[i].used: 
				break
			i += 1
		if i == len(self.faceInfoList):
			return # no unused faces...
		
		while 1:
			# 1. select faces with no one behind them -- these guys get drawn first
			self.backClusters.append([False]*len(self.mFaces))
			for i in range(0, len(self.faceInfoList)):
				if not self.faceInfoList[i].used and not allSet(self.faceInfoList[i].isBehindMe) and not allSet(self.faceInfoList[i].isCutByMe):
					self.backClusters[-1][i] = True
					self.faceInfoList[i].used = True # select as used so we don't grab it below
			
			# 2. select faces with no one in front of them -- these guys get drawn last
			self.frontClusters.insert(0,[False]*len(self.mFaces))
			for i in range(0, len(self.faceInfoList)):
				if not self.faceInfoList[i].used and not allSet(self.faceInfoList[i].isInFrontOfMe) and not allSet(self.faceInfoList[i].isCutByMe):
					self.frontClusters[0][i] = True
					self.faceInfoList[i].used = True # this won't have any effect, but it's here to parallel above
			
			# 3. clear above faces and repeat 1&2 until no more faces found in either step
			removeThese = overlapSet(self.backClusters[-1], self.frontClusters[0])
			if not allSet(removeThese):
				# didn't remove anything
				break
			
			self.clearFaces(removeThese)
			
		# 4. pick face cutting fewest other faces and resulting in most balanced split, call this cutFace
		fewestCuts = 0
		balance = 0
		priority = 0
		cutFace = -1
		for i in range(0, len(self.mFaces)):
			if self.faceInfoList[i].used:
				continue
			cut, front, back = 0,0,0
			for j in range(0, len(self.mFaces)):
				if self.faceInfoList[j].used:
					continue
				if self.faceInfoList[i].isCutByMe[j]:
					cut += 1
				if self.faceInfoList[i].isInFrontOfMe[j]:
					front += 1
				if self.faceInfoList[i].isBehindMe[j]:
					back += 1
			if cutFace != -1:
				if self.faceInfoList[i].priority < priority:
					continue
				if self.faceInfoList[i].priority == priority:
					if (cut>fewestCuts) or (cut==fewestCuts and math.fabs(front-back)>=balance):
						continue

			# if we get this far, this is our new cutFace
			cutFace = i
			fewestCuts = cut
			priority = faceInfoList[i].priority
			balance = math.fabs(front-back)
		
		if cutFace >= 0 and self.currentDepth < self.mMaxDepth:
			# 5. cut all faces cut by cutFace
			if allSet(self.faceInfoList[cutFace].isCutByMe):
				startSize = len(mFaces) # won't need to split beyond here, even though more faces added
				for i in range(0, startSize):
					if not self.faceInfoList[i].used and self.faceInfoList[cutFace].isCutByMe[i]:
						self.splitFace(i,self.faceInfoList[cutFace].normal,self.faceInfoList[cutFace].k)
	
				# may be new faces and some old faces may have been disabled, recompute face info
				for i in range(0, len(self.mFaces)):
					if not self.faceInfoList[i].used:
						self.setFaceInfo(self.mFaces[i],self.faceInfoList[i])
		
			startNumFaces = len(self.mFaces)
			disableSet = [False]*len(self.mFaces)
			
			# 6. branch into two orders depending on which side of cutFace camera is, perform translucent sort on each
			
			# back
			self.backSort = self.makefrom()
			for i in range(0, len(self.mFaces)):
				if self.backSort.faceInfoList[i].used or self.backSort.faceInfoList[cutFace].isBehindMe[i]:
					continue
				if self.backSort.faceInfoList[cutFace].isCutByMe[i]:
					print "TODO: Assert" #  doh, perform hard assert :(...
				
				if self.backSort.faceInfoList[cutFace].isCoplanarWithMe[i] or cutFace==i:
					if self.backSort.faceInfoList[cutFace].normal.dot(backsort.faceInfoList[i].normal) > 0.0:
						continue
				elif not self.backSort.faceInfoList[cutFace].isInFrontOfMe[i] and cutFace != i:
					print "TODO: Assert"
				disableSet[i] = True
			
			if not allSet(disableSet):
				print "TODO: Assert"
			
			self.backSort.clearFaces(disableSet)
			self.backSort.sort()
			
			if backSort.backSort == None and backSort.frontSort == None and len(backSort.frontClusters) == 0 and len(backSort.backClusters) == 0:
				# empty, no reason to keep backSort
				del self.backSort
				self.backSort = None
			
			# create faceInfo entry for any faces that got added (set used=True)
			self.faceInfoList = [None] * (len(self.faceInfoList)-len(self.mFaces))
			for i in range(startNumFaces, len(self.faceInfoList)):
				self.faceInfoList[i] = FaceInfo()
				self.faceInfoList[i].used = True
			 
			# front
			self.frontSort = self.makefrom()
			disableSet = [False]*len(self.mFaces)
			for i in range(0, len(self.mFaces)):
				if self.frontSort.faceInfoList[i].used or self.frontSort.faceInfoList[cutFace].isInFrontOfMe[i]:
					continue
				if self.frontSort.faceInfoList[cutFace].isCutByMe[i]:
					print "TODO: Assert" # doh, perform hard assert...
	
				if self.frontSort.faceInfoList[cutFace].isCoplanarWithMe[i] or cutFace==i:
					if frontSort.faceInfoList[cutFace].normal.dot(frontSort.faceInfoList[i].normal)>0.0:
						continue
				elif not frontSort.faceInfoList[cutFace].isBehindMe[i] and i!= cutFace:
					print "TODO: Assert" 
	
				disableSet[i] = True
	
			if not allSet(disableSet):
				print "TODO: Assert" 
	
			self.frontSort.clearFaces(disableSet)
	
			self.frontSort.sort()
	
			if self.frontSort.backSort==None and self.frontSort.frontSort==None and len(self.frontSort.frontClusters == 0) and len(self.frontSort.backClusters == 0):
				# empty, no reason to keep backSort
				del self.backSort
				self.backSort = None
			
			# setup cut plane
			self.splitNormal = self.faceInfoList[cutFace].normal
			self.splitK = self.faceInfoList[cutFace].k
		elif cutFace >= 0:
			# we've gotten too deep, just dump the remaing faces -- but dump in best order we can
			if mZLayerUp:
				self.middleCluster = self.layerSort(True)
			elif mZLayerDown:
				self.middleCluster = self.layerSort(False)
			else:
				self.middleCluster = self.copeSort()
	
	# routines for sorting faces when there is no perfect solution for all cases
	def copeSort(self):
		frontOrderedCluster, backOrderedCluster, cluster = [],[],[]
		
		# restore after following loop
		self.saveFaceInfo()
	
		while 1:
			bestFace = -1
			bestCount = 0x7FFFFFFF
			front = False
	
			# we need to find face with fewest polys behind or in front (cut implies both)
			for i in range(0, len(self.faceInfoList)):
				if self.faceInfoList[i].used:
					continue
				frontCount = 0
				backCount = 0
				for j in range(0, len(self.faceInfoList)):
					if self.faceInfoList[j].used:
						continue
					if self.faceInfoList[i].isInFrontOfMe[j]:
						frontCount += 1
					elif self.faceInfoList[i].isBehindMe[j]:
						backCount += 1
					elif self.faceInfoList[i].isCutByMe[j]:
						frontCount += 1
						backCount += 1
				
				if backCount < bestCount or bestFace<0:
					bestCount = backCount
					bestFace = i
					front = false
				
				if frontCount==0 and frontCount < bestCount:
					bestCount = frontCount
					bestFace = i
					front = true
			
			if bestFace != -1:
				if front:
					frontOrderedCluster.insert(0,bestFace)
				else:
					backOrderedCluster.append(bestFace)
				self.clearFaces([True]*len(self.mFaces))
			else:
				break
		
		cluster = backOrderedCluster + frontOrderedCluster
		
		# we need face info back...
		self.restoreFaceInfo()
	
		# we have a good ordering...but see if we can make some local optimizations
		i = 0
		while i < len(cluster):
			face1 = cluster[i]
			faceInfo1 = self.faceInfoList[face1]
			for j in range(i+1, len(cluster)):
				face2 = cluster[j]
				faceInfo2 = self.faceInfoList[face2]
				if (faceInfo1.isBehindMe[face2] and faceInfo2.isInFrontOfMe[face1]) or (faceInfo1.isCutByMe[face2] and faceInfo2.isInFrontOfMe[face1])  or (faceInfo1.isBehindMe[face2] and faceInfo2.isCutByMe[face1]):
					# these two guys should be switched...now check to see if we can do it
					k = i
					while k < j:
						k += 1
						face12 = cluster[k]
						faceInfo12 = self.faceInfoList[face12]
						
						# Currently, face1 precedes face12 in the list...under what conditions is it ok
						# to have face1 follow face12?  Answer:  face12 behind face1, or face1 in front of face12.
						# Similarly, face12 precedes face2...
						if (faceInfo1.isBehindMe[face12] or faceInfo12.isInFrontOfMe[face1]) and (faceInfo12.isBehindMe[face2] or faceInfo2.isInFrontOfMe[face12]):
							continue
						break
					
					if k==j:
						# switch has been approved...
						cluster[i] = face2
						cluster[j] = face1
						i -= 1
						break # TODO:  do we need to make sure no infinite loop occurs?
			i += 1
	
	def layerSort(self, upFirst):
		# sort up-pointing faces from bottom to top and down-pointing faces from top to bottom
		upCluster, downCluster,cluster = [],[],[]
		upZ, downZ = [],[]
	
		# go through each face, decide which list to add it to and where
		for i in range(0, len(self.faceInfoList)):
			if self.faceInfoList[i].used:
				continue
			face = self.mFaces[i]
			idx0 = self.mIndices[face.firstElement + 0]
			idx1 = self.mIndices[face.firstElement + 1]
			idx2 = self.mIndices[face.firstElement + 2]
			v0 = self.mVerts[idx0]
			v1 = self.mVerts[idx1]
			v2 = self.mVerts[idx2]
			
			# find smallest z
			if v0[2] < v1[2]: smallZ = v0[2]
			else: smallZ = v1[2]
			if smallZ < v2[2]: smallZ = smallZ
			else: smallZ = v2[2]
			
			# find largest z
			if v0[2] > v1[2]: bigZ = v0[2]
			else: bigZ = v1[2]
			if smallZ > v2[2]: bigZ = bigZ
			else: bigZ = v2[2]
			
			if pointUp: sortBy = smallZ
			else: sortBy = bigZ
	
			if faceInfoList[i].normal[2]>0.0:
				# we face up
				if len(upCluster) == 0:
					upCluster.append(i)
					upZ.append(sortBy)
				else:
					# keep sorted in order of increasing z (so bottom faces are first)
					j = 0
					while j < len(upZ):
						if sortBy<upZ[j]:
							break
						j += 1
					upZ.insert(j, sortBy)
					upCluster.insert(j,i)
			else:
				# we face down
				if len(downCluster) == 0:
					downCluster.append(i)
					downZ.append(sortBy)
				else:
					# keep sorted in order of decreasing z (so top faces are first)
					j = 0
					while j < len(downZ):
						if sortBy>downZ[j]:
							break
						j += 1
					downZ.insert(j,sortBy)
					downCluster.insert(j,i)
		
		if pointUp:
			cluster = upCluster + downCluster
		else:
			cluster = downCluster + upCluster
	
	# these are for debugging
	def anyInFrontOfPlane(self, normal, k):
		# make sure no face in use is behind plane
		for i in range(0, len(self.mFaces)):
			if self.faceInfoList[i].used:
				continue
			idx0 = self.mIndices[self.mFaces[i].firstElement + 0]
			idx1 = self.mIndices[self.mFaces[i].firstElement + 1]
			idx2 = self.mIndices[self.mFaces[i].firstElement + 2]
			if normal.dot(self.mVerts[idx0]) > k + PlaneF.EPSILON:
				return True
			if normal.dot(self.mVerts[idx1]) > k + PlaneF.EPSILON:
				return True
			if normal.dot(self.mVerts[idx2]) > k + PlaneF.EPSILON:
				return True
		return False
	
	def anyBehindPlane(self, normal, k):
		# make sure no face in use is behind plane
		for i in range(0, len(self.mFaces)):
			if self.faceInfoList[i].used:
				continue
			idx0 = self.mIndices[self.mFaces[i].firstElement + 0]
			idx1 = self.mIndices[self.mFaces[i].firstElement + 1]
			idx2 = self.mIndices[self.mFaces[i].firstElement + 2]
			if normal.dot(self.mVerts[idx0]) < k - PlaneF.EPSILON:
				return True
			if normal.dot(self.mVerts[idx1]) < k - PlaneF.EPSILON:
				return True
			if normal.dot(self.mVerts[idx2]) < k - PlaneF.EPSILON:
				return True
		return False
	
	#
	def generateClusters(self, clusters, faces, indices, retIndex=-1):
		global noAddNormals
		idx = len(clusters)
		clusters = [Cluster(),Cluster()]
		# add back faces
		clusters[idx].startPrimitive = len(faces)
		self.addFaces(self.backClusters,faces,indices)
		clusters[idx].endPrimitive = len(faces)
		
		clusters[idx].normal = self.splitNormal
		clusters[idx].k = self.splitK
	
		if self.frontSort and self.backSort:
			# Note: below there are some lines dealing with the variable "noAddNormal" scattered in.  Kind of a hack.
			# Here is what it does:  it is an optimization.  Any face with a normal matching an entry in that list will
			# not be added to the mesh.  This is desired if we know we are on one side of a plane (then we don't want
			# to bother adding faces that face the opposite direction).
	
			# back then front -- but add in opp. order because we know where to return from self.frontSort but not self.backSort
			frontSide = len(clusters)
			self.frontSort.generateClusters(clusters,faces,indices,idx+1)
			clusters[idx].frontCluster = len(clusters)
			noAddNormals.append(-self.splitNormal)
			self.backSort.generateClusters(clusters,faces,indices,frontSide)
			noAddNormals.pop(-1)
			clusters[idx].backCluster = clusters[idx].frontCluster
	
			# front then back -- but add in opp. order because we know where to return from self.backSort but not self.frontSort
			backSide = len(clusters)
			self.backSort.generateClusters(clusters,faces,indices,idx+1)
			clusters[idx].backCluster = len(clusters)
			noAddNormals.append(self.splitNormal)
			self.frontSort.generateClusters(clusters,faces,indices,backSide)
			noAddNormals.pop(-1)
		elif self.frontSort:
			clusters[idx].frontCluster = clusters[idx].backCluster = len(clusters)
			self.frontSort.generateClusters(clusters,faces,indices,idx+1)
		elif self.backSort:
			clusters[idx].frontCluster = clusters[idx].backCluster = len(clusters)
			self.backSort.generateClusters(clusters,faces,indices,idx+1)
		else:
			self.addOrderedFaces(self.middleCluster,faces,indices,clusters[idx].startPrimitive!=len(faces))
			self.addFaces(self.frontClusters,faces,indices,clusters[idx].startPrimitive!=len(faces))
			clusters[idx].endPrimitive = len(faces)
			clusters[idx].frontCluster = clusters[idx].backCluster = retIndex
	
		if self.frontSort or self.backSort:
			clusters[idx+1].normal = Vector(0.0,0.0,0.0)
			clusters[idx+1].k = 0.0
	
			clusters[idx+1].startPrimitive = len(faces)
			self.addFaces(self.frontClusters,faces,indices)
			clusters[idx+1].endPrimitive = len(faces)
			
			clusters[idx+1].frontCluster = clusters[idx+1].backCluster = retIndex
		else:
			clusters.pop(-1)

from Torque_Util import *
from Dts_Mesh import Cluster, DtsMesh, Primitive
from Dts_Stream import *
