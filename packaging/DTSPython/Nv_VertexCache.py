
class VertexCache:
	def __init__(self, size=16):
		self.numEntries = size
		self.entries = []
		for i in range(0, self.numEntries):
			self.entries.append(-1)

	def __del__(self):
		del self.entries

	def InCache(self, entry):
		for i in range(0, numEntries):
			if self.entries[i] == entry:
				return True
		return False

	def AddEntry(self, entry):
		removed = self.entries[self.numEntries - 1]

		# Push everything right one
		i = self.numEntries - 2
		while i >= 0:
			self.entries[i+1] = self.entries[i]
			i -= 1

		self.entries[0] = entry
		return removed

	def Clear(self):
		for i in range(0, self.numEntries):
			self.entries[i] = -1

	def Copy(self, inVcache):
		for i in range(0, self.numEntries):
			inVcache.Set(i, self.entries[i])

	def At(self, index):
		return self.entries[index]

	def Set(self, index, value):
		self.entries[index] = value
