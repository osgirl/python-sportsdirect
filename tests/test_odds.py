import os.path
from unittest import TestCase

from lxml import etree

import sportsdirect.odds
from sportsdirect.odds import OddsFeed
from sportsdirect.fetch import FilesystemFetcher

TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'test_data')

class OddsTestCase(TestCase):
    def test_get_odds(self):
        test_xml = os.path.join(TEST_DATA_DIR, 'odds_NFL.xml')
        fetcher = FilesystemFetcher(path=test_xml)
        odds = sportsdirect.odds.get_odds(sport='football', league='NFL',
            fetcher=fetcher)
        self.assertTrue(len(odds) > 0)
        point_spread = next(o for o in odds
                            if o.line_id == '/betting/odds:77824198')
        self.assertEqual(point_spread.odds_type, 'point_spread')
        self.assertEqual(point_spread.sportsbook, 'bet365')
        self.assertEqual(point_spread.opening, False)
        self.assertEqual(point_spread.home_handicap, 0)
        self.assertEqual(point_spread.home_odds, -111)
        self.assertEqual(point_spread.away_odds, -111)
               

class OddsFeedTestCase(TestCase):
    def test_parse_competition(self):
        xml_text = """
<competition>
    <id>/sport/football/competition:47352</id>
    <start-date>2015-08-28T19:30:00.000-04:00</start-date>
	<name>New England vs. Carolina</name>
	<home-team-content>
        <team>
            <id>/sport/football/team:29</id>
	        <name>Carolina</name>
        </team>
    </home-team-content>
	<away-team-content>
        <team>
            <id>/sport/football/team:18</id>
	        <name>New England</name>
        </team>
    </away-team-content>
</competition>    
"""
        feed = OddsFeed(sport='football', league='NFL')
        competition_node = etree.fromstring(xml_text) 
        competition = feed._parse_competition(competition_node) 
        self.assertEqual(competition.competition_id, '/sport/football/competition:47352')
        self.assertEqual(competition.name, 'New England vs. Carolina')
        self.assertEqual(competition.home_team.name, 'Carolina')
        self.assertEqual(competition.away_team.name, 'New England')
