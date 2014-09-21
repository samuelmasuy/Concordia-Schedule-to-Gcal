
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

    Holidays
    Data fetched from:
    - http://www.concordia.ca/events/university-holidays.html

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
from datetime import datetime

import requests
from lxml import html

URL_HOLIDAY = 'http://www.concordia.ca/events/university-holidays.html'


def make_tree(url, arg=''):
    """Create a lxml tree from a url with possibly some arguments."""
    response = requests.get('{0}{1}'.format(url, arg)).text
    return html.fromstring(response)


def get_general_holidays():
    """Get all the dates of when the university is closed."""
    tree = make_tree(URL_HOLIDAY)
    table_data_with_title = tree.xpath("//td[@title]")

    h_dates = []
    for table_data in table_data_with_title:
        j = table_data.getparent().getparent()
        for k in j.getchildren()[0]:
            month_year = k.text
        if table_data.text:
            day = table_data.text
        else:
            for tag in table_data.getchildren():
                day = tag.text
        h_dates.append(
            datetime.strptime(' '.join([month_year, day]), '%B %Y %d'))
    return h_dates
