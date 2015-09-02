import math
import scipy.stats

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

    This represents the probability the home team wins by 1 point or more, plus the probability a
    tie occurs (in which case they have a 50% chance to win, which seems sketchy to me but hey...)

    However, we first need to adjust the away_margin to account for the current set of in-game
    circumstances (down, field possession, ball, etc). To do that, use those circumstances to
    find the best-fitting expected-points situation and the resulting EP value, and add or
    subtract that to the current margin as necessary.

    Note that we'll only need to calculate win probability for the home team, since that will
    also give us the probability for the away team.
    """
    if play.seconds_remaining_in_game < 1:
        return None
    if not play.down or not play.yards_to_go:
        score = game_feed.calculate_score_at_play(play.play_id)
    else:
        score = game_feed.calculate_ep_adjusted_score_at_play(play.play_id)
    away_margin = score['away'] - score['home']
    vegas_line = {'home': 7, 'away': 0}
    total_minutes = 60
    if play.period_number not in [1, 2, 3, 4]:
        total_minutes = 15
    minutes_remaining = math.ceil(float(play.seconds_remaining_in_game)/float(60))

    p_win = 1 - scipy.stats.norm(
        -vegas_line['home'] * (minutes_remaining / total_minutes),
        (13.45 / math.sqrt((60 / minutes_remaining)))
    ).cdf(away_margin + 0.5)

    p_tie = scipy.stats.norm(
        -vegas_line['home'] * (minutes_remaining / total_minutes),
        (13.45 / math.sqrt((60 / minutes_remaining)))
    ).cdf(away_margin + 0.5) - scipy.stats.norm(
        -vegas_line['home'] * (minutes_remaining / total_minutes),
        (13.45 / math.sqrt((60 / minutes_remaining)))
    ).cdf(away_margin - 0.5)

    return {'home': p_win + (0.5 * p_tie), 'away': 1 - (p_win + (0.5 * p_tie))}
