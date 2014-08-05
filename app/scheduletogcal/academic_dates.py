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

    Start and end of the 2014-2015 academic terms.
    Data manually fetched from:
    http://www.concordia.ca/students/registration/term-dates-deadlines.html
    TO-DO: Scrape the above website in order to get a dict just like the
    one below.

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
from datetime import date

_ACADEMIC_DATES = {
    "summer_4A": {
        "date": (date(2014, 5, 7), date(2014, 6, 23)),
        "withdraw": date(2014, 6, 4)
    },
    "summer_5B": {
        "date": (date(2014, 5, 7), date(2014, 8, 19)),
        "withdraw": date(2014, 7, 14)
    },
    "summer_6C": {
        "date": (date(2014, 7, 7), date(2014, 8, 19)),
        "withdraw": date(2014, 7, 31)
    },
    "summer_7D": {
        "date": (date(2014, 7, 7), date(2014, 7, 25)),
        "withdraw": date(2014, 7, 17)
    },
    "summer_8E": {
        "date": (date(2014, 7, 7), date(2014, 8, 15)),
        "withdraw": date(2014, 7, 30)
    },
    "summer_9F": {
        "date": (date(2014, 7, 28), date(2014, 8, 15)),
        "withdraw": date(2014, 8, 7)
    },
    "fall": {
        "date": (date(2014, 9, 2), date(2014, 12, 1)),
        "withdraw": date(2014, 10, 26)
    },
    "fall_winter": {
        "date": (date(2014, 9, 2), date(2015, 4, 14)),
        "withdraw": date(2015, 3, 8)
    },
    "winter": {
        "date": (date(2015, 1, 7), date(2015, 4, 14)),
        "withdraw": date(2015, 3, 8)
    }
}


def get_academic_dates(semester):
    """returns 2 datetime.date instances representing the start
    and ending days, of a specific academic semester."""
    return _ACADEMIC_DATES[semester]['date']
