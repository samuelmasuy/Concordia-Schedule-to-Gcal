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
    Test.
    ~~~~~

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
from os import listdir
from os.path import isfile, join
from pprint import pprint

from bs4 import BeautifulSoup

from app import eventParser


def make_beatiful_soup(url):
    """Open and read html files and turn it into a BeautifulSoup Object."""
    with open(url, "r") as f:
        response = f.read()
        return BeautifulSoup(response, "html5lib")

path = join("app", "html_schedules_debug")
testurls = [join(path, f) for f in listdir(path) if isfile(join(path, f))]

for i, url in enumerate(testurls):
    pre_soup = make_beatiful_soup(url)
    events = eventParser.get_events(pre_soup)
    print "%s\n\n\t\t test %d \non %s\n" % (79 * '_', i + 1, url)
    pprint(events)
