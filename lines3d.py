import sys, math
from matrix import *

rgbArray = [[[0]*3 for row in range(500)] for column in range(500)]
color = [255,255,255]
WHITE = [255,255,255]
RED = [255,0,0]
CYAN = [0,127,127]
pixelWorldSize = (500,500) #width, height
screen = (-5,-5, 5,5,) #xleft  ybottom  xright  ytop: cartesiancoordinates
edgeMat = EdgeMatrix()
transMat = TransMatrix()

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
					fWrite.write ("P3\n{} {}\n255\n".format(*pixelWorldSize)) #file type, width, height, max color value
					s = " ".join(str(rgb) for y in rgbArray for x in y for rgb in x)
					fWrite.write(s)
					fWrite.write(" ")
			elif command == "end":
				return
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
					tempMat = TransMatrix()
					rad = math.radians(int(args[0]))
					cos, sin = math.cos(rad), math.sin(rad)
					if command == "rotate-x":
						tempMat.set(1,1, cos)
						tempMat.set(1,2, -sin)
						tempMat.set(2,1, sin)
						tempMat.set(2,2, cos)
					elif command == "rotate-y":
						tempMat.set(0,0, cos)
						tempMat.set(0,2, sin)
						tempMat.set(2,0, -sin)
						tempMat.set(2,2, cos)
					elif command == "rotate-z":
						tempMat.set(0,0, cos)
						tempMat.set(0,1, -sin)
						tempMat.set(1,0, sin)
						tempMat.set(1,1, cos)
					else: 
						print "unregonized rotate command:", command
						return
					transMat = tempMat.mult(transMat)
					#print "trans",transMat.matrix
			elif command == "move":
				if len(args) != 3:
					print "require 3 float argument (x,y,z) for translation."
				else:
					tempMat = TransMatrix()
					tempMat.set(0,3, float(args[0]))
					tempMat.set(1,3, float(args[1]))
					tempMat.set(2,3, float(args[2]))
					transMat = tempMat.mult(transMat)
			elif command == "identity":
				transMat.identity()
			elif command == "transform":
				pass
				#print "EDGE:\n", edgeMat
				#print "trans",transMat.matrix
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
def renderParallel():
	global color
	color = WHITE
	m = edgeMat.matrix
	xyCoors = [r1[:-2]+r2[:-2] for r1,r2 in zip(m[::2],m[1::2])]
	for line in xyCoors:
		pasteLine(*line)
def renderCyclops(ex,ey,ez, c = WHITE):
	#one perspective line. requires x,y,z for the one eye
	global color
	color = c
	m = edgeMat.matrix
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
		print("notice: a line with endpoints same points")
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
			rgbArray[col][row] = color 
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

		
	



def check(argv):
	if (len(argv) != 2):
		print """
		provide 1 argument
		lines3d.py filename.lines3d
		will translate a filename.lines3d file to a .ppm file 
		"""
	if (argv[1][-8:] != ".lines3d"):
		print "require a filename.lines3d as the argument"


if __name__ == "__main__":
	main()