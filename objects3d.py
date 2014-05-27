import sys, math#, pygame
from matrix import *

rgbArray = None
color = (255,255,255)
WHITE = (255,255,255)
RED =   (255,0,0)
CYAN =  (0,127,127)
pixelWorldSize = (500,500) #width, height
screen = (-5,-5, 5,5,) #xleft  ybottom  xright  ytop: cartesiancoordinates

GTR = [] #global Triangles Repository. 
CST = Matrix(None, 4,4) #current Coordinate-System Transformation Matrix. uses 4 x 4 matrix
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
					box_t(*[float(x) for x in args])
			elif command == "sphere-t":
				if len(args) != 9:
					print "require 9 floats: sx,sy,sz,rx,ry,rz,mx,my,mz"
				else:
					sphere_t(*[float(x) for x in args])
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
				for triangleO in GTR:
					triangleO.transform(CST) 
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
	for triangle in GTR:
		drawTriangle(triangle)
def renderCyclops(ex,ey,ez, c = WHITE):
	#one perspective triangles. requires eye's x,y,z for the one eye
	global color
	color = c
	for triangleO in GTR:
		vertexList = map(list, zip(*triangleO.matrix.list2d[:-1])) 
		for i in range(len(vertexList)):
			x,y,z = vertexList[i][0], vertexList[i][1], vertexList[i][2]
			xNew = -ez*(x-ex)/(z-ez) + ex
			yNew = -ez*(y-ey)/(z-ez) + ey
			vertexList[i][0], vertexList[i][1] = xNew, yNew
		drawTriangle(Triangle(*vertexList))
def renderStereo(lx,ly,lz,rx,ry,rz):
	#two perspective lines. Left and right eye coords required
	#uses red for left eye cyan for right for 3-d efffect
	renderCyclops(lx,ly,lz,RED)
	renderCyclops(rx,ry,rz,CYAN)
def drawTriangle(triangleO):
	temp = triangleO.matrix.list2d
	vertex1 = [temp[0][0], temp[1][0], temp[2][0]]
	vertex2 = [temp[0][1], temp[1][1], temp[2][1]]
	vertex3 = [temp[0][2], temp[1][2], temp[2][2]]
	drawLine(vertex1, vertex2)
	drawLine(vertex2, vertex3)
	drawLine(vertex3, vertex1)
#given args could be float or convertable to desired floats
def drawLine(v1,v2): #2 vertices
	global color, rgbArray
	#scaling/transforming from catesian coordinates to pixel coordinates
	xLeft, xRight, yBot, yTop = screen[0], screen[2], screen[1], screen[2]
	'''
		assuming pxLeft and pyTop are zero
		px = width * (x-xLeft)/(xRight-xLeft)
		py = height * (y-yTop)/ (yBot - yTop)
	'''
	px1 = pixelWorldSize[0] * (float(v1[0])-xLeft) / (xRight - xLeft)
	px2 = pixelWorldSize[0] * (float(v2[0])-xLeft) / (xRight - xLeft)
	py1 = pixelWorldSize[1] * (float(v1[1])-yTop) / (yBot - yTop)
	py2 = pixelWorldSize[1] * (float(v2[1])-yTop) / (yBot - yTop)
	p1 = [px1,py1] #point 1
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


#=============================objects3d using traingle tessellation
def box_t(sx,sy,sz,rx,ry,rz,mx,my,mz):
	box = Box()
	#transformations
	box.scale(sx,sy,sz)
	if rx != 0:
		box.rotateX(rx)
	if ry != 0:
		box.rotateY(ry)
	if rz != 0:
		box.rotateZ(rz)
	box.transform(CST)
	GTR.extend(box.triangleList)
def sphere_t(sx,sy,sz,rx,ry,rz,mx,my,mz):
	sphere = Sphere()
	#transformations
	sphere.scale(sx,sy,sz)
	if rx != 0:
		sphere.rotateX(rx)
	if ry != 0:
		sphere.rotateY(ry)
	if rz != 0:
		sphere.rotateZ(rz)
	sphere.transform(CST)
	GTR.extend(sphere.triangleList)
def check(argv):
	if (len(argv) != 2):
		print """
		provide 1 argument
		objects3d.py filename.objects3d
		will translate a filename.objects3d file to a .ppm file 
		"""
	if (argv[1][-10:] != ".objects3d"):
		print "require a filename.objects3d as the argument"



if __name__ == "__main__":
	main()
