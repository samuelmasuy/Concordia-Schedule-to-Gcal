# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================
import urllib2

from flask.ext.wtf import Form
from wtforms.validators import Required
from wtforms.fields.html5 import URLField


class InputUrlForm(Form):
    url = URLField('url', validators=[Required()])

    def validate(self):
        url_error = [
            "Make sure to login on " +
            "<a href='http://psis.concordia.ca/personalschedule/login.asp'>" +
            "MyConcordia portal.</a> and paste the url of your schedule."]
        if not Form.validate(self):
            self.errors['url'] = "not validated"
            return False
        try:
            urllib2.urlopen(self.url.data, timeout=1)
        except urllib2.URLError:
            self.errors['url'] = url_error
            return False
        except ValueError:
            self.errors['url'] = url_error
            return False
        else:
            if "psis.concordia.ca" not in self.url.data:
                self.errors['url'] = url_error
                return False
            if "ClassSchedule1" not in self.url.data:
                if "ClassSchedule2" in self.url.data:
                    self.url.data = self.url.data.replace(
                        "ClassSchedule2", "ClassSchedule1")
                    return True
                else:
                    self.errors['url'] = url_error
                    return False
        return True
