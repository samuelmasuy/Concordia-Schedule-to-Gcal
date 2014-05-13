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
import urllib2

from flask.ext.wtf import Form
from wtforms.fields import RadioField
from wtforms.validators import Required
from wtforms.fields.html5 import URLField


class InputUrlForm(Form):
    sec_label = 'Create a new secondary Calendar: "Schedule Concordia" or' \
        ' append the events to your existing "Schedule Concordia" secondary' \
        ' Calendar.'
    prim_label = 'Append the events to your primary calendar.'
    url = URLField('url', validators=[Required()])
    cal_id = RadioField('cal_id',
                        choices=[('sec', sec_label), ('prim', prim_label)],
                        default='sec')

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
