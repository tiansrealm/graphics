import math, itertools

class Matrix(object):
	
	def __init__(self, list2d, numRow = None, numCol = None):
		if list2d != None:
			self.numRow = len(list2d)
			self.numCol= len(list2d[0])
			self.list2d = list2d
		else:
			self.numRow = numRow
			self.numCol = numCol
			self.list2d = [ [0]*numCol for i in range(numRow)]
			if numRow == numCol:
				self.identity()
	def set(self, row , col, value):
		if (row <= self.numRow and col <= self.numCol):
			self.list2d[row][col] = value
		else:
			print "warning: attepmt to set in a out of bound location in a Matrix"

	def getValue(self, row , col):
		if (row <= self.numRow and col <= self.numCol):
			return self.list2d[row][col]
		else:
			print "warning: attepmt to get a out of bound value in a Matrix"
	def identity(self):
		assert(self.numRow == self.numCol), "not a square matrix for identity()"
		for i in range(self.numRow):
			self.set(i,i,1)	
	def addRow(self, newRow):
		if len(newRow) > self.numCol:
			raise Exception("adding a row to matrix that is too large")
		self.list2d.append(newRow)
		self.numRow +=1
	def addCol(self, newCol):
		length = len(newCol)
		if length > self.numRow:
			raise Exception("adding a col to matrix that is too large")
		for i in range(length):
			self.list2d[i].extend(newCol[i]) 
	def mult(self, other):
		'''self(matrix) is multiplied by other and result is new matrix
			the order is :   self * other

		'''
		assert(self.numCol == other.numRow), \
		"invalid matrix dimension for multiplication {} x {}".format(self.numCol, other.numRow)
		
		ans = []
		for row in range(self.numRow): 
			currentRow = []
			for c2 in range(other.numCol):
				s = 0;
				for col in range(self.numCol):
					s += self.list2d[row][col] * other.list2d[col][c2] 
				currentRow.append(s)
			ans.append(currentRow)
		return Matrix(ans)

	def __str__(self):
		s = ""
		for row in self.list2d:
			s += str(row) + "\n"
		return s
	#note: map(list,zip(*matrix)) returns same matrix with rows and cols swapped
	'''
	[ [1, 2, 3],		[ [1, 4, 7],
  	  [4, 5, 6],   =>     [2, 5, 8],
  	  [7, 8, 9] ]		  [3, 6, 9] ]
  	'''

#functions that generates transformation matrixs that you can use to multiply with
def moveMat(x,y,z):
	return Matrix([ [1, 0, 0, x],
					[0, 1, 0, y],
					[0, 0, 1, z],
					[0, 0, 0, 1] ])
def scaleMat(x,y,z):
	return Matrix([ [x, 0, 0, 0],
					[0, y, 0, 0],
					[0, 0, z, 0],
					[0, 0, 0, 1] ])
def rotateXMat(angle):
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	return Matrix([ [1,   0,    0, 0],
					[0, cos, -sin, 0],
					[0, sin,  cos, 0],
					[0,   0,    0, 1] ])

def rotateYMat(angle):
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	return Matrix([ [ cos, 0, sin, 0],
					[   0, 1, 0  , 0],
					[-sin, 0, cos, 0],
					[   0, 0, 0  , 1] ])
def rotateZMat(angle):
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	return Matrix([ [cos,-sin, 0, 0],
					[sin, cos, 0, 0],
					[  0,   0, 1, 0],
					[  0,   0, 0, 1] ])


#---------------SHAPES CLASSES---------------------
#Uses Matrices
class MatrixShape(object):
	def __init__(self,triangleList):
		self.triangleList = triangleList
	def move(self, mx,my,mz):
		self.transform(moveMat(mx,my,mz))
	def scale(self, sx,sy,sz):
		self.transform(scaleMat(sx,sy,sz))
	def rotateX(self, angle):
		self.transform(rotateXMat(angle))
	def rotateY(self, angle):
		self.transform(rotateYMat(angle))
	def rotateZ(self, angle):
		self.transform(rotateZMat(angle))
	def transform(self, transMatrixO):
		for triangle in self.triangleList:
			triangle.transform(transMatrixO)

class Point(MatrixShape): # not used
	def __init__(self,x,y,z):
		self.x, self.y, self.z = x, y, z
	def transform(self, transMatrixO):
		self.x, self.y, self.z = transMatrixO.mult(Matrix([[x,y,z,1]])).matrix[:-1]

