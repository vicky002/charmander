""" ~search <query> will return the top google result for that query """

from bs4 import BeautifulSoup
import re
import requests

__author__ = 'vikesh'

try:
    from urllib import quote, unquote
except ImportError:
    from urllib.request import quote, unquote


def google(query):
    query = quote(query)
    url = "https://encrypted.google.com/search?q={0}".format(query)
    soup = BeautifulSoup(requests.get(url).text, "html5lib")

    answer = soup.findAll("h3", attrs={"class": "r"})
    if not answer:
        return ":fire: Sorry, Google doesn't have an answer for your Query :fire:"

    return unquote(re.findall(r"q=(.*?)&", str(answer[0]))[0])


def message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"~(?:google|search) (.*)", text)

    if not match:
        return

    return google(match[0])
