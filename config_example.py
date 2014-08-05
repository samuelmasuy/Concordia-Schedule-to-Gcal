# -*- coding: utf-8 -*-
#  ===========================================================================
#
#  Copyright (C) 2014 Samuel Masuy. All rights reserved.
#  samuel.masuy@gmail.com
#
#  ===========================================================================

import os
# Protects against cross-site request forgery
CSRF_ENABLED = True

SECRET_KEY = os.urandom(66)

# CLIENT_ID = YOUR_CLIENT_ID
# CLIENT_SECRET = YOUR_CLIENT_SECRET
