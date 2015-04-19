# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================
"""
    Course.
    ~~~~~~~

    Represents a course, its characteristics are also being modified,
    such as the dates, and location.

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
from re import findall
from datetime import datetime, time, timedelta
from dateutil import relativedelta as rdelta

from academic_dates import get_academic_dates


class Course(object):
    """Define an university class"""
    def __init__(self):
        self.datetime_start = None
        self.datetime_end = None
        self.datetime_until = None
        self.datetime_day = None
        self.time = None
        self.summary = None
        self.section = None
        self.room = None
        self.campus = None
        self.professor = None
        self.description = None
        self.semester = None
        self.colorid = 0
        self.location = None

    def format_data(self, buildings):
        """Formats the data as needed."""
        # Append dates formatted with days of the week a course is given,
        # first and last day of semester for a specific course.
        self.datetime_day = day_abbr(self.datetime_day)
        first_day_semester, self.datetime_until = first_last_day_semester(
            self.semester, self.datetime_day)
        self.datetime_start, self.datetime_end = first_day_datetime(
            first_day_semester, self.time)
        self.datetime_day = str(self.datetime_day)

        # Get physical location of where the course is given.
        self.room = self.room[:-1]
        building_full_name, self.location = set_location(self.room, buildings)
        # Make the title for an event; course + number + location.
        self.summary = ' '.join([format_course_name(self.summary),
                                 self.campus,
                                 self.room])
        # Get type of course; Lecture, tutorial or labs.
        self.section = self.section[:-1]
        # Get the name of the professor who is teaching a certain course.
        self.professor = self.professor[:-1]
        # Join the professor, the section and the building name together
        #  to make up the description.
        self.description = '{} with professor: {} in {}'.format(
            self.section, self.professor, building_full_name)


def format_course_name(course_name):
    """ COMP 249 / 2 => COMP 249 """
    return course_name.split(' / ')[0]


def day_abbr(day):
    """Generator to associate a day of the week to its
    relativedelta type correspondent.
    Returns a dateutil.relativedelta.weekday object."""
    day_to_abbr = dict(
        zip('Monday Tuesday Wednesday Thursday Friday'.split(),
            (getattr(rdelta, d) for d in 'MO TU WE TH FR'.split())))
    return day_to_abbr[day]


def first_last_day_semester(semester, day_of_the_week):
    """Get first and last day of a specific course during a semester.
    Returns a tuple with the fist day as a datetime.date objects and
    the last day as a string of the form YYYYmmdd."""
    # First day of the semester
    semester_dates = get_academic_dates(semester)
    first_day_semester, last_day_semester = semester_dates
    last_day_semester = last_day_semester + timedelta(days=1)

    # Get first day of the academic year a specific course is given.
    relative_day_add = rdelta.relativedelta(
        weekday=day_of_the_week)
    day = first_day_semester + relative_day_add
    return (day, last_day_semester.strftime("%Y%m%d"))


def first_day_datetime(first_day_date, time_of_course):
    """Get the date and time of the first course of the semester
    for a specific course.
    Returns a tuple of 2 isoformat datetime strings."""
    hours = findall(r"[\dd']+", time_of_course)

    start_t = time(int(hours[0]), int(hours[1]))
    end_t = time(int(hours[2]), int(hours[3]))

    # Get start_time and end_time by concatenating the previous result.
    start_datetime = datetime.isoformat(
        datetime.combine(first_day_date, start_t))
    end_datetime = datetime.isoformat(
        datetime.combine(first_day_date, end_t))
    return (start_datetime, end_datetime)


def set_location(room, buildings):
    """Set the location where a certain course is taking place."""
    room = get_room_name(room)
    for building in buildings:
        if building['buildingcode'] == room:
            building_name = building['buildingname']
            address = building['geocodeaddress']
            break
    else:
        building_name = 'Concordia University'
        address = ('Concordia University - Sir George Williams Campus,'
                   ' Montreal, QC H3G 1M8, Canada')
    return (building_name, address)


def get_room_name(room):
    """ Get room name. """
    return room.split("-")[0]
