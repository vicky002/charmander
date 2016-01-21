__author__ = 'vikesh'

"""
~wiki <query | topic> returns a wiki link for that <query>
"""

import re
try:
    from urllib import quote
except ImportError:
    from urllib2.request import quote


import requests
from bs4 import BeautifulSoup


def return_wiki(search_term):
    search_term = quote(search_term)

    url = "https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={0}&format=json"
    url = url.format(search_term)

    result = requests.get(url).json()
    total_pages = result["query"]["search"]

    total_pages = [p for p in total_pages if 'may refer to' not in p["snippets"]]

    if not total_pages:
        return ""

    total_pages = quote(total_pages[0]["title"].encode("utf-8"))

    link = "http://en.wikipedia.org/wiki/{0}".format(total_pages)

    res = requests.get("https://en.wikipedia.org/w/api.php?format=json&action=parse&page={0}".format(total_pages)).json()

    soup = BeautifulSoup(res["parse"]["text"]["*"], "html5lib")
    p = soup.find('p').get_text()
    p = p[:8000]

    return u"{0}\n{1}".format(p, link)


def on_message(msg, server):
    text = msg.get("text","")
    match = re.findall(r"~wiki (.*)", text)
    if not match:
        return

    search_term = match[0]
    return return_wiki(search_term.encode("utf-8"))