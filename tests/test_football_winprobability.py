import os.path
import sportsdirect

from unittest import TestCase

from sportsdirect.fetch import FilesystemFetcher
from sportsdirect.playbyplay import PlayByPlayFeed
from sportsdirect.football.winprobability import calculate_winprobability


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'test_data')


class WinProbabilityTestCase(TestCase):
    def test_calculate_win_probability(self):
        test_xml = os.path.join(TEST_DATA_DIR, 'playbyplay_NFL_20152016_Preseason.xml')
        fetcher = FilesystemFetcher(path=test_xml)

        game_feed = PlayByPlayFeed(
            sport='football', league='NFL', season='2015-2016', competition=47344, fetcher=fetcher)
        game_feed.load()

        play = next(p for p in game_feed.plays
                    if p.play_id == '/sport/football/play-by-play/event:290742')
        probability = calculate_winprobability(game_feed, play)
        self.assertEqual(probability, {
            'home': 0.30150159990239772,
            'away': 0.69849840009760222
        })

        play = next(p for p in game_feed.plays
                    if p.play_id == '/sport/football/play-by-play/event:290768')
        probability = calculate_winprobability(game_feed, play)
        self.assertEqual(probability, {
            'home': 0.237626448924734,
            'away': 0.76237355107526605
        })

        play = next(p for p in game_feed.plays
                    if p.play_id == '/sport/football/play-by-play/event:290797')
        probability = calculate_winprobability(game_feed, play)
        self.assertEqual(probability, {
            'home': 0.54826788703312823,
            'away': 0.45173211296687177
        })

        play = next(p for p in game_feed.plays
                    if p.play_id == '/sport/football/play-by-play/event:290847')
        probability = calculate_winprobability(game_feed, play)
        self.assertEqual(probability, {
            'home': 0.90513273272574235,
            'away': 0.094867267274257649
        })
