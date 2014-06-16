import sys, pygame, math
from matrix import *
from pygame.locals import *

WHITE = (255,255,255)
BLACK = (0,0,0)
RED =   (255,0,0)
CYAN =  (0,127,127)
######pygame#########
FPS = 30

######################3
color = WHITE
WorldRGBArray = None
pixelWorldSize = (600,600) #width, height
screen = (-5,-5, 5,5,) #xleft  ybottom  xright  ytop: cartesiancoordinates

GTR = [] #global Triangles Repository. 
CST = Matrix(None, 4,4) #current Coordinate-System Transformation Matrix. uses 4 x 4 matrix
shapes = []

pygame.init()
DISPLAYSURF = pygame.display.set_mode(pixelWorldSize)
pygame.display.set_caption('Hello World!')
WorldSurf = pygame.Surface(pixelWorldSize)
WorldRGBArray = pygame.PixelArray(WorldSurf)
def main():
	global color, WorldRGBArray, screen, pixelWorldSize, CST, GTR, FPSCLOCK
	FPSCLOCK = pygame.time.Clock()
	#sphereA = sphere_t(1,1,1,0,0,0,1,0,0) 
	personShape = importShape("lumberJack.obj")
	personShape.rotateZ(90)
	personShape.scale(3,3,3)
	#carShape = importShape
	while(True):
    	#event loop
 		for event in pygame.event.get():
 			if event.type == QUIT:
 				pygame.quit()
 				sys.exit()
		#game loop
		#sphereA.rotateX(5, sphereA.cx,sphereA.cy,sphereA.cz)
		#sphereA.rotateY(5, sphereA.cx,sphereA.cy,sphereA.cz)
		personShape.rotateX(5)

		#display
		renderParallel()
		tempWorldSurf = WorldRGBArray.make_surface()
		WorldSurf.fill(BLACK)
		DISPLAYSURF.blit(tempWorldSurf,(0,0))
		pygame.display.update()
		FPSCLOCK.tick(FPS)

	

def renderParallel():
	global color, WorldRGBArray
	color = WHITE
	for triangleO in GTR:
		if triangleO.inLineOfSight(0,0,55555):
			drawTriangle(triangleO)
def renderCyclops(ex,ey,ez, c = WHITE):
	#one perspective triangles. requires eye's x,y,z for the one eye
	global color
	color = c
	for triangleO in GTR:
		if triangleO.inLineOfSight(ex,ey,ez):
			copyTriangle = Triangle(None,None,None,triangleO.matrix)
			vertexList = map(list, zip(*triangleO.matrix.list2d[:-1])) 
			for i in range(len(vertexList)):
				x,y,z = vertexList[i][0], vertexList[i][1], vertexList[i][2]
				xNew = -ez*(x-ex)/(z-ez) + ex
				yNew = -ez*(y-ey)/(z-ez) + ey
				copyTriangle.matrix.list2d[0][i], copyTriangle.matrix.list2d[1][i] = xNew, yNew
			drawTriangle(copyTriangle)
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
	global color, WorldRGBArray
	#scaling/transforming from catesian coordinates to pixel coordinates
	xLeft, yBot, xRight, yTop = screen[0], screen[1], screen[2], screen[3]
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
	if px1 < 0 or px2 < 0 or px1 > pixelWorldSize[0] or px2 > pixelWorldSize[0] \
		or py1 < 0 or py2 < 0 or py1 > pixelWorldSize[1] or py2 > pixelWorldSize[1]:
		print "Point coordinate out of range"
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
			if is_cyanRedOverlap(WorldRGBArray[col][row], color):
				WorldRGBArray[col][row] = WHITE
			else:
				WorldRGBArray[col][row] = color 
		else:
			if is_cyanRedOverlap(WorldRGBArray[row][col], color):
				WorldRGBArray[row][col] = WHITE
			else: 
				WorldRGBArray[row][col] = color
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
	box.move(mx,my,mz)
	box.transform(CST)
	GTR.extend(box.triangleList)
	return box
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
	sphere.move(mx,my,mz)
	sphere.transform(CST)
	GTR.extend(sphere.triangleList)
	return sphere





def importShape(filename):
	fread = open(filename,"r")
	vertexList = []
	normalList = []
	triangleList = []
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
			if command == "v":
				#print len(args)
				args = map(float,args)
				vertexList.append(args)
	fread = open(filename,"r")
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
			if command == "vn":
				args = map(float,args)
				normalList.append(args)
	fread = open(filename,"r")
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
			if command == "f":
				vertices = []
				normals = []
				for section in args:
					values = map(int, section.split('/'))
					for i in range(len(values)):
						if values[i] > 0:
							values[i] -= 1
					vertices.append(vertexList[values[0]])
					normals.append(normalList[values[2]])
				if len(vertices) == 3:
					t1 = Triangle(vertices[0], vertices[1], vertices[2])
					t1.normal = linearMatrix(*normals[0])
					triangleList.append(t1)
				if len(vertices) == 4:
					t2 = Triangle(vertices[2], vertices[3], vertices[0])
					t2.normal = linearMatrix(*normals[2])
					triangleList.append(t2)
	shape = MatrixShape(triangleList)
	GTR.extend(shape.triangleList)
	return shape
if __name__ == "__main__":
	main()
