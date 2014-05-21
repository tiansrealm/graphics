import sys, math#, pygame
from matrix import *

rgbArray = None
color = (255,255,255)
WHITE = (255,255,255)
RED =   (255,0,0)
CYAN =  (0,127,127)
pixelWorldSize = (500,500) #width, height
screen = (-5,-5, 5,5,) #xleft  ybottom  xright  ytop: cartesiancoordinates

GTR = TriangleEdgeMatrix() #global Triangles Repository. uses reverseMult
CST = TransMatrix() #current transformation matrix. uses regular mult
shapes = []
def main(argv=sys.argv):
	global color, rgbArray, screen, pixelWorldSize, CST, GTR
	check(argv)

	fread = open(argv[1],"r")

	for textLine in fread:
		#handle comments
		commentIndex = textLine.find("#")
		if (commentIndex != -1):
			textLine = textLine[:commentIndex]
		#
		textLine = textLine.split()
		if textLine:
			command = textLine[0]
			args = textLine[1:]
			#the Sizers
			if command == "pixels":
				if len(args) != 2:
					print "require 2 int argument for width and height"
				else:
					pixelWorldSize = int(args[0]), int(args[1])
					rgbArray = [[[0]*3 for row in range(pixelWorldSize[0])] \
									   for column in range(pixelWorldSize[1])]
			elif command == "screen":
				if len(args) != 4:
					print "require 4 int argument for screen. xleft  ybottom  xright  ytop"
				else:
					screen = int(args[0]), int(args[1]), int(args[2]), int(args[3])
			#the Makers
			elif command == "box-t":
				if len(args) != 9:
					print "require 9 floats: sx,sy,sz,rx,ry,rz,mx,my,mz"
				else:
					Box(*[float(x) for x in args])
			elif command == "sphere-t":
				if len(args) != 9:
					print "require 9 floats: sx,sy,sz,rx,ry,rz,mx,my,mz"
				else:
					Sphere(*[float(x) for x in args])
					'''
			elif command == "line":
				if len(args) != 6:
					print "require 6 int argument for line placement. x1,y1,z1,x2,y2,z2"
				else:
					coordinates = [ float(x) for x in args]
					edgeMat.addLine(*coordinates)
					'''
			#the changers a.k.a  transformers
			elif command[:6] == "rotate":
				if len(args) != 1:
					print "require 1 int argument (degrees) for rotation degree"
				else:
					angle = int(args[0])					
					if command == "rotate-x":
						tempMat = rotateXMat(angle)
						CST = tempMat.mult(CST)
					elif command == "rotate-y":
						tempMat = rotateYMat(angle)
						CST = tempMat.mult(CST)
					elif command == "rotate-z":
						tempMat = rotateZMat(angle)
						CST = tempMat.mult(CST)
					else: 
						print "unregonized rotate command:", command
						return
			elif command == "scale":
				if len(args) != 3:
					print "require 3 float argument (x,y,z) for scaling."
				else:
					tempMat = scaleMat(float(args[0]),float(args[1]),float(args[2]))
					CST = tempMat.mult(CST)
			elif command == "move":
				if len(args) != 3:
					print "require 3 float argument (x,y,z) for translation."
				else:
					tempMat = moveMat(float(args[0]),float(args[1]),float(args[2]))
					CST = tempMat.mult(CST)
			elif command == "identity":
				CST.identity()
			elif command == "transform":
				GTR = TriangleEdgeMatrix(CST.reverseMult(GTR))
			#rendering=====The Quantizers
			elif command == "render-parallel":
				renderParallel()
			elif command == "render-perspective-cyclops":
				if len(args) != 3:
					print "require 3 float argument (Ex,Ey,Ez) for one eye perspective."
				else:
					renderCyclops(float(args[0]),float(args[1]),float(args[2]))
			elif command == "render-perspective-stereo":
				if len(args) != 6:
					print "require 6 float argument (x,y,z) for each eye."
				else:
					renderStereo(*map(float, args))
			#the Senders
			elif command == "file":
				if len(args) != 1:
					print "require 1 string for destination filename specification"
				else:
					destination = args[0]
					if destination[-4:] != ".ppm":
						print "ERROR: destination file must be of .ppm"
						print "Given destination file is", destination[-4:]
						break 
					fWrite = open(destination, "w")
					#file type, width, height, max color value
					fWrite.write ("P3\n{} {}\n255\n".format(*pixelWorldSize)) 
					s = " ".join(str(rgb) for y in rgbArray for x in y for rgb in x)
					fWrite.write(s)
					fWrite.write(" ")
			#the Terminator
			elif command == "end":
				return
			#the others
			else:
				print "unregonized command:", command
			command = None


