

for level in range(1,6):
	FILE_IN_LEVEL = "output/New-YN-test-"+str(level)+".txt"
	WORDS = [w for w in open(FILE_IN_LEVEL).read().split("\n") if w.strip() != '']

	FILE_OUT_LEVEL = open("output/New-YN-test-"+str(level)+"-formatted.txt", "w")
	for i in range(0, len(WORDS)-1, 3):
		print("%s,%s,%s" % (WORDS[i],WORDS[i+1],WORDS[i+2]), file=FILE_OUT_LEVEL)
	print(WORDS[-1], file=FILE_OUT_LEVEL)

