from .fetch import HTTPFetcher

class BaseFeed(object):
    BASE_URL = 'http://xml.sportsdirectinc.com/sport/v2'

    def __init__(self, fetcher=None):
        if fetcher is None:
            self.fetcher = HTTPFetcher(url=self.get_url())
        else:
            self.fetcher = fetcher

    def fetch(self):
        return self.fetcher.fetch()

    def load(self):
        xml_text = self.fetch()
        return self.parse(xml_text)
