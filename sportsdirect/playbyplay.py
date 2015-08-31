import posixpath

from csv import DictReader
from lxml import etree

from .base import Competition, Team, Player
from .feed import BaseFeed

EP_DATA_PATH = 'sportsdirect/data/football_ep_values.csv'


class PlayByPlayFeed(BaseFeed):
    def __init__(self, sport, league, season, competition, fetcher=None):
        self.sport = sport
        self.league = league
        self.season = season
        self.competition = competition
        self.home_team = None
        self.away_team = None
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
        self.home_team = competition.home_team
        self.away_team = competition.away_team

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

    def get_distance_to_endzone_at_play(self, play_id):
        play = next(p for p in self.plays if p.play_id == play_id)
        if ((play.yard_line_align == 'home' and self.home_team == play.team) or
                (play.yard_line_align == 'away' and self.away_team == play.team)):
            return 50 - play.yard_line + 50
        else:
            return play.yard_line

    def calculate_ep_adjusted_score_at_play(self, play_id):
        play = next(p for p in self.plays if p.play_id == play_id)
        score = self.calculate_score_at_play(play_id)
        yardline = self.get_distance_to_endzone_at_play(play_id)
        signature = '%d-%d-%d' % (self.down, self.distance, yardline)
        # Load ep data as dict, look for this exact signature. If not found, look
        # for closest match (presumably there will be 2 candidates for yardline).
        # If a tie on yardline (1 3 yards too short; the other 3 yards too long, say)
        # arbitrarily pick one to use. If no exact down/distance candidates exist,
        # or they're more than 20 yards off, fuzz the distance value as well and look
        # for best candidates with fuzzy distance and fuzzy yardline.
        with open(EP_DATA_PATH) as fh:
            reader = DictReader(fh)
            for line in reader:
                if line['State'] == signature:
                    return float(line['Markov EP'])
        return score

    def calculate_score_at_play(self, play_id):
        score = {'home': 0, 'away': 0}
        event_points = {
            'defensive_touchdown': 6,
            'field_goal_by': 3,
            'one_point_conversion': 1,
            'safety': 2,
            'touchdown': 6,
            'two_point_conversion': 2
        }
        idx = 0
        play = self.plays[idx]
        while play.play_id != play_id:
            for pe in play.play_events:
                if pe.event_type in event_points:
                    if play.team == self.home_team:
                        score['home'] += event_points[pe.event_type]
                    elif play.team == self.away_team:
                        score['away'] += event_points[pe.event_type]
            idx += 1
            if idx < len(self.plays):
                play = self.plays[idx]
        return score


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
            yard_line=None, yard_line_align=None, down=None, yards_to_go=None,
            possession=None):
        self.possession = possession
        self.play_id = play_id
        self.period_number = period_number
        self.time = play_time
        self.seconds_remaining_in_game = self._generate_seconds_remaining()
        self.team = team
        self.yard_line = yard_line
        self.yard_line_align = yard_line_align
        self.down = down
        self.yards_to_go = yards_to_go

        self.play_events = []

    def _generate_seconds_remaining(self):
        if self.time.startswith('PT') and self.time.endswith('S'):
            (minutes, seconds) = self.time[2:-1].split('M')
            offset = 0
            if self.period_number < 4:
                offset = (4 - self.period_number) * 15 * 60
            return offset + int(seconds) + (60 * int(minutes))
        else:
            return -1

    @classmethod
    def parse(cls, element):
        try:
            yard_line = int(element.xpath('./yard-line/text()')[0])
            yard_line_align = element.xpath('./yard-line/@align')[0]
        except IndexError:
            yard_line = None
            yard_line_align = None

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
            yard_line_align=yard_line_align,
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
