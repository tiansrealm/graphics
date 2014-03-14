import sys

rgbArray = [[[0]*3 for row in range(500)] for column in range(500)]
color = [0,0,0]

def main(argv=sys.argv):
	global color, rgbArray
	check(argv)

	fread = open(argv[1],"r")

	command = None;
	for line in fread:
		#handle comments
		commentIndex = line.find("#")
		if (commentIndex != -1):
			line = line[:commentIndex]
		#
		line = line.split()
		if line:
			if (command is None) and (len(line) != 0):
				if (len(line) == 1):
					command = line[0]
				else:
					print "missing command"
			else:
				if command == 'c':
					if len(line) != 3:
						print "require 3 int argument for color change"
					else:
						for i in range(len(line)):
							line[i] = int(line[i]) 
						color = line
				elif command == "l":
					if len(line) != 4:
						print "require 4 int argument for line placement"
					else:
						insertLine(*line)
				elif command == "g":
					if len(line) != 1:
						print "require 1 string for destination filename specification"
					else:
						destination = line[0]
						if destination[-4:] != ".ppm":
							print "ERROR: destination file must be of .ppm"
							print "Given destination file is", destination[-4:]
							break 
						fWrite = open(destination, "w")
						fWrite.write ("P3\n500 500\n255\n") #file type, width, height, max color value
						s = " ".join(str(rgb) for y in rgbArray for x in y for rgb in x)
						fWrite.write(s)
						fWrite.write(" ")
				elif command == "q":
					return
				else:
					print "invalid command. Must be one of 'c', 'l', 'g, 'q'"
				command = None

	
#given args could be ints or convertable to desired ints
def insertLine(x1,y1,x2,y2):
	global color, rgbArray
	p1 = [int(x1),int(y1)]
	p2 = [int(x2),int(y2)]
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
		col,row = x,y
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
		line.py filename.linedate
		will translate a filename.linedata file to a .ppm file 
		"""
	if (argv[1][-9:] != ".linedata"):
		print "require a filename.linedata as the argument"


if __name__ == "__main__":
	main()