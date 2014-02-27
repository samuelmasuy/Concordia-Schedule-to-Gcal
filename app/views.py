#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  This file is part of ScheduleToGoogleCal.
#
#  This file may be used under the terms of the GNU General Public
#  License version 2.0 as published by the Free Software Foundation
#  and appearing in the file license.txt included in the packaging of
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
from app import app
from flask import (render_template, session, url_for,
                   request, redirect, flash, abort)
from forms import InputUrlForm

import os

from apiclient.discovery import build
import httplib2
from oauth2client.client import OAuth2Credentials

from calendar_controller import (insert_calendar, insert_event,
                                 rollback, get_flow)


@app.route('/login')
def login():
    flow = get_flow(request.url_root)
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)


@app.route('/logout')
def logout():
    session.pop('credentials', None)
    app.SECRET_KEY = os.urandom(66)
    return render_template('schedule_logout.html')


@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    if code:
        flow = get_flow(request.url_root)
        try:
            credentials = flow.step2_exchange(code)
        except Exception:
            redirect(url_for('schedule_index'))

        c = credentials.to_json()
        session['credentials'] = c
    return redirect(url_for('schedule_index'))


def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text, error))


@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500


@app.route('/', methods=['GET', 'POST'])
@app.route('/schedule_index', methods=['GET', 'POST'])
def schedule_index():
    # Create form.
    form = InputUrlForm()
    url = ''
    events = []
    # User is not loggedIn!
    isAnonymous = True

    # If the user didn't log in, before submitting form,
    # save what was in the url box.
    if 'url' in session:
        form.url.data = session['url']

    # Check if the user is loggedIn.
    if 'credentials' in session:
        isAnonymous = False

    # When the form is validated, see forms.py for validation.
    if form.validate_on_submit():
        # Save what is in the field.
        url = form.url.data
        new_cal = form.new_cal.data
        session['url'] = url

        # Make sure the user is actually loggedIn.
        try:
            tokken = session['credentials']
        except KeyError:
            flash(
                "Please accept that this application writes"
                + " into your google calendar.")
            return render_template('schedule_index.html', tilte="Schedule App",
                                   form=form, isAnonymous=isAnonymous)

        credentials = OAuth2Credentials.from_json(tokken)
        http = httplib2.Http()
        http = credentials.authorize(http)
        # Create service required to manipulate the user calendar.
        service = build("calendar", "v3", http=http)

        # Insert a secondary if the user check the box.
        if new_cal is True:
            cal = insert_calendar(service)
        else:
            cal = 'primary'
        # Insert events.
        events = insert_event(service, url, cal)
        # Save events and calendar created in case the user wants to rollback.
        session['events'] = events
        session['cal'] = cal
        session.pop('url', None)
    else:
        # When the form is not valid, render appropriate message.
        flash_errors(form)
    return render_template('schedule_index.html', tilte="Schedule App",
                           form=form, url=url, isAnonymous=isAnonymous)


@app.route('/schedule_delete')
def schedule_delete():
    try:
        cal = session['cal']
        if session['cal'] is None:
            return abort(404)

        credentials = session['credentials']

        credentials = OAuth2Credentials.from_json(credentials)
        http = httplib2.Http()
        http = credentials.authorize(http)
        service = build("calendar", "v3", http=http)

        events_to_delete = session['events']
        rollback(service, events_to_delete, cal)

        session.pop('cal', None)
        session.pop('events', None)
        return render_template('schedule_delete.html',
                               title="Deleted events and calendar", cal=cal)
    except KeyError:
        return abort(404)
