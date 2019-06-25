
import random
import libs.wiktionary as wiktionary

def buildStart(nGramDictionary, gram_size):
	# Get a list of all ngrams that can be used at the start of a word
	startingNgrams = []
	for ngram, ngramStats in nGramDictionary.items():
		if gram_size == -1 and ngramStats[0] > 0:
			startingNgrams.append(ngram) 
		elif gram_size != -1 and len(ngram) == (gram_size) and ngramStats[0] > 0:
			startingNgrams.append(ngram) 
	return list(set(startingNgrams))

def buildPword(startingSequence, nGramDictionaryBand, gram_size):

	start, end = True, False
	pseudoword = startingSequence;
	sequence = startingSequence[((len(startingSequence)-1)*-1):]

	while(True):
		# Find all ngrams that match curr ngram
		# Exclude ngrams that are the wrong length
		matchingNgrams = []
		for ngram, ngramStats in nGramDictionaryBand.items():
			if gram_size == -1 and ngram.startswith(sequence) and len(ngram) >= len(sequence)+1:
				if start and ngramStats[0] > 0:
					matchingNgrams.append([ngram, ngramStats[0], ngramStats[1], ngramStats[2]]) 
				elif start == False and ngramStats[1] > ngramStats[0]:
					matchingNgrams.append([ngram, ngramStats[0], ngramStats[1], ngramStats[2]])
			elif gram_size != -1 and ngram.startswith(sequence) and len(ngram) == len(sequence)+1:
				if start and ngramStats[0] > 0:
					matchingNgrams.append([ngram, ngramStats[0], ngramStats[1], ngramStats[2]]) 
				elif start == False and ngramStats[1] > ngramStats[0]:
					matchingNgrams.append([ngram, ngramStats[0], ngramStats[1], ngramStats[2]])

		# If there are no ngrams left, return pseudoword
		if len(matchingNgrams) == 0:
			return [pseudoword, "incomplete"]

		# Otherwise pick an ngram from the resulting list of ngrams
		# In this version we are trying to find the best match for a real word
		# so pick the ngram based on probability 
		# (i.e. the higher the occurance, the more likely it will be picked)
		matchingNgrams = sorted(matchingNgrams, key=lambda row: row[2])
		chosenNgram = ngramProbabilityBasedPicker(matchingNgrams)

		# Add ngram to pseudoword and determine next ngram sequence
		difference = (len(chosenNgram[0]) - len(sequence))
		pseudoword += chosenNgram[0][difference*-1:] # plus last chars of chosen ngram
		if "random" in str(gram_size):
			sequence = chosenNgram[0][random.randint(1, difference):] # chosen ngram minus random num starting characters
		else:
			sequence = chosenNgram[0][difference:] # chosen ngram minus first characters

		# If chosen ngram is an end gram, return pseudoword
		if chosenNgram[3] > 0:
			return [pseudoword, "complete"]

		# Change start to be false after first iteration 
		if start: start = False

def buildPwords(WORDS, nGramDictionary, gram_size, count, perc_max_iterations, len_pwords):

	pseudowords = set()
	realWords = set()
	incompletePseudo = set()
	pseudoArray = []

	startingNgrams = buildStart(nGramDictionary, gram_size)
	
	count_pseudo =  count
	count_total_tries = (count_pseudo * perc_max_iterations)
	running_total = 0

	while (len(pseudoArray) < count_pseudo) and (running_total < count_total_tries):

		# Randomly select a starting sequence
		startingSequence = startingNgrams[random.randint(0, len(startingNgrams)-1)]
		
		# Build pseudoword
		pseudoword = buildPword(startingSequence, nGramDictionary, gram_size)

		# If the pseudoword has already been seen
		if len_pwords > 0 and len(pseudoword[0]) != len_pwords:
			continue
		if pseudoword[0] in realWords or pseudoword[0] in pseudowords or pseudoword[0] in incompletePseudo:
			continue
		# If pseudoword is a real word from the wordlist
		elif pseudoword[0] in WORDS:
			realWords.add(pseudoword[0])
		# If pseudoword is incomplete
		elif "incomplete" in pseudoword[1]:
			incompletePseudo.add(pseudoword[0])
		# If pseudoword is a real word according to wiktionary
		elif wiktionary.isRealWord(pseudoword[0]):
			realWords.add(pseudoword[0])
		else:
			pseudowords.add(pseudoword[0])
			pseudoArray.append(pseudoword[0])

		running_total += 1

	return pseudoArray

def ngramProbabilityBasedPicker(matchingNgrams):
	# Get total count
	total = 0
	for ngram in matchingNgrams:
		total += ngram[2]
	# Get random number between 0 and total
	chosenNum = random.randint(1, total)
	# Give each ngram a number for probability
	# If chosenNum is within an ngrams range, pick it.
	counter = 0
	for ngram in matchingNgrams:
		ngramRange = counter + ngram[2]
		if chosenNum > counter and chosenNum <= ngramRange:
			return ngram
		counter = ngramRange