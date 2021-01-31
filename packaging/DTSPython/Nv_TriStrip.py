from Nv_TriStripObjects import *
import array
from array import *

# TODO: Need to check!
# TODO: Don't forget another pythonization pass!

CACHESIZE_GEFORCE1_2 = 16
CACHESIZE_CACHESIZE_GEFORCE3 = 24

cacheSize = CACHESIZE_GEFORCE1_2
bStitchStrips = True
minStripSize = 0
bListsOnly = False

'''
 SetListsOnly()

 If set to true, will return an optimized list, with no strips at all.

 Default value: False
'''
def SetListsOnly(_bListsOnly):
	global bListsOnly 
	bListsOnly = _bListsOnly

'''
 SetCacheSize()

 Sets the cache size which the stripfier uses to optimize the data.
 Controls the length of the generated individual strips.
 This is the "actual" cache size, so 24 for GeForce3 and 16 for GeForce1/2
 You may want to play around with this number to tweak performance.

 Default value: 16
'''
def SetCacheSize(_cacheSize):
	global cacheSize
	cacheSize = _cacheSize


'''
 SetStitchStrips()

 bool to indicate whether to stitch together strips into one huge strip or not.
 If set to true, you'll get back one huge strip stitched together using degenerate
  triangles.
 If set to false, you'll get back a large number of separate strips.

 Default value: true
'''
def SetStitchStrips(_bStitchStrips):
	global bStitchStrips
	bStitchStrips = _bStitchStrips


'''
 SetMinStripSize()

 Sets the minimum acceptable size for a strip, in triangles.
 All strips generated which are shorter than this will be thrown into one big, separate list.

 Default value: 0
'''
def SetMinStripSize(_minStripSize):
	global minStripSize
	minStripSize = _minStripSize

