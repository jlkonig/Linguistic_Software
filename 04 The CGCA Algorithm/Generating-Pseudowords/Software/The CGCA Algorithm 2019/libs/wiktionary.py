import asyncio  
import aiohttp  
import json
from html.parser import HTMLParser

URL         = 'https://en.wiktionary.org/w/api.php?action=parse&format=json&prop=text|revid|displaytitle&page='
LANGUAGE    = "English"
ASYNC_COUNT = 50

semaphore = asyncio.Semaphore(ASYNC_COUNT)

class My_HTML_Parser(HTMLParser):
    
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

async def create_session():
    return aiohttp.ClientSession()

async def close_session(client):
    return await client.close()

async def get_json(client, url):  
    async with client.get(url) as response:
        assert response.status == 200
        return await response.read()

async def get_wiki_words(client, word): 
    async with semaphore: 
        response = await get_json(client, URL + word)
        response_string = json.loads(response.decode('utf-8'))
        return [response_string, word]

def is_real_word(response, word):
    try:
        jsonWiki = response
        if "error" in jsonWiki: 
          print('    "'+word+'"', "is not in wiktionary")
          return False
        else:
            textContent   = jsonWiki["parse"]["text"]["*"]
            parser        = My_HTML_Parser()
            htmlResponse  = parser.feed(textContent)
            if parser.hasDefinition: return True
            else: 
              print('    "'+word+'"', "is not an English word")
              return False
    except Exception as error: 
      print('    "'+word+'":', "an error occurred when parsing")
      return False

def return_real_words(words):
    loop        = asyncio.get_event_loop()  
    client      = loop.run_until_complete(create_session())
    results     = asyncio.gather(*[get_wiki_words(client, word) for word in words])
    responses  = loop.run_until_complete(results)
    loop.run_until_complete(close_session(client))

    real_words = []
    for resp in responses:
        if is_real_word(resp[0], resp[1]): real_words.append(resp[1])
    return real_words

def check_is_real_word(word):
    words = return_real_words([word])
    if len(words) ==  1: return True
    else: return False 