#python code to generate interesting image
#by- Tianci Lin 
import random , math
def main():
	f = open("lolipop.ppm","w")
	f.write("P3\n500 500\n255\n") #file type, width, height, max color value

	pr = (250,200)
	pg = (210,280)
	pb = (290,280)
	for i in range(500):
		for j in range(500):
			r = (distance((i,j), pr) * 2) % 511
			g = (distance((i,j), pg) * 2) % 511
			b = (distance((i,j), pb) * 2) % 511
			if (r > 255):
				r = 255 - (r - 255) 
			if (g > 255):
				g = 255 - (g - 255) 
			if (b > 255):
				b = 255 - (b - 255) 	
			pixel = "{} {} {} ".format(r, g, b)
			f.write(pixel)
			
def distance((x,y),(ox,oy)):
	return int(math.sqrt( pow(x-ox, 2) + pow(y-oy,2)))


if __name__ == "__main__":
	main()