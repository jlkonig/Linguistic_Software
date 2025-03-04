import sys
import random

PERC_MAX_ITERATIONS = 100

def buildStart(nGramDictionary, gram_size):
	# Get a list of all ngrams that can be used at the start of a word
	startingNgrams = []
	for ngram, ngramStats in nGramDictionary.items():
		if gram_size == -1:
			if ngramStats[0] > 0:
				startingNgrams.append(ngram) 
		else:
			if len(ngram) == (gram_size) and ngramStats[0] > 0:
				startingNgrams.append(ngram) 
	return list(set(startingNgrams))


def buildPword(startingSequence, ngrams_dict, ngram_size):

	curr = startingSequence
	pseudoword = curr

	while(True):
	
		match = curr[1:]
		matches = {}

		# Find all ngrams that match ngram
		# Exclude ngrams that are the wrong length
		for ngram, stats in ngrams_dict.items():
			if ngram.startswith(match) and stats[1] > stats[0]:
				if ngram_size == -1 and len(ngram) > len(match):
					matches[ngram] = [ngram, stats[0], stats[1], stats[2]]
				elif ngram_size != -1 and len(ngram) == (len(match)+1):
					matches[ngram] = [ngram, stats[0], stats[1], stats[2]]

		# If there are no matches, return pseudoword
		if len(matches) == 0:
			return [pseudoword, "incomplete"]

		# Otherwise pick an ngram from the matches
		# In this version we are trying to find the best match for a real word
		# so pick the ngram based on probability 
		# (i.e. the higher the occurance, the more likely it will be picked)
		matches = sorted(matches.values(), key=lambda row: row[2])
		picked = ngramPicker(matches)

		# Add end of ngram to pseudoword
		# Done like this to ghandle r-grams
		diff = (len(picked[0]) - len(match))
		pseudoword += picked[0][diff*-1:] 

		# Return pseudoword if finished
		if picked[3] > 0:
			if picked[3] == picked[2] or ngramFinisher(picked):
				return [pseudoword, "complete"]
			else:
				pass

		curr = picked[0]


def buildPwords(WORDS, nGramDictionary, gram_size, count, len_pwords):

	pseudowords = set()
	realWords = set()
	incompletePseudo = set()
	pseudoArray = []

	startingNgrams = buildStart(nGramDictionary, gram_size)

	if len(startingNgrams) == 0:
		gram = ('r' if gram_size == -1 else str(gram_size))
		print("    Whoops, there are no n-grams of length", gram_size)
		sys.exit()
	
	count_pseudo =  count
	count_total_tries = (count_pseudo * PERC_MAX_ITERATIONS)
	running_total = 0

	while (len(pseudoArray) < count_pseudo) and (running_total < count_total_tries):

		# Randomly select a starting sequence
		startingSequence = startingNgrams[random.randint(0, len(startingNgrams)-1)]
		
		# Build pseudoword
		pseudoword = buildPword(startingSequence, nGramDictionary, gram_size)
		
		if -1 in len_pwords:
			pass
		elif len(pseudoword[0]) not in len_pwords:
			continue

		# If the pseudoword has already been seen
		if pseudoword[0] in realWords or pseudoword[0] in pseudowords or pseudoword[0] in incompletePseudo:
			continue
		# If the pseudoword has already been seen
		elif len(pseudoword[0]) > 10:
			continue
		# If pseudoword is a real word from the wordlist
		elif pseudoword[0] in WORDS:
			realWords.add(pseudoword[0])
		# If pseudoword is incomplete
		elif "incomplete" in pseudoword[1]:
			incompletePseudo.add(pseudoword[0])
		else:
			pseudowords.add(pseudoword[0])
			pseudoArray.append([gram_size,pseudoword[0]])

		running_total += 1

	return pseudoArray

def ngramPicker(matches):
	# Get total count
	total = 0
	for ngram in matches:
		total += ngram[2]

	# Get random number between 0 and total
	chosenNum = random.randint(1, total)

	# Give each ngram a number for probability
	# If chosenNum is within an ngrams range, pick it.
	ngramNum = 0
	for ngram in matches:
		ngramNum += ngram[2]
		if chosenNum <= ngramNum:
			return ngram

def ngramFinisher(picked):
	# Get total count
	total = picked[2] + picked[3]

	# Get random number between 0 and total
	chosenNum = random.randint(1, total)

	if chosenNum <= picked[2]:
			return False
	return True