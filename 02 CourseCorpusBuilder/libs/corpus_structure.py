import os
import re

DIR_IN 		= "01_corpus_in/"
DIR_OUT		= "02_corpus_structured/"
WORD_COUNT 	= 0
COVERAGE 	= 0
COLLECTION 	= {}

def cleanDirectory(DIR_OUT):
	folder = DIR_OUT
	for the_file in os.listdir(folder):
		file_path = os.path.join(folder, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
			elif os.path.isdir(file_path): shutil.rmtree(file_path)
		except Exception as e:
			print(e)

def printStatsAndCorpus(DIR_OUT, topic, entries, file):
	# print("---> Printing " + topic + "s")
	global WORD_COUNT; global COVERAGE
	wordCount = 0
	for entry in entries:
		topic, step, content = entry[0], entry[1], entry[2]
		file_out = open(DIR_OUT+entry[3]+"-"+topic+"-"+step+".txt", "a", encoding="utf-8")
		print(content.strip("\n"), file=file_out)
		wordCount += len(content.split())
	print("%s,%s,%s" % (topic, len(entries), wordCount), file=file)
	WORD_COUNT += wordCount
	COVERAGE += len(entries)

def extractTranscript(COLLECTION, topic, step, content, course):
	# print("---> Extracting transcripts")
	splitContent =  content.replace("<End Transcript>", "").split("<Start Transcript>")
	if(len(splitContent) == 2):
		categorizeContent(COLLECTION, topic, step, splitContent[0], course)
		categorizeContent(COLLECTION, "Transcript", step, splitContent[1], course)

def categorizeContent(COLLECTION, topic, step, content, course):
	# print("---> Categorizing " + topic)
	if "<Start Transcript>" in content:
		extractTranscript(COLLECTION, topic, step, content,course)
	else:
		if topic not in COLLECTION:
			COLLECTION[topic] = [[topic, step, content, course]]
		else:
			COLLECTION[topic].append([topic, step, content, course])

def extractContent(COLLECTION, DIR_IN, file):
	course = file.split("-")[0]
	fileContent = cleanQuizzes(open(DIR_IN+file,"r", encoding="utf-8").read())
	splitText = re.split('(<-- .*? -->)', fileContent)
	for i in range(1,len(splitText),2): 
		topic = splitText[i]
		content = splitText[i+1]
		if "<--" in topic: 
			matchTopic = re.search('([a-zA-Z]+)', topic)
			matchStep = re.search('([0-9]+\.[0-9]+)', topic)
			if matchTopic and matchStep: 
				categorizeContent(COLLECTION, matchTopic.group(1), matchStep.group(1), content, course)

def cleanQuizzes(content):
	quizHeaders = set(re.findall('(<-- .*? Quiz -->\n.*\n)', content))
	for header in quizHeaders:
		# print(header)
		headers = re.findall(re.escape(header), content)
		if len(headers) > 0:
			content = ''.join(content.rsplit(headers[0], len(headers)-1))
	return content

def run():
	print("    - setting up")
	cleanDirectory(DIR_OUT)

	print("    - retrieving files")
	FILES = os.listdir(DIR_IN)
	for file in FILES: 
		print("    - extracting content from " + file)
		extractContent(COLLECTION, DIR_IN, file)

	print("    - saving")
	file_out = open("corpus-stats.csv", "w", encoding="utf-8")
	print("%s,%s,%s" % ("topic", "coverage", "wordcount"), file=file_out)
	for key, value in COLLECTION.items():
		printStatsAndCorpus(DIR_OUT, key, value, file_out)
	print("%s,%s,%s" % ("TOTAL", str(COVERAGE), str(WORD_COUNT)), file=file_out)


