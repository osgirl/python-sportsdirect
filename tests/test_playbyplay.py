import os.path
from unittest import TestCase

from sportsdirect.fetch import FilesystemFetcher
import sportsdirect.playbyplay


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'test_data')

class PlayByPlayTestCase(TestCase):
    def test_get_plays(self):
        test_xml = os.path.join(TEST_DATA_DIR, 'playbyplay_NFL.xml')
        fetcher = FilesystemFetcher(path=test_xml)
        plays = sportsdirect.playbyplay.get_plays(sport='football',
            league='NFL', season='2010-2011', competition=28192, fetcher=fetcher)
        play = next(p for p in plays
                    if p.play_id == '/sport/football/play-by-play/event:636')
        self.assertEqual(play.team.name, "N.Y. Giants")
        self.assertEqual(play.period_number, 4)

        possession = play.possession
        self.assertEqual(possession.team.name, "N.Y. Giants")

        play_event = play.play_events[0]
        self.assertEqual(play_event.event_type, 'snap_to')
        self.assertEqual(play_event.player.first_name, 'Rhett')
        self.assertEqual(play_event.player.last_name, 'Bomar')
