# -*- coding: utf-8 -*-

# turbogears imports
from tg import expose, redirect, validate, flash, session, request
from tg.decorators import *

# third party imports
from repoze.what import predicates, authorize
from repoze.what.predicates import not_anonymous, in_group, has_permission

# project specific imports
from vatsystem.lib.base import BaseController
from vatsystem.model import *


from vatsystem.util.common import *
from vatsystem.widgets.access import *


class AccessController(BaseController):

    allow_only=authorize.not_anonymous()

    @expose('vatsystem.templates.access.index')
    @paginate("result", items_per_page=20)
    @tabFocus(tab_type="access")
    def index(self, **kw):
        if not kw:
            result=[]
        else:
            result=DBSession.query(User).filter(User.__table__.c.user_name.op("ilike")("%%%s%%"%kw["user_name"])).order_by(User.user_name).all()
        return {"widget" : access_search_form, "result" : result}


    @expose('vatsystem.templates.access.add')
    @tabFocus(tab_type="access")
    def add(self, **kw):
        return {}


    @expose()
    def save_new(self, **kw):
        if kw["type"]=="user" :
            password=kw["password"] if kw["password"] else gerRandomStr(8, allAlpha)
            u=User(user_name=kw["user_name"], display_name=kw["display_name"], email_address=kw["email_address"], password=password, phone=kw["phone"], fax=kw["fax"])
            DBSession.add(u)
            DBSession.flush()
            redirect("/access/user_manage?id=%d"%u.user_id)
        elif kw["type"]=="group" :
            g=Group(group_name=kw["group_name"])
            DBSession.add(g)
            DBSession.flush()
            redirect("/access/group_manage?id=%d"%g.group_id)
        elif kw["type"]=="permission" :
            p=Permission(permission_name=kw["permission_name"], description=kw["description"])
            ag=DBSession.query(Group).filter_by(group_name="Admin").one()
            ag.permissions.append(p)
            DBSession.add(p)
            DBSession.flush()
            redirect("/access/permission_manage?id=%d"%p.permission_id)
        else:
            flash("No such type operation!")
            redirect("/access/index")


    @expose("vatsystem.templates.access.user_manage")
    def user_manage(self, **kw):
        u=getOr404(User, kw["id"])
        included=u.groups
        excluded=DBSession.query(Group).filter(~Group.users.any(User.user_id==u.user_id)).order_by(Group.group_name)
        return {
                "widget" : user_update_form,
                "values" : {"id" : u.user_id, "user_name" : u.user_name, "email_address" : u.email_address, "display_name" : u.display_name, "phone" : u.phone, "fax" : u.fax},
                "included" : included,
                "excluded" : excluded,
                }

    @expose()
    def save_user(self, **kw):
        u=getOr404(User, kw["id"])
        if kw.get("user_name", None) : u.user_name=kw["user_name"]
        if kw.get("password", None) : u.password=kw["password"]
        if kw.get("display_name", None) : u.display_name=kw["display_name"]
        if kw.get("email_address", None) : u.email_address=kw["email_address"]
        if kw.get("phone", None) : u.phone=kw["phone"]
        if kw.get("fax", None) : u.fax=kw["fax"]

        if not kw["igs"] : u.groups=[]
        else : u.groups=DBSession.query(Group).filter(Group.group_id.in_(kw["igs"].split("|"))).all()
        flash("Save the update successfully!")
        redirect("/access/index")



    @expose("vatsystem.templates.access.permission_manage")
    def permission_manage(self, **kw):
        p=getOr404(Permission, kw["id"])

        included=p.groups
        excluded=DBSession.query(Group).filter(~Group.permissions.any(Permission.permission_id==p.permission_id)).order_by(Group.group_name)

        return {"widget" : permission_update_form,
                "values" : {"id" : p.permission_id, "permission_name" : p.permission_name},
                "included" : included,
                "excluded" : excluded
                }

    @expose()
    def save_permission(self, **kw):
        p=getOr404(Permission, kw["id"])
        p.permission_name=kw["permission_name"]
        if not kw["igs"] : p.groups=[]
        else : p.groups=DBSession.query(Group).filter(Group.group_id.in_(kw["igs"].split("|"))).all()
        flash("Save the update successfully!")
        redirect("/access/index")

    @expose('vatsystem.templates.access.group_manage')
    @tabFocus(tab_type="access")
    def group_manage(self, **kw):
        g=getOr404(Group, kw["id"])
        included=g.users
        excluded=DBSession.query(User).filter(~User.groups.any(Group.group_id==g.group_id)).order_by(User.user_name)

        got=g.permissions

        #myLog(got)

        lost=DBSession.query(Permission).filter(~Permission.groups.any(Group.group_id==g.group_id)).order_by(Permission.permission_name)
        return {"widget" : group_update_form , "values" : { "id" : g.group_id, "group_name" : g.group_name },
                "included" : included , "excluded" : excluded,
                "got" : got, "lost" : lost }


    @expose()
    def save_group(self, **kw):
        g=getOr404(Group, kw["id"])

        g.group_name=kw["group_name"]

        uigs=kw["uigs"]
        pigs=kw["pigs"]

        if not uigs : g.users=[]
        else : g.users=DBSession.query(User).filter(User.user_id.in_(uigs.split("|"))).all()

        if not pigs : g.permissions=[]
        else : g.permissions=DBSession.query(Permission).filter(Permission.permission_id.in_(pigs.split("|"))).all()

        flash("Save the update successfully!")
        redirect("/access/index")


    @expose("vatsystem.templates.access.test")
    def test(self, **kw):
        return {}
