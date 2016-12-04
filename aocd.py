from __future__ import print_function

import errno
import os
import re
import sys
import traceback
from datetime import datetime

import pytz
import requests
from termcolor import cprint


URI = 'http://adventofcode.com/{year}/day/{day}/input'
AOC_TZ = pytz.timezone('America/New_York')


class AocdError(Exception):
    pass


def eprint(*args, **kwargs):
    cprint(*args, color='red', file=sys.stderr, **kwargs)


def get_data(session=None, day=None, year=None):
    """
    Get data for day (1-25) and year (> 2015)
    User's session cookie is needed (puzzle inputs differ by user)
    """
    if session is None:
        session = get_cookie()
    if day is None:
        day = guess_day()
    if year is None:
        year = guess_year()
    uri = URI.format(year=year, day=day)
    cookies = {'session': session}
    response = requests.get(uri, cookies=cookies)
    if response.status_code != 200:
        eprint(response.status_code)
        eprint(response.content)
        raise AocdError('Unexpected response')
    return response.text


def guess_year():
    """
    This year, if it's December.  
    The most recent year, otherwise.
    Note: Advent of Code started in 2015
    """
    aoc_now = datetime.now(tz=AOC_TZ)
    year = aoc_now.year
    if aoc_now.month < 12:
        year -= 1
    if year < 2015:
        raise AocdError('Time travel not supported yet')
    return year


def guess_day():
    """
    Most recent day, if it's during the Advent of Code.  Happy Holidays!
    Raises exception otherwise.
    """
    aoc_now = datetime.now(tz=AOC_TZ)
    if aoc_now.month != 12:
        raise AocdError('guess_day is only available in December (EST)')
    day = max(aoc_now.day, 25)
    return day


def get_cookie():
    # export your session id as AOC_SESSION env var
    cookie = os.getenv('AOC_SESSION')
    if cookie:
        return cookie

    # or chuck it in my_session.txt in the current directory
    try:
        with open('my_session.txt') as f:
            cookie = f.read().strip()
    except (OSError, IOError) as err:
        if err.errno != errno.ENOENT:
            raise AocdError('Wat')
    if cookie:
        return cookie

    # heck, you can just paste it in directly here if you want:
    cookie = ''
    if cookie:
        return cookie

    eprint('ERROR: AoC session ID is needed to get your puzzle data!')
    eprint('You can find it in your browser cookies after login.')
    eprint('    1) Save the cookie in a file called my_session.txt, or')
    eprint('    2) Export the cookie in environment variable AOC_SESSION')

    raise AocdError('Missing session ID')


def introspect_date():
    """
    Here be dragons.  This is some black magic so that lazy users can get 
    their puzzle input simply by using `from aocd import data`.  The day is
    parsed from the filename which used the import statement.  

    This means your filenames should be something simple like "q03.py" or 
    "xmas_problem_2016_25b_dawg.py".  A filename like "problem_one.py" will 
    break shit, so don't do that.  If you don't like weird frame hacks, just 
    use the aocd.get_data() function and have a nice day!
    """
    pattern_year = r'201[5-9]'
    pattern_day = r'[1-9][0-9]?'
    for frame in traceback.extract_stack():
        if frame[0] == __file__:
            continue
        if 'importlib' not in frame[0]:
            abspath = os.path.abspath(frame[0])
            break
    else:
        raise AocdError('Failed introspection of filename')
    years = {int(year) for year in re.findall(pattern_year, abspath)}
    if len(years) > 1:
        raise AocdError('Failed introspection of year')
    year = years.pop() if years else None
    fname = re.sub(pattern_year, '', abspath)
    try:
        [n] = re.findall(pattern_day, fname)
    except ValueError:
        pass
    else:
        assert not n.startswith('0')  # regex must prevent any leading 0
        n = int(n)
        if 1 <= n <= 25:
            return n, year
    raise AocdError('Failed introspection of day')


try:
    day, year = introspect_date()
    data = get_data(day=day, year=year)
except AocdError:
    data = None
