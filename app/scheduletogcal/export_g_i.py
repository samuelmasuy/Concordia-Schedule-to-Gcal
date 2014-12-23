from pytz import timezone
from dateutil import parser

from icalendar import Calendar
from icalendar import Event


def to_gcal(course_list):
    """This function takes all the data parsed and returns a dictionary
    with all formated data needed to transmit to Google calendar."""
    gcal = []
    for courses in course_list:
        for course in courses:
            entry = dict()
            entry["summary"] = course.summary
            # Type of class, its section and the professor that gives it.
            entry["description"] = course.description
            entry["location"] = course.location
            entry["colorId"] = course.colorid
            # Date of the first course of the year and time when
            # the class begins.
            start_dic = dict()
            entry["start"] = start_dic
            start_dic["dateTime"] = course.datetime_start
            start_dic["timeZone"] = 'America/Montreal'
            # Date of the first course of the year and time when
            # the class ends.
            end_dic = dict()
            entry["end"] = end_dic
            end_dic["dateTime"] = course.datetime_end
            end_dic["timeZone"] = 'America/Montreal'
            # Repeat events weekly until the end of the academic year.
            entry["recurrence"] = [
                'RRULE:FREQ=WEEKLY;UNTIL={};BYDAY={}'.format(
                    course.datetime_until, course.datetime_day)]
            gcal.append(entry)
    return gcal


def to_ical(course_list):
    """This function takes all the data parsed and returns an
    icalendar."""
    ical = Calendar()
    current_tz = timezone("America/Montreal")
    for courses in course_list:
        for course in courses:
            bydays = course.datetime_day.split(',')
            for byday in bydays:
                entry_ical = Event()
                entry_ical.add('summary', course.summary)
                entry_ical.add('description', course.description)
                entry_ical.add('location', course.location)
                dtstart = parser.parse(
                    course.datetime_start).replace(tzinfo=current_tz)
                entry_ical.add('dtstart', dtstart)
                dtend = parser.parse(
                    course.datetime_end).replace(tzinfo=current_tz)
                entry_ical.add('dtend', dtend)
                until = parser.parse(
                    course.datetime_until).replace(tzinfo=current_tz)
                entry_ical.add('rrule', {'freq': 'weekly',
                                         'until': until,
                                         'byday': byday})
                ical.add_component(entry_ical)
    return ical
