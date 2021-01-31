from Nv_VertexCache import *

# TODO: Need to check!

class PrimType:
	PT_LIST = 0
	PT_STRIP = 1
	PT_FAN = 2

class PrimitiveGroup:
	def __init__(self, tp=PrimType.PT_STRIP):
		self.type = None
		self.numIndices = 0
		self.indices = array('H')
	def __del__(self):
		del self.indices

class MyVertex:
	def __init__(self, vx=0.0,vy=0.0,vz=0.0,vnx=0.0,vny=0.0,vnz=0.0):
		self.x, self.y, self.z = vx, vy, vz
		self.nx, self.ny, self.nz = vnz, vny, vnz


class MyFace:
	def __init__(self, vn1=0,vn2=0,vn3=0,vnx=0.0,vny=0.0,vnz=0.0):
		self.v1, self.v2, self.v3 = vn1, vn2, vn3
		self.nx, self.ny, self.nz = vnz, vny, vnz

class NvFaceInfo:
	# vertex indices
	def __init__(self,v0,v1,v2):
		self.m_v0, self.m_v1, self.m_v2 = v0, v1, v2
		self.m_stripId      = -1
		self.m_testStripId  = -1
		self.m_experimentId = -1

# nice and dumb edge class that points knows its
# indices, the two faces, and the next edge using
# the lesser of the indices
class NvEdgeInfo:
	# constructor puts 1 ref on us
	def __init__(self, v0, v1):
		self.m_v0       = v0
		self.m_v1       = v1
		self.m_face0    = None
		self.m_face1    = None
		self.m_nextV0   = None
		self.m_nextV1   = None

		# we will appear in 2 lists.  this is a good
		# way to make sure we delete it the second time
		# we hit it in the edge infos
		self.m_refCount = 2

	# ref and unref
	def Unref(self):
		self.m_refCount -= 1
		if self.m_refCount == 0:
			del self

# This class is a quick summary of parameters used
# to begin a triangle strip.  Some operations may
# want to create lists of such items, so they were
# pulled out into a class
class NvStripStartInfo:
	def __init__(self, startFace, startEdge, toV1):
		self.m_startFace = startFace
		self.m_startEdge = startEdge
		self.m_toV1 = toV1


