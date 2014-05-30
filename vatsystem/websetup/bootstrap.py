# -*- coding: utf-8 -*-
"""Setup the vatsystem application"""

import logging
from tg import config
from vatsystem import model

import transaction


def bootstrap(command, conf, vars):
    """Place any commands to setup vatsystem here"""

    # <websetup.bootstrap.before.auth
    from sqlalchemy.exc import IntegrityError
    try:
        u = model.User()
        u.user_name = u'admin'
        u.display_name = u'Administrator manager'
        u.email_address = u'manager@somedomain.com'
        u.password = u'ecrmadmin'
    
        model.DBSession.add(u)
    
        g = model.Group()
        g.group_name = u'Admin'
        g.display_name = u'Admin Group'
    
        g.users.append(u)
    
        model.DBSession.add(g)
    
    except IntegrityError:
        print 'Warning, there was a problem adding your auth data, it may have already been added:'
        import traceback
        print traceback.format_exc()
        transaction.abort()
        print 'Continuing with bootstrapping...'
        

    # <websetup.bootstrap.after.auth>
