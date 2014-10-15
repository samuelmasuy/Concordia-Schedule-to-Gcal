# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================
import urllib2

from flask import request
from flask.ext.wtf import Form
from wtforms.validators import Required
from wtforms.fields.html5 import URLField


class InputUrlForm(Form):
    url = URLField('url')

    def validate(self):
        url_error = ("Make sure to login on " +
                     "<a href='http://psis.concordia.ca/personalschedule/login.asp'>" +
                     "MyConcordia</a> portal and paste the url of your schedule.")
        url_response = request.form.get('url')
        try:
            urllib2.urlopen(url_response, timeout=1)
        except urllib2.URLError:
            self.errors['url'] = url_error
            return False
        except ValueError:
            self.errors['url'] = url_error
            return False
        else:
            if "psis.concordia.ca" not in url_response:
                self.errors['url'] = url_error
                return False
            if "ClassSchedule1" not in url_response:
                if "ClassSchedule2" in url_response:
                    url_response = url_response.replace(
                        "ClassSchedule2", "ClassSchedule1")
                    return True
                else:
                    self.errors['url'] = url_error
                    return False
        return True
