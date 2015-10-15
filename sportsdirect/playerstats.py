import posixpath

from lxml import etree

from .base import Player, Stat
from .feed import BaseFeed


class PlayerStatsFeed(BaseFeed):
    def __init__(self, sport, league, season, team_id, fetcher=None):
        self.sport = sport
        self.league = league
        self.season = season
        self.team_id = team_id

        self.players = []

        super(PlayerStatsFeed, self).__init__(fetcher=fetcher)

    def get_url(self):
        # Example (Cubs, 2015):
        # http://xml.sportsdirectinc.com/sport/v2/baseball/MLB/player-stats/2015/player_stats_2982_MLB.xml
        xml_filename = 'player_stats_{team_id}_{league}.xml'.format(
            team_id=self.team_id, league=self.league)
        url = self.BASE_URL + posixpath.join('/', self.sport, self.league,
            'player-stats', self.season, xml_filename)
        return url


class BaseballPlayerStatsFeed(PlayerStatsFeed):
    def parse(self, xml_text):
        self.players = []

        root = etree.fromstring(xml_text)

        for player_el in root.xpath('//*/player-content'):
            player = Player.parse(player_el.xpath('./player')[0])

            for stat_group_el in player_el.xpath('./stat-group'):
                season_phase_from = stat_group_el.xpath("./scope[@type='season-phase-from']")[0].attrib['str']
                season_phase_to = stat_group_el.xpath("./scope[@type='season-phase-to']")[0].attrib['str']
               
                for stat_el in stat_group_el.xpath('./stat'):
                    stat = Stat.parse(stat_el)
                    stat.season_phase_from = season_phase_from
                    stat.season_phase_to = season_phase_to
                    stat.player = player
                    player.add_stat(stat)

            self.players.append(player)        



def get_player_stats(sport, league, season, team_id, fetcher=None):
    feed_cls_name = sport.title() + 'PlayerStatsFeed'
    try:
        feed_cls = globals()[feed_cls_name]
    except KeyError:
        msg = "Parsing of {sport} feeds is not yet supported.".format(
            sport=sport)
        raise ValueError(msg)

    feed = feed_cls(sport=sport, league=league, season=season, team_id=team_id,
        fetcher=fetcher)
    feed.load()
    return feed.players
