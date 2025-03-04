# -*- coding: utf-8 -*-

FREQ_START 	= 0;
FREQ_ALL 	= 1;
FREQ_END 	= 2;

#
# Method GENERATE N-GRAMS
#
def makeNgrams(_tokens):
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