import sys, math
from matrix import *

rgbArray = None
color = (255,255,255)
WHITE = (255,255,255)
RED =   (255,0,0)
CYAN =  (0,127,127)
pixelWorldSize = (500,500) #width, height
screen = (-5,-5, 5,5,) #xleft  ybottom  xright  ytop: cartesiancoordinates
edgeMat = EdgeMatrix()
transMat = TransMatrix()
shapes = [edgeMat]
def main(argv=sys.argv):
	global color, rgbArray, screen, pixelWorldSize, transMat, edgeMat
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
			elif command == "end":
				return
			#shapes
			elif command == "sphere":
				if len(args) != 4:
					print "require 4 floats: radius, and x, y, z coordinates"
				else:
					sphere(*[float(x) for x in args])
			#transforming===============================================
			elif command == "line":
				if len(args) != 6:
					print "require 6 int argument for line placement. x1,y1,z1,x2,y2,z2"
				else:
					coordinates = [ float(x) for x in args]
					edgeMat.addLine(*coordinates)
			elif command[:6] == "rotate":
				if len(args) != 1:
					print "require 1 int argument (degrees) for rotation degree"
				else:
					angle = int(args[0])					
					if command == "rotate-x":
						rotateX(angle)
					elif command == "rotate-y":
						rotateY(angle)
					elif command == "rotate-z":
						rotateZ(angle)
					else: 
						print "unregonized rotate command:", command
						return
			elif command == "scale":
				if len(args) != 3:
					print "require 3 float argument (x,y,z) for scaling."
				else:
					scale(float(args[0]),float(args[1]),float(args[2]))
			elif command == "move":
				if len(args) != 3:
					print "require 3 float argument (x,y,z) for translation."
				else:
					move(float(args[0]),float(args[1]),float(args[2]))
			elif command == "identity":
				transMat.identity()
			elif command == "transform":
				pass
				#print "EDGE:\n", edgeMat
				#print "trans",transMat.mat
				edgeMat = EdgeMatrix(transMat.mult(edgeMat.reverse()).reverse())
				#print "trans:\n", transMat, "edge:\n" ,edgeMat
			#rendering============================================
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
			else:
				print "unregonized command:", command
			command = None
def move(x,y,z):
	global transMat
	tempMat = TransMatrix()
	tempMat.set(0,3, x)
	tempMat.set(1,3, y)
	tempMat.set(2,3, z)
	transMat = tempMat.mult(transMat)
def scale(x,y,z):
	global transMat
	tempMat = TransMatrix()
	tempMat.set(0,0, x)
	tempMat.set(1,1, y)
	tempMat.set(2,2, z)
	transMat = tempMat.mult(transMat)
def rotateX(angle):
	global transMat
	tempMat = TransMatrix()
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	tempMat.set(1,1, cos)
	tempMat.set(1,2, -sin)
	tempMat.set(2,1, sin)
	tempMat.set(2,2, cos)
	transMat = tempMat.mult(transMat)

def rotateY(angle):
	global transMat
	tempMat = TransMatrix()
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	tempMat.set(0,0, cos)
	tempMat.set(0,2, sin)
	tempMat.set(2,0, -sin)
	tempMat.set(2,2, cos)
	transMat = tempMat.mult(transMat)
def rotateZ(angle):	
	global transMat
	tempMat = TransMatrix()
	rad = math.radians(angle)
	cos, sin = math.cos(rad), math.sin(rad)
	tempMat.set(0,0, cos)
	tempMat.set(0,1, -sin)
	tempMat.set(1,0, sin)
	tempMat.set(1,1, cos)
	transMat = tempMat.mult(transMat)

def renderParallel():
	global color
	color = WHITE
	m = edgeMat.mat
	xyCoors = [r1[:-2]+r2[:-2] for r1,r2 in zip(m[::2],m[1::2])]
	for line in xyCoors:
		pasteLine(*line)
def renderCyclops(ex,ey,ez, c = WHITE):
	#one perspective line. requires x,y,z for the one eye
	global color
	color = c
	m = edgeMat.mat
	p1, p2 = None, None
	for point in m:
		x,y,z = point[0], point[1], point[2]
		xNew = -ez*(x-ex)/(z-ez) + ex
		yNew = -ez*(y-ey)/(z-ez) + ey
		if (p1 == None):
			p1 = [xNew,yNew]
		elif(p2 == None):
			p2 = [xNew,yNew]
			pasteLine(*(p1+p2))
			p1 = p2 = None
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

#given args could be float or convertable to desired floats
def pasteLine(x1,y1,x2,y2):
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

def is_cyanRedOverlap(color1, color2):
	return (color1 == CYAN and color2 == RED) \
				or (color1 == RED and color2 == CYAN)



def check(argv):
	if (len(argv) != 2):
		print """
		provide 1 argument
		lines3d.py filename.lines3d
		will translate a filename.lines3d file to a .ppm file 
		"""
	if (argv[1][-8:] != ".lines3d"):
		print "require a filename.lines3d as the argument"



#---------------SHAPES---------------------
def sphere(r, cx, cy, cz, angleStep = 10): # radius and center coords
	#first make unit sphere 
	if (angleStep < 0 or angleStep > 45):
		print "please choose and angleStep that is 0 < angle <= 45"
		return
	horizontal = []
	#drawing vertical lines
	for i in range(360 / angleStep):
		theta = i * angleStep
		vertical = []
		for j in range(180/angleStep+1):
			phi = j * angleStep
			radTheta = math.radians(theta)
			radPhi = math.radians(phi)
			x = r * math.sin(radPhi) * math.cos(radTheta)
			y = r * math.sin(radPhi) * math.sin(radTheta)
			z = r * math.cos(radPhi) 
			vertical.append([x,y,z])
			if not phi == 0:
				a = vertical[j-1]+vertical[j]
				if len(a) != 6:
					print "error", a
				edgeMat.addLine(*(vertical[j-1]+vertical[j]))
			j+=1
		horizontal.append(vertical)
		i+=1
	#drawing horizontal lines
	for i in range(len(horizontal)):
		for j in range(1,len(horizontal[0])-1):
			p1 = horizontal[i][j]
			p2 = horizontal[(i+1)%len(horizontal)][j]
			edgeMat.addLine(*(p1+p2))
			j+=1
		i+=1





if __name__ == "__main__":
	main()
