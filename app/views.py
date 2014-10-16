# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================
import os
import requests
from flask import (render_template, session, url_for,
                   request, redirect, flash, abort, jsonify)
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

        cred = credentials.to_json()
        session['credentials'] = cred
    return redirect(url_for('schedule_index'))


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
    form = InputUrlForm(request.form)
    events = []
    # When the form is validated, see forms.py for validation.
    if request.method == 'POST':
        if form.validate():
            # Save what is in the field.
            username = request.form.get('username')
            password = request.form.get('password')
            semester = request.form.get('session')
            print username, password, semester
            url = "https://psis.concordia.ca/personalschedule/start.asp"
            payload = {'userid': username,
                    'pwd': password,
                    'sess': semester,
                    'SUBMIT2': 'Get+Your+Class+Schedule'}
            with requests.Session() as s:
                response = s.get(url, data=payload)
                print response.url
                if 'Invalid' in response.url:
                    response = jsonify(message='The creditentials you entered are not valid! Please, try again.')
                    response.status_code = 401
                    return response
                desired_url = response.url.replace('ClassSchedule2', 'ClassSchedule1')

            # Insert events.
            cal, events = insert_event(desired_url)
            # Save events and calendar created in case the user wants to rollback.
            session['events'] = events
            session['cal'] = cal
            return render_template('schedule_result.html', tilte="Schedule App")
        else:
            ## When the form is not valid, render appropriate message.
            response = jsonify(message=form.errors)
            response.status_code = 400
            return response
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
            return abort(500)

        events_to_delete = session['events']
        rollback(events_to_delete, cal)

        session.pop('cal', None)
        session.pop('events', None)
        return render_template('schedule_delete.html',
                               title="Schedule App", cal=cal)
    except KeyError:
        return abort(500)
