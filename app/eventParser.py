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
from datetime import datetime, time
from dateutil import relativedelta as rdelta

from bs4 import BeautifulSoup

from location import get_buildings_location
from academic_dates import get_academic_dates


def make_beautiful_html(url):
    """Open and read URL and turn it into a BeautifulSoup Object."""
    response = urllib2.urlopen(url).read().replace("&nbsp;", "")
    return BeautifulSoup(response, "html5lib")


def strip_html(url):
    """Returns a beautiful soup Object
                TODO
    This function finds the semester which will be dealt with."""
    soup = make_beautiful_html(url)
    semester_names = []
    for i, q in enumerate(soup.find_all(attrs={'class': 'cusisheaderdata'})):
        s = q.text.split(" ")
        if len(s) > 3:
            q.findNext('table').extract()
            q.extract()
        if i == 1:
            year = s[2]
        term = s[0].lower()

        if 'summer' in term:
            q.findNext('table').extract()
            term = (term + "_" + str(i + 1))
            q.extract()
        semester_names.append(term)
    return semester_names, year, soup


def get_data(url):
    """Return a list of all courses formatted from the html file."""
    term, year, soup = strip_html(url)
    tables = soup.findAll('table')
    courses = []
    for i, table in enumerate(tables):
        data = []
        rows = table.findAll('tr')
        # Navigate the html table and get text needed.
        for tr in rows:
            cols = tr.findAll('td', attrs={'class': 'cusistabledata'})
            row = []
            for td in cols:
                row.append(td.find(text=True))
            if row != []:
                data.append(row)
        semester = term[i % 2]
        data = parse_data(year, semester, data)
        courses.append(data)
    return courses


def parse_data(year, semester, data):
    """This function returns a version of the data that is parsed as needed."""
    BUILDINGS = get_buildings_location()
    new_data = []
    seen = {}
    for i, course in enumerate(data):
        row = []
        # Append dates formatted with days of the week a course is given,
        # first and last day of semester for a specific course.
        row.append(format_dates(year,
                                semester,
                                course[0],
                                re.findall(r"[\dd']+", course[1])))
        # This is the course subject and the course number.
        name_course = (course[2] + " " + course[3].split(" / ")[0])
        # Group same course together.
        result, seen = same_course(name_course, seen, i + 1)
        # Make the title for an event; course + number + location.
        row.append(result[1] + " " + course[6] + " " + course[5][:-1])
        # Get type of course; Lecture, tutorial or labs.
        row.append(course[4][:-1])
        # Get the name of the professor who is teaching a certain course.
        row.append(course[7][:-1])
        # Attribute a integer to a course.
        row.append(result[0])
        # Get physical location of where the course is given
        if course[5] == '--':
            row.append(u"Concordia University, Montreal, QC")
        else:
            row.append(BUILDINGS[course[5][:-1].split("-")[0]])
        new_data.append(row)
    # Make sure to not to have same classes considered as similars.
    new_data = recurent_event_factor(new_data)
    return new_data


def same_course(course, seen, index):
    """Allows to gather courses together."""
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


def format_dates(year, semester, day_of_the_week, hours):
    """Return an array with the dates formatted to iso format."""
    # generator to associate each day of the week to its relativedelta type
    # correspondant.
    days_of_week_gen = dict(
        zip('monday tuesday wednesday thursday friday'.split(),
            (getattr(rdelta, d) for d in 'MO TU WE TH FR'.split())))

    # first day of the semester
    first_day_semester, last_day_semester = get_academic_dates(year, semester)

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
    with all formated data needed for transmitting to Google calendar."""
    entries = []
    for s in data:
        for e in s:
            entry = dict()
            entry["summary"] = e[1]
            # type of class, its section and the professor that gives it.
            entry["description"] = ("%s with professor: %s" % (e[2], e[3]))
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
    data = get_data(url)
    dics = to_dict(data)
    return dics
