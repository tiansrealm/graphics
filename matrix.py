import math

class Matrix(object):
	
	def __init__(self, row, col, list2d = None):
		if list2d != None:
			self.row = len(list2d)
			self.col = len(list2d[0])
			self.mat = list2d
		else:
			self.row = row
			self.col = col
			self.mat = [ [0]*col for i in range(row)]
			if row == col:
				self.identity()
	def set(self, row , col, value):
		if (row <= self.row and col <= self.col):
			self.mat[row][col] = value
		else:
			print "warning: attepmt to get a out of bound value in a Matrix"

	def get(self, row , col):
		if (row <= self.row and col <= self.col):
			return self.mat[row][col]
		else:
			print "warning: attepmt to get a out of bound value in a Matrix"
	def identity(self):
		if(self.row != self.col):
			print "not a square matrix for identity()"
		else:
			for i in range(self.row):
				self.set(i,i,1)	
	def mult(self, other):
		'''self(matrix) is multiplied by other and result is new matrix
			the order is :   self.matrix * other
		'''
		assert(self.col == other.row), \
			"invalid matrix dimension for multiplication {} x {}".format(self.col, other.row)
		ans = Matrix(self.row, other.col)

		reversedOther = map(list, zip(*other.mat))
		for row in range(self.row): 
			for r2 in range(other.col): #col of other = row of reversedOther
				s = 0;
				for col in range(self.col): 
					s += self.mat[row][col] * reversedOther[r2][col] 
				ans.set(row,r2, s)
		return ans
	def reverseMult(self, reversedOther):
		'''unique multiplacation process
			the other matrix's row and col are swapped
			-for the reversed treat col as row and row as col when apply matrix logic
			-ultimately,we want the multiplication to 
			 apply on the second matrix as if it wasn't reversed.
			 Lastly reverse the answer matrix
		'''
		assert(self.col == reversedOther.col), \
			"invalid matrix dimension for reverse multiplication \
				 self.col x reversedOther.col = {} x {}".format(self.col, reversedOther.col)
		ans = Matrix(self.row, reversedOther.row)

		for row in range(self.row): 
			for r2 in range(reversedOther.row): 
				s = 0;
				for col in range(self.col): 
					s += self.mat[row][col] * reversedOther.get(r2,col) 
				ans.set(row,r2, s)
		return ans.reverse()
		
	def reverse(self): 
		self.mat = map(list, zip(*self.mat))
		self.row, self.col = self.col, self.row
		return self
		
	def __str__(self):
		s = ""
		for row in self.mat:
			s += str(row) + "\n"
		return s
	#note: zip(*matrix) returns same matrix with rows and cols swapped
	'''
	[ [1, 2, 3],		[ [1, 4, 7],
  	  [4, 5, 6],   =>     [2, 5, 8],
  	  [7, 8, 9] ]		  [3, 6, 9] ]
  	'''

class TransMatrix(Matrix):
	"""
	4 by 4 matrix used to transformation another
	matrix(with 4 rows) through matrix multiplication 
	"""
	def __init__(self):
		super(TransMatrix, self).__init__(4, 4)	

class EdgeMatrix(Matrix):
	"""EdgeMatrix
	This matrix is actually a veritcal version.
	Three columns with infinite many rows
	Plus a forth colum filled with 1's
	Starts with zero rows. 

	#SHOULD USE matrix reverseMult method for multiplication
	"""
	def __init__(self, sourceMat = None):
		if sourceMat:
			self.mat = sourceMat.mat
			self.row = sourceMat.row
			self.col = sourceMat.col
		else:
			super(EdgeMatrix, self).__init__(0, 4)
class LineEdgeMatrix(EdgeMatrix):
	'''
	Each row is a point
	Every two rows represent a line
	'''
	def __init__(self, sourceMat = None):
		super(LineEdgeMatrix, self).init__(sourceMat)	

	def addLine(self,x1,y1,z1,x2,y2,z2):
		self.mat.append([x1,y1,z1,1])
		self.mat.append([x2,y2,z2,1])
		self.row += 2
class TriangleEdgeMatrix(EdgeMatrix):
	'''
	Each row is a point
	Every three rows represent a line
	'''
	def __init__(self, sourceMat = None):
		super(TriangleEdgeMatrix, self).__init__(sourceMat)

	def addTriangle(self,x1,y1,z1,x2,y2,z2,x3,y3,z3):
		self.mat.append([x1,y1,z1,1])
		self.mat.append([x2,y2,z2,1])
		self.mat.append([x3,y3,3,1])
		self.row += 3

#transformation functions returns a matrixs that you can use to multiply
def moveMat(x,y,z):
	tempMat = TransMatrix()
	tempMat.set(0,3, x) #could've just typed in the matrix
	tempMat.set(1,3, y)
	tempMat.set(2,3, z)
	return tempMat
def scaleMat(x,y,z):
	tempMat = TransMatrix()
	tempMat.set(0,0, x)
	tempMat.set(1,1, y)
	tempMat.set(2,2, z)
	return tempMat
def rotateXMat(angle):
	tempMat = TransMatrix()
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	tempMat.set(1,1, cos)
	tempMat.set(1,2, -sin)
	tempMat.set(2,1, sin)
	tempMat.set(2,2, cos)
	return tempMat

def rotateYMat(angle):
	tempMat = TransMatrix()
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	tempMat.set(0,0, cos)
	tempMat.set(0,2, sin)
	tempMat.set(2,0, -sin)
	tempMat.set(2,2, cos)
	return tempMat
def rotateZMat(angle):	
	tempMat = TransMatrix()
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	tempMat.set(0,0, cos)
	tempMat.set(0,1, -sin)
	tempMat.set(1,0, sin)
	tempMat.set(1,1, cos)
	return tempMat
