import posixpath

from lxml import etree

from .base import Competition, Team
from .feed import BaseFeed


class BoxScoreFeed(BaseFeed):
    def __init__(self, sport, league, season, competition, fetcher=None):
        self.sport = sport
        self.league = league
        self.season = season
        self.competition = competition
        self.home_team = None
        self.away_team = None
        super(BoxScoreFeed, self).__init__(fetcher=fetcher)

    def get_url(self):
        xml_filename = 'boxscore_{league}_{competition}.xml'.format(
            league=self.league, competition=self.competition)
        url = self.BASE_URL + posixpath.join('/', self.sport, self.league, 'boxscores',
            self.season, xml_filename)
        return url

    def parse(self, xml_text):
        root = etree.fromstring(xml_text)
        c = root.xpath('//team-sport-content/league-content/season-content/competition')[0]
        self.home_handicap = int(
            c.xpath('./betting/point-spread[@closing="true"]/home-handicap/text()')[0])
        return self
