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
        self.datetime = None
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
        self.datetime = format_dates(self.semester,
                                     self.datetime,
                                     self.time)

        # Get physical location of where the course is given.
        building_full_name, self.location = set_location(self.room, buildings)
        # Make the title for an event; course + number + location.
        self.summary = ' '.join([self.summary, self.campus, self.room[:-1]])
        # Get type of course; Lecture, tutorial or labs.
        self.section = self.section[:-1]
        # Get the name of the professor who is teaching a certain course.
        self.professor = self.professor[:-1]
        # Join the professor, the section and the building name together
        #  to make up the description.
        self.description = '{} with professor: {} in {}'.format(
            self.section, self.professor, building_full_name)


def format_dates(semester, day_of_the_week, time_of_course):
    """Return a list of the dates formatted to iso format."""
    # Generator to associate each day of the week to its
    # relativedelta type correspondent.
    days_of_week_gen = dict(
        zip('monday tuesday wednesday thursday friday'.split(),
            (getattr(rdelta, d) for d in 'MO TU WE TH FR'.split())))

    # First day of the semester
    semester_dates, _ = get_academic_dates(semester)
    first_day_semester, last_day_semester = semester_dates
    last_day_semester = last_day_semester + timedelta(days=1)

    # Get first day of the academic year a specific course is given.
    relative_day_add = rdelta.relativedelta(
        weekday=days_of_week_gen[day_of_the_week.lower()])
    day = first_day_semester + relative_day_add

    hours = findall(r"[\dd']+", time_of_course)

    start_t = time(int(hours[0]), int(hours[1]))
    end_t = time(int(hours[2]), int(hours[3]))

    # Get start_time and end_time by concatenating the previous result.
    start_datetime = datetime.isoformat(datetime.combine(day, start_t))
    end_datetime = datetime.isoformat(datetime.combine(day, end_t))

    return [str(days_of_week_gen[day_of_the_week.lower()]), start_datetime,
            end_datetime, last_day_semester.strftime("%Y%m%d")]


def set_location(room, buildings):
    """Set the location where a certain course is taking place."""
    if room == '--':
        return ("Concordia University", "Concordia University - Sir George Williams Campus, Montreal, QC H3G 1M8, Canada")
    else:
        for building in buildings:
            if building['buildingcode'] == room[:-1].split("-")[0]:
                return (building['buildingname'], building['geocodeaddress'])