'''
 GenerateStrips()

 in_indices: input index list, the indices you would use to render
 in_numIndices: number of entries in in_indices
 primGroups: array of optimized/stripified PrimitiveGroups
 numGroups: number of groups returned

 Be sure to call delete[] on the returned primGroups to adef leaking mem
'''
def GenerateStrips(in_indices):
	# NOTE: Needs to return indices and prim groups
	global bListsOnly 
	global minStripSize
	global bStitchStrips
	global cacheSize
	# put data in format that the stripifier likes
	tempIndices = []*len(in_indices)
	maxIndex = 0
	
	for i in range(0, len(in_indices)):
		tempIndices[i] = in_indices[i]
		if in_indices[i] > maxIndex:
			maxIndex = in_indices[i]
	
	tempStrips = NVStripInfoVec()
	tempFaces = NVFaceInfoVec()

	stripifier = NvStripifier()
	
	# do actual stripification
	stripifier.Stripify(tempIndices, cacheSize, minStripSize, maxIndex, tempStrips, tempFaces)

	# stitch strips together
	stripIndices = IntVec()
	numSeparateStrips = 0

	if bListsOnly:
		# if we're outputting only lists, we're done
		*numGroups = 1
		(*primGroups) = new PrimitiveGroup[*numGroups]
		PrimitiveGroup* primGroupArray = *primGroups

		# count the total number of indices
		numIndices = 0
		for i in range(0, len(tempStrips)):
			numIndices += len(tempStrips[i].m_faces) * 3

		# add in the list
		numIndices += len(tempFaces) * 3

		primGroupArray[0].type       = PT_LIST
		primGroupArray[0].numIndices = numIndices
		primGroupArray[0].indices    = new unsigned short[numIndices]

		# do strips
		indexCtr = 0
		for i in range(0, len(tempStrips):
			for j in range(0, len(tempStrips[i].m_faces)):
				# degenerates are of no use with lists
				if not NvStripifier().IsDegenerate(tempStrips[i].m_faces[j]):
					primGroupArray[0].indices[indexCtr++] = tempStrips[i].m_faces[j].m_v0
					primGroupArray[0].indices[indexCtr++] = tempStrips[i].m_faces[j].m_v1
					primGroupArray[0].indices[indexCtr++] = tempStrips[i].m_faces[j].m_v2
				else:
					# we've removed a tri, reduce the number of indices
					primGroupArray[0].numIndices -= 3

		# do lists
		for i in range(0, len(tempFaces)):
			primGroupArray[0].indices[indexCtr++] = tempFaces[i].m_v0
			primGroupArray[0].indices[indexCtr++] = tempFaces[i].m_v1
			primGroupArray[0].indices[indexCtr++] = tempFaces[i].m_v2
	else:
		stripifier.CreateStrips(tempStrips, stripIndices, bStitchStrips, numSeparateStrips)

		# if we're stitching strips together, we better get back only one strip from CreateStrips()
		#assert( (bStitchStrips && (numSeparateStrips == 1)) || !bStitchStrips)
		
		# convert to output format
		*numGroups = numSeparateStrips #for the strips
		if len(tempFaces.size) != 0:
			(*numGroups)++  #we've got a list as well, increment
		(*primGroups) = new PrimitiveGroup[*numGroups]
		
		PrimitiveGroup* primGroupArray = *primGroups
		
		# first, the strips
		startingLoc = 0
		for stripCtr in range(0, numSeperateStrips):
			stripLength = 0

			if not bStitchStrips:
				# if we've got multiple strips, we need to figure out the correct length
				for i in range(startingLoc, len(stripIndices)):
					if(stripIndices[i] == -1)
						break
				
				stripLength = i - startingLoc
			else:
				stripLength = len(stripIndices)
			
			primGroupArray[stripCtr].type       = PT_STRIP
			primGroupArray[stripCtr].indices    = new unsigned short[stripLength]
			primGroupArray[stripCtr].numIndices = stripLength
			
			indexCtr = 0
			for(int i = startingLoc i < stripLength + startingLoc i++)
				primGroupArray[stripCtr].indices[indexCtr++] = stripIndices[i]

			# we add 1 to account for the -1 separating strips
			# this doesn't break the stitched case since we'll exit the loop
			startingLoc += stripLength + 1 
		
		# next, the list
		if len(tempFaces) != 0:
			faceGroupLoc = (*numGroups) - 1    #the face group is the last one
			primGroupArray[faceGroupLoc].type       = PT_LIST
			primGroupArray[faceGroupLoc].indices    = new unsigned short[len(tempFaces) * 3]
			primGroupArray[faceGroupLoc].numIndices = len(tempFaces) * 3
			indexCtr = 0
			for i in range(0, len(tempFaces)):
				primGroupArray[faceGroupLoc].indices[indexCtr++] = tempFaces[i].m_v0
				primGroupArray[faceGroupLoc].indices[indexCtr++] = tempFaces[i].m_v1
				primGroupArray[faceGroupLoc].indices[indexCtr++] = tempFaces[i].m_v2

	# clean up everything

	# delete strips
	while len(tempStrips) != 0:
		while len(tempStrips[0].m_faces) != 0:
			del tempStrips[0].m_faces[0]
		del tempStrips[0]
	# delete faces
	while len(tempFaces) != 0:
		del tempFaces[0]
	


'''
 RemapIndices()

 Function to remap your indices to improve spatial locality in your vertex buffer.

 in_primGroups: array of PrimitiveGroups you want remapped
 numGroups: number of entries in in_primGroups
 numVerts: number of vertices in your vertex buffer, also can be thought of as the range
  of acceptable values for indices in your primitive groups.
 remappedGroups: array of remapped PrimitiveGroups

 Note that, according to the remapping handed back to you, you must reorder your 
 vertex buffer.
'''
def RemapIndices(const PrimitiveGroup* in_primGroups, const unsigned short numGroups,const unsigned short numVerts, PrimitiveGroup** remappedGroups):
	global bListsOnly 
	global minStripSize
	global bStitchStrips
	global cacheSize
	(*remappedGroups) = new PrimitiveGroup[numGroups]

	#caches oldIndex -. newIndex conversion
	indexCache = array('l')
	for i in range(0, numVerts): indexCache.append(-1)
	
	#loop over primitive groups
	indexCtr = 0
	for i in range(0, numGroups):
		numIndices = in_primGroups[i].numIndices

		#init remapped group
		(*remappedGroups)[i].type       = in_primGroups[i].type
		(*remappedGroups)[i].numIndices = numIndices
		(*remappedGroups)[i].indices    = new unsigned short[numIndices]

		for j in range(0, numIndices):
			cachedIndex = indexCache[in_primGroups[i].indices[j]]
			if cachedIndex == -1: #we haven't seen this index before
				#point to "last" vertex in VB
				(*remappedGroups)[i].indices[j] = indexCtr

				#add to index cache, increment
				indexCache[in_primGroups[i].indices[j]] = indexCtr++
			else:
				#we've seen this index before
				(*remappedGroups)[i].indices[j] = cachedIndex

	del indexCache
