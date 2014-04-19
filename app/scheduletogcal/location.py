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
    Location.
    ~~~~~~~~~

    Parses the address of every single building owned by Concordia University
    and associates the building's address with its abbreviation.
    ex: 'H' (Hall Building) : '1455 De Maisonneuve W. Montreal, QC'

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
import urllib2
from lxml import html


def make_tree(url):
    """Open and read URL and turn it into a lxml tree."""
    response = urllib2.urlopen(url).read()
    return html.fromstring(response)


def parse(url):
    campus_buildings = dict()
    tree = make_tree(url)
    # Find all the links that contain the mapping of the building
    # initial and its adress.
    links = tree.xpath('//a[contains(@class, "cc")]')

    for link in links:
        address = link.xpath("@data-content")[0] + ' Montreal, QC'
        campus_buildings[link.text] = address
    return campus_buildings


def get_buildings_location():
    """Returns a dictionary of all the buildings' address associated
    with their abbreviations."""
    SGW = "http://www.concordia.ca/maps/sgw-campus.html"
    LOY = "http://www.concordia.ca/maps/loyola-campus.html"

    # 'Add' one dictionary to the other.
    buildings_concordia = parse(SGW)
    buildings_concordia.update(parse(LOY))
    return buildings_concordia