def renderParallel():
	global color
	color = WHITE
	m = GTR.mat
	xyTriangles = [[r1[:-2],r2[:-2],r3[:-2]] for r1,r2,r3 in zip(m[::3],m[1::3],m[2::3])]
	for triangle in xyTriangles:
		#drawing triangle
		drawTriangle(triangle)
def renderCyclops(ex,ey,ez, c = WHITE):
	#one perspective triangles. requires eye's x,y,z for the one eye
	global color
	color = c
	m = GTR.mat
	p1, p2, p3 = None, None
	for point in m:
		x,y,z = point[0], point[1], point[2]
		xNew = -ez*(x-ex)/(z-ez) + ex
		yNew = -ez*(y-ey)/(z-ez) + ey
		if (p1 == None):
			p1 = [xNew,yNew]
		elif(p2 == None):
			p2 = [xNew,yNew]
		elif(p3 == None):
			drawLine(*(p1+p2+p3))
			p1 = p2 = p3 = None
		else:
			print "error in renderCyclops"
			return
		#xNew = -ez(x-ex)/(z-ez) + ex
		#yNew = -ez(y-ey)/(z-ez) + ey
def renderStereo(lx,ly,lz,rx,ry,rz):
	#two perspective lines. Left and right eye coords required
	#uses red for left eye cyan for right for 3-d efffect
	renderCyclops(lx,ly,lz,RED)
	renderCyclops(rx,ry,rz,CYAN)

def drawTriangle(vertices):
	drawLine(*(vertices[0]+vertices[1]))
	drawLine(*(vertices[1]+vertices[2]))
	drawLine(*(vertices[2]+vertices[0]))
#given args could be float or convertable to desired floats
def drawLine(x1,y1,x2,y2):
	global color, rgbArray
	#scaling/transforming from catesian coordinates to pixel coordinates
	xLeft, xRight, yBot, yTop = screen[0], screen[2], screen[1], screen[2]
	'''
		assuming pxLeft and pyTop are zero
		px = width * (x-xLeft)/(xRight-xLeft)
		py = height * (y-yTop)/ (yBot - yTop)
	'''
	px1 = pixelWorldSize[0] * (float(x1)-xLeft) / (xRight - xLeft)
	px2 = pixelWorldSize[0] * (float(x2)-xLeft) / (xRight - xLeft)
	py1 = pixelWorldSize[1] * (float(y1)-yTop) / (yBot - yTop)
	py2 = pixelWorldSize[1] * (float(y2)-yTop) / (yBot - yTop)
	p1 = [px1,py1]
	p2 = [px2,py2]
	deltaX = abs(p1[0] - p2[0])
	deltaY = abs(p1[1] - p2[1])
	reversedXY = False
	for i in range(2):
		if p1[i] < 0 or p2[i] < 0 or p1[i] > 499 or p2[i] > 499:
			print "Point coordinate out of range of 0-499"
			return
	if(p1 == p2):
		return
	if deltaX < deltaY: # shorter x difference
		#swap x and y to force x as the longer difference
		p1[0], p1[1] = p1[1], p1[0]
		p2[0], p2[1] = p2[1], p2[0]
		deltaX, deltaY = deltaY, deltaX
		reversedXY = True
	if p1[0] > p2[0]:
		#swap points to alway start with lower point
		p1[0], p1[1], p2[0], p2[1] = p2[0], p2[1],  p1[0], p1[1]
	is_yIncreasing = True if p2[1] > p1[1] else False
	x,y = p1[0], p1[1]
	counter = deltaX / 2
	while(x <= p2[0]):
		col,row = int(x),int(y)
		if reversedXY:
			#cyan and red 3-d cancellation
			if is_cyanRedOverlap(rgbArray[col][row], color):
				rgbArray[col][row] = WHITE
			else:
				rgbArray[col][row] = color 
		else:
			if is_cyanRedOverlap(rgbArray[row][col], color):
				rgbArray[row][col] = WHITE
			else: 
				rgbArray[row][col] = color
		#increment
		x += 1
		counter += deltaY
		if counter >= deltaX:
			if is_yIncreasing:
				y += 1
			else:
				y -= 1
			counter -= deltaX
#=======================Tools===========================================
def is_cyanRedOverlap(color1, color2):
	return (color1 == CYAN and color2 == RED) \
				or (color1 == RED and color2 == CYAN)



def check(argv):
	if (len(argv) != 2):
		print """
		provide 1 argument
		objects3d.py filename.objects3d
		will translate a filename.objects3d file to a .ppm file 
		"""
	if (argv[1][-10:] != ".objects3d"):
		print "require a filename.objects3d as the argument"

