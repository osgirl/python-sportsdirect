import posixpath

from lxml import etree

from .base import Competition
from .feed import BaseFeed


class ScheduleFeed(BaseFeed):
    def __init__(self, sport, league, fetcher=None):
        self.sport = sport
        self.league = league
        super(ScheduleFeed, self).__init__(fetcher=fetcher)

        self.competitions = []

    def get_url(self):
        xml_filename = 'schedule_{league}.xml'.format(league=self.league)
        url = self.BASE_URL + posixpath.join('/', self.sport, self.league, 'schedule',
            xml_filename) 
        return url

    def parse(self, xml_text):
        root = etree.fromstring(xml_text)
        elements = root.xpath('//*/season-content/competition')
        self.competitions = [Competition.parse(e) for e in elements]


def get_schedule(sport, league, team=None, fetcher=None):
    feed = ScheduleFeed(sport, league, fetcher)
    feed.load()
    competitions = feed.competitions
    if team is not None:
        competitions = [c for c in competitions
                        if (c.home_team.team_id == team or
                            c.away_team.team_id == team)]

    return competitions
