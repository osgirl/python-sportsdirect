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
            away_team=None, venue=None):
        self.competition_id = competition_id
        self.start_date = start_date
        self.name = name
        self.home_team = home_team
        self.away_team = away_team
        self.venue = venue

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

        try:
            venue = Venue.parse(
                element.xpath('./details/venue')[0])
        except IndexError:
            venue = None

        return cls(competition_id=competition_id,
            start_date=start_date,
            name=name,
            home_team=home_team,
            away_team=away_team,
            venue=venue)


class Player(object):
    def __init__(self, player_id, first_name, last_name):
        self.player_id = player_id
        self.first_name = first_name
        self.last_name = last_name

        self._stats = []

    @classmethod
    def parse(cls, element):
        return cls(
            player_id=element.xpath('./id/text()')[0],
            first_name=element.xpath("./name[@type='first']/text()")[0],
            last_name=element.xpath("./name[@type='last']/text()")[0],
        )

    @property
    def stats(self):
        return self._stats

    def add_stat(self, stat):
        self._stats.append(stat)


class Stat(object):
    def __init__(self, num, stat_type, player=None, season_phase_from=None,
            season_phase_to=None):
        self.num = num
        self.stat_type = stat_type
        self.player = player
        self.season_phase_from = season_phase_from
        self.season_phase_to = season_phase_to

    @classmethod
    def parse(cls, element):
        return cls(
            num=cls.parse_num(element.attrib['num']),
            stat_type=element.attrib['type'],
        )

    @classmethod
    def parse_num(cls, val):
        try:
            return int(val)
        except ValueError:
            return float(val)


class Venue(object):
    def __init__(self, venue_id, name, city=None, state=None, country=None,
            timezone=None, capacity=None, field_type_id=None,
            field_type_name=None):
        self.venue_id = venue_id
        self.name = name
        self.city = city
        self.state = state
        self.country = country
        self.timezone = timezone
        self.capacity = capacity
        self.field_type_id = field_type_id
        self.field_type_name = field_type_name

    @classmethod
    def parse(cls, element):
        # XML for a venue looks like this:
        #
        # <venue>
        #   <id>/sport/football/venue:243</id>
        #   <name>Bank of America Stadium</name>
        #   <name type="short">BOA</name>
        #   <location>
        #     <city>Charlotte</city>
        #     <state>North Carolina</state>
        #     <country>USA</country>
        #     <timezone>US/Eastern</timezone>
        #  </location>
        #  <season-details>
        #    <capacity>73778</capacity>
        #    <field-type>
        #      <id>/sport/football/field-type:1</id>
        #      <name>Grass</name>
        #    </field-type>
        #  </season-details>
        # </venue>
        venue_id = element.xpath('./id/text()')[0]
        name = element.xpath('./name/text()')[0]

        # QUESTION: Should location be parsed into a separate object?
        city = element.xpath('./location/city/text()')[0]
        state = element.xpath('./location/state/text()')[0]
        country = element.xpath('./location/country/text()')[0]
        timezone = element.xpath('./location/timezone/text()')[0]

        capacity = element.xpath('./season-details/capacity/text()')[0]
        field_type_id = element.xpath('./season-details/field-type/id/text()')[0]
        field_type_name = element.xpath('./season-details/field-type/name/text()')[0]

        return cls(
                venue_id=venue_id,
                name=name,
                city=city,
                state=state,
                country=country,
                timezone=timezone,
                capacity=capacity,
                field_type_id=field_type_id,
                field_type_name=field_type_name)
