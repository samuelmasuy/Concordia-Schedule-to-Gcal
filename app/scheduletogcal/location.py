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


def get_buildings_location():
    """Returns a dictionary of all the buildings' address associated
    with their abbreviations."""
    buildings_concordia = None
    file_name = 'app/scheduletogcal/location.json'

    with open(file_name, 'rb') as fip:
        buildings_concordia = json.load(fip)

    return buildings_concordia
