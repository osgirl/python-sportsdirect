import posixpath

from lxml import etree

from .base import Competition, Team, Player
from .feed import BaseFeed


class PlayByPlayFeed(BaseFeed):
    def __init__(self, sport, league, season, competition, fetcher=None):
        self.sport = sport
        self.league = league
        self.season = season
        self.competition = competition
        super(PlayByPlayFeed, self).__init__(fetcher=fetcher)

        self.plays = []


    def get_url(self):
        xml_filename = 'play_by_play_{league}_{competition}.xml'.format(
            league=self.league, competition=self.competition)
        url = self.BASE_URL + posixpath.join('/', self.sport, self.league, 'play-by-play',
            self.season, xml_filename)
        return url

    def parse(self, xml_text):
        self.plays = []

        root = etree.fromstring(xml_text)

        competition_el = root.xpath('//*/competition')[0]
        competition = Competition.parse(competition_el)

        possession = None
        for el in competition_el.xpath('./play-by-play/possession|./play-by-play/play'):
            if el.tag == 'possession':
                possession = Possession.parse(el)
                possession.competition = competition
            elif el.tag == 'play':
                play = Play.parse(el)
                play.possession = possession
                play.play_events = [PlayEvent.parse(e)
                                    for e
                                    in el.xpath('./play-events/play-event')]
                self.plays.append(play)


class Possession(object):
    def __init__(self, possession_id, period_number, possession_time, team,
            competition=None):
        self.competition = competition
        self.possession_id = possession_id
        self.period_number = period_number
        self.time = possession_time
        self.team = team

    @classmethod
    def parse(cls, element):
        return cls(
            possession_id=element.xpath('./id/text()')[0],
            period_number=int(element.xpath('./event-time/period-number/text()')[0]),
            possession_time=element.xpath('./event-time/time/text()')[0],
            team=Team.parse(element.xpath('./team')[0])
        )


class Play(object):
    def __init__(self, play_id, period_number, play_time, team,
            yard_line=None, down=None, yards_to_go=None, possession=None):
        self.possession = possession
        self.play_id = play_id
        self.period_number = period_number
        self.time = play_time
        self.team = team
        self.yard_line = yard_line
        self.down = down
        self.yards_to_go = yards_to_go

        self.play_events = []

    @classmethod
    def parse(cls, element):
        try:
            yard_line = int(element.xpath('./yard-line/text()')[0])
        except IndexError:
            yard_line = None

        try:
            down = int(element.xpath('./down/text()')[0])
        except IndexError:
            down = None

        try:
            yards_to_go = int(element.xpath('./yards-to-go/yards/text()')[0])
        except IndexError:
            yards_to_go = None

        return cls(
            play_id=element.xpath('./id/text()')[0],
            period_number=int(element.xpath('./event-time/period-number/text()')[0]),
            play_time=element.xpath('./event-time/time/text()')[0],
            team=Team.parse(element.xpath('./team')[0]),
            yard_line=yard_line,
            down=down,
            yards_to_go=yards_to_go
        )


class PlayEvent(object):
    def __init__(self, event_type, player=None, yards=None, play=None):
        self.event_type = event_type
        self.player = player
        self.yards = yards
        self.play = play

    @classmethod
    def parse(cls, element):
        try:
            yards = int(element.xpath('./yards/text()')[0])
        except IndexError:
            yards = None

        try:
            player = Player.parse(element.xpath('./player')[0])
        except IndexError:
            player = None

        return cls(
          event_type=element.xpath('./type/text()')[0],
          player=player,
          yards=yards
        )


def get_plays(sport, league, season, competition, fetcher=None):
    feed = PlayByPlayFeed(sport, league, season, competition, fetcher)
    feed.load()
    return feed.plays
