
import re
import json
import urllib.request
from html.parser import HTMLParser

LANGUAGE = "English"

class MyHTMLParser(HTMLParser):
	
	isEnglish = False
	hasDefinition = False
	partOfSpeech = ['Noun', 'Verb', 'Adverb', 'Adjective', 'Pronoun', 'Preposition', 'Conjunction']

	def handle_starttag(self, tag, attrs):
		if tag == "h2":
			self.isEnglish = False
		elif tag == "span":
			for attr in attrs:
				if attr[0] == "id" and attr[1] == LANGUAGE:  
					self.isEnglish = True
				if self.isEnglish and attr[0] == "id" and attr[1] in self.partOfSpeech:
					self.hasDefinition = True

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