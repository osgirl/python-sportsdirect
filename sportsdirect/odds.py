import posixpath

import dateutil.parser
from lxml import etree

from .base import Competition
from .feed import BaseFeed

class OddsFeed(BaseFeed):
    def __init__(self, sport, league, fetcher=None):
        self.sport = sport
        self.league = league
        super(OddsFeed, self).__init__(fetcher=fetcher)

        self.competitions = []

    def get_url(self):
        xml_filename = 'odds_{league}.xml'.format(league=self.league)
        url = self.BASE_URL + posixpath.join('/', self.sport, self.league, 'odds',
            xml_filename)
        return url

    def parse(self, xml_text):
        root = etree.fromstring(xml_text)
        self.competitions = [self._parse_competition(c)
                             for c in root.xpath('//competition')]
        return self


    def _parse_competition(self, element):
        competition = Competition.parse(element)

        competition.point_spread = [self._parse_point_spread(b, competition)
            for b in element.xpath('./betting/point-spread')]
        competition.over_under = [self._parse_over_under(b, competition)
            for b in element.xpath('./betting/over-under')]

        return competition

    def _parse_odds(self, element):
        return dict(
            line_id=element.xpath('./id/text()')[0],
            date=dateutil.parser.parse(element.get('date')),
            opening=(element.get('opening') == 'true'),
            status=element.get('status'),
            sportsbook=element.xpath('./sportsbook/text()')[0],
        )

    def _parse_point_spread(self, element, competition):
        common_kwargs = self._parse_odds(element)
        return PointSpread(
            competition=competition,
            home_handicap=float(element.xpath('./home-handicap/text()')[0]),
            home_odds=int(element.xpath('./home-odds/american/text()')[0]),
            away_odds=int(element.xpath('./away-odds/american/text()')[0]),
            **common_kwargs
        )

    def _parse_over_under(self, element, competition):
        common_kwargs = self._parse_odds(element)
        return OverUnder(
            competition=competition,
            total=float(element.xpath('./total/text()')[0]),
            over_odds=int(element.xpath('./over-odds/american/text()')[0]),
            under_odds=int(element.xpath('./under-odds/american/text()')[0]),
            **common_kwargs
        )


class BaseOdds(object):
    def __init__(self, competition, line_id, date, opening, status, sportsbook):
        self.competition = competition
        self.line_id = line_id
        self.date = date
        self.opening = opening
        self.status = status
        self.sportsbook = sportsbook


class MoneyLine(BaseOdds):
    def __init__(self, competition, line_id, date, opening, status, sportsbook,
                 home_odds, away_odds):
        super(MoneyLine, self).__init__(competition, line_id, date, opening, status,
            sportsbook)
        self.odds_type = 'money_line'
        self.home_odds = home_odds
        self.away_odds = away_odds


class PointSpread(BaseOdds):
    def __init__(self, competition, line_id, date, opening, status, sportsbook,
                 home_handicap, home_odds, away_odds):
        super(PointSpread, self).__init__(competition, line_id, date, opening, status,
            sportsbook)
        self.odds_type = 'point_spread'
        self.home_handicap = home_handicap
        self.home_odds = home_odds
        self.away_odds = away_odds


class OverUnder(BaseOdds):
    def __init__(self, competition, line_id, date, opening, status, sportsbook,
                 total, over_odds, under_odds):
        super(OverUnder, self).__init__(competition, line_id, date, opening, status,
            sportsbook)
        self.odds_type = 'over_under'
        self.total = total
        self.over_odds = over_odds
        self.under_odds = under_odds


def get_odds(sport, league, competition=None, odds_type=None, fetcher=None):
    feed = OddsFeed(sport, league, fetcher=fetcher)
    feed.load()
    competitions = feed.competitions
    if competition is not None:
        competitions = [c for c in competitions
                        if c.competition_id == competition.competition_id]

    odds = []
    for c in competitions:
        if odds_type is None:
            odds += c.odds
        else:
            odds += getattr(c, odds_type)

    return odds