# This is a summary of a strip that has been built
class NvStripInfo:
	#  A little information about the creation of the triangle strips
	def __init__(self, startInfo, stripId, experimentId = -1):
		self.m_stripId = stripId
		self.m_experimentId = experimentId
		self.visited = 0
		self.m_startInfo = startInfo
		self.m_faces = []

	def __del__(self):
		del self.m_startInfo
		del self.m_faces

	def IsExperiment(self):
		if self.m_experimentId >= 0: return True
		else: return False

	def IsInStrip(self, faceInfo):
		if faceInfo == None:
			return False

		if self.m_experimentId >= 0:
			if faceInfo.m_testStripId == self.m_stripId:
				return True
			else:
				return False
		else:
			if faceInfo.m_stripId == self.n_stripId:
				return True
			else:
				return False

	def SharesEdge(self, faceInfo, edgeInfos):
		# check v0 -> v1 edge
		currEdge = NvStripifier().FindEdgeInfo(edgeInfos, faceInfo.m_v0, faceInfo.m_v1)

		if (self.IsInStrip(currEdge.m_face0)) or (self.IsInStrip(currEdge.m_face1)):
			return True

		# check v1 -> v2 edge
		currEdge = NvStripifier().FindEdgeInfo(edgeInfos, faceInfo.m_v1, faceInfo.m_v2)

		if (self.IsInStrip(currEdge.m_face0)) or (self.IsInStrip(currEdge.m_face1)):
			return True

		# check v2 -> v0 edge
		currEdge = NvStripifier().FindEdgeInfo(edgeInfos, faceInfo.m_v2, faceInfo.m_v0)

		if (self.IsInStrip(currEdge.m_face0)) or (self.IsInStrip(currEdge.m_face1)):
			return True

		return False

	# take the given forward and backward strips and combine them together
	def Combine(self, forward, backward):
		for i in range(len(backward)-1, -1):
			self.m_faces.append(backward[i])

		for i in range(0, len(forward)):
			self.m_faces.append(forward[i])

	# returns true if the face is "unique", i.e. has a vertex which doesn't exist in the faceVec
	def Unique(self, faceVec, face):
		bv0, bv1, bv2 = False,False,False # bools to indicate whether a vertex is in the faceVec or not

		for i in range(0, len(faceVec)):
			if not bv0:
				if (faceVec[i].m_v0 == face.m_v0) and (faceVec[i].m_v1 == face.m_v0) and (faceVec[i].m_v2 == face.m_v0):
					bv0 = True
			if not bv1:
				if (faceVec[i].m_v0 == face.m_v1) and (faceVec[i].m_v1 == face.m_v1) and (faceVec[i].m_v2 == face.m_v1):
					bv1 = True
			if not bv2:
				if (faceVec[i].m_v0 == face.m_v2) and (faceVec[i].m_v1 == face.m_v2) and (faceVec[i].m_v2 == face.m_v2):
					bv2 = True
			# the face is not unique, all it's vertices exist in the face vector
			if bv0 and bv1 and bv2:
				return False

		# if we get out here, it's unique
		return True

	# mark the triangle as taken by this strip
	def IsMarked(self, faceInfo):
		if (faceInfo.m_stripId >= 0) or (self.IsExperiment() and (faceInfo.m_experimentId == self.m_experimentId)):
			return True
		else:
			return False

	def MarkTriangle(self, faceInfo):
		if self.IsMarked(faceInfo):
			print "WARNING: strip error!"
		if self.IsExperiment():
			faceInfo.m_experimentId = self.m_experimentId
			faceInfo.m_testStripId = self.m_stripId
		else:
			if faceInfo.m_stripId != -1:
				print "WARNING: strip error!"
			faceInfo.m_experimentId = -1
			faceInfo.m_stripId = self.m_stripId

	# build the strip
	def Build(self, edgeInfos, faceInfos):
		# used in building the strips forward and backward
		scratchIndices = array('H')

		# build forward... start with the initial face
		forwardFaces, backwardFaces = [], []
		forwardFaces.append(self.m_startInfo.m_startFace) # pointer

		self.MarkTriangle(self.m_startInfo.m_startFace)

		if self.m_startInfo.m_toV1: v0 = self.m_startInfo.m_startEdge.m_v0
		else: v0 = self.m_startInfo.m_startEdge.m_v1

		if self.m_startInfo.m_toV1: v1 = self.m_startInfo.m_startEdge.m_v1
		else: v1 = self.m_startInfo.m_startEdge.m_v0

		# easiest way to get v2 is to use this function which requires the
		# other indices to already be in the list.
		scratchIndices.append(v0)
		scratchIndices.append(v1)
		v2 = NvStripifier().GetNextIndex(scratchIndices, self.m_startInfo.m_startFace)
		scratchIndices.append(v2)

		#
		# build the forward list
		#
		nv0 = v1
		nv1 = v2

		nextFace = NvStripifier().FindOtherFace(edgeInfos, nv0, nv1, self.m_startInfo.m_startFace)
		while (nextFace != None) and (not self.IsMarked(nextFace)):
			# this tests to see if a face is "unique", meaning that its vertices aren't already in the list
			# so, strips which "wrap-around" are not allowed
			if not self.Unique(forwardFaces, nextFace):
				break

			# add this to the strip
			forwardFaces.append(nextFace)

			self.MarkTriangle(nextFace)

			# add the index

			nv0 = nv1
			nv1 = NvStripifier().GetNextIndex(scratchIndices, nextFace)
			scratchIndices.append(nv1)

			# and get the next face
			nextFace = NvStripifier().FindOtherFace(edgeInfos, nv0, nv1, nextFace)

		# tempAllFaces is going to be forwardFaces + backwardFaces
		# it's used for Unique()
		tempAllFaces = []
		for i in range(0, len(forwardFaces)):
			tempAllFaces.append(forwardFaces[i])

		#
		# reset the indices for building the strip backwards and do so
		#
		del scratchIndices
		scratchIndices = array('H')
		scratchIndices.append(v2)
		scratchIndices.append(v1)
		scratchIndices.append(v0)
		nv0 = v1
		nv1 = v0

		nextFace = NvStripifier().FindOtherFace(edgeInfos, nv0, nv1, self.m_startInfo.m_startFace)
		while (nextFace != None) and (not self.IsMarked(nextFace)):
			# this tests to see if a face is "unique", meaning that its vertices aren't already in the list
			# so, strips which "wrap-around" are not allowed
			if not self.Unique(tempAllFaces, nextFace):
				break

			# add this to the strip
			backwardFaces.append(nextFace)

			# this is just so Unique() will work
			tempAllFaces.append(nextFace)

			self.MarkTriangle(nextFace)

			# add the index
			nv0 = nv1
			nv1 = NvStripifier().GetNextIndex(scratchIndices, nextFace)
			scratchIndices.append(nv1)

			# and get the next face
			nextFace = NvStripifier().FindOtherFace(edgeInfos, nv0, nv1, nextFace)

		# Combine the forward and backwards stripification lists and put into our own face vector
		self.Combine(forwardFaces, backwardFaces)

