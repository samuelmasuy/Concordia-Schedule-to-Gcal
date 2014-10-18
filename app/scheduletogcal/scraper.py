# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
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


class ScheduleScraper(object):
    """Parse courses from schedule website"""
    def __init__(self, url, semester):
        self.url = url
        self.buildings = get_buildings_location()
        self.index_color = 0
        self.semester = semester


    def parse(self):
        """Return a list of all courses formatted from the html file."""
        tree = make_tree(self.url)
        is_summer = (self.semester == 'summer')
        tree = clean_html(tree, is_summer)

        tables = tree.xpath('//table')
        courses = []
        for t in tables:
            td = t.xpath("td[contains(@class, 'cusistabledata')]")
            # Since it is not possible to find the tr elements using
            # lxml we find all the td elements and make a 2 dimensional
            # array representing the table.
            rows = [td[i:i + 8] for i in xrange(0, len(td), 8)]

            course_term = []
            seen_course = {}
            result = None
            for row in rows:
                course = Course()
                # Course name ex: Comp 249
                course_name = parse_course_name(row[2].text, row[3].text)
                # Group same course together.
                result, seen_course = self.same_course(course_name, seen_course)
                course.colorid = result[0]
                course.summary = result[1]

                course.datetime = row[0].text
                course.time = row[1].text
                course.room = row[5].text
                course.campus = row[6].text
                course.professor = row[7].text

                course.section = row[4].text
                course.semester = self.semester
                # Append the summer section.
                if is_summer:
                    course.semester += get_summer_section(
                        course.section.split(' ')[1][0])
                # Append the buildings address of a specific course and format
                # the data.
                course.format_data(self.buildings)
                course_term.append(course)
            # Make sure to not to have 2 instances of the same course.
            course_term = recurent_event_factor(course_term)
            courses.append(course_term)
        return courses

    def same_course(self, course, seen):
        """Gather course of the same type together."""
        if course in seen:
            result = [seen[course], course]
        else:
            self.index_color += 1
            seen[course] = self.index_color
            result = [self.index_color, course]
        return result, seen

    def to_dict(self):
        """This function takes all the data parsed and returns a dictionary
        with all formated data needed to transmit to Google calendar."""
        course_list = self.parse()
        entries = []
        for courses in course_list:
            for course in courses:
                entry = dict()
                entry["summary"] = course.summary
                # Type of class, its section and the professor that gives it.
                entry["description"] = course.description
                entry["location"] = course.location
                entry["colorId"] = course.colorid
                # Date of the first course of the year and time when
                # the class begins.
                start_dic = dict()
                entry["start"] = start_dic
                start_dic["dateTime"] = course.datetime[1]
                start_dic["timeZone"] = 'America/Montreal'
                # Date of the first course of the year and time when
                # the class ends.
                end_dic = dict()
                entry["end"] = end_dic
                end_dic["dateTime"] = course.datetime[2]
                end_dic["timeZone"] = 'America/Montreal'
                # Repeat events weekly until the end of the academic year.
                entry["recurrence"] = [
                    'RRULE:FREQ=WEEKLY;UNTIL={};BYDAY={}'.format(
                        course.datetime[3], course.datetime[0])]
                entries.append(entry)
        return entries


def make_tree(url):
    """Create a lxml tree from a url """
    response = requests.get(url, verify=False).text
    tree = html.fromstring(response)
    return tree


def clean_html(tree, is_summer):
    """ Remove online courses, extra data in summer schedules and
    coop terms """
    p_tags = tree.xpath('//p[contains(@class, "cusisheaderdata")]')
    for p in p_tags:
        # Remove unnecessary data
        if is_summer:
            p.getparent().remove(p.xpath('following-sibling::table[1]')[0])
        # Remove online course and coop terms
        if len(p.text) > 15:
            p.getparent().remove(p.xpath('following-sibling::table[1]')[0])
    return tree


def parse_course_name(name, number):
    """ Comp 249 /2 => Comp 249 """
    return ' '.join([name, number.split(' / ')[0]])


def get_summer_section(section_initial):
    """Specifies the summer semester according to its initial"""
    map_section = (('4', 'A'),
                   ('5', 'B'),
                   ('6', 'C'),
                   ('7', 'D'),
                   ('8', 'E'),
                   ('9', 'F'))

    for i, j in map_section:
        if section_initial == i or section_initial == j:
            return '{}{}'.format(i, j)


def recurent_event_factor(seq):
    """Find the course that are the same type i.e. lectures and tutorials,
    and append the first occurence the day(s) of the next occurences."""
    # values = set(map(lambda x: x.summary, seq))
    values = set([(x.summary, x.section) for x in seq])
    newlist = [[y for y in seq if y.summary == x and y.section == z]
               for x, z in values]
    result = []
    for course in newlist:
        first_course = min(course, key=lambda arr: arr.datetime[1])
        first_date = first_course.datetime[0]
        course.remove(first_course)
        for i in course:
            first_course.datetime[0] = ','.join([first_date, i.datetime[0]])
        result.append(first_course)
    return result
