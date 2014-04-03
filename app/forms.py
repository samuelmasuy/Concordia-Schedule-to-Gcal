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
from wtforms import BooleanField
from wtforms.validators import Required
from wtforms.fields.html5 import URLField


class InputUrlForm(Form):
    url = URLField('url', validators=[Required()])
    new_cal = BooleanField('new_cal')

    def validate(self):
        url_error = ["Wrong type of URL!"]
        if not Form.validate(self):
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
