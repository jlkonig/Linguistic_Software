import re
from functools import reduce
from collections import Counter
from difflib import SequenceMatcher

'''
Based on the code written by Peter Norvig for spell correction
Retrieved from http://norvig.com/spell-correct.html
APA reference:
Norvig, P. (2016, August). How to Write a Spelling Corrector. Retrieved May, 2018, from http://norvig.com/spell-correct.html
'''

def words(text): return re.findall(r'\w+', text.lower())
WORDS = Counter(words(open('res/wordlist.txt').read()))

# Similarity metric calculation
# Replaces probability function P and correction function by Peter Norvig.
# Probability based on word occurance will not be effective 
# for my work becauce each word only occurs once in 
# the wordlist.txt that is being used as the dictionary
# Returns the average similarity metric for the pseduo-word
def maxSimMetric(word):
    sms = [SequenceMatcher(None, word, w).ratio() for w in candidates(word)]
    sm_max = max(sms)
    return sm_max if sm_max != 1 else 0

def candidates(word): 
    "Generate possible spelling corrections for word."
    return (known([word]) or known(edits1(word)) or known(edits2(word)) or [word])

def known(words): 
    "The subset of `words` that appear in the dictionary of WORDS."
    return set(w for w in words if w in WORDS)

def edits1(word):
    "All edits that are one edit away from `word`."
    letters    = 'abcdefghijklmnopqrstuvwxyz'
    splits     = [(word[:i], word[i:])    for i in range(len(word) + 1)]
    deletes    = [L + R[1:]               for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R)>1]
    replaces   = [L + c + R[1:]           for L, R in splits if R for c in letters]
    inserts    = [L + c + R               for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)

def edits2(word): 
    "All edits that are two edits away from `word`."
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))
