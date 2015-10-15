import os.path
from unittest import TestCase

from sportsdirect.fetch import FilesystemFetcher
import sportsdirect.playerstats


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'test_data')


class PlayerStatsTestCase(TestCase):
    def test_get_player_stats(self):
        test_xml = os.path.join(TEST_DATA_DIR, 'playerstats_MLB.xml')
        fetcher = FilesystemFetcher(path=test_xml)
        players = sportsdirect.playerstats.get_player_stats(sport='baseball',
            league='MLB', season='2015', team_id='2982', fetcher=fetcher)
        player = next(p for p in players
                      if p.first_name == "Kyle" and p.last_name == "Schwarber")
        stat = next(s for s in player.stats
                    if s.stat_type == "home_runs" and
                       s.season_phase_from == "Regular Season")
        stat = next(s for s in player.stats
                    if s.stat_type == "slugging_percentage" and
                       s.season_phase_from == "Regular Season")
        self.assertEqual(stat.num, 0.48706895)