#The actual stripifier
class NvStripifier:	
	def __init__(self):
		self.indices = array('H')
		self.cacheSize = 0
		self.minStripLength = 0
		self.meshJump = 0.0
		self.bFirstTimeResetPoint = 0

	def __del__(self):
		if self.indices != None:
			del self.indices
			self.indices = None

	# the target vertex cache size, the structure to place the strips in, and the input indices
	def Stripify(self, in_indices, in_cacheSize, in_minStripLength, outStrips, outFaceList):
		self.meshJump = 0.0
		self.bFirstTimeResetPoint = 1 # used in FindGoodResetPoint()

		# the number of times to run the experiments
		numSamples = 10
		self.cacheSize = in_cacheSize
		self.minStripLength = in_minStripLength # this is the strip size threshold below which we dump the strip into a list

		self.indices = in_indices

		# build the stripification info
		allFaceInfos = []
		allEdgeInfos = []

		self.BuildStripifyInfo(allFaceInfos, allEdgeInfos)

		allStrips = []

		# stripify
		self.FindAllStrips(allStrips, allFaceInfos, allEdgeInfos, numSamples)

		# split up the strips into cache friendly pieces, optimize them, then dump these into outStrips
		self.SplitUpStripsAndOptimize(allStrips, outStrips, allEdgeInfos, outFaceList)

		# clean up
		del allStrips[0:]

		for i in range(0, len(allEdgeInfos)):
			info = allEdgeInfos[i]
			while info != None:
				if info.m_v0 == i:
					next = info.m_nextV0
				else:
					next = info.m_nextV1
				info.Unref()
				info = next

	def GetUniqueVertexInB(self, faceA, faceB):
		facev0 = faceB.m_v0
		if (facev0 != faceA.m_v0) and (facev0 != faceA.m_v1) and (facev0 != faceA.m_v2):
			return facev0

		facev1 = faceB.m_v1
		if (facev1 != faceA.m_v0) and (facev1 != faceA.m_v1) and (facev1 != faceA.m_v2):
			return facev1

		facev2 = faceB.m_v2
		if (facev2 != faceA.m_v0) and (facev2 != faceA.m_v1) and (facev2 != faceA.m_v2):
			return facev2

		# Nothing is shared
		return -1

	def GetSharedVertex(self, faceA, faceB):
		facev0 = faceB.m_v0
		if (facev0 == faceA.m_v0) or (facev0 == faceA.m_v1) or (facev0 == faceA.m_v2):
			return facev0

		facev1 = faceB.m_v1
		if (facev1 == faceA.m_v0) or (facev1 == faceA.m_v1) or (facev1 == faceA.m_v2):
			return facev1

		facev2 = faceB.m_v2
		if (facev2 == faceA.m_v0) or (facev2 == faceA.m_v1) or (facev2 == faceA.m_v2):
			return facev2

		# Nothing is shared
		return -1

	# Big mess of functions called during stripification

	def FindTraversal(self, faceInfos, edgeInfos, strip, startInfo):
		# if the strip was v0->v1 on the edge, then v1 will be a vertex in the next edge.

		if strip.m_startInfo.m_toV1:
			v = strip.m_startInfo.m_startEdge.m_v1
		else:
			v = strip.m_startInfo.m_startEdge.m_v0

		untouchedFace = None
		edgeIter = edgeInfos[v]

		while edgeIter != None:
			face0 = edgeIter.m_face0
			face1 = edgeIter.m_face1
			if (face0 != None) and (not strip.IsInStrip(face0)) and (face1 != None) and (not strip.IsMarked(face1)):
				untouchedFace = face1
				break
			if (face1 != None) and (not strip.IsInStrip(face1)) and (face0 != None) and (not strip.IsMarked(face0)):
				untouchedFace = face0
				break

			# find the next edgeIter
			if edgeIter.m_v0 == v:
				edgeIter = edgeIter.m_nextV0
			else:
				edgeIter = edgeIter.m_nextV1

		startInfo.m_startFace = untouchedFace
		startInfo.m_startEdge = edgeIter
		if edgeIter != None:
			if strip.SharesEdge(startInfo.m_startFace, edgeInfos):
				if edgeIter.m_v0 == v:
					startInfo.m_toV1 = True # note! used to be m_v1
				else:
					startInfo.m_toV1 = False
			else:
				if edgeIter.m_v1 == v:
					startInfo.m_toV1 = True # note! used to be m_v1
				else:
					startInfo.m_toV1 = False
		if startInfo.m_startFace != None:
			return True
		else:
			return False

	def GetNextIndex(self, indices, face):
		# NOTE: do we use the self.indices?!
		numIndices = len(indices)
		if numIndices < 2:
			print "WARNING: Strip Error"

		v0 = indices[numIndices-2]
		v1 = indices[numIndices-1]

		fv0 = face.m_v0
		fv1 = face.m_v1
		fv2 = face.m_v2

		if (fv0 != v0) and (fv0 != v1):
			if ((fv1 != v0) and (fv1 != v1)) or ((fv2 != v0) and (fv2 != v1)):
				# TODO: put into dump file
				print "HMM"
				# 0,"GetNextIndex: Triangle doesn't have all of its vertices\n"
				# 0,"GetNextIndex: Duplicate triangle probably got us derailed\n"
			return fv0
		if (fv1 != v0) and (fv1 != v1):
			if ((fv0 != v0) and (fv0 != v1)) or ((fv2 != v0) and (fv2 != v1)):
				# TODO: put into dump file
				print "HMM"
				# 0,"GetNextIndex: Triangle doesn't have all of its vertices\n"
				# 0,"GetNextIndex: Duplicate triangle probably got us derailed\n"
			return fv1
		if (fv2 != v0) and (fv2 != v1):
			if ((fv0 != v0) and (fv0 != v1)) or ((fv1 != v0) and (fv1 != v1)):
				# TODO: put into dump file
				print "HMM"
				# 0,"GetNextIndex: Triangle doesn't have all of its vertices\n"
				# 0,"GetNextIndex: Duplicate triangle probably got us derailed\n"
			return fv2

		# shouldn't get here
		# TODO: put into dump file
		# 0,"GetNextIndex: Duplicate triangle sent\n"
		return -1

	def FindEdgeInfo(self, edgeInfos, v0, v1):
		# we can get to it through either array
		# because the edge infos have a v0 and v1
		# and there is no order except how it was
		# first created.

		# TODO: Fix
		# TODO: determine if problem still exists!!
		# We are caught in a lovely infinate loop here

		infoIter = edgeInfos[v0]
		while infoIter != None:
			if infoIter.m_v0 == v0:
				if infoIter.m_v1 == v1:
					return infoIter
				else:
					infoIter = infoIter.m_nextV0

			else:
				if infoIter.m_v1 != v0:
					print "WARNING: Strip Error"
				if infoIter.m_v0 == v1:
					return infoIter
				else:
					infoIter = infoIter.m_nextV1
		return None

	def FindOtherFace(self, edgeInfos, v0, v1, faceInfo):
		edgeInfo = self.FindEdgeInfo(edgeInfos, v0, v1)
		if edgeInfo == None:
			print "WARNING: Strip Error"

		if edgeInfo.m_face0 == faceInfo:
			return edgeInfo.m_face1
		else:
			return edgeInfo.m_face0

	def FindGoodResetPoint(self, faceInfos, edgeInfos):
		# we hop into different areas of the mesh to try to get
		# other large open spans done.  Areas of small strips can
		# just be left to triangle lists added at the end.
		result = None

		if result == None:
			numFaces = len(faceInfos)
			startPoint = 0
			if self.bFirstTimeResetPoint:
				# first time, find a face with few neighbors (look for an edge of the mesh)
				startPoint = self.FindStartPoint(faceInfos, edgeInfos)
				bFirstTimeResetPoint = 0
			else:
				startPoint = int((numFaces - 1) * self.meshJump)

			if startPoint == -1:
				startPoint = int((numFaces - 1) * self.meshJump)

			i = startPoint

			# (Do code in following while first)

			# if this guy isn't visited, try him
			if faceInfos[i].m_stripId < 0:
				result  = faceInfos[i]
				return result

			# update the index and clamp to 0-(numfaces-1)
			if (i+1 >= numFaces):
				i = 0

			while i != startPoint:
				# if this guy isn't visited, try him
				if faceInfos[i].m_stripId < 0:
					result  = faceInfos[i]
					break

				# update the index and clamp to 0-(numfaces-1)
				if (i+1 >= numFaces):
					i = 0

			# update the meshJump
			self.meshJump += 0.1
			if self.meshJump > 1.0:
				self.meshJump = .05

		# return the best face we found
		return result

	def FindAllStrips(self, allStrips, allFaceInfos, allEdgeInfos, numSamples):
		# the experiments
		experimentId = 0
		stripId = 0
		done = 0

		loopCtr = 0

		while not done:
			loopCtr += 1

			#
			# PHASE 1: Set up numSamples * numEdges experiments
			#

			experiments = [] #array of tests
			for i in range(0, numSamples * 6):
				experiments.append([])
			experimentIndex = 0
			resetPoints = []
			for i in range(0, numSamples):

				# Try to find another good reset point.
				# If there are none to be found, we are done
				nextFace = self.FindGoodResetPoint(allFaceInfos, allEdgeInfos)
				if nextFace == None:
					done = 1
					break
				else:
					# If we have already evaluated starting at this face in this slew
					# of experiments, then skip going any further

					for i in range(0, len(resetPoints)):
						if resetPoints[i] == nextFace:
							break
					if i != len(resetPoints):
						continue

				# trying it now...
				resetPoints.append(nextFace)

				# otherwise, we shall now try experiments for starting on the 01,12, and 20 edges
				if nextFace.m_stripId >= 0:
					print "WARNING: strip error!"

				# build the strip off of this face's 0-1 edge
				edge01 = self.FindEdgeInfo(allEdgeInfos, nextFace.m_v0, nextFace.m_v1)
				strip01 = NvStripInfo(NvStripStartInfo(nextFace, edge01, 0), stripId, experimentId)
				stripId += 1
				experimentId += 1
				experiments[experimentIndex].append(strip01)
				experimentIndex += 1

				# build the strip off of this face's 1-0 edge
				edge10 = self.FindEdgeInfo(allEdgeInfos, nextFace.m_v1, nextFace.m_v0)
				strip10 = NvStripInfo(NvStripStartInfo(nextFace, edge10, 0), stripId, experimentId)
				stripId += 1
				experimentId += 1
				experiments[experimentIndex].append(strip10)
				experimentIndex += 1

				# build the strip off of this face's 1-2 edge
				edge12 = self.FindEdgeInfo(allEdgeInfos, nextFace.m_v1, nextFace.m_v2)
				strip12 = NvStripInfo(NvStripStartInfo(nextFace, edge12, 0), stripId, experimentId)
				stripId += 1
				experimentId += 1
				experiments[experimentIndex].append(strip12)
				experimentIndex += 1

				# build the strip off of this face's 2-1 edge
				edge21 = self.FindEdgeInfo(allEdgeInfos, nextFace.m_v2, nextFace.m_v1)
				strip21 = NvStripInfo(NvStripStartInfo(nextFace, edge21, 0), stripId, experimentId)
				stripId += 1
				experimentId += 1
				experiments[experimentIndex].append(strip21)
				experimentIndex += 1

				# build the strip off of this face's 2-0 edge
				edge20 = self.FindEdgeInfo(allEdgeInfos, nextFace.m_v2, nextFace.m_v0)
				strip20 = NvStripInfo(NvStripStartInfo(nextFace, edge20, 0), stripId, experimentId)
				stripId += 1
				experimentId += 1
				experiments[experimentIndex].append(strip20)
				experimentIndex += 1

				# build the strip off of this face's 0-2 edge
				edge02 = self.FindEdgeInfo(allEdgeInfos, nextFace.m_v0, nextFace.m_v2)
				strip02 = NvStripInfo(NvStripStartInfo(nextFace, edge10, 0), stripId, experimentId)
				stripId += 1
				experimentId += 1
				experiments[experimentIndex].append(strip02)
				experimentIndex += 1

			#
			# PHASE 2: Iterate through that we setup in the last phase
			# and really build each of the strips and strips that follow to see how
			# far we get
			#
			numExperiments = experimentIndex
			for i in range(0, numExperiments):

				# get the strip set

				# build the first strip of the list
				experiments[i][0].Build(allEdgeInfos, allFaceInfos)
				experimentId = experiments[i][0].m_experimentId

				stripIter = experiments[i][0]
				startInfo = NvStripStartInfo(None, None, 0)
				while self.FindTraversal(allFaceInfos, allEdgeInfos, stripIter, startInfo):

					# create the new strip info
					stripIter = NvStripInfo(startInfo, stripId, experimentId)
					stripId += 1

					# build the next strip
					stripIter.Build(allEdgeInfos, allFaceInfos)

					# add it to the list
					experiments[i].append(stripIter)

			#
			# Phase 3: Find the experiment that has the most promise
			#
			bestIndex = 0
			bestValue = 0
			for i in range(0, numExperiments):
				avgStripSizeWeight = 1.0
				numTrisWeight = 1.0
				avgStripSize = self.AvgStripSize(experiments[i])
				numStrips = float(len(experiments[i]))
				value = avgStripSize * avgStripSizeWeight + (avgStripSize * numStrips * numTrisWeight)

				if value > bestValue:
					bestValue = value
					bestIndex = i

			#
			# Phase 4: commit the best experiment of the bunch
			#
			self.CommitStrips(allStrips, experiments[bestIndex])

			# and destroy all the others

			for i in range(0, numExperiments):
				if i != bestIndex:
					j = 0
					while len(experiments[i]) != 0:
						del experiments[i][j]

			# delete the array that we used for all experiments
			del experiments

	def SplitUpStripsAndOptimize(self, allStrips, outStrips, edgeInfos, outFaceList):
		threshold = self.cacheSize - 4
		tempStrips = []

		# split up strips into threshold-sized pieces
		for i in range(0, len(allStrips)):
			currentStrip = None
			startInfo = NvStripStartInfo(None, None, 0)

			if len(allStrips[i].m_faces) > threshold:

				numTimes = int(len(allStrips[i].m_faces) / threshold)
				numLeftover = int(len(allStrips[i].m_faces) % threshold)

				for j in range(0, numTimes):
					currentStrip = NvStripInfo(startInfo, 0, -1)

					for faceCtr in range(j*threshold, threshold+(j*threshold)):
						currentStrip.m_faces.append(allStrips[i].m_faces[faceCtr])

					tempStrips.append(currentStrip)

				leftOff = j * threshold

				if numLeftover != 0:
					currentStrip = NvStripInfo(startInfo, 0, -1)

					for k in range(0, numLeftover):
						currentStrip.m_faces.append(allStrips[i].m_faces[leftOff])
						leftOff += 1

					tempStrips.append(currentStrip)
			else:
				# we're not just doing a tempStrips.push_back(allBigStrips[i]) because
				# this way we can delete allBigStrips later to free the memory
				currentStrip = NvStripInfo(startInfo, 0, -1)

				for j in range(0, len(allStrips[i].m_faces)):
					currentStrip.m_faces.append(allStrips[i].m_faces[j])

				tempStrips.append(currentStrip)

		# add small strips to face list
		tempStrips2 = []
		self.RemoveSmallStrips(tempStrips, tempStrips2, outFaceList)

		del outStrips
		outStrips = []

		if len(tempStrips2) != 0:
			# Optimize for the vertex cache
			vcache = VertexCache(cacheSize)

			bestNumHits = -1.0
			numHits = 0.0
			bestIndex = 0
			done = 0

			firstIndex = 0
			minCost = 100000.0

			for i in range(0, len(tempStrips2)):
				numNeighbours = 0

				# find strip with least number of neighbors per face
				for j in tempStrips2[i].m_faces:
					numNeighbours += self.NumNeighbors(j, edgeInfos)

				currCost = float(numNeighbors)
				if currCost < minCost:
					minCost = currCost
					firstIndex = i

			self.UpdateCacheStrip(vcache, tempStrips2[firstIndex])
			outStrips.append(tempStrips2[firstIndex])

			tempStrips2[firstIndex].visited = True

			# this n^2 algo is what slows down stripification so much....
			# needs to be improved
			while (1):
				bestNumHits = -1.0

				for i in range(0, len(tempStrips2)):
					if tempStrips2[i].visited:
						continue

					numHits = self.CalcNumHitsStrip(vache, tempStrips2[i])
					if numHits > bestNumHits:
						bestNumHits = numHits
						bestIndex = i

				if bestNumHits == -1.0:
					break
				tempStrips2[bestIndex].visited = True
				self.UpdateCacheStrip(vcache, tempStrips2[bestIndex])
				outStrips.append(tempStrips2[bestIndex])

			del vcache

	def RemoveSmallStrips(self, allStrips, allBigStrips, faceList):
		del faceList
		faceList = []
		del allBigStrips
		allBigStrips = [] # make sure these are empty
		tempFaceList = []

		i = 0
		while i < len(allStrips):
			if len(allStrips[i].m_faces) < self.minStripLength:
				# strip is too small, add faces to faceList
				for j in range(0, len(allStrips[i].m_faces)):
					tempFaceList.append(allStrips[i].m_faces[j])

				# and free memory
				del allStrips[i]
			else:
				allBigStrips.append(allStrips[i])
			i += 1

		bVisitedList = []
		for b in range(0, len(tempFaceList)):
			bVisitedList.append(False)

		vcache = VertexCache(self.cacheSize)

		bestNumHits = -1
		numHits = -1
		bestIndex = -1

		while 1:
			bestNumHits = -1

			# find best face to add next, given the current cache
			for i in range(0, len(tempFaceList)):
				if bVisitedList[i]:
					continue

				numHits = self.CalcNumHitsFace(vcache, tempFaceList[i])
				if numHits > bestNumHits:
					bestNumHits = numHits
					bestIndex = i

			if bestNumHits == -1.0:
				break
			bVisitedList[bestIndex] = True
			self.UpdateCacheFace(vcache, tempFaceList[bestIndex])
			faceList.append(tempFaceList[bestIndex])

		del vcache
		del bVisitedList

	def CountRemainingTris(self, itera, end, tris):
		count = 0
		while itera != end:
			count += len(tris[itera].m_faces)
			itera += 1
		return count

	def CommitStrips(self, allStrips, strips):
		# Iterate through strips
		numStrips = len(strips)
		for i in range(0, numStrips):
			# Tell the strip that it is now real
			strips[i].m_experimentId = -1

			# add to the list of real strips
			allStrips.append(strips[i])

			# Iterate through the faces of the strip
			# Tell the faces of the strip that they belong to a real strip now
			faces = strips[i].m_faces
			numFaces = len(faces)

			for j in range(0, numFaces):
				strips[i].MarkTriangle(faces[j])

	def AvgStripSize(self, strips):
		sizeAccum = 0
		numStrips = len(strips)
		for i in range(0, numStrips):
			sizeAccum += len(strips[i].m_faces)

		return float(sizeAccum / numStrips)

	def FindStartPoint(self, faceInfos, edgeInfos):
		for i in range(0, len(faceInfos)):
			ctr = 0
			if self.FindOtherFace(edgeInfos, faceInfos[i].m_v0, faceInfos[i].m_v1, faceInfos[i]) == None:
				ctr += 1
			if self.FindOtherFace(edgeInfos, faceInfos[i].m_v1, faceInfos[i].m_v2, faceInfos[i]) == None:
				ctr += 1
			if self.FindOtherFace(edgeInfos, faceInfos[i].m_v2, faceInfos[i].m_v0, faceInfos[i]) == None:
				ctr += 1
			if ctr > 1:
				return True
		return -1

	def UpdateCacheStrip(self, vcache, strip):
		for f in strip.m_faces:
			self.UpdateCacheFace(vcache, f)

	def UpdateCacheFace(self, vcache, face):
		if not vcache.InCache(face.m_v0):
			vcache.addEntry(face.m_v0)
		if not vcache.InCache(face.m_v1):
			vcache.addEntry(face.m_v1)
		if not vcache.InCache(face.m_v2):
			vcache.addEntry(face.m_v2)

	def CalcNumHitsStrip(self, vcache, strip):
		numHits = 0
		numFaces = 0

		for f in strip.m_faces:
			numHits += self.CalcNumHitsFace(vcache, f)
			numFaces += 1

		return float(numHits / numFaces)

	def CalcNumHitsFace(self, vcache, face):
		numHits = 0

		if vcache.InCache(face.m_v0):
			numHits += 1

		if vcache.InCache(face.m_v1):
			numHits += 1

		if vcache.InCache(face.m_v2):
			numHits += 1

		return numHits

	def NumNeighbors(self, face, edgeInfoVec):
		numNeighbors = 0

		if self.FindOtherFace(edgeInfoVec, face.m_v0, face.m_v1, face) != None:
			numNeighbours += 1
		if self.FindOtherFace(edgeInfoVec, face.m_v1, face.m_v2, face) != None:
			numNeighbours += 1
		if self.FindOtherFace(edgeInfoVec, face.m_v2, face.m_v0, face) != None:
			numNeighbours += 1
		return numNeighbours

	def BuildStripifyInfo(self, faceInfos, edgeInfos):
		# reserve space for the face infos, but do not resize them.
		numIndices = len(self.indices)

		# we actually resize the edge infos, so we must initialize to NULL
		for i in range(0, numIndices):
			edgeInfos.append(None)

		# iterate through the triangles of the triangle list
		numTriangles = numIndices / 3
		index = 0
		for i in range(0, numTriangles):
			# grab the indices
			v0 = self.indices[index]
			v1 = self.indices[index+1]
			v2 = self.indices[index+2]
			index += 3 # << TODO: check

			# create the face info and add it to the list of faces, but only if this exact face doesn't already
			# exist in the list
			faceInfo = NvFaceInfo(v0, v1, v2)
			if not self.AlreadyExists(faceInfo, faceInfos):
				faceInfos.append(faceInfo)

				# grab the edge infos, creating them if they do not already exist
				edgeInfo01 = self.FindEdgeInfo(edgeInfos, v0, v1)
				if edgeInfo01 == None:

					# create the info
					edgeInfo01 = NvEdgeInfo(v0, v1)

					# update the linked list on both
					edgeInfo01.m_nextV0 = edgeInfos[v0]
					edgeInfo01.m_nextV1 = edgeInfos[v1]
					edgeInfos[v0] = edgeInfo01
					edgeInfos[v1] = edgeInfo01

					# set face 0
					edgeInfo01.m_face0 = faceInfo
				else:
					if edgeInfo01.m_face1 != None:
						# TODO: not an assert...dump in dump file or something...
						print "BuildStripifyInfo: > 2 triangles on an edge... uncertain consequences"
					else:
						edgeInfo01.m_face1 = faceInfo

				# grab the edge infos, creating them if they do not already exist
				edgeInfo12 = self.FindEdgeInfo(edgeInfos, v1, v2)
				if edgeInfo12 == None:

					# create the info
					edgeInfo12 = NvEdgeInfo(v1, v2)

					# update the linked list on both
					edgeInfo12.m_nextV0 = edgeInfos[v1]
					edgeInfo12.m_nextV1 = edgeInfos[v2]
					edgeInfos[v1] = edgeInfo12
					edgeInfos[v2] = edgeInfo12

					# set face 0
					edgeInfo12.m_face0 = faceInfo
				else:
					if edgeInfo12.m_face1 != None:
						# TODO: not an assert...dump in dump file or something...
						print "BuildStripifyInfo: > 2 triangles on an edge... uncertain consequences"
					else:
						edgeInfo12.m_face1 = faceInfo

				# grab the edge infos, creating them if they do not already exist
				edgeInfo20 = self.FindEdgeInfo(edgeInfos, v2, v0)
				if edgeInfo20 == None:

					# create the info
					edgeInfo20 = NvEdgeInfo(v2, v0)

					# update the linked list on both
					edgeInfo20.m_nextV0 = edgeInfos[v2]
					edgeInfo20.m_nextV1 = edgeInfos[v0]
					edgeInfos[v2] = edgeInfo20
					edgeInfos[v0] = edgeInfo20

					# set face 0
					edgeInfo20.m_face0 = faceInfo
				else:
					if edgeInfo20.m_face1 != None:
						# TODO: not an assert...dump in dump file or something...
						print "BuildStripifyInfo: > 2 triangles on an edge... uncertain consequences"
					else:
						edgeInfo20.m_face1 = faceInfo

	def AlreadyExists(self, faceInfo, faceInfos):
		for i in range(0, len(faceInfos)):
			if (faceInfos[i].m_v0 == faceInfo.m_v0) and (faceInfos[i].m_v1 == faceInfo.m_v1) and (faceInfos[i].m_v2 == faceInfo.m_v2):
			   	return True
		return False


