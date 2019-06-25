import re
import nltk
import glob
import string
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

FAMILIES = {}
DIR_WORD_FAMILIES = "res/word_families"

def loadWordFamilyFiles(FAMILIES):
	for list_index in range(1,26):
		file_name = DIR_WORD_FAMILIES+"/basewrd"+str(list_index)+".txt"
		lines = open(file_name, "r", encoding="utf-8").read().split("\n")
		for i in range(0,len(lines)):
			if lines[i] != "" and not lines[i].startswith("\t"):
				index = i+1
				head_word = lines[i].lower().strip().split(" ")[0]
				FAMILIES[head_word] = [head_word, str(list_index)]
				while index<len(lines) and lines[index].startswith("\t"):
					word = lines[index].lower().strip().split(" ")[0] 
					FAMILIES[word] = [head_word, str(list_index)]
					index += 1
	return FAMILIES

def annotate(text):

	FAMILIES = {}
	FAMILIES = loadWordFamilyFiles(FAMILIES)

	response = ""
	wnl = WordNetLemmatizer()
	# Split into paragraphs
	paragraps = text.split("\n")
	for paragraph in paragraps:
		# Tokenize
		tokens = word_tokenize(paragraph)
		# Tag w POS
		tokens = nltk.pos_tag(tokens)
		# Tag w headwords, lemmas, and wordlists
		for token in tokens:
			word = token[0]
			key = word.lower().strip(string.punctuation)
			if key in FAMILIES:
				response += word + "/" + token[1] + "/" + FAMILIES[key][0] + "/" + FAMILIES[key][1] + " "
			else:
				response += word + "/" + token[1] + "/" + wnl.lemmatize(word.lower()) + "/0 "
		response += "\n"
	return response

def run():
	COUNT_FILES = 1
	CORPUS_PATH = "02_corpus_structured/*.txt"
	FILE_OUT 	= "03_corpus_annotated/"

	corpus_files = glob.glob(CORPUS_PATH)
	print("    - annotating " + str(len(corpus_files)) + " files")
	for file_name in corpus_files:
		text = open(file_name, "r", encoding="utf-8").read()
		response = annotate(text)
		file_name_out = FILE_OUT + file_name.split("\\")[-1]
		file_out = open(file_name_out, "w", encoding="utf-8")
		print(response, file=file_out)
		print("    - file " + str(COUNT_FILES) + " tagged"); COUNT_FILES+=1




