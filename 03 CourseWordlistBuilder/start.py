import nltk
import glob
import math
from collections import Counter

WORDS = {}
CORPUS_PATH = "corpus_annotated/*.txt"
GSL = open("res/GSL.txt", "r", encoding="utf-8").read().split("\n")
FUNCTION_WORDS = open("res/function_words.txt", "r", encoding="utf-8").read().split("\n")


THRESH_MAIN_COVERAGE, THRESH_SUB_COVERAGE, THRESH_FREQ_TOTAL, THRESH_WRITTEN_FRE, THRESH_SPOKEN_FRE = 0,0,0,0,0

def calculateThresholds():
	global THRESH_MAIN_COVERAGE; global THRESH_SUB_COVERAGE 
	global THRESH_FREQ_TOTAL; global THRESH_WRITTEN_FRE
	global THRESH_SPOKEN_FRE

	analysis = open("corpus_stats.csv", "r", encoding="utf-8").read().split("\n")
	analysis = [line.split(",") for line in analysis if line != ""]
	total 	 = analysis[-1]
	analysis = analysis[1:-1]
	
	spoken 	= [int(data[2]) for data in analysis if data[0] == "Transcript"]
	written = [int(data[2]) for data in analysis if data[0] != "Transcript"]
	spoken  = sum(spoken)
	written = sum(written)

	THRESH_MAIN_COVERAGE = 2 # spoken and written
	THRESH_SUB_COVERAGE = math.ceil((len(analysis)-2) / 2)
	THRESH_FREQ_TOTAL = math.ceil(float(total[2]) * 0.0000286)
	THRESH_SPOKEN_FRE = math.ceil(float(spoken) * 0.0000114)
	THRESH_WRITTEN_FRE = math.ceil(float(written) * 0.0000114)

def calculateMainCoverage(coverage_by_english_type):
	main_coverage = 0
	if coverage_by_english_type["written"] > 0: main_coverage += 1
	if coverage_by_english_type["spoken"]  > 0: main_coverage += 1
	return main_coverage

def calculateSubCoverage(coverage_by_material):
	sub_coverage = 0
	if coverage_by_material["Article"] 	  > 0: sub_coverage += 1
	if coverage_by_material["Discussion"] > 0: sub_coverage += 1
	if coverage_by_material["Video"] 	  > 0: sub_coverage += 1
	if coverage_by_material["Transcript"] > 0: sub_coverage += 1
	if coverage_by_material["Quiz"]  	  > 0: sub_coverage += 1
	if coverage_by_material["Todo"] 	  > 0: sub_coverage += 1
	return sub_coverage

def processFiles():
	corpus_files = glob.glob(CORPUS_PATH)
	for i in range(0, len(corpus_files)):
		text = open(corpus_files[i], "r", encoding="utf-8").read()
		words = text.strip("\n").split(" ")
		material = corpus_files[i].split("-")[1] + "-" + str(i)
		for w in words:
			if w.strip() == "": continue
			word = w.split("/")[2]
			list_index = w.split("/")[3]
			if word in WORDS:
				WORDS[word][0] += 1
				WORDS[word][1].append(i)
				WORDS[word][2].append(material)
			else:
				WORDS[word] = [1, [i], [material], list_index]
		print("    - processing " + str(i) + " files")
	return WORDS

def GenerateAndSave(WORDS):
	WORDLIST = []
	for key,value in WORDS.items():
		if key.isalpha() and key not in GSL:
			# Total frequency across all categories
			word = key
			test = value[2]
			freq_total = value[0]
			coverage_by_file = len(value[1])
			freq_by_file = Counter(value[2])
			
			# Frequency and coverage by material
			materials = []
			freq_by_material = {}
			for key, value in freq_by_file.items(): 
				material = key.split("-")[0]
				materials.append(key.split("-")[0])
				if material in freq_by_material:
					freq_by_material[material] += value
				else:
					freq_by_material[material] = value
			coverage_by_material = Counter(materials)

			# Frequency and coverage by language
			english_types = []
			freq_by_english_type = {}
			for key, value in freq_by_file.items(): 
				material = key.split("-")[0]
				english = "written"
				if material == "Transcript": english = "spoken"
				english_types.append(english)
				if english in freq_by_english_type:
					freq_by_english_type[english] += value
				else:
					freq_by_english_type[english] = value
			coverage_by_english_type = Counter(english_types)

			# Analysing
			print_writte_cov = coverage_by_english_type["written"]
			print_spoken_cov = coverage_by_english_type["spoken"]

			print_art_cov = coverage_by_material["Article"]
			print_dis_cov = coverage_by_material["Discussion"]
			print_vid_cov = coverage_by_material["Video"]
			print_tra_cov = coverage_by_material["Transcript"]
			print_qui_cov = coverage_by_material["Quiz"]
			print_tod_cov = coverage_by_material["Todo"]

			print_writte_fre = 0
			print_writte_fre = 0 if "written" not in freq_by_english_type else freq_by_english_type["written"]
			print_spoken_fre = 0 if "spoken" not in freq_by_english_type else freq_by_english_type["spoken"]

			print_art_fre = 0 if "Article" not in freq_by_material else freq_by_material["Article"]
			print_dis_fre = 0 if "Discussion" not in freq_by_material else freq_by_material["Discussion"]
			print_vid_fre = 0 if "Video" not in freq_by_material else freq_by_material["Video"]
			print_tra_fre = 0 if "Transcript" not in freq_by_material else freq_by_material["Transcript"]
			print_qui_fre = 0 if "Quiz" not in freq_by_material else freq_by_material["Quiz"]
			print_tod_fre = 0 if "Todo" not in freq_by_material else freq_by_material["Todo"]

			main_coverage = calculateMainCoverage(coverage_by_english_type)
			sub_coverage = calculateSubCoverage(coverage_by_material)

			if main_coverage == THRESH_MAIN_COVERAGE and sub_coverage >= THRESH_SUB_COVERAGE and freq_total >= THRESH_FREQ_TOTAL and print_writte_fre >= THRESH_WRITTEN_FRE and print_spoken_fre >= THRESH_SPOKEN_FRE:
				WORDLIST.append([word,freq_total,print_writte_fre,print_spoken_fre,main_coverage,sub_coverage])
	return WORDLIST

def printWordList(WORDLIST):
	file_out_csv = open("wordlist+counts.csv", "w", encoding="utf-8")
	file_out_txt = open("wordlist.txt", "w", encoding="utf-8")
	print("word,Frequency (total),Frequency (written),Frequency (spoken),Coverage (main-categories),Coverage (sub-categories)", file=file_out_csv)
	WORDLIST = sorted(WORDLIST,key=lambda w:w[1], reverse=True)
	for word in WORDLIST:
		print(word[0]+","+str(word[1])+","+str(word[2])+","+str(word[3])+","+str(word[4])+","+str(word[5]), file=file_out_csv) 
	WORDLIST = sorted(WORDLIST,key=lambda w:w[0])
	for word in WORDLIST:
		print(word[0], file=file_out_txt) 

print("(1) Calculating the thresholds")
calculateThresholds()
print("(2) Processing corpora files")
WORDS = processFiles()
print("(3) Generating the wordlist")
WORDLIST = GenerateAndSave(WORDS)
print("(4) Saving the wordlist")
printWordList(WORDLIST)