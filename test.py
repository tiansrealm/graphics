rgbArray = [[[0]*3 for row in range(3)] for column in range(3)]
print rgbArray
print "============================================"
s = " ".join(str(rgb) for y in rgbArray for x in y for rgb in x)
print s