# -*- coding: utf-8 -*-
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
"""
    Scraper.
    ~~~~~~~~

    Parses the data from a given Concordia schedule url.

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
from lxml import html
import requests

from course import Course
from location import get_buildings_location


class ScheduleScraper():

    def __init__(self, url):
        self.response = requests.get(url).text
        self.buildings = get_buildings_location()

    def parse(self):
        """Return a list of all courses formatted from the html file."""
        tree = html.fromstring(self.response)
        paras = tree.xpath('//p[contains(@class, "cusisheaderdata")]')

        term = paras[0].text.lower().split(" ")[0]
        isSummer = False
        for p in paras:
            # Remove unnecessary data
            if 'summer' in term:
                p.getparent().remove(p.xpath('following-sibling::table[1]')[0])
                isSummer = True
            # Remove online course
            if len(p.text) > 15:
                p.getparent().remove(p.xpath('following-sibling::table[1]')[0])

        tables = tree.xpath("//table")
        courses = []
        for t in tables:
            td = t.xpath("td[contains(@class, 'cusistabledata')]")
            # Since it is not possible to find the tr elements using
            # lxml we find all the td elements and make a 2 dimensional
            # array representing the table.
            rows = [td[i:i + 8] for i in xrange(0, len(td), 8)]
            course_term = []
            seen = {}
            result = None
            # term = header[0].lower()
            for i, row in enumerate(rows):
                course = Course()
                # Course name ex: Comp 249
                course_name = (row[2].text + " " + row[3].text.split(" / ")[0])
                # Group same course together.
                result, seen = self.same_course(course_name, seen, i + 1)
                course.colorid = result[0]
                course.summary = result[1]
                course.datetime = row[0].text
                course.time = row[1].text
                course.section = row[4].text
                course.room = row[5].text
                course.campus = row[6].text
                course.professor = row[7].text
                if isSummer:
                    course.term = self.which_summer_term(
                        course.section.split(" ")[1][0])
                else:
                    course.term = term
                course.format_data(self.buildings)
                course_term.append(course)
            # Make sure to not to have 2 instance of the same course.
            course_term = self.recurent_event_factor(course_term)
            courses.append(course_term)
        return courses

    def which_summer_term(self, section_initial):
        map_section = (('4', 'A'), ('5', 'B'), ('6', 'C'), ('7', 'D'),
                      ('8', 'E'), ('9', 'F'))
        for i, j in map_section:
            if section_initial == i or section_initial == j:
                return "summer_" + i + j

    def same_course(self, course, seen, index):
        """Allows to gather courses together."""
        if course in seen:
            result = [seen[course], course]
        else:
            seen[course] = index
            result = [index, course]
        return result, seen

    def recurent_event_factor(self, seq):
        """Find the course that are the same type i.e.
        lectures and tutorials, and append the first occurence
        the day(s) of the next occurences."""
        seen_type = {}
        result = []
        for item in seq:
            marker = item.summary
            if marker in seen_type:
                to_add = item.datetime[0]
                for course in result:
                    if course.summary == marker:
                        course.datetime[0] = ("%s,%s"
                                              % (course.datetime[0], to_add))
                continue
            seen_type[marker] = 1
            result.append(item)
        return result

    def to_dict(self):
        """This function takes all the data parsed and returns a dictionary
        with all formated data needed to transmit to Google calendar."""
        courses = self.parse()
        entries = []
        for t in courses:
            for c in t:
                entry = dict()
                entry["summary"] = c.summary
                # type of class, its section and the professor that gives it.
                entry["description"] = ("%s with professor: %s" %
                                        (c.section, c.professor))
                entry["location"] = c.location
                entry["colorId"] = c.colorid
                # Date of the first course of the year and time when
                # the class begins.
                start_dic = dict()
                entry["start"] = start_dic
                start_dic["dateTime"] = c.datetime[1]
                start_dic["timeZone"] = "America/Montreal"
                # Date of the first course of the year and time when
                # the class ends.
                end_dic = dict()
                entry["end"] = end_dic
                end_dic["dateTime"] = c.datetime[2]
                end_dic["timeZone"] = "America/Montreal"
                # Repeat events weekly until the end of the academic year.
                entry["recurrence"] = ["RRULE:FREQ=WEEKLY;UNTIL=%s;BYDAY=%s" %
                                       (c.datetime[3], c.datetime[0])]
                entries.append(entry)
        return entries, c.term
