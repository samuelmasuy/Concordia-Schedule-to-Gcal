
# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================
"""
    Academic_dates.
    ~~~~~~~~~~~~~~

    Start and end of the 2014-2015 academic terms + Holidays
    Data fetched from:
    - http://www.concordia.ca/students/registration/term-dates-deadlines.html
    - http://www.concordia.ca/events/university-holidays.html
    - http://www.concordia.ca/students/registration/term-dates-deadlines.html

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
import re
import json
from datetime import datetime, timedelta, date
from os import path

import requests
from lxml import html
from dateutil import parser
from bson import json_util

URL_HOLIDAY = 'http://www.concordia.ca/events/university-holidays.html'
BASE_ACADEMIC_URL = ('http://portico.concordia.ca/cq/'
                     'daily-events/ac_search.php?start=')
TERM_DATES_URL = ('http://www.concordia.ca/students/'
                  'registration/term-dates-deadlines.html')
SEMESTER_NAMES = ['summer_4A', 'summer_5B', 'summer_6C', 'summer_7D',
                  'summer_8E', 'summer_9F', 'fall', 'fall_winter', 'winter']


def make_tree(url, arg=''):
    """Create a lxml tree from a url with possibly some arguments."""
    response = requests.get('{0}{1}'.format(url, arg)).text
    return html.fromstring(response)


def expand_date_range(current, last):
    """Generate all the dates in between a range of dates."""
    while not current > last:
        yield current
        current += timedelta(days=1)


def adjust_year(_date):
    """Relative adjustement of dates' years to allow update of this
    script at any time of the year."""
    today = date.today()
    if _date.month in range(1, 5) and today.month in range(5, 13):
        _date = _date.replace(year=_date.year+1)
    elif _date.month in range(5, 13) and today.month in range(1, 5):
        _date = _date.replace(year=_date.year-1)
    return _date


def get_general_holidays():
    """Get all the dates of when the university is closed."""
    tree = make_tree(URL_HOLIDAY)
    table_data_with_title = tree.xpath("//td[@title]")

    h_dates = []
    for table_data in table_data_with_title:
        j = table_data.getparent().getparent()
        for k in j.getchildren()[0]:
            month_year = k.text
        if table_data.text:
            day = table_data.text
        else:
            for tag in table_data.getchildren():
                day = tag.text
        h_dates.append(
            datetime.strptime(' '.join([month_year, day]), '%B %Y %d'))
    return h_dates


def christmas(academic_dates):
    """Expand the Christmas holidays."""
    return list(expand_date_range(
        academic_dates['fall']['date'][1] + timedelta(days=1),
        academic_dates['winter']['date'][0] - timedelta(days=1)))


def spring_break():
    """Get start and end of the spring break."""
    spring_break_dates = []
    for index in xrange(0, 45+1, 15):
        tree = make_tree(BASE_ACADEMIC_URL, arg=index)
        paragraphs = tree.xpath("//p[@class='academicitem']")
        for paragraph in paragraphs:
            if u'Mid‑term break' in paragraph.text:
                for tag in paragraph.getprevious():
                    dates = datetime.strptime(tag.text, '%A, %B %d, %Y')
                    spring_break_dates.append(dates)
    return spring_break_dates


def range_date_format_parse(date_range):
    """Parse and format a given range of dates."""
    date_range = date_range.encode('ascii', 'ignore')

    match = re.match(r"([A-Za-z]+)\.?\s*([0-9]+)\s+"
                     r"([A-Za-z]+)\.?\s*([0-9]+)", date_range)
    groups = match.groups()

    if len(groups) != 4:
        raise Exception('Wrong dates format in re!')

    groups = [' '.join([i, j])
              for i, j in zip(groups[::2], groups[1::2])]

    groups = ['{month_day} {year}'.format(
        month_day=i, year=date.today().year) for i in groups]

    start_end = []
    for members in groups:
        members = parser.parse(members, fuzzy=True)

        start_end.append(adjust_year(members))
    return start_end


def school_start_end(academic_dates):
    """Return dates of start and end of each academic semesters."""
    tree = make_tree(TERM_DATES_URL)
    table_datas = tree.xpath("//td[@width='180' or @width='185']")
    index = 0
    for table_data in table_datas:
        k = table_data.getchildren()
        if k[0].text and 'term' not in k[0].text.lower():
            next_table_data = table_data.getnext()
            tags = next_table_data.getchildren()
            if tags:
                for tag in tags:
                    date_range = tag.text
            else:
                date_range = next_table_data.text

            start_end = range_date_format_parse(date_range)

            academic_dates[SEMESTER_NAMES[index]] = {'date': start_end}
            index += 1
    return academic_dates


def append_holidays(academic_dates, holidays):
    """Append all the holidays to the academic_dates dictionary."""
    for key, value in academic_dates.iteritems():
        academic_dates[key]['holidays'] = []
        for holiday_date in holidays:
            if value['date'][0] <= holiday_date <= value['date'][1]:
                academic_dates[key]['holidays'].append(holiday_date)
    return academic_dates


def act():
    """ACT  TODO  """
    academic_dates = {}
    holidays = get_general_holidays()
    spring_break_range = spring_break()
    spring_break_holidays = list(
        expand_date_range(spring_break_range[0], spring_break_range[1]))
    holidays = holidays + spring_break_holidays

    academic_dates = school_start_end(academic_dates)

    christmas_holidays = christmas(academic_dates)

    holidays = holidays + christmas_holidays

    academic_dates = append_holidays(academic_dates, holidays)

    return academic_dates


def get_academic_dates(semester):
    """Returns 2 datetime.date instances representing the start
    and ending days, of a specific academic semester
    Also returns the hollidays occuring during that semester."""
    academic_dates = None
    file_name = 'academic_dates.json'

    if path.exists(file_name):
        two_semesters_ago = datetime.now() - timedelta(days=240)
        filetime = datetime.fromtimestamp(path.getctime(file_name))

    if path.isfile(file_name) and filetime > two_semesters_ago:
        with open(file_name, 'rb') as fip:
            academic_dates = json.load(fip, object_hook=json_util.object_hook)
    else:
        academic_dates = act()
        with open(file_name, 'w') as fip:
            json.dump(academic_dates, fip, default=json_util.default)

    dates = academic_dates[semester]['date']
    dates = [old_date.date() for old_date in dates]
    holidays = academic_dates[semester]['holidays']
    holidays = [old_holiday.date() for old_holiday in holidays]
    return dates, holidays
