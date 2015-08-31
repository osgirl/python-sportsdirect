import os.path
from unittest import TestCase

from sportsdirect.fetch import FilesystemFetcher
import sportsdirect.playbyplay

from sportsdirect.football.winprobability import calculate_winprobability


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'test_data')


class PlayByPlayTestCase(TestCase):
    def test_get_plays(self):
        test_xml = os.path.join(TEST_DATA_DIR, 'playbyplay_NFL.xml')
        fetcher = FilesystemFetcher(path=test_xml)
        sport = 'football'
        league = 'NFL'
        season = '2010-2011'
        competition = 28192

        game_feed = PlayByPlayFeed(sport, league, season, competition, fetcher)
        feed.load()

        plays = sportsdirect.playbyplay.get_plays(
            sport=sport, league=league, season=season, competition=competition, fetcher=fetcher)
        for p in plays:
            calculate_winprobability(game_feed, p)