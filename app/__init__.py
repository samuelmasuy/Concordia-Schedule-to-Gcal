# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================
from flask import Flask
# from flask_debugtoolbar import DebugToolbarExtension

# Declare app object
app = Flask(__name__)
# tell flask where is the config file
app.config.from_object('config')
app.debug = True
# toolbar = DebugToolbarExtension(app)

from app import views
