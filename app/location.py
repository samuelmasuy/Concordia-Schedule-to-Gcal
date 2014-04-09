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

from bs4 import BeautifulSoup


sgw = "http://www.concordia.ca/maps/sgw-campus.html"
loy = "http://www.concordia.ca/maps/loyola-campus.html"


def make_beautiful_soup(url):
    """Open and read URL and turn it into a BeautifulSoup Object."""
    response = urllib2.urlopen(url).read()
    return BeautifulSoup(response, "html5lib")


def get_buildings_location():
    """Returns a dictionary of all the buildings' address associated
    with their abbreviations."""
    # Make BeautifulSoup object out of the 2 campus urls.
    soup_sgw = make_beautiful_soup(sgw)
    soup_loy = make_beautiful_soup(loy)

    # Find all the data that matter for us.
    links_sgw = soup_sgw.find_all(attrs={'class': 'acc'})
    links_loy = soup_loy.find_all(attrs={'class': 'acc'})

    # Get data for SGW Campus.
    build_sgw = dict()
    for link in links_sgw:
        build_sgw[link.text] = (link['data-content'] + ' Montreal, QC')
    # Get data for Loyola Campus.
    build_loy = dict()
    for link in links_loy:
        build_loy[link.text] = (link['data-content'] + ' Montreal, QC')

    # 'Add' one dictionary to the other.
    buildings_concordia = dict(build_sgw)
    buildings_concordia.update(build_loy)

    return buildings_concordia
