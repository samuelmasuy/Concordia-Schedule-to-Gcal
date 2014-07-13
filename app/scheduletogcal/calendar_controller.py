# -*- coding: utf-8 -*-
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
"""
    Calendar controller.
    ~~~~~~~~~~~~~~~~~~~

    Gestion of google calendar events and secondary calendars.

    :copyright: (c) 2014 by Samuel Masuy.
    :license: GNU version 2.0, see LICENSE for more details.
"""
import httplib2
import datetime

from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials
from apiclient.discovery import build
from flask import session, redirect, url_for

from app import app
from scraper import ScheduleScraper
from academic_dates import get_academic_dates


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
    created_calendar = service.calendars().insert(body=calendar).execute()
    return created_calendar['id']


def insert_event(url):
    """ Insert events in the user calendar. """
    service = create_service()
    created_events_id = []

    cs = ScheduleScraper(url)
    # Parse the schedule and get the events.
    events, term = cs.to_dict()

    # Check if a secondary calendar for the schedule exists.
    calendar_id = cal_lookup_id(service)

    if calendar_id is None:
        # Create a new secondary calendar.
        calendar_id = insert_calendar(service)

    else:
        # Delete all the events during the semester concerned.
        del_old_events(service, calendar_id, term)

    # Create all the events and get their ids.
    created_events_id = [service.events().insert(calendarId=calendar_id,
                                                 body=event).execute()['id']
                         for event in events]

    return calendar_id, created_events_id


def cal_lookup_id(service):
    """Finds the id, if existant, of the Schedule Concordia user calendar."""
    calendar_list = service.calendarList().list().execute()
    for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == 'Schedule Concordia':
            return calendar_list_entry['id']
    return None


def del_old_events(service, cal_id, term):
    """Delete all the events previously created, in the secondary calendar,
    in order to sustain an eventual update."""
    first_day, last_day = get_academic_dates(term)

    # Get datetime range of the first week of the semester.
    dt_min = datetime.datetime(first_day.year, first_day.month, first_day.day)
    dt_max = dt_min + datetime.timedelta(days=8)
    dt_min = dt_min.isoformat() + "-04:00"
    dt_max = dt_max.isoformat() + "-04:00"
    # Create a list of all the events we need to delete.
    old_events_list = service.events().list(calendarId=cal_id,
                                            timeMin=dt_min,
                                            timeMax=dt_max).execute()
    for old_event in old_events_list['items']:
        # Make sure we delete the events that were created only by
        # this application.
        if 'with professor' in old_event['description']:
            service.events().delete(calendarId=cal_id,
                                    eventId=old_event['id']).execute()


def rollback(created_events, calendar):
    """ Undo all changes that has been created in this application. """
    service = create_service()
    for event in created_events:
        service.events().delete(calendarId=calendar, eventId=event).execute()
