import dateutil.parser

class Team(object):
    def __init__(self, team_id, name):
        self.team_id = team_id
        self.name = name
        
    @classmethod
    def parse(cls, element):
        team_id = element.xpath('./id/text()')[0]
        name = element.xpath('./name/text()')[0]
        return cls(
            team_id=team_id,
            name=name
        )


class Competition(object):
    def __init__(self, competition_id, start_date, name=None, home_team=None,
            away_team=None):
        self.competition_id = competition_id
        self.start_date = start_date
        self.name = name
        self.home_team = home_team
        self.away_team = away_team

    @property
    def odds(self):
        return self.point_spread + self.over_under

    @classmethod
    def parse(cls, element):
        competition_id = element.xpath('./id/text()')[0]
        start_date = dateutil.parser.parse(
            element.xpath('./start-date/text()')[0]) 
        try:
            name = element.xpath('./name/text()')[0]
        except IndexError:
            name = None
        home_team = Team.parse(
            element.xpath('./home-team-content/team')[0])
        away_team = Team.parse(
            element.xpath('./away-team-content/team')[0])
       
        return cls(competition_id=competition_id,
            start_date=start_date,
            name=name,
            home_team=home_team,
            away_team=away_team)

