

class Matrix(object):
	
	def __init__(self, row, col):
		self.maxRow = row
		self.maxCol = col
		self.matrix = [ [0]*col for i in range(row)]
		self.identity()
	def identity(self):
		pass
	def set(self, row , col, value):
		if (row <= self.maxRow and col <= self.maxCol):
			self.matrix[row][col] = value
		else:
			print "warning: attepmt to get a out of bound value in a Matrix"

	def get(self, row , col):
		if (row <= self.maxRow and col <= self.maxCol):
			return self.matrix[row][col]
		else:
			print "warning: attepmt to get a out of bound value in a Matrix"
	def mult(self, other):
		'''self(matrix) is multiplied by other and result is new matrix
			the order is :   self.matrix * other
		'''
		assert(other.maxRow == self.maxCol), "invalid matrix dimension for multiplication"
		ans = Matrix(self.maxRow, other.maxCol)

		reversedOther = zip(*other.matrix) 
		for row in range(self.maxRow): 
			for r2 in range(other.maxCol): #maxCol of other = maxRow of reversedOther
				s = 0;
				for col in range(self.maxCol): 
					s += self.matrix[row][col] * reversedOther[r2][col] 
				ans.set(row,r2, s)
		return ans

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
	Each row is 3 coordinates x,yz of a point
	Every two rows is coupled to form a line. a.k.a edge
	Starts with zero rows. 
	"""
	def __init__(self):
		super(EdgeMatrix, self).__init__(0, 3)
	
	def addLine(x1,y1,z1,x2,y2,z2):
		self.matrix.append([x1,y1,z1])
		self.matrix.append([x2,y2,z2])
		
m = EdgeMatrix()
t = Matrix(2,3)
for i in range(2):
	for j in range(3):
		t.set(i,j, i * 3 + j +1)
t2 = Matrix(3,2)
for i in range(3):
	for j in range(2):
		t2.set(i,j, i * 2 + j + 7)

print t.matrix
print t2.matrix
print t.mult(t2).matrix