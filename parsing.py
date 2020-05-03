import requests
from bs4 import BeautifulSoup
import re


def parsing(urls: list):
    """
    :param urls: list of site urls
    :return: list of texts
    """
    texts = []
    for url in urls:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'lxml')
        paragraphs = soup.find_all('p')
        text = ""
        for paragraph in paragraphs:
            for child in paragraph.descendants:
                try:
                    text += child.string
                except TypeError:
                    pass
        text = text.lower()
        text = re.split(r"\W+|[\d]+", text)
        text = list(filter(None, text))
        texts.append(text)
    return texts
