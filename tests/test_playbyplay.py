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
        print plays
