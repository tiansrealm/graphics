

class Matrix(object):
	
	def __init__(self, row, col):
		self.maxRow = row
		self.maxCol = col
		self.storage = [ [0]*row for i in range(col)]

	def set(self, row , col, value):
		if (row <= self.maxRow and col <= self.maxCol):
			self.storage[row][col] = value
		else:
			print "warning: attepmt to get a out of bound value in a Matrix"

	def get(self, row , col):
		if (row <= self.maxRow and col <= self.maxCol):
			return self.storage[row][col]
		else:
			print "warning: attepmt to get a out of bound value in a Matrix"

m = Matrix(3,3)
print m.get(1,1)
m.set(1,1,5)
print m.get(1,1)
print m.storage