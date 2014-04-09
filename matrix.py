

class Matrix(object):
	
	def __init__(self, row, col):
		self.row = row
		self.col = col
		self.mat = [ [0]*col for i in range(row)]
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

class EdgeMatrix(Matrix):
	"""EdgeMatrix
	This matrix is actually a veritcal version.
	Three columns with infinite many rows
	Each row is 3 coordinates x,y,z of a point
	Every two rows is coupled to form a line. a.k.a edge
	Starts with zero rows. 


	"""
	def __init__(self, Mat = None):
		if Mat:
			self.mat = Mat.mat
			self.row = Mat.row
			self.col = Mat.col
		else:
			super(EdgeMatrix, self).__init__(0, 4)
	def addLine(self,x1,y1,z1,x2,y2,z2):
		self.mat.append([x1,y1,z1,1])
		self.mat.append([x2,y2,z2,1])
		self.row += 2
class TransMatrix(Matrix):
	"""
	4 by 4 matrix used to transformation another
	matrix(with 4 rows) through matrix multiplication 
	"""
	def __init__(self):
		super(TransMatrix, self).__init__(4, 4)	
		self.identity()

		