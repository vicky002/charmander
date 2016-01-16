__author__ = 'vikesh'

""" ~youtube <seach query> will return the first youtube search result for the given term. """

import re

try:
    from urllib import quote
except ImportError:
    from urllib.request import quote

import requests


def youtube(searchquery):
    url = "https://www.youtube.com/results?search_query={0}"
    url = url.format(quote(searchquery))

    r = requests.get(url)
    results = re.findall('a href="(/watch[^&]*?)"', r.text)

    if not results:
        return "Sorry, charmander couldn't find any videos :crying_cat:"

    return "https://www.youtube.com{0}".format(results[0])


def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"~youtube (.*)", text)

    if not match:
        return

    searchquery = match[0]
    return youtube(searchquery.encode("utf8"))
