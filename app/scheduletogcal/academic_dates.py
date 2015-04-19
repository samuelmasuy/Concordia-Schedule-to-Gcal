import re
import json
from datetime import datetime, timedelta
from os import path
import string

import requests
from lxml import html
from dateutil import parser
from bson import json_util

TERM_DATES_URL = ('http://www.concordia.ca/students/'
                  'registration/term-dates-deadlines.html')
SEMESTER_NAMES = ['summer_4A', 'summer_5B', 'summer_6C', 'summer_7D',
                  'summer_8E', 'summer_9F', 'fall', 'fall_winter', 'winter']


def make_tree(url, arg=''):
    """Create a lxml tree from a url with possibly some arguments."""
    response = requests.get('{0}{1}'.format(url, arg)).text
    return html.fromstring(response)


def remove_non_ascii(text):
        return filter(lambda x: x in string.printable, text)


def range_date_format_parse(date_range, years=('2015', '2016')):
    """Parse and format a given range of dates."""


    match = re.match(r"([A-Za-z]+)\.?\s*([0-9]+)\s*"
                     r"([A-Za-z]+)\.?\s*([0-9]+)", date_range)
    groups = match.groups()

    if len(groups) != 4:
        raise Exception('Wrong dates format in re!')

    groups = [' '.join([i, j])
              for i, j in zip(groups[::2], groups[1::2])]

    groups = ['{month_day} {year}'.format(
        month_day=i, year=9999) for i in groups]
    start_end = []
    for members in groups:
        members = parser.parse(members, fuzzy=True)
        if members.month < 5:
            members = members.replace(year=int(years[1]))
        else:
            members = members.replace(year=int(years[0]))
        start_end.append(members)
    return start_end


def school_start_end():
    """Return dates of start and end of each academic semesters."""
    tree = make_tree(TERM_DATES_URL)

    academic_dates = {}

    title_year = tree.xpath("//h1")[0].text
    match = re.match(r".*(\d\d)(\d\d)-(\d\d)", title_year)
    groups = match.groups()
    years = (groups[0] + groups[1], groups[0] + groups[2])

    summer_link, fall_winter_link = tree.xpath("//div[@class='parbase table section']")[:2]
    summer_tbody = summer_link.xpath('.//tbody')[0]
    fall_winter_tbody = fall_winter_link.xpath('.//tbody')[0]

    trs = summer_tbody.getchildren()

    trs = trs + fall_winter_tbody.getchildren()

    index = 0
    for tr in trs:
        children_tr = tr.getchildren()
        if len(children_tr) == 6 or len(children_tr) == 7:
            date_td = children_tr[1]
            tags = date_td.getchildren()
            if tags:
                for tag in tags:
                    date_range = tag.text
            else:
                date_range = date_td.text
            date_range = remove_non_ascii(date_range)
            start_end = range_date_format_parse(date_range, years)

            academic_dates[SEMESTER_NAMES[index]] = {'date': start_end}
            index += 1

    return academic_dates


def get_academic_dates(semester):
    """Returns 2 datetime.date instances representing the start
    and ending days, of a specific academic semester.
    Writes to a json file if file is older then 2 semesters.
    Also returns the hollidays occuring during that semester."""
    academic_dates = None
    file_name = 'academic_dates.json'

    if path.exists(file_name):
        two_semesters_ago = datetime.now() - timedelta(days=20)
        filetime = datetime.fromtimestamp(path.getctime(file_name))

    if path.isfile(file_name) and filetime > two_semesters_ago:
        with open(file_name, 'rb') as fip:
            academic_dates = json.load(fip, object_hook=json_util.object_hook)
    else:
        academic_dates = school_start_end()
        with open(file_name, 'w') as fip:
            json.dump(academic_dates, fip, default=json_util.default)

    dates = academic_dates[semester]['date']
    return dates
