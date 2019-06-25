import json
import urllib.request

from random import *
from libs import sym_metric
from html.parser import HTMLParser

class MyHTMLParser(HTMLParser):
	isEnglish = False
	hasDefinition = False
	partOfSpeech = ['Noun', 'Verb', 'Adverb', 'Adjective', 'Pronoun', 'Preposition', 'Conjunction']
	def handle_starttag(self, tag, attrs):
		if tag == "h2":
			self.isEnglish = False
		elif tag == "span":
			for attr in attrs:
				if attr[0] == "id" and attr[1] == "English":  
					self.isEnglish = True
				if self.isEnglish and attr[0] == "id" and attr[1] in self.partOfSpeech:
					self.hasDefinition = True

#
# Method: generatePseudo
# param: _tokens (wordlist), ngram_size, count (num pseudos to generate)
# returns: pseudowords (a list of pseudowords)
#
def generatePseudo(_tokens, ngram_size, count, SYM_RATE):
	ngrams = makeNgrams(_tokens)
	pseudowords = getPseudowords(_tokens, ngrams, ngram_size, count, SYM_RATE)
	return pseudowords

#
# Method: makeNgrams
# param: _tokens (wordlist)
# returns: ngrams (a dictionary of ngrams with start/mid/end counts)
#
def makeNgrams(_tokens):
	FREQ_START, FREQ_ALL, FREQ_END = 0,1,2
	ngrams = {}
	# for each token in the tokenlist:
	for token in _tokens:
		currNgrams = {}
		# Token must be:
		# - all alpha 
		# - longer than 2 chars
		if len(token) > 2 and token.isalpha():
			# For each char in the token,
			# Extracts n-grams from min to max 
			# Move forward one character each time
			for i, char in enumerate(token):
				# Extract n-grams 
				for x in range(0,len(token)): 
					ngram = token[i:i+x]
					if len(ngram) > 1 and ngram not in currNgrams:
						currNgrams[ngram] = ngram
						# Determine if n-gram is 
						# at the start or finish
						freqS = 0
						freqE = 0
						freqA = 1
						if i == 0:
							freqS = 1
						if i+x >= (len(token)):
							freqE = 1
						# Save n-gram into dic with freq counts
						# Pos 0 = frequency for starting word
						# Pos 1 = frequency for anywhere in word
						# Pos 2 = frequency for ending word
						if ngram in ngrams:
							ngrams[ngram] = [ngrams[ngram][FREQ_START] + freqS, ngrams[ngram][FREQ_ALL] + freqA, ngrams[ngram][FREQ_END] + freqE]
						else:
							ngrams[ngram] = [freqS, freqA, freqE];	
	return ngrams


def getPseudoword(starting_ngram, ngrams, order_of_text, SYM_RATE):

	start, end = True, False
	pseudoword, sequence = starting_ngram, starting_ngram

	while(True):
		# Find all ngrams that match curr ngram
		# Exclude ngrams that are the wrong length
		matchingNgrams = []
		for ngram, ngramStats in ngrams.items():
			if "random" in str(order_of_text) and ngram.startswith(sequence) and len(ngram) >= len(sequence)+1:
				if start and ngramStats[0] > 0:
					matchingNgrams.append([ngram, ngramStats[0], ngramStats[1], ngramStats[2]]) 
				elif start == False and ngramStats[1] > ngramStats[0]:
					matchingNgrams.append([ngram, ngramStats[0], ngramStats[1], ngramStats[2]])
			elif "random" not in str(order_of_text) and ngram.startswith(sequence) and len(ngram) == len(sequence)+1:
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

		if "random" in str(order_of_text): sequence = chosenNgram[0][randint(1, difference):] # chosen ngram minus random num starting characters
		else: sequence = chosenNgram[0][difference:] # chosen ngram minus first characters

		# If chosen ngram is an end gram, return pseudoword
		if chosenNgram[3] > 0:
			sym = sym_metric.maxSimMetric(pseudoword)
			if sym <= SYM_RATE:
				# print("Pseudoword: " + pseudoword)
				return [pseudoword, "complete"]
			else:
				return [pseudoword, "incomplete"]
		# Change start to be false after first iteration 
		if start: start = False

def getStartingNgrams(ngrams, order_of_text):
	startingNgrams = {}
	for ngram, ngramStats in ngrams.items():
		if "random" in str(order_of_text) and ngramStats[0] > 0:
			startingNgrams[ngram] = (ngram[:-1]) 
		elif "random" not in str(order_of_text) and len(ngram) == (order_of_text+1) and ngramStats[0] > 0:
			startingNgrams[ngram] = (ngram[:-1])
	return list(startingNgrams.keys())

# def getComparePseudowords(tokensAll1D, nGramDictionary, gram, count, fout, start_time):
def getPseudowords(_tokens, ngrams, ngram_size, count, SYM_RATE):

	# Declare starting variables
	ORDER_OF_TEXT = ngram_size -1
	running_total, count_total_tries = 0, ((count * 99) + count)
	pseudowords, realWords, incompletePseudo, pseudoArray, statsArray = set(), set(), set(), [], [0,0,0,0,0,0,0]

	# Get a list of all ngrams that can be used at the start of a word
	startingNgrams = getStartingNgrams(ngrams, ORDER_OF_TEXT)

	while (len(pseudoArray) < count) and (running_total < count_total_tries):
		
		# Randomly select a starting sequence
		starting_ngram = startingNgrams[randint(0, len(startingNgrams)-1)]
		# Get potential pseudoword
		pseudoword = getPseudoword(starting_ngram, ngrams, ORDER_OF_TEXT, SYM_RATE)

		# Determine whether the potential pseudoword has already been seen
		if pseudoword[0] in realWords: continue
		if pseudoword[0] in pseudowords: continue
		if pseudoword[0] in incompletePseudo: continue
		
		# If not previously seen, determine if it's a real pseudoword
		if pseudoword[0] in _tokens:
			realWords.add(pseudoword[0])
		elif "incomplete" in pseudoword[1]:
			incompletePseudo.add(pseudoword[0])
		elif isRealWord(pseudoword[0]):
			realWords.add(pseudoword[0])
		else:
			print(pseudoword[0])
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
	chosenNum = randint(1, total)
	# Give each ngram a number for probability
	# If chosenNum is within an ngrams range, pick it.
	counter = 0
	for ngram in matchingNgrams:
		ngramRange = counter + ngram[2]
		if chosenNum > counter and chosenNum <= ngramRange:
			return ngram
		counter = ngramRange

def isRealWord(word):
	try:
		urlWiki = "https://en.wiktionary.org/w/api.php?action=parse&format=json&prop=text|revid|displaytitle&page="
		response = urllib.request.urlopen(urlWiki + word).read().decode("utf-8") 
		jsonWiki = json.loads(response)
		if "error" in jsonWiki:
			return False
		else:
			textContent = jsonWiki["parse"]["text"]["*"]
			parser = MyHTMLParser()
			htmlResponse = parser.feed(textContent)
			if parser.hasDefinition:
				return True
			else:
				return False
	except Exception as error:
		return False