# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
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
from datetime import datetime, timedelta, time
from pytz import timezone

from oauth2client.client import OAuth2WebServerFlow, OAuth2Credentials
from apiclient.discovery import build
from flask import session, redirect, url_for

from app import app
from scraper import ScheduleScraper
from academic_dates import get_academic_dates

TIMEZONE = timezone("America/Montreal")


def get_flow(url):
    scope = "https://www.googleapis.com/auth/calendar"
    return OAuth2WebServerFlow(client_id=app.config['CLIENT_ID'],
                               client_secret=app.config['CLIENT_SECRET'],
                               scope=scope,
                               redirect_uri=(url + 'oauth2callback'))


def create_service():
    """Create a service to communicate with the Google API."""
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

    calendar_schedule = ScheduleScraper(url)
    # Parse the schedule and get the events.
    events, term = calendar_schedule.to_dict()

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

    del_holliday(service, calendar_id, created_events_id, term)

    return calendar_id, created_events_id


def del_holliday(service, cal_id, created_events_ids, term):
    """Delete all the instances of the days when there is a holiday"""
    _, holiday_list = get_academic_dates(term)

    for holiday in holiday_list:
        start_datetime = datetime.isoformat(
            datetime.combine(holiday, time.min.replace(tzinfo=TIMEZONE)))
        end_datetime = datetime.isoformat(
            datetime.combine(holiday, time.max.replace(tzinfo=TIMEZONE)))

        old_recur_events = []
        for old_event_id in created_events_ids:
            old_recur_events.append(
                service.events().instances(calendarId=cal_id,
                                           eventId=old_event_id,
                                           timeMin=start_datetime,
                                           timeMax=end_datetime).execute())

    for summ in old_recur_events:
        for ite in summ['items']:
            service.events().delete(calendarId=cal_id,
                                    eventId=ite['id']).execute()


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
    semester_dates, _ = get_academic_dates(term)
    first_day, last_day = semester_dates
    last_day = last_day + timedelta(days=1)

    # Get datetime range of the first week of the semester.
    dt_min = datetime(first_day.year, first_day.month, first_day.day,
                      tzinfo=TIMEZONE)
    dt_max = datetime(last_day.year, last_day.month, last_day.day,
                      tzinfo=TIMEZONE)

    # Create a list of all the events we need to delete.
    old_events_list = service.events().list(
        calendarId=cal_id,
        timeMin=dt_min.isoformat(),
        timeMax=dt_max.isoformat()).execute()

    old_recur_events = []
    for old_event_id in old_events_list:
        old_recur_events.append(
            service.events().instances(calendarId=cal_id,
                                       eventId=old_event_id,
                                       timeMin=dt_min.isoformat(),
                                       timeMax=dt_max.isoformat()).execute())

    for summ in old_recur_events:
        for ite in summ['items']:
            service.events().delete(calendarId=cal_id,
                                    eventId=ite['id']).execute()


def rollback(created_events, calendar):
    """ Undo all changes that has been created in this application. """
    service = create_service()
    for event in created_events:
        service.events().delete(calendarId=calendar, eventId=event).execute()
