# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================

from flask.ext.wtf import Form
from wtforms import TextField, PasswordField
from wtforms.validators import DataRequired, Length, Regexp


class InputUrlForm(Form):
    username = TextField(u'Concordia Username',
                         validators=[DataRequired(message='notEmpty'),
                         Length(min=4, max=9, message='stringLength'),
                         Regexp("^[A-z]+_[A-z]+$", message='regexp')])
    password = PasswordField(u'Concordia Password',
                             validators=[DataRequired(message='notEmpty'),
                             Length(min=4, max=25, message='stringLength'),
                             Regexp(".+", message='regexp')])
