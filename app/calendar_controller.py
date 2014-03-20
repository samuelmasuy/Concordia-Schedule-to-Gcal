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
    Calendar controller.
    ~~~~~~~~~~~~~~~~~~~

    Gestion of google calendar events and secondary calendars.

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
from oauth2client.client import OAuth2WebServerFlow
from oauth2client import client

from app import app
import eventParser


def get_flow(url):
    return OAuth2WebServerFlow(client_id=app.config['CLIENT_ID'],
                               client_secret=app.config['CLIENT_SECRET'],
                               scope="https://www.googleapis.com/auth/calendar",
                               redirect_uri=(url + 'oauth2callback'))


def insert_calendar(service):
    """ Insert a secondary calendar in the user's calendar repository. """
    calendar = {
        'summary': 'Schedule Concordia',
        'timeZone': 'America/Montreal'
    }
    try:
        created_calendar = service.calendars().insert(body=calendar).execute()
        return created_calendar['id']
    except client.AccessTokenRefreshError:
        print("The credentials have been revoked or are expired")


def insert_event(service, url, calendar='primary'):
    """ Insert events in the user calendar. """
    try:
        created_events = []
        events = eventParser.get_events(url)
        for event in events:
            created_event = service.events().insert(
                calendarId=calendar, body=event).execute()
            created_events.append(created_event['id'])
        return created_events

    except client.AccessTokenRefreshError:
        print("The credentials have been revoked or are expired")


def rollback(service, created_events, calendar):
    """ Undo all changes that has been created in this application. """
    for event in created_events:
        service.events().delete(calendarId=calendar, eventId=event).execute()
    if calendar != 'primary':
        service.calendars().delete(calendarId=calendar).execute()
