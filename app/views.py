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
import os

from flask import (render_template, session, url_for,
                   request, redirect, flash, abort)
from forms import InputUrlForm

from app import app
from scheduletogcal.calendar_controller import (
    insert_event, rollback, get_flow)


@app.route('/login')
def login():
    flow = get_flow(request.url_root)
    auth_uri = flow.step1_get_authorize_url()
    return redirect(auth_uri)


@app.route('/logout')
def logout():
    app.SECRET_KEY = os.urandom(66)
    if 'credentials' in session:
        session.pop('credentials', None)
        session.pop('cal', None)
        session.pop('events', None)
        session.pop('new_cal', None)
        return render_template('schedule_logout.html')
    else:
        return redirect(url_for('schedule_login'))


@app.route('/oauth2callback')
def oauth2callback():
    code = request.args.get('code')
    if code:
        flow = get_flow(request.url_root)
        try:
            credentials = flow.step2_exchange(code)
        except Exception:
            return redirect(url_for('schedule_login'))

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
    # Check if the user is loggedIn.
    if 'credentials' not in session:
        return redirect(url_for('schedule_login'))

    # Create form.
    form = InputUrlForm()
    events = []
    # When the form is validated, see forms.py for validation.
    if form.validate_on_submit():
        # Save what is in the field.
        url = form.url.data
        new_cal = form.cal_id.data
        # Insert events.
        cal, events = insert_event(url, new_cal)
        # Save events and calendar created in case the user wants to rollback.
        session['events'] = events
        session['cal'] = cal
        return render_template('schedule_result.html', tilte="Schedule App")
    else:
        # When the form is not valid, render appropriate message.
        flash_errors(form)
    return render_template('schedule_index.html', tilte="Schedule App",
                           form=form)


@app.route('/schedule_login')
def schedule_login():
    # User is not loggedIn!
    isAnonymous = True
    # Check if the user is loggedIn.
    if 'credentials' in session:
        isAnonymous = False
    return render_template('schedule_login.html', tilte="Schedule App",
                           isAnonymous=isAnonymous)


@app.route('/schedule_delete')
def schedule_delete():
    try:
        cal = session['cal']
        if session['cal'] is None:
            return abort(404)

        events_to_delete = session['events']
        calendar_to_delete = session['new_cal']
        rollback(events_to_delete, calendar_to_delete, cal)

        session.pop('cal', None)
        session.pop('events', None)
        return render_template('schedule_delete.html',
                               title="Schedule App", cal=cal)
    except KeyError:
        return abort(404)