def RectToTriangles(vList):
	error = "error: need 4 xyz vertices facing counter clockwise for a rectangle"
	if len(vList) != 4:
		print error
		return
	triangles = [[vList[1],vList[2],vList[3]], [vList[2],vList[3],vList[1]]]
	return triangles

#---------------SHAPES CLASSES---------------------
#Uses Natrices
class MatrixShape(object):
	#use TriangleEdgeMatrix class for meshMat only
	def __init__(self,meshMat):
		self.meshMat = meshMat
	def move(self, mx,my,mz):
		print self.meshMat.row,self.meshMat.col
		self.meshMat = moveMat(mx,my,mz).reverseMult(self.meshMat)
	def scale(self, sx,sy,sz):
		self.meshMat = scaleMat(sx,sy,sz).reverseMult(self.meshMat)
	def rotateX(self, angle):
		self.meshMat = rotateXMat(rx).reverseMult(self.meshMat)
	def rotateY(self, angle):
		self.meshMat = rotateYMat(ry).reverseMult(self.meshMat)
	def rotateZ(self, angle):
		self.meshMat = rotateZMat(rz).reverseMult(self.meshMat)
	def transform(self, transMat):
		self.meshMat = transMat.reverseMult(self.meshMat)



class Box(MatrixShape):
	'''
	the initialization of a box uses (also spheres)
	9 parameters. scaling(sx,sy,sz),rotation(rx,ry,rz), and translation(mx,my,mz)
	'''
	def __init__(self,sx,sy,sz,rx,ry,rz,mx,my,mz):
		#unit box
		self.meshMat = TriangleEdgeMatrix()
		#vertices: in front counter closewise starting from top left corner
				# then repeat for the back. total 8 vertices
		v1 = [-.5, .5, .5]
		v2 = [-.5,-.5, .5]
		v3 = [ .5,-.5, .5]
		v4 = [ .5, .5, .5]
		v5 = [-.5, .5,-.5]
		v6 = [-.5,-.5,-.5]
		v7 = [ .5,-.5,-.5]
		v8 = [ .5, .5,-.5]
		rectCombinations = [[v1,v2,v3,v4],[v5,v6,v7,v8], #front and backface
							[v5,v6,v1,v2],[v8,v7,v3,v4],	#side faces
							[v5,v1,v4,v8],[v6,v2,v3,v7]]#top and bottom
		triangleCombinations = 	map(RectToTriangles,rectCombinations)
		for triangleDou in triangleCombinations:
			self.meshMat.addTriangle(*(triangleDou[0][0]+triangleDou[0][1]+triangleDou[0][2]))
			self.meshMat.addTriangle(*(triangleDou[1][0]+triangleDou[1][1]+triangleDou[1][2]))
		#transformations
		self.scale(sx,sy,sz)
		if rx != 0:
			self.rotateX(rx)
		if ry != 0:
			self.rotateY(ry)
		if rz != 0:
			self.rotateZ(rz)
		self.transform(CST)
		shapes.append(self)
		(GTR.mat).extend(self.meshMat.mat)

class Sphere(MatrixShape):
	def __init__(self,sx,sy,sz,rx,ry,rz,mx,my,mz,angleStep = 10): # radius and center coords
		#first make unit sphere 
		if (angleStep < 0 or angleStep > 45 or 180%angleStep != 0):
			print "sphere error with angleStep"
			return
		nodes = [] # will be a 2-d matrix 
		numRows = 360 / angleStep
		numCols = 180/angleStep + 1
			#making nodes
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
				if not phi == 0:
					a = vertical[j-1]+vertical[j]
					if len(a) != 6:
						print "error", a
				j+=1
			nodes.append(vertical)
			i+=1
		self.meshMat = TriangleEdgeMatrix()
			#triangle  tessalation
		for i in range(numRows): 
			for j in range(numCols-1):
				triangles = RectToTriangles( #counter-clockwise 
					[nodes[i][j],nodes[(i+1)%numRows][j],nodes[(i+1)%numRows][j+1],nodes[i][j+1]])
				self.meshMat.addTriangle(*(triangles[0][0]+triangles[0][1]+triangles[0][2]))
				self.meshMat.addTriangle(*(triangles[0][0]+triangles[0][1]+triangles[0][2]))
		#transformations
		self.scale(sx,sy,sz)
		if rx != 0:
			self.rotateX(rx)
		if ry != 0:
			self.rotateY(ry)
		if rz != 0:
			self.rotateZ(rz)
		self.move(mx,my,mz)
		self.transform(CST)
		shapes.append(self)
		(GTR.mat).extend(self.meshMat.mat)



if __name__ == "__main__":
	main()
