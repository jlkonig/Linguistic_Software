import nltk
import glob

FUNCTION_WORDS = open("res/function_words.txt", "r", encoding="utf-8").read().split("\n")
CORPUS_PATH = "03_corpus_annotated/*.txt"
WORDS = {}

def run():
	print("    - processing files")
	corpus_files = glob.glob(CORPUS_PATH)
	for i in range(0, len(corpus_files)):
		text = open(corpus_files[i], "r", encoding="utf-8").read()
		words = text.strip("\n").split(" ")
		for w in words:
			if w.strip() == "": continue
			word = w.split("/")[2]
			list_index = w.split("/")[3]
			# print(word,list_index)
			if word in WORDS:
				WORDS[word][0] += 1
				WORDS[word][1].append(i)
				WORDS[word][1] = list(set(WORDS[word][1]))
			else:
				WORDS[word] = [1, [i], list_index]

	print("    - saving analysis")
	file_out = open("corpus_analysis.csv", "w", encoding="utf-8")
	print("%s,%s,%s,%s,%s" % ("word", "frequency", "coverage", "band", "pos"), file=file_out)
	for key,value in WORDS.items():
		if key.isalpha() and key not in FUNCTION_WORDS: 
			print("%s,%d,%d,%s,%s" % (key, value[0], len(value[1]), value[2], nltk.pos_tag([key])[0][1]), file=file_out)