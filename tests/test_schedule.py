import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

from app.scheduletogcal import course
from app.scheduletogcal import location
from app.scheduletogcal import scraper


# buildings = location.get_buildings_location()


# def test_set_building_name_unknown():
    # building_name, _ = course.set_location('AA', buildings)
    # assert building_name == 'Concordia University'


# def test_set_building_name():
    # building_name, _ = course.set_location('H', buildings)
    # assert building_name == 'Henry F. Hall Building'


# def test_set_building_address_not_setted():
    # _, geoaddress = course.set_location('--', buildings)
    # assert geoaddress == ('Concordia University - Sir George Williams'
                          # ' Campus, Montreal, QC H3G 1M8, Canada')


# def test_set_building_address():
    # _, geoaddress = course.set_location('H', buildings)
    # assert geoaddress == ('1455 Maisonneuve Boulevard West, Montreal,'
                          # ' QC H3G 1M8, Canada')


def test_format_course_name():
    assert course.format_course_name('COMP 352 / 1') == 'COMP 352'


def test_format_room():
    assert course.get_room_name('MB-S2.330-'[:-1]) == 'MB'


def test_day_abbr():
    assert str(course.day_abbr('Monday')) == 'MO'


def test_first_last_day_semester_fall():
    """This test is static"""
    from dateutil import relativedelta as rdelta
    first_day, last_day = course.first_last_day_semester(
        'fall', rdelta.weekday(0))
    from datetime import date
    assert first_day == date(2014, 9, 8)
    assert last_day == '20141202'


def test_first_last_day_semester_summer():
    """This test is static"""
    from dateutil import relativedelta as rdelta
    first_day, last_day = course.first_last_day_semester(
        'summer_4A', rdelta.weekday(3))
    from datetime import date
    assert first_day == date(2014, 5, 8)
    assert last_day == '20140624'


def test_first_day_datetime():
    from datetime import date
    first_day_start, first_day_end = course.first_day_datetime(
        date(2014, 5, 8), '14:45-17:15')
    assert first_day_start == '2014-05-08T14:45:00'
    assert first_day_end == '2014-05-08T17:15:00'


def test_summer_section_letter():
    assert scraper.get_summer_section('A') == '4A'


def test_summer_section_number():
    assert scraper.get_summer_section('4') == '4A'
