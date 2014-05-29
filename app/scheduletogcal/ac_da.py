from datetime import datetime
import requests
from lxml import html


def make_tree(url):
    """Open and read URL and turn it into a lxml tree."""
    response = requests.get(url).text
    return html.fromstring(response)


def make_url_list(base_url):
    """Make a list of the url pages where the academic events are."""
    urls = []
    # there are 15 events per page
    for i in range(0, 100, 15):
        url = base_url + str(i)
        urls.append(url)
    return urls


def parse(base_url = "http://portico.concordia.ca/cq/daily-events/ac_search.php?start="):
    events = {}
    closed = []
    default_event = {'summer_1': [], 'summer_2': [],
                     'fall': [], 'winter': []}
    urls = make_url_list(base_url)
    for i in urls:
        tree = make_tree(i)
        paras = tree.xpath('//p[contains(@class, "academicitem")]')
        for p in paras:
            p_text = p.text.lower()
            # Find the date of the event
            d_raw = p.xpath('preceding-sibling::h4[1]/strong')[0].text
            # Convert the date to a datetime.date object
            dt = datetime.strptime(d_raw, "%A, %B %d, %Y").date()
            d_year = str(dt.year)
            # create a list of the date the university is close (hollidays.)
            if "university closed" in p_text:
                closed.append(dt)
            # Create a dict in case the year is not a key of the events
            if d_year not in events:
                events.update({d_year: default_event})
            semester = None
            if dt.month <= 4:
                semester = 'winter'
            elif (dt.month >= 5 and dt.month <= 6):
                semester = 'summer_1'
            elif (dt.month >= 7 and dt.month <= 8):
                semester = 'summer_2'
            elif dt.month >= 9:
                semester = 'fall'

            if "last day of classes" in p_text or "classes begin" in p_text:
                if u'three‑week' not in p_text:
                    events[d_year][semester].append(dt)
    return events, closed

def parse2(url="http://www.concordia.ca/students/registration/term-dates-deadlines.html"):
    tree = make_tree(url)
    return tree


def get_academic_dates(year, semester):
    """returns 2 datetime.date instances representing the start
    and ending days, of a specific academic semester."""
    base = "http://portico.concordia.ca/cq/daily-events/ac_search.php?start="
    academic_dates, closed = parse(base)
    return academic_dates[year][semester][0], academic_dates[year][semester][1]

ev = {
    "summer_4A": {
        "date": [datetime.date(2014, 5, 7), datetime.date(2014, 6, 23)],
        "withdraw": datetime.date(2014, 6, 4)
    },
    "summer_5B": {
        "date": [datetime.date(2014, 5, 7), datetime.date(2014, 8, 19)],
        "withdraw": datetime.date(2014, 7, 14)
    },
    "summer_6C": {
        "date": [datetime.date(2014, 7, 7), datetime.date(2014, 8, 19)],
        "withdraw": datetime.date(2014, 7, 31)
    },
    "summer_7D": {
        "date": [datetime.date(2014, 7, 7), datetime.date(2014, 7, 25)],
        "withdraw": datetime.date(2014, 7, 17)
    },
    "summer_8E": {
        "date": [datetime.date(2014, 7, 7), datetime.date(2014, 8, 15)],
        "withdraw": datetime.date(2014, 7, 30)
    },
    "summer_9F": {
        "date": [datetime.date(2014, 7, 28), datetime.date(2014, 8, 15)],
        "withdraw": datetime.date(2014, 8, 7)
    },
    "fall": {
        "date": [datetime.date(2014, 9, 2), datetime.date(2014, 12, 1)],
        "withdraw": datetime.date(2014, 10, 26)
    },
    "fall_winter": {
        "date": [datetime.date(2014, 9, 2), datetime.date(2015, 4, 14)],
        "withdraw": datetime.date(2015, 3, 8)
    },
    "winter": {
        "date": [datetime.date(2015, 1, 7), datetime.date(2015, 4, 14)],
        "withdraw": datetime.date(2015, 3, 8)
    }
}

# for i in an:
#     try:
#         dt = datetime.strptime(i, "%b %d %Y").date()
#     except ValueError:
#         dt = datetime.strptime(i, "%B %d %Y").date()
#     dat.append(dt)
# [datetime.date(2014, 5, 7),
#  datetime.date(2014, 6, 23),
#  datetime.date(2014, 6, 4),
#  datetime.date(2014, 5, 7),
#  datetime.date(2014, 8, 19),
#  datetime.date(2014, 7, 14),
#  datetime.date(2014, 7, 7),
#  datetime.date(2014, 8, 19),
#  datetime.date(2014, 7, 31),
#  datetime.date(2014, 7, 7),
#  datetime.date(2014, 7, 25),
#  datetime.date(2014, 7, 17),
#  datetime.date(2014, 7, 7),
#  datetime.date(2014, 8, 15),
#  datetime.date(2014, 7, 30),
#  datetime.date(2014, 7, 28),
#  datetime.date(2014, 8, 15),
#  datetime.date(2014, 8, 7),
#  datetime.date(2014, 9, 2),
#  datetime.date(2014, 12, 1),
#  datetime.date(2014, 10, 26),
#  datetime.date(2014, 9, 2),
#  datetime.date(2015, 4, 14),
#  datetime.date(2015, 3, 8),
#  datetime.date(2015, 1, 7),
#  datetime.date(2015, 4, 14),
#  datetime.date(2015, 3, 8)]
# summer_4
# May/June
# Sections begin with “4” and “A” and "EC"
# May 7 – June 23 June 4

# summer_5
# May/August
# Sections begin with “5” and “B” and "EC"
# May 7 – Aug. 19 July 14

# summer_6
# July/August
# Sections begin with “6” and “C” and "EC"
# July 7 – Aug. 19 July 31

# summer_7
# July
# Sections begin with “7” and “D”
# July 7 – July 25 July 17

# summer_8
# July/August
# Sections begin with “8” and “E”
# July 7 – Aug. 15 July 30

# summer_9
# July/August
# Sections begin with “9” and “F”
# July 28 – Aug. 15 August 7

# Fall /2 Sept. 2 – Dec. 1 October 26

# Fall/Winter /3  Sept. 2 – April 14 March 8

# Winter /4   Jan. 7 – April 14 March 8
