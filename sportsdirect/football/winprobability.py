import math

from ..base import Competition, Team, Player
from ..playbyplay import PlayByPlayFeed, Possession, Play, PlayEvent
from ..odds import get_odds


def calculate_winprobability(game_feed, play):
    """
    Calculation taken from http://www.pro-football-reference.com/about/win_prob.htm, with
    Expected Points data from http://www.drivebyfootball.com/2012/08/modifying-markov-model.html

    In Excel-speak, the formula (for the home team) is:

    (1 -
        NORMDIST(
            ((away_margin) + 0.5),
            (-home_vegas_line * (minutes_remaining / 60)),
            (13.45 / SQRT((60 / minutes_remaining))),
            TRUE
        )
    )
    +
    (0.5 * (
        NORMDIST(
            ((away_margin) + 0.5),
            (-home_vegas_line * (minutes_remaining / 60)),
            (13.45 / SQRT((60 / minutes_remaining))),
            TRUE
        ) - NORMDIST(
            ((away_margin) - 0.5),
            (-home_vegas_line * (minutes_remaining / 60)),
            (13.45 / SQRT((60 / minutes_remaining))),
            TRUE
        ))
    )

    However, we first need to adjust the away_margin to account for the current set of in-game
    circumstances (down, field possession, ball, etc). To do that, use those circumstances to
    find the best-fitting expected-points situation and the resulting EP value, and add or
    subtract that to the current margin as necessary.
    """
    # Need to calculate margin at beginning of this play in the game, then add expected points
    score = game_feed.calculate_ep_adjusted_score_at_play(play.play_id)
    margin = {'home': score['home'] - score['away'], 'away': score['away'] - score['home']}
    vegas_line = {'home': 0, 'away': 0}
    total_minutes = 60
    if play.period_number not in [1, 2, 3, 4]:
        total_minutes = 15
    minutes_remaining = math.ceil(play.seconds_remaining_in_game/60)
    #print play.play_id
    #print play.possession.team.name, play.possession.time, play.period_number, play.team.name,
    #play.down, play.time
    #for pe in play.play_events:
    #    print pe.event_type
