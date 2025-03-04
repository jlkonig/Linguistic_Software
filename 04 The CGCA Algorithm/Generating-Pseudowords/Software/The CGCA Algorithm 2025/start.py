# --------------------------------------------------------------------------
# --------------------------------------------------------------------------
# The CGCA Algorithm -------------------------------------------------------
# --------------------------------------------------------------------------
# --------------------------------------------------------------------------

# --------------------------------------------------------------------------
# imports ----------------------------------------------------------------
# --------------------------------------------------------------------------

import re
import sys
from libs import util
from libs import ngrams
from libs import pseudowords

# --------------------------------------------------------------------------
# variables ----------------------------------------------------------------
# --------------------------------------------------------------------------

FILE_IN, FILE_OUT, NGRAM_SIZE, PWORD_COUNT, PWORD_LENGTH = '', 'out.csv', [-1,2,3,4,5,6,7,8], 20, [-1]

# --------------------------------------------------------------------------
# functions ----------------------------------------------------------------
# --------------------------------------------------------------------------

def displayHelp():
	help_text = open(".help.txt").read()
	print(help_text)

def validateCount(pword_count):
	try:
		pword_count = int(pword_count)
		if pword_count > 0: return pword_count
		else:
			print(util.ERR_COUNT_FORMAT)
			sys.exit()
	except:
		print(util.ERR_COUNT_FORMAT)
		sys.exit()

def convertRangeToNums(range_type, range_nums):
	nums = []
	tmps = range_nums.split(",")
	for tmp in tmps:
		try:
			if range_type == "ngram_size":
				if tmp.strip() == "r": nums.append(-1)
				else: nums.append(int(tmp))
			elif range_type == "pword_length":
				if tmp.strip() == "a": 
					return [-1]
				else: nums.append(int(tmp))
		except:
			try:
				ts = tmp.split("-")
				min = int(ts[0]) if int(ts[0]) < int(ts[1]) else int(ts[1])
				max = int(ts[1]) if int(ts[1]) > int(ts[0]) else int(ts[0])  
				nums += list(range(min, max+1))
			except:
				if range_type == "ngram_size": print(util.ERR_NGRAM_FORMAT)
				elif range_type == "pword_length": print(util.ERR_PWORD_FORMAT)
				sys.exit()
	nums.sort()
	return nums

def processArgs(argv):
	global FILE_IN, NGRAM_SIZE, PWORD_COUNT, PWORD_LENGTH, FILE_OUT
	if len(sys.argv) <= 1:
		return
	for i in range(1, len(argv)):
		if argv[i]=="-fi" or argv[i]=="-filein":
			FILE_IN = argv[i+1] 
		if argv[i]=="-fo" or argv[i]=="-fileout":
			FILE_OUT = argv[i+1] 
		if argv[i]=="-n" or argv[i]=="-ngram":
			NGRAM_SIZE = convertRangeToNums("ngram_size", argv[i+1])
		if argv[i]=="-c" or argv[i]=="-count":
			PWORD_COUNT = validateCount(argv[i+1])
		if argv[i]=="-l" or argv[i]=="-length":
			PWORD_LENGTH = convertRangeToNums("pword_length", argv[i+1])

def getWords(text): 
	return re.findall(r'\w+', text.lower())

def getOrigin(FILE_IN):
	print("(2) Extracting tokens to build the origin wordlist")
	try:
		origin = getWords(open(FILE_IN, 'r', encoding='utf-16').read())
		print("    (2a) the origin contains", len(origin), "words (" + str(len(list(set(origin)))), "unique)")
		return list(set(origin))
	except Exception:
		print(util.ERR_FILE_READ)

def cleanOrigin(ORIGIN):
	print("(3) Cleaning the origin wordlist")
	print("    (3b) the origin contains", len(ORIGIN), "unique words before cleaning")
	kupu_list = [kupu.strip("\n") for kupu in ORIGIN if kupu.strip("\n") != '']
	kupu_list = [kupu for kupu in kupu_list if len(kupu) > 3]
	kupu_list = [kupu for kupu in kupu_list if '-' not in kupu]
	words = kupu_list
	print("    (3b) the origin contains", len(words), "unique words after cleaning")
	return words

# --------------------------------------------------------------------------
# main ---------------------------------------------------------------------
# --------------------------------------------------------------------------

# Process arguments
print("\n(1) Processing command-line arguments")
try:
	if "-h" in sys.argv or "-help" in sys.argv:
		displayHelp()	
	else: 
		processArgs(sys.argv)
	if FILE_IN == "": 
		print(util.ERR_ARGS_FILE)
		quit()
except Exception:
	print(util.ERR_ARGS)
	quit()

# Extract tokens from input to build the origin wordlist
ORIGIN = getOrigin(FILE_IN)

# Cleaning origin wordlist, removing any 'words' that are not 
# COMMENT OUT this line if you do not want the origin 'cleaned'
# ORIGIN = cleanOrigin(ORIGIN)

# Use ORIGIN to generate all possible ngrams
print("(4) Generating all possible ngrams")
NGRAMS = ngrams.makeNgrams(ORIGIN)

# Generating pseudowords 
print("(5) Generating pseudowords")
PSEUDOWORDS = []
for ngram_size in NGRAM_SIZE:
	gram = ('r' if ngram_size == -1 else str(ngram_size))
	print("    (5a) Generating", PWORD_COUNT, "pseudowords using", gram+"-grams")
	PSEUDOWORDS += pseudowords.buildPwords(ORIGIN, NGRAMS, ngram_size, PWORD_COUNT, PWORD_LENGTH)

# Print pseudowords
print("(6) Printing pseudowords\n\n")
file_out = open(FILE_OUT, "w", encoding='utf-16')
print("{:7s}{:s}".format("ngram","pseudoword"))
print("{:s},{:s}".format("ngram","pseudoword"), file=file_out)
for pseudoword in PSEUDOWORDS:
	gram = ('r-gram' if pseudoword[0] == -1 else str(pseudoword[0])+"-gram")
	print("{:8s}{:s}".format(gram,pseudoword[1]))
	print("{:s},{:s}".format(gram,pseudoword[1]), file=file_out)





