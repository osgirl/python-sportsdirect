import os.path
from unittest import TestCase

from sportsdirect.fetch import FilesystemFetcher
import sportsdirect.schedule


TEST_DATA_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             'test_data')

class ScheduleTestCase(TestCase):
    def test_get_schedule(self):
        test_xml = os.path.join(TEST_DATA_DIR, 'schedule_NFL.xml')
        fetcher = FilesystemFetcher(path=test_xml)
        competitions = sportsdirect.schedule.get_schedule(sport='football',
            league='NFL', fetcher=fetcher)
        self.assertTrue(len(competitions) > 0)
        competition = next(c for c in competitions
                           if c.competition_id == '/sport/football/competition:47352')
        self.assertEqual(competition.home_team.name, "Carolina")
        self.assertEqual(competition.away_team.name, "New England")
        self.assertEqual(competition.venue.name, "Bank of America Stadium")
