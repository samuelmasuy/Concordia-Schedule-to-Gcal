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
# import pytz

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
    # session['new_cal'] = 'no_new_sec'
    service = create_service()
    created_events_id = []
    cs = ScheduleScraper(url)
    events, term = cs.to_dict()
    # events = [{'colorId': 1,
    #            'description': 'Lec U  with professor: TALEB, MOHAMED',
    #            'end': {'dateTime': '2014-09-08T10:00:00', 'timeZone': 'America/Montreal'},
    #            'location': '1455 De Maisonneuve W. Montreal, QC',
    #            'recurrence': ['RRULE:FREQ=WEEKLY;UNTIL=20141201;BYDAY=MO,WE'],
    #            'start': {'dateTime': '2014-09-08T08:45:00', 'timeZone': 'America/Montreal'},
    #            'summary': 'COMP 348 SGW H-411'}]
    # Insert a secondary or insert the events in the user's main calendar.
    calendar_id = cal_lookup_id(service)
    if calendar_id is None:
        # session['new_cal'] = 'new_sec'
        calendar_id = insert_calendar(service)

    del_old_events(service, calendar_id, term)

    for event in events:
        # dt_min = dateutil.parser.parse(event["start"]["dateTime"]).isoformat()
        # dt_max = dateutil.parser.parse(event["end"]["dateTime"]).isoformat()
        # dt_min = dt_min.replace(tzinfo=pytz.timezone(time_zone)).isoformat()
        # dt_max = dt_max.replace(tzinfo=pytz.timezone(time_zone)).isoformat()
        # dt_min = dt_min + "-04:00"
        # dt_max = dt_max + "-04:00"
        # existing_event = event_lookup(service, calendar_id, dt_min, dt_max)
        # print event_id
        # created_event = None
        # if existing_event is None:
        created_event = service.events().insert(calendarId=calendar_id,
                                                body=event).execute()
        # else:
            # event_id = existing_event['items'][0]['id']
            # new_event = service.events().get(calendarId=calendar_id,
            #                                  eventId=event_id).execute()

            # event_description = existing_event['items'][0]['description']
            # if event['summary'] != new_event['summary']:
            #     new_event['summary'] = event['summary']
            #     created_event = service.events().update(calendarId=calendar_id,
            #                                             eventId=event_id,
            #                                             body=new_event
            #                                             ).execute()
            # elif event['description'] != event_description:
            #     created_event = service.events().update(calendarId=calendar_id,
            #                                             eventId=event_id,
            #                                             body=event,
            #                                             description=event[
            #                                                 'description']
            #                                             ).execute()
        # if created_event is not None:
        created_events_id.append(created_event['id'])
        # else:
        #     created_events_id.append(created_event)
    return calendar_id, created_events_id


def cal_lookup_id(service):
    """Finds the id, if existant, of the Schedule Concordia user calendar."""
    calendar_list = service.calendarList().list().execute()
    for calendar_list_entry in calendar_list['items']:
        if calendar_list_entry['summary'] == 'Schedule Concordia':
            return calendar_list_entry['id']
    return None


# def event_lookup(service, cal_id, dt_min, dt_max):
#     """Finds same events id, if existant, in the calendar, in order to
#     sustain an eventual update."""
#     event = service.events().list(calendarId=cal_id,
#                                   timeMin=dt_min,
#                                   timeMax=dt_max).execute()
#     if len(event["items"]) == 0:
#         return None
#     else:
#         return event


def del_old_events(service, cal_id, term):
    """Finds same events id, if existant, in the calendar, in order to
    sustain an eventual update."""
    first_day, last_day = get_academic_dates(term)
    dt_min = datetime.datetime(first_day.year, first_day.month, first_day.day)
    dt_max = dt_min + datetime.timedelta(days=8)
    dt_min = dt_min.isoformat() + "-04:00"
    dt_max = dt_max.isoformat() + "-04:00"
    old_events_list = service.events().list(calendarId=cal_id,
                                            timeMin=dt_min,
                                            timeMax=dt_max).execute()
    for old_event in old_events_list['items']:
        if 'with professor' in old_event['description']:
            service.events().delete(calendarId=cal_id,
                                    eventId=old_event['id']).execute()


def rollback(created_events, calendar):
    """ Undo all changes that has been created in this application. """
    service = create_service()
    for event in created_events:
        service.events().delete(calendarId=calendar, eventId=event).execute()
    # if created_calendar == 'new_sec':
    #     service.calendars().delete(calendarId=calendar).execute()
