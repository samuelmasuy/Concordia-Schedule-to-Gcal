# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================

__author__ = 'Samuel Masuy'
__email__ = 'samuel.masuy@gmail.com'

from app import app
from flask_wtf.csrf import CsrfProtect

CsrfProtect(app)
app.run()

