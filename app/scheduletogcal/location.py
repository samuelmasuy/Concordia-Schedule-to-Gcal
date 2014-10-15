# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================
"""
    Location.
    ~~~~~~~~~

    Parses the address of every single building owned by Concordia University
    and associates the building's address with its abbreviation.
    ex: 'H' (Hall Building) : '1455 De Maisonneuve W. Montreal, QC'

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
import json
from datetime import datetime, timedelta
from os import path

import requests
from lxml import html

def make_tree(url):
    """Open and read URL and turn it into a lxml tree."""
    response = requests.get(url).text
    return html.fromstring(response)


def parse(url):
    """Parse addresses of the university"""
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
    buildings_concordia = None
    SGW = 'http://www.concordia.ca/maps/sgw-campus.html'
    LOY = 'http://www.concordia.ca/maps/loyola-campus.html'
    file_name = 'app/scheduletogcal/location.json'

    if path.exists(file_name):
        two_months_ago = datetime.now() - timedelta(days=60)
        filetime = datetime.fromtimestamp(path.getctime(file_name))

    if path.isfile(file_name) and filetime > two_months_ago:
        with open(file_name, 'rb') as fip:
            buildings_concordia = json.load(fip)
    else:
        print path.dirname(path.abspath(__file__))
        # 'Add' one dictionary to the other.
        buildings_concordia = parse(SGW)
        buildings_concordia.update(parse(LOY))
        with open(file_name, 'w') as fip:
            json.dump(buildings_concordia, fip)
    return buildings_concordia
