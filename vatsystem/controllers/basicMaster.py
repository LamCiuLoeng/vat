# -*- coding: utf-8 -*-
from datetime import datetime as dt
import traceback

from tg import redirect, validate, flash, expose, request, override_template
from repoze.what import predicates, authorize
from repoze.what.predicates import not_anonymous, in_group, has_permission
from tg.decorators import paginate

from vatsystem.lib.base import BaseController
from vatsystem.model import DBSession, metadata
from vatsystem.util.common import *
import vatsystem

__all__=["BasicMasterController"]

class BasicMasterController(BaseController):
    #Uncomment this line if your controller requires an authenticated user
    allow_only=authorize.not_anonymous()

    url="__MUST__BE__CHANGE__"
    dbObj=None
    searchWidget=None
    updateWidget=None
    formFields=[]


    @expose('vatsystem.templates.masters.index')
    @paginate("result", items_per_page=20)
    @tabFocus(tab_type="master")
    def index(self, **kw):
        override_template(self.index, "mako:"+self.template)
        if not kw:
            result=[]
        else:
            result=self.searchMaster(kw)
        return {
                "searchWidget" : self.searchWidget,
                "result" : result,
                "funcURL" :self.url,
                "values" : kw,
                }

    @expose('vatsystem.templates.masters.form')
    @tabFocus(tab_type="master")
    def add(self, **kw):
        return {
                "widget" : self.updateWidget,
                "values" : {},
                "saveURL" : "/%s/saveNew"%self.url,
                "funcURL" :self.url
                }

    @expose()
    def saveNew(self, **kw):
        print request.identity["user"]
        params={"issuedBy":request.identity["user"], "lastModifyBy":request.identity["user"], "lastModifyTime":dt.now()}
        for f in self.formFields:
            if f in kw : params[f]=kw[f]
        params=self.beforeSaveNew(kw, params)
        obj=self.dbObj(**params)
        DBSession.add(obj)
        flash("Save the new master successfully!")
        redirect("/%s/index"%self.url)

    @expose('vatsystem.templates.masters.form')
    @tabFocus(tab_type="master")
    def update(self, **kw):
        obj=getOr404(self.dbObj, kw["id"], "/%s/index"%self.url)
        values={}
        for f in self.formFields : values[f]=getattr(obj, f)

        return {
                "widget" : self.updateWidget,
                "values" : values,
                "saveURL" : "/%s/saveUpdate?id=%d"%(self.url, obj.id),
                "funcURL" :self.url
                }

    @expose()
    def saveUpdate(self, **kw):
        obj=getOr404(self.dbObj, kw["id"], "/%s/index"%self.url)
        params={"lastModifyBy":request.identity["user"], "lastModifyTime":dt.now()}
        for f in self.formFields:
            if f in kw : params[f]=kw[f] if kw[f] else None
        params=self.beforeSaveUpdate(kw, params)
        for k in params : setattr(obj, k, params[k])
#       obj.set(**params)
        flash("Update the master successfully!")
        redirect("/%s/index"%self.url)

    @expose()
    def delete(self, **kw):
        obj=getOr404(self.dbObj, kw["id"], "/%s/index"%self.url)
        obj.lastModifyBy=request.identity["user"]
        obj.lastModifyTime=dt.now()
        obj.status=1
        flash("Delete the master successfully!")
        redirect("/%s/index"%self.url)


    def searchMaster(self, kw):
        search_config={"name":["name", str],
                         "email":["email", str],
                         "phone":["phone", str],
                         "countryId":["country_id", int],
                         "customer_id": ["customer_id", int],
                         "company": ["company", str],
                         "address": ["address", str],
                         "attn": ["attn", str],
                         "tel": ["tel", str],
                         "fax": ["fax", str],
                         "countryName": ["countryName", str],
                         "countryCode": ["countryCode", str],
                         "item_code": ["item_code", str],
                         "packaging_code": ["packaging_code", str],
                         "washing_instruction": ["washing_instruction", bool],
                         "fiber_content": ["fiber_content", bool],
                         "country_of_origin": ["country_of_origin", bool],
                         "special_value": ["special_value", bool],
                         "path": ["path", str],
                         "status": ["status", int],
                         }
        obj=DBSession.query(self.dbObj)
        for field, value in kw.items():
            if value:
                if search_config[field][1]==str:
                    obj=obj.filter(getattr(self.dbObj.__table__.c, search_config.get(field, "")[0]).op("ILIKE")("%%%s%%"%value))
                elif search_config[field][1]==int:
                    obj=obj.filter(getattr(self.dbObj.__table__.c, search_config.get(field, "")[0])==int(value))
                else:
                    obj=obj.filter(getattr(self.dbObj.__table__.c, search_config.get(field, "")[0])==value)
            else:
                continue

#        q = DBSession.query(self.dbObj).filter(self.dbObj.__table__.c.name.op("ILIKE")("%%%s%%" %kw["name"]))
#        if not in_group("Admin"):
#            obj = obj.filter(self.dbObj.status==0)
        return obj.order_by(self.dbObj.id).all()

    def beforeSaveNew(self, kw, params):
        return params

    def beforeSaveUpdate(self, kw, params):
        return params

