from bs4 import BeautifulSoup
import requests, re

async def get_soup_object(url):
	    return BeautifulSoup(requests.get(url).text, features="html.parser")

class quDict(object):

    @staticmethod #Modified version of PyDictionary meaning method (Will be used until I find a better dictionary to scape definitions from)
    async def get_top_meanings(input: str, limit_per: int = 3):
        input = input.replace(" ", "+")
        try:
            html_parser = await get_soup_object(f"http://wordnetweb.princeton.edu/perl/webwn?s={input}")
            types = html_parser.find_all("h3")
            lists = html_parser.find_all("ul")
            result = {}
            for t in types:
                regEx = str(lists[types.index(t)].text)
                meanings = []
                counter = 0
                for x in re.findall(r'\((.*?)\)', regEx):
                    if 'often followed by' in x:
                        pass
                    elif len(x) > 5 or ' ' in str(x):
                        meanings.append(x)
                        counter += 1
                        if(counter >= limit_per):
                            break
                result[t.text] = meanings
            return result
        except Exception as ex:
            print(f"Error: {ex}")

    @staticmethod
    async def get_top_synonyms(input: str, limit: int = 5):
        input = input.replace(" ", "%20")
        try:
            html_parser = await get_soup_object(f"http://www.thesaurus.com/browse/{input}")
            synonyms = html_parser.select(".MainContentContainer > section > div > section > ul")[0].find_all("a")[:limit]
            result = []
            for s in synonyms:
                result.append(s.text)
            return result
        except Exception as ex:
            print(f"Error: {ex}")

    @staticmethod
    async def get_top_antonyms(input: str, limit: int = 5):
        input = input.replace(" ", "%20")
        try:
            html_parser = await get_soup_object(f"http://www.thesaurus.com/browse/{input}")
            antonyms = html_parser.select(".MainContentContainer > section > div > section > ul")[1].find_all("a")[:limit]
            result = []
            for s in antonyms:
                result.append(s.text)
            return result
        except Exception as ex:
            print(f"Error: {ex}")

    @staticmethod
    async def get_urbandict_definitions(input: str, limit: int = 1):
        input = input.replace(" ", "%20")
        try:
            data = requests.get(f"http://api.urbandictionary.com/v0/define?term={input}").json()
            data = data["list"][:limit]
            result = []
            for item in data:
                definition = item["definition"]
                for ch in ['[',']']:
                    if ch in definition:
                        definition = definition.replace(ch,"**")
                result.append(definition)
            return result
        except Exception as ex:
            print(f"Error: {ex}")