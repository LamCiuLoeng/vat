# -*- coding: utf-8 -*-
from repoze.what.predicates import not_anonymous
from tg import expose
from tg import flash
from tg import redirect
from tg import request
from tg import require
from tg import session
from tg import url
from tg import config
from vatsystem.controllers.ar import *
from vatsystem.controllers.ap import *
from vatsystem.controllers.cost import *
from vatsystem.controllers.report import *
from vatsystem.controllers.access import *
from vatsystem.controllers.master import *
from vatsystem.lib.base import BaseController
from vatsystem.util import const
from vatsystem.util.common import *

__all__=['RootController']

class RootController(BaseController):

    
    ar = ARController()
    ap = APController() 
    cost = COSTController() 
    report = ReportController()
    access = AccessController()
    user = UserController()
    
    
    @require(not_anonymous())
    @expose('vatsystem.templates.index')
    @tabFocus(tab_type="main")
    def index(self):
        """Handle the front-page."""
        return dict(page='index')

    @expose('vatsystem.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        if request.identity: redirect(came_from)
        login_counter=request.environ['repoze.who.logins']
        if login_counter>0:
            flash('Wrong credentials', 'warning')
        return dict(page='login', login_counter=str(login_counter), came_from=came_from)

    @expose()
    def post_login(self, came_from=url('/')):
        if not request.identity:
            login_counter=request.environ['repoze.who.logins']+1
            redirect(url('/login', came_from=came_from, __logins=login_counter))
        #userid = request.identity['repoze.who.userid']
        #flash('Welcome back, %s!' % userid)
        session['company_code'] = config['company_code']
        session.save()
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        #flash('We hope to see you soon!')
        redirect(came_from)

    @require(not_anonymous())
    @expose('vatsystem.templates.page_master')
    @tabFocus(tab_type="master")
    def master(self):
        """Handle the front-page."""
        return {}

