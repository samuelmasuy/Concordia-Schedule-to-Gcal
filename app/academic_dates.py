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
    Academic_dates.
    ~~~~~~~~~~~~~~

    Start and end of an term from the 2014-2015 academic year.

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
from datetime import date


terms = ['summer_1', 'summer_2', 'fall', 'winter']


def get_academic_dates(year, semester):
    academic_dates = {
        u'2014': [date(2014, 5, 7),
                  date(2014, 6, 23),
                  date(2014, 7, 7),
                  date(2014, 8, 19),
                  date(2014, 9, 2),
                  date(2014, 12, 1),
                  date(2015, 1, 7),
                  date(2015, 4, 14)],
    }

    dates = academic_dates[year]
    academic_dates = dict(zip(terms, zip(*([iter(dates)] * 2))))
    return academic_dates[semester]

# May 7, 2014 (07,05,2014)
# June 23, 2014 (23,06,2014)
# July 3, 2014 (03,07,2014) Summer_1 Exam
# July 7, 2014 (07,07,2014)
# August 19, 2014 (19,08,2014)
# August 26, 2014 (26,08,2014) Summer_2 Exam
# September 2, 2014 (02,09,2014)
# December 1, 2014 (01,12,2014)
# December 18, 2014 (18,12,2014) Fall Exam
# January 7, 2015 (07,01,2015)
# February 23, 2015 (23,02,2015) Spring Break Start
# March 1, 2015 (01,03,2015) Spring Break End
# April 14, 2015 (14,04,2015)
