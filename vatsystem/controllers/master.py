# -*- coding: utf-8 -*-

from tg import expose

from vatsystem.controllers.basicMaster import *
from vatsystem.model import *
from vatsystem.widgets.master import *

__all__=["UserController", ]

#class ItemCodeController(BasicMasterController):
#    url = "itemcode"
#    template = "vatsystem.templates.masters.index"
#    dbObj  = JCPItemCodeMaster
#    searchWidget = itemCodeSearchFormInstance
#    updateWidget = itemCodeUpdateFormInstance
#    formFields = ["name","description"]


class UserController(BasicMasterController):
    url="user"
    dbObj=User
    template="vatsystem.templates.masters.index_user"
    searchWidget=userSearchFormInstance
    updateWidget=userUpdateFormInstance
    formFields=["user_name", "display_name", "phone", "fax", "email_address"]

    def beforeSaveNew(self, kw, params):
        useless_keys=["issuedBy", "lastModifyBy", "lastModifyTime"]
        params=dict([key, params[key]] for key in params.keys() if key not in useless_keys)
        #params['password']=None
        return params

    def beforeSaveUpdate(self, kw, params):
        useless_keys=["issuedBy", "lastModifyBy", "lastModifyTime"]
        params=dict([key, params[key]] for key in params.keys() if key not in useless_keys)
        #params['password']=None
        return params

    def searchMaster(self, kw):
        search_config={
                       "user_name":["user_name", str],
                       "display_name":["display_name", str],
                       "phone":["phone", str],
                       "fax":["fax", str],
                       "email_address":["email_address", str],
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
        return obj.order_by(self.dbObj.user_id).all()

    @expose('vatsystem.templates.masters.form')
    @tabFocus(tab_type="master")
    def update(self, **kw):
        obj=getOr404(self.dbObj, kw["id"], "/%s/index"%self.url)
        values={}
        for f in self.formFields : values[f]=getattr(obj, f)

        return {
                "widget" : self.updateWidget,
                "values" : values,
                "saveURL" : "/%s/saveUpdate?id=%d"%(self.url, obj.user_id),
                "funcURL" :self.url
                }

#class ContactController(BasicMasterController):
#    url="contact"
#    dbObj=JCPContact
#    template="vatsystem.templates.masters.index_contact"
#    searchWidget=contactSearchFormInstance
#    updateWidget=contactUpdateFormInstance
#    formFields=["name", "email", "countryId"]
#
#class BillToController(BasicMasterController):
#    url="billto"
#    dbObj=JCPBillTo
#    template="vatsystem.templates.masters.index_billto"
#    searchWidget=billToSearchFormInstance
#    updateWidget=billToUpdateFormInstance
#    formFields=["customer_id", "company", "address", "attn", "tel", "fax", "email"]
#
#    def beforeSaveNew(self, kw, params):
#        params['is_default']=1
#        return params
#
#class ShipToController(BasicMasterController):
#    url="shipto"
#    dbObj=JCPShipTo
#    template="vatsystem.templates.masters.index_shipto"
#    searchWidget=shipToSearchFormInstance
#    updateWidget=shipToUpdateFormInstance
#    formFields=["customer_id", "company", "address", "attn", "tel", "fax", "email"]
#
#    def beforeSaveNew(self, kw, params):
#        params['is_default']=1
#        return params
#
#class CountryCodeController(BasicMasterController):
#    url="countrycode"
#    dbObj=JCPCountryCode
#    template="vatsystem.templates.masters.index_countrycode"
#    searchWidget=countryCodeSearchFormInstance
#    updateWidget=countryCodeUpdateFormInstance
#    formFields=["countryName", "countryCode"]
#
#class ItemInfoController(BasicMasterController):
#    url="iteminfo"
#    dbObj=JCPItemInfo
#    template="vatsystem.templates.masters.index_iteminfo"
#    searchWidget=itemInfoSearchFormInstance
#    updateWidget=itemInfoUpdateFormInstance
#    formFields=["item_code",
#                "packaging_code",
#                "washing_instruction",
#                "fiber_content",
#                "country_of_origin",
#                "special_value",
#                "path",
#                "status",
#                ]
#
#    def beforeSaveNew(self, kw, params):
#        version=JCPItemInfo.get_max_version(pkg_code=params['packaging_code'])
#        print version
#        params['version']=int(version)+1 if version else 1
#        return params
#
#    def beforeSaveUpdate(self, kw, params):
#        version=JCPItemInfo.get_max_version(pkg_code=params['packaging_code'])
#        params['version']=int(version) if version else 1
#        return params
#
#class CustomerController(BasicMasterController):
#    url="customer"
#    dbObj=JCPCustomer
#    template="vatsystem.templates.masters.index_customer"
#    searchWidget=customerSearchFormInstance
#    updateWidget=customerUpdateFormInstance
#    formFields=["name"]