class Triangle(MatrixShape):
	def __init__(self,p1,p2,p3,matrix = None):
		'''
		matrix should be 4x3 Matrix(object). Last row all 1s. each column represent a vertex.
		taking vertices in counter-clockwise order is the front face of the triangle
		x1 x2 x3
		y1 y2 y3
		z1 z2 z3
		1  1  1
		'''
		if matrix == None:
			temp = [[p1[0],p2[0],p3[0]],
					[p1[1],p2[1],p3[1]],
					[p1[2],p2[2],p3[2]], 
					[    1,    1,    1]]
			self.matrix  = Matrix(temp)
		else:
			self.matrix = matrix
	
	def transform(self, transMatrixO):
		self.matrix = transMatrixO.mult(self.matrix)
	#used for prespective graphics 3d
	def inLineOfSight(self, ex,ey,ez):
		m = self.matrix.list2d
		v1 = [(m[i][1]-m[i][0]) for i in range(3)] #vector_p1p2
		v2 = [(m[i][2]-m[i][1]) for i in range(3)] #vector_p2p3
		sightVector = [m[0][0]-ex, m[0][1]-ey, m[0][2]-ez]
		'''cross product
		v1 X v2 = <v1y*v2z-v1z*v2y, v1z*v2x-v1x*v2z, v1x*v2y-v1y*v2x>
		'''
		normal = \
			[(v1[1]*v2[2]-v1[2]*v2[1]), (v1[2]*v2[0]-v1[0]*v2[2]), (v1[0]*v2[1]-v1[1]*v2[0])]
		dotProduct = sightVector[0]*normal[0]+sightVector[1]*normal[01]+sightVector[2]*normal[2]
		return dotProduct < 0

class Box(MatrixShape):
	'''
	the initialization of a box uses (also spheres)
	9 parameters. scaling(sx,sy,sz),rotation(rx,ry,rz), and translation(mx,my,mz)
	'''
	def __init__(self):
		#unit box
		#vertices: in front counter closewise starting from top left corner
				# then repeat for the back. total 8 vertices
		c = [[-.5, .5, .5],[-.5,-.5, .5],[ .5,-.5, .5],[ .5, .5, .5],
			 [-.5, .5,-.5],[-.5,-.5,-.5],[ .5,-.5,-.5],[ .5, .5,-.5]] #coordinates

		combinations = [ [c[0],c[1],c[2]], [c[2],c[3],c[0]], [c[7],c[6],c[5]],
						 [c[5],c[4],c[7]], [c[4],c[5],c[1]], [c[1],c[0],c[4]],
						 [c[3],c[2],c[6]], [c[6],c[7],c[3]], [c[4],c[0],c[3]],
						 [c[3],c[7],c[4]], [c[1],c[5],c[6]], [c[6],c[2],c[1]] ]
		self.triangleList = list(itertools.starmap(Triangle,combinations))
		


class Sphere(MatrixShape):
	def __init__(self,angleStep = 10): # radius and center coords
		#first make unit sphere 
		assert(angleStep >= 0 or angleStep <= 45 or 180%angleStep == 0)
		pointsArray2d = [] # will be a 2-d matrix 
		numRows = 360 / angleStep
		numCols = 180/angleStep + 1
			#making pointsArray2d
		for i in range(numRows): #horizontal sweep
			theta = i * angleStep
			vertical = []
			for j in range(numCols): #vertical sweep
				phi = j * angleStep
				radTheta = math.radians(theta)
				radPhi = math.radians(phi)
				x = math.sin(radPhi) * math.cos(radTheta)
				y = math.sin(radPhi) * math.sin(radTheta)
				z = math.cos(radPhi) 
				vertical.append([x,y,z])
				j+=1
			pointsArray2d.append(vertical)
			i+=1
			#triangle  tessalation
		self.triangleList = []
		for i in range(numRows): 
			for j in range(numCols-1):
				self.triangleList.append( Triangle(
					pointsArray2d[i][j], pointsArray2d[(i+1)%numRows][j], pointsArray2d[(i+1)%numRows][j+1]))
				self.triangleList.append( Triangle(
					pointsArray2d[(i+1)%numRows][j+1], pointsArray2d[i][j+1], pointsArray2d[i][j]))

