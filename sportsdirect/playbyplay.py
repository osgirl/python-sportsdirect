import posixpath

from lxml import etree

from .base import Competition
from .feed import BaseFeed


class PlayByPlayFeed(BaseFeed):
    def __init__(self, sport, league, season, competition, fetcher=None):
        self.sport = sport
        self.league = league
        self.season = season
        self.competition = competition
        super(PlayByPlayFeed, self).__init__(fetcher=fetcher)

        self.competitions = []

    def get_url(self):
        xml_filename = 'play_by_play_{league}_{competition}.xml'.format(
            league=self.league, competition=self.competition)
        url = self.BASE_URL + posixpath.join('/', self.sport, self.league, 'play-by-play',
            self.season, xml_filename) 
        return url

    def parse(self, xml_text):
        root = etree.fromstring(xml_text)
        elements = root.xpath('//*/play-by-play')
        print elements[0].keys()
        self.plays = [] #[Competition.parse(e) for e in elements]


def get_plays(sport, league, season, competition, fetcher=None):
    feed = PlayByPlayFeed(sport, league, season, competition, fetcher)
    feed.load()
    return feed.plays
