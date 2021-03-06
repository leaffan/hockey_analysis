#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import argparse

from adjusted_goals.goals_per_game import retrieve_goals_per_season
from adjusted_goals.goals_per_game import calculate_adjustment_factors
from adjusted_goals.goal_leaders import retrieve_career_leaders
from adjusted_goals.goal_leaders import retrieve_yearly_top
from adjusted_goals.adjust_goals import retrieve_and_adjust_goal_totals

from utils import prepare_logging, retrieve_season

if __name__ == '__main__':

    prepare_logging(log_types=['screen'])

    parser = argparse.ArgumentParser(
        description="Adjusting individual goal scoring totals in dependance" +
                    "of league-wide scoring rate.")
    parser.add_argument(
        'steps',
        metavar='processing_steps',
        help='Processing step(s) to conduct.',
        choices=['1', '2', '3', 'all'])
    parser.add_argument(
        '-f', '--from', dest='from_season', required=False, default=1917,
        metavar='first season to include in analysis', type=int,
        help="The first season to be considered for analysis")
    parser.add_argument(
        '-t', '--to', dest='to_season', required=False, default=9999,
        metavar='last season to include in analysis', type=int,
        help="The last season to be considered for analysis")
    # TODO: add arguments for goal scoring leader retrieval, i.e. maximum top
    # position threshold or minimum career season total

    args = parser.parse_args()
    setup_steps = args.steps
    from_season = args.from_season
    to_season = args.to_season

    if to_season == 9999:
        to_season = retrieve_season()

    goals_per_season_path = os.path.join(
        "results", "goals_per_season.json")
    goal_leaders_path = os.path.join(
        "results", "career_goal_leaders.json")
    adjusted_goal_data_path = os.path.join(
        "results", "adjusted_goal_data.json")

    # retrieving goals per season and season adjustment factors
    if setup_steps in ['1', 'all']:
        season_data = retrieve_goals_per_season(from_season, to_season)
        calculate_adjustment_factors(season_data)

        open(goals_per_season_path, 'w').write(
            json.dumps(season_data, sort_keys=True, indent=2))

    # retrieving goal scoring leaders
    if setup_steps in ['2', 'all']:
        career_goal_leaders = list()
        yearly_top = list()
        # retrieving all players with at least 300 career goals
        career_goal_leaders = retrieve_career_leaders(300)
        # retrieving top five goalscorers per season
        yearly_top = retrieve_yearly_top(5, from_season, to_season)

        # retrieving urls to player pages for goal-scoring career leaders
        career_leaders_urls = [d['url'] for d in career_goal_leaders]
        # creating new list of all goal-scoring leaders
        goal_leaders = career_goal_leaders
        # adding goal-scoring per season leaders to list of all goal-scoring
        # leaders if they are not yet a part of it
        for yearly_leader in yearly_top:
            if yearly_leader['url'] not in career_leaders_urls:
                goal_leaders.append(yearly_leader)

        open(goal_leaders_path, 'w').write(
            json.dumps(goal_leaders, indent=2))

    # adjusting goal scoring totals according to goals scored per season
    if setup_steps in ['3', 'all']:
        adjusted_goal_data = retrieve_and_adjust_goal_totals(
            goal_leaders_path, goals_per_season_path)

        open(adjusted_goal_data_path, 'w').write(
            json.dumps(adjusted_goal_data, sort_keys=True, indent=2))
