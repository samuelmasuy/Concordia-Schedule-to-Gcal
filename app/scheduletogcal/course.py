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
    Course.
    ~~~~~~~

    TO-DO.

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
import re
from datetime import datetime, time
from dateutil import relativedelta as rdelta

from academic_dates import get_academic_dates


class Course():

    def __init__(self):
        self.datetime = None
        self.time = None
        self.summary = None
        self.section = None
        self.room = None
        self.campus = None
        self.professor = None
        self.term = None
        self.colorid = 0
        self.location = None

    def format_data(self, buildings):
        """This basically format the data as needed."""
        # Append dates formatted with days of the week a course is given,
        # first and last day of semester for a specific course.
        self.datetime = self.format_dates(self.term,
                                          self.datetime,
                                          re.findall(r"[\dd']+", self.time))

        # Get physical location of where the course is given.
        self.location = self.set_location(self.room, buildings)
        # Make the title for an event; course + number + location.
        self.summary = self.summary + " " + self.campus + " " + self.room[:-1]
        # Get type of course; Lecture, tutorial or labs.
        self.section = self.section[:-1]
        # Get the name of the professor who is teaching a certain course.
        self.professor = self.professor[:-1]

    def format_dates(self, semester, day_of_the_week, hours):
        """Return a list of the dates formatted to iso format."""
        # Generator to associate each day of the week to its
        # relativedelta type correspondent.
        days_of_week_gen = dict(
            zip('monday tuesday wednesday thursday friday'.split(),
                (getattr(rdelta, d) for d in 'MO TU WE TH FR'.split())))

        # First day of the semester
        first_day_semester, last_day_semester = get_academic_dates(semester)

        # Get first day of the academic year a specific course is given.
        r = rdelta.relativedelta(
            weekday=days_of_week_gen[day_of_the_week.lower()])
        day = first_day_semester + r

        start_t = time(int(hours[0]), int(hours[1]))
        end_t = time(int(hours[2]), int(hours[3]))

        # Get start_time and end_time by concatenating the previous result.
        start_datetime = datetime.isoformat(datetime.combine(day, start_t))
        end_datetime = datetime.isoformat(datetime.combine(day, end_t))

        return [str(days_of_week_gen[day_of_the_week.lower()]), start_datetime,
                end_datetime, last_day_semester.strftime("%Y%m%d")]

    def set_location(self, room, buildings):
        """Set the location where a certain course is taking place."""
        if room == '--':
            return "Concordia University, Montreal, QC"
        else:
            building_initial = room[:-1].split("-")[0]
            return buildings[building_initial]
