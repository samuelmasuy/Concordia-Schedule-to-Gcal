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
import httplib2

from oauth2client.client import (OAuth2WebServerFlow,
                                 OAuth2Credentials,
                                 AccessTokenRefreshError)
from apiclient.discovery import build
from flask import session, redirect, url_for

from app import app
from scraper import CalScraper


def get_flow(url):
    scope = "https://www.googleapis.com/auth/calendar"
    return OAuth2WebServerFlow(client_id=app.config['CLIENT_ID'],
                               client_secret=app.config['CLIENT_SECRET'],
                               scope=scope,
                               redirect_uri=(url + 'oauth2callback'))


def create_service():
    try:
        tokken = session['credentials']
    except KeyError:
        return redirect(url_for('schedule_login'))

    credentials = OAuth2Credentials.from_json(tokken)
    http = httplib2.Http()
    http = credentials.authorize(http)
    # Create service required to manipulate the user calendar.
    service = build("calendar", "v3", http=http)
    return service


def insert_calendar(service):
    """ Insert a secondary calendar in the user's calendar repository. """
    calendar = {
        'summary': 'Schedule Concordia',
        'timeZone': 'America/Montreal'
    }
    try:
        created_calendar = service.calendars().insert(body=calendar).execute()
        return created_calendar['id']
    except AccessTokenRefreshError:
        print("The credentials have been revoked or are expired")


def insert_event(url, new_cal):
    """ Insert events in the user calendar. """
    try:
        service = create_service()
        created_events = []
        cs = CalScraper(url)
        events = cs.to_dict()
        # Insert a secondary or insert the events in the user's main calendar.
        if new_cal == 'sec':
            calendar = cal_lookup(service)
            if calendar is None:
                session['new_cal'] = 'new_sec'
                calendar = insert_calendar(service)
        else:
            calendar = 'primary'
        for event in events:
            created_event = service.events().insert(
                calendarId=calendar, body=event).execute()
            created_events.append(created_event['id'])
        return calendar, created_events

    except AccessTokenRefreshError:
        print("The credentials have been revoked or are expired")


def cal_lookup(service):
    calendar_list = service.calendarList().list().execute()
    for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == 'Schedule Concordia':
            return calendar_list_entry['id']
    return None


def rollback(created_events, created_calendar, calendar):
    """ Undo all changes that has been created in this application. """
    service = create_service()
    for event in created_events:
        service.events().delete(calendarId=calendar, eventId=event).execute()
    if created_calendar == 'new_sec':
        service.calendars().delete(calendarId=calendar).execute()
