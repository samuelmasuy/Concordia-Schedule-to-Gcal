#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  This file is part of ScheduleToGoogleCal.
#
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file LICENSE included in the packaging of
#  this file.  Please review this information to ensure GNU
#  General Public Licensing requirements will be met.
#
#  This file is provided AS IS with NO WARRANTY OF ANY KIND, INCLUDING THE
#  WARRANTY OF DESIGN, MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#  For use of this library in commercial applications, please contact
#  samuel.masuy@gmail.com
#
#  ===========================================================================
# -*- coding: utf-8 -*-
"""
    Event Parser.
    ~~~~~~~~~~~~~

    Parses the data from a given Concordia schedule url.

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
import urllib2
import re
from bs4 import BeautifulSoup
from datetime import datetime, date, time
from dateutil import relativedelta as rdelta

from location import get_buildings_location


def get_data(url):
    """Return a list with row data from the html file."""
    soup = make_beautiful_html(url)
    data = []
    # Navigate the html table.
    rows = soup.findAll('tr')
    for tr in rows:
        cols = tr.findAll('td', attrs={'class': 'cusistabledata'})
        row = []
        for td in cols:
            row.append(td.find(text=True))
        if row != []:
            data.append(row)
    return data


def make_beautiful_html(url):
    """Open and read URL and turn it into a BeautifulSoup Object."""
    response = urllib2.urlopen(url).read().replace("&nbsp;", "")
    return BeautifulSoup(response, "html5lib")


def parse_data(data):
    """This function returns a version of the data that is parsed as needed"""
    BUILDINGS = get_buildings_location()
    new_data = []
    seen = {}
    for i, course in enumerate(data):
        row = []
        # we don't take into consideration online courses.
        if course[0][0] == '-':
            continue
        row.append(
            format_dates(course[0], re.findall(r"[\dd']+", course[1])))

        name_course = (course[2] + " " + course[3].split(" / ")[0])
        result, seen = same_course(name_course, seen, i + 1)

        row.append(result[1] + " " + course[6] + " " + course[5][:-1])
        row.append(course[4][:-1])
        row.append(course[7][:-1])
        row.append(result[0])
        row.append(BUILDINGS[course[5][:-1].split("-")[0]])
        new_data.append(row)
    new_data = recurent_event_factor(new_data)
    return new_data


def same_course(course, seen, index):
    """Allows to gather courses together"""
    if course in seen:
        result = [seen[course], course]
    else:
        seen[course] = index
        result = [index, course]
    return result, seen


def recurent_event_factor(seq):
    """Allows to gather course together if they are the same type i.e.
    lectures and tutorials."""
    seen_type = {}
    result = []
    for item in seq:
        marker = item[1]
        if marker in seen_type:
            to_add = item[0][0]
            for course in result:
                if course[1] == marker:
                    course[0][0] = ("%s,%s" % (course[0][0], to_add))
            continue
        seen_type[marker] = 1
        result.append(item)
    return result


def format_dates(day_of_the_week, hours):
    """Return an array with the dates formatted to iso format"""
    # generator to associate each day of the week to its relativedelta type
    # correspondant.
    days_of_week_gen = dict(
        zip('monday tuesday wednesday thursday friday'.split(),
            (getattr(rdelta, d) for d in 'MO TU WE TH FR'.split())))

    # get first day of the semester
    first_day_semester = date(2014, 1, 6)
    last_day_semester = date(2014, 4, 12)

    # get first day of the academic year a specific course is given.
    r = rdelta.relativedelta(weekday=days_of_week_gen[day_of_the_week.lower()])
    day = first_day_semester + r

    start_t = time(int(hours[0]), int(hours[1]))
    end_t = time(int(hours[2]), int(hours[3]))

    # get start_time and end_time by concatenating the previous result.
    start_datetime = datetime.isoformat(datetime.combine(day, start_t))
    end_datetime = datetime.isoformat(datetime.combine(day, end_t))
    return [str(days_of_week_gen[day_of_the_week.lower()]), start_datetime,
            end_datetime, last_day_semester.strftime("%Y%m%d")]


def to_dict(data):
    """This function takes all the data parsed and returns a dictionary
    with all formated data."""
    entries = []
    for e in data:
        entry = dict()
        entry["summary"] = e[1]
        # type of class, its section and the professor that gives it.
        entry["description"] = ("%s with professor: %s" % (e[2], e[3]))
        # To-do: need to get the exact location according to the classroom.
        entry["location"] = e[5]
        entry["colorId"] = e[4]

        start_dic = dict()
        entry["start"] = start_dic
        start_dic["dateTime"] = e[0][1]
        start_dic["timeZone"] = "America/Montreal"
        end_dic = dict()
        entry["end"] = end_dic
        end_dic["dateTime"] = e[0][2]
        end_dic["timeZone"] = "America/Montreal"

        entry["recurrence"] = ["RRULE:FREQ=WEEKLY;UNTIL=%s;BYDAY=%s" %
                               (e[0][3], e[0][0])]
        entries.append(entry)
    return entries


def get_events(url):
    """Entry point for the script."""
    data = parse_data(get_data(url))
    dics = to_dict(data)
    return dics
