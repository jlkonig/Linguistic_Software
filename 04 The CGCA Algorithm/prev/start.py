import re
import sys
import time
import csv
import libs.ngram as ngram
import libs.pword as pword
import datetime
import random 
from difflib import SequenceMatcher
import libs.wiktionary as wiktionary

try:
	filename_in = input("\nPlease enter the path for the input corpus or wordlist (must be a text file): ")
	ngram_size 	= int(input("Please enter the character-gram size (either a whole number or \"-1\" for random): "))
	num_pwords 	= int(input("Please enter the number of pseudowords to generate: "))
	len_pwords 	= int(input("Please enter the length of pseudowords to generate (either a whole number or \"-1\" for any length): "))
except:
	print("\nERROR: Please ensure that ngram size and pseudoword numbers are integers")
	sys.exit()

PERC_MAX_ITERATIONS = 200

# Update user
currentDT = datetime.datetime.now()
print("\n=>Starting pseudoword generation at " + str(currentDT))

# Retrieve list of all words in the wordlist
print("====>Reading input file and generating origin wordlist")
def words(text): return re.findall(r'\w+', text.lower())
try:
	WORDS = list(set(words(open(filename_in).read())))
	print("Number of unique words in the origin wordlist:", len(WORDS))
except:
	print("\nERROR: There was an issue reading in the wordlist file")
	sys.exit()

# Note: This checks each word in the wordlist against Wiktionary to
#  validate that they are all real words. It can take some time for
#  large corpora/wordlists. 
# Comment out this code if your corpus/wordlist only contains real words. 
print("====>Cleaning origin wordlist")
print("Note: This checks each word in the wordlist against Wiktionary to validate that they are all real words. It can take some time for large corpora/wordlists. \nComment out the corresponding code if your corpus/wordlist only contains real words.")
WORDS = [w for w in WORDS if wiktionary.isRealWord(w)]
for w in WORDS:
	print(w)

# Use words to generate all possible ngrams
print("====>Generating all possible ngrams")
ngrams = ngram.makeNgrams(WORDS)

# Start timer
start_time = time.time()

# Generate x-many pseudowords 
if ngram_size == (-1):
	print("====>Generating pseudowords using r-grams" )
else:
	print("====>Generating pseudowords using " + str(ngram_size) + "-grams" )
responsePwords = pword.buildPwords(WORDS, ngrams, ngram_size, num_pwords, PERC_MAX_ITERATIONS, len_pwords)

# Update user
elapse_time = time.time() - start_time
currentDT = datetime.datetime.now()
print("=>Completed pseudoword generation at " + str(currentDT))

# Print pseudowords
print("{:7s},{:s}".format("ngram","pword"))
if ngram_size == (-1):
	ngram_size = "r"
for pseudoword in responsePwords:
	print("{:d},{:s}".format(ngram_size,pseudoword))