'''
Dts_Decimate.py

Copyright (c) 2004 - 2005 James Urquhart(j_urquhart@btinternet.com)

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

'''
	Generic Decimator Interface
'''
use_decimator = ""
use_decimator = "VTK"

class Decimate:
	def __init__(self):
		self.clear()
	def __del__(self):
		del self.faces
	def process(self,target=0.5):
		print "Decimate Faces"
	def clear(self):
		self.faces = []

from Decimate_VTK import *

def chooseDecimate():
	global use_decimator
	if use_decimator == "VTK": return VTKDecimate()
	else: return None