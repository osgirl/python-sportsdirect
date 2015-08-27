import requests

class Fetcher(object):
    def fetch(self):
        return ""

class FilesystemFetcher(Fetcher):
    def __init__(self, path):
        self.path = path

    def fetch(self):
        with open(self.path) as f:
            return f.read()


class HTTPFetcher(Fetcher):
    def __init__(self, url):
        self.url = url

    def fetch(self):
        resp = requests.get(self.url)
        return resp.content
