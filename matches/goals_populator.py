import json
import operator
import re
import time
from datetime import date, timedelta
from functools import reduce

import requests
from background_task import background
from django.db.models import Q

from matches.models import Match, VideoGoal


@background(schedule=60)
def fetch_videogoals():
    print('Fetching new goals')
    _fetch_reddit_goals()
    # How to get historic data
    # _fetch_reddit_goals_from_date(days_ago=30)


def _fetch_reddit_goals():
    i = 0
    after = None
    while i < 10:
        response = _fetch_data_from_reddit_api(after)
        data = json.loads(response.content)
        if 'data' not in data.keys():
            print(f'No data in response: {response.content}')
            return
        results = data['data']['dist']
        print(f'{results} posts fetched...')
        for post in data['data']['children']:
            post = post['data']
            if post['url'] is not None and 'Thread' not in post['title'] and 'reddit.com' not in post['url']:
                title = post['title']
                find_and_store_match(post, title)
        after = data['data']['after']
        i += 1
    print('Finished fetching goals')


def _fetch_reddit_goals_from_date(days_ago=2):
    start_date = date.today() - timedelta(days=days_ago)
    for single_date in (start_date + timedelta(n) for n in range(days_ago + 1)):
        response = _fetch_historic_data_from_reddit_api(single_date)
        data = json.loads(response.content)
        if 'data' not in data.keys():
            print(f'No data in response: {response.content}')
            return
        results = len(data['data'])
        print(f'{results} posts fetched...')
        for post in data['data']:
            if post['url'] is not None and 'Thread' not in post['title'] and 'reddit.com' not in post['url']:
                title = post['title']
                find_and_store_match(post, title)
    print('Finished fetching goals')


def find_and_store_match(post, title):
    home_team, away_team, minute_str = extract_names_from_title(title)
    if home_team is None or away_team is None:
        return
    matches_results = find_match(home_team, away_team, from_date=date.today())
    if matches_results.exists():
        match = matches_results.first()
        # print(f'Match {match} found for: {title}')
        try:
            videogoal = VideoGoal.objects.get(permalink__exact=post['permalink'])
        except VideoGoal.DoesNotExist:
            videogoal = VideoGoal()
            videogoal.permalink = post['permalink']
        videogoal.match = match
        videogoal.url = post['url']
        videogoal.title = post['title']
        videogoal.minute = minute_str
        videogoal.save()
        # print('Saved: ' + title)
    else:
        print(f'No match found in database [{home_team}]-[{away_team}] for: {title}')
        pass


def extract_names_from_title(title):
    home = re.findall(r'\[?\]?\s?((\w|\s|-)+)((\d|\[\d\])([-x]| [-x] | [-x]|[-x] ))(\d|\[\d\])', title)
    away = re.findall(r'(\d|\[\d\])([-x]| [-x] | [-x]|[-x] )(\d|\[\d\])\s?(((\w|\s|-)(?!- ))+)(:|\s?\||-)?',
                      title)
    minute = re.findall(r'(\S*\d+\S*)\'', title)
    if len(home) > 0:
        home_team = home[0][0].strip()
        if len(away) > 0:
            away_team = away[0][3].strip()
            if len(minute) > 0:
                minute_str = minute[-1].strip()
            else:
                minute_str = ''
                print(f'Minute not found for: {title}')
            return home_team, away_team, minute_str
        else:
            print('Failed away: ' + title)
    else:
        print('Failed home and away: ' + title)
    return None, None, None


def find_match(home_team, away_team, from_date=date.today()):
    affiliate_terms = ['W', 'U19', 'U20', 'U21', 'U23', 'II', 'B']
    regex_string = r'( ' + r'| '.join(affiliate_terms) + r')$'
    affiliate_home = re.findall(regex_string, home_team)
    affiliate_away = re.findall(regex_string, away_team)
    matches = Match.objects.filter(Q(home_team__name__unaccent__trigram_similar=home_team) |
                                   Q(home_team__alias__alias__unaccent__trigram_similar=home_team),
                                   Q(away_team__name__unaccent__trigram_similar=away_team) |
                                   Q(away_team__alias__alias__unaccent__trigram_similar=away_team),
                                   datetime__gte=(from_date - timedelta(days=2)))
    if len(affiliate_home) > 0:
        matches = matches.filter(home_team__name__endswith=affiliate_home[0])
    else:
        matches = matches.exclude(
            reduce(operator.or_, (Q(home_team__name__endswith=f' {term}') for term in affiliate_terms)))
    if len(affiliate_away) > 0:
        matches = matches.filter(away_team__name__endswith=affiliate_away[0])
    else:
        matches = matches.exclude(
            reduce(operator.or_, (Q(away_team__name__endswith=f' {term}') for term in affiliate_terms)))
    return matches


def _fetch_data_from_reddit_api(after):
    headers = {
        "User-agent": "Goals Populator 0.1"
    }
    response = requests.get(f'http://api.reddit.com/r/soccer/new?limit=100&after={after}',
                            headers=headers)
    return response


def _fetch_historic_data_from_reddit_api(from_date):
    after = int(time.mktime(from_date.timetuple()))
    before = int(after + 86400)  # a day
    headers = {
        "User-agent": "Goals Populator 0.1"
    }
    response = requests.get(
        f'https://api.pushshift.io/reddit/search/submission/'
        f'?subreddit=soccer&sort=desc&sort_type=created_utc&after={after}&before={before}&size=1000',
        headers=headers)
    return response
