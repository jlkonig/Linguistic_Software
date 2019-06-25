import random
from libs import pseudogen

LEVEL = 5

FILE_OUT_LEVEL = "AEFL_vocabulary_test.txt"
FILE_IN_LEXICON = "dmww_wordlist.txt"

NGRAM_SIZE, PSEUDO_COUNT, SYM_RATE = 3, 20, 0.85
WORDS = [w.strip().lower() for w in open(FILE_IN_LEXICON).read().split("\n") if w.strip() != '']

# Randomly select 40 words from the wordlist
def getRealWords(WORDS):
	return random.sample(WORDS, 40)

def getPseudoWords(WORDS):
	return pseudogen.generatePseudo(WORDS, NGRAM_SIZE, PSEUDO_COUNT, SYM_RATE)

print("==> Randomly selecting 40 real words")
realwords = [[w,"r"] for w in getRealWords(WORDS)]
print("==> Generating 20 pseudowords")
pseudowords = [[p,"p"] for p in getPseudoWords(WORDS)]
print("==> Merging resulting lists and generating vocabulary test")
vocabtest = realwords + pseudowords

file_name = FILE_OUT_LEVEL
file_out = open(file_name, "w")
random.shuffle(vocabtest); 
answer_codes = ''
for index, item in enumerate(vocabtest):
	if item[1] == "p":
		answer_codes += (str(index+1) + ", ")
	print(item[0])
	print(item[0], file=file_out)
print(("Answer code: " + answer_codes[:-2] + ".\n\n"))
print(("Answer code: " + answer_codes[:-2] + "."), file=file_out)

