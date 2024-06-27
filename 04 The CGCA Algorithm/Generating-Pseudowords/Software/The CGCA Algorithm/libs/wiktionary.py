import asyncio
import aiohttp
import json
import sys

URL = 'https://en.wiktionary.org/w/api.php?action=parse&format=json&prop=text|revid|displaytitle&page='
LANGUAGE = "English"
ASYNC_COUNT = 50
semaphore = asyncio.Semaphore(ASYNC_COUNT)

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
            print(f'    "{word}" is not in wiktionary')
            return False
        else:
            textContent = jsonWiki["parse"]["text"]["*"]
            
            # Check if the language section exists
            if f'id="{LANGUAGE}"' not in textContent:
                print(f'    "{word}" does not have an {LANGUAGE} entry')
                return False
            
            hasDefinition = False
            foundPartOfSpeech = False
            
            # Check for parts of speech and definitions
            parts_of_speech = ['Noun', 'Verb', 'Adjective', 'Adverb', 'Pronoun', 'Preposition', 'Conjunction']
            for pos in parts_of_speech:
                if (f'<span class="mw-headline" id="{pos}">{pos}</span>' in textContent or
                    f'<div class="mw-heading mw-heading3"><h3 id="{pos}">{pos}</h3>' in textContent or
                    f'<div class="mw-heading mw-heading4"><h4 id="{pos}">{pos}</h4>' in textContent):
                    foundPartOfSpeech = True
                    # Check for definition list after the part of speech
                    if '<ol>' in textContent.split(pos, 1)[1]:
                        hasDefinition = True
                        print(f'    "{word}" is a real {LANGUAGE} word ({pos})')
                        return True
            
            if foundPartOfSpeech and not hasDefinition:
                print(f'    "{word}" has a part of speech but no clear definition')
            elif not foundPartOfSpeech:
                print(f'    "{word}" is in wiktionary but no clear part of speech found')
            
            return hasDefinition

    except Exception as error:
        print(f'    "{word}": an error occurred when parsing')
        print(f"Error details: {str(error)}")
        return False

def return_real_words(words):
    loop = asyncio.get_event_loop()
    client = loop.run_until_complete(create_session())
    results = asyncio.gather(*[get_wiki_words(client, word) for word in words])
    responses = loop.run_until_complete(results)
    loop.run_until_complete(close_session(client))
    real_words = []
    for resp in responses:
        if is_real_word(resp[0], resp[1]): 
            real_words.append(resp[1])
    return real_words

def check_is_real_word(word):
    words = return_real_words([word])
    if len(words) == 1: 
        return True
    else: 
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 wiktionary.py <word>")
    else:
        word = sys.argv[1]
        if check_is_real_word(word):
            print(f'"{word}" is a real word.')
        else:
            print(f'"{word}" is not a real word.')
