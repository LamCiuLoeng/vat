# -*- coding: utf-8 -*-

from vatsystem.model import *
from vatsystem.widgets.components import *

__all__=[#"itemCodeSearchFormInstance","itemCodeUpdateFormInstance",
           "userSearchFormInstance", "userUpdateFormInstance",
#           "contactSearchFormInstance", "contactUpdateFormInstance",
#           "billToSearchFormInstance", "billToUpdateFormInstance",
#           "shipToSearchFormInstance", "shipToUpdateFormInstance",
#           "countryCodeSearchFormInstance", "countryCodeUpdateFormInstance",
#           "itemInfoSearchFormInstance", "itemInfoUpdateFormInstance",
#           "customerSearchFormInstance", "customerUpdateFormInstance"
           ]


##--------------------- for master item code
#class ItemCodeSearchForm(RPACForm):
#    fields = [RPACText("name",label_text="Item Code Name")]
#
#itemCodeSearchFormInstance = ItemCodeSearchForm()
#
#class ItemCodeUpdateForm(RPACForm):
#    fields = [RPACText("name",label_text="Item Code Name"),RPACTextarea("description",label_text="Description")]
#
#itemCodeUpdateFormInstance = ItemCodeUpdateForm()


#--------------------- for master country
class UserSearchForm(RPACForm):
    fields=[RPACText("user_name", label_text="User Name"),
            RPACText("display_name", label_text="Display Name"),
            RPACText("phone", label_text="Phone"),
            RPACText("fax", label_text="Fax"),
            RPACText("email_address", label_text="Email Address")]
userSearchFormInstance=UserSearchForm()

class UserUpdateForm(RPACForm):
    fields=[RPACText("user_name", label_text="User Name"),
            RPACText("display_name", label_text="Display Name"),
            RPACText("phone", label_text="Phone"),
            RPACText("fax", label_text="Fax"),
            RPACText("email_address", label_text="Email Address")]
userUpdateFormInstance=UserUpdateForm()

##--------------------- for master contact
#class ContactSearchForm(RPACForm):
#    Countryoptions=DBSession.query(JCPCountry.id, JCPCountry.name).all()
#    options=[]
#    for v in Countryoptions:
#        options.append((unicode(v[0]), unicode(v[1])))
#    options.append(("", ""))
#    options.reverse()
#
#    fields=[RPACText("name", label_text="contact name"),
#              RPACText("email", label_text="email"),
#              RPACSelect("countryId", label_text="Country", options=options),
#              ]
#contactSearchFormInstance=ContactSearchForm()
#
#class ContactUpdateForm(RPACForm):
#    Countryoptions=DBSession.query(JCPCountry.id, JCPCountry.name).all()
#    options=[]
#    for v in Countryoptions:
#        options.append((unicode(v[0]), unicode(v[1])))
#    options.append(("", ""))
#    options.reverse()
#    fields=[RPACText("name", label_text="contact name"),
#              RPACText("email", label_text="email"),
#              RPACSelect("countryId", label_text="Country", options=options),
#              ]
#contactUpdateFormInstance=ContactUpdateForm()
#
#class BillToSearchForm(RPACForm):
#    customers=DBSession.query(JCPCustomer.id, JCPCustomer.name).all()
#    options=[]
#    for v in customers:
#        options.append((unicode(v[0]), unicode(v[1])))
#
#    options.append(('', ''))
#    options.reverse()
#    fields=[RPACSelect("customer_id", label_text="Customer", options=options),
#              RPACText("company", label_text="Company"),
#              RPACText("address", label_text="Address"),
#              RPACText("attn", label_text="Attn"),
#              RPACText("tel", label_text="Tel"),
#              RPACText("fax", label_text="Fax"),
#              RPACText("email", label_text="E-mail")
#              ]
#billToSearchFormInstance=BillToSearchForm()
#
#class BillToUpdateForm(RPACForm):
#    customers=DBSession.query(JCPCustomer.id, JCPCustomer.name).all()
#    options=[]
#    for v in customers:
#        options.append((unicode(v[0]), unicode(v[1])))
#
#    options.append(('', ''))
#    options.reverse()
#    fields=[RPACSelect("customer_id", label_text="Customer", options=options),
#              RPACText("company", label_text="Company"),
#              RPACText("address", label_text="Address"),
#              RPACText("attn", label_text="Attn"),
#              RPACText("tel", label_text="Tel"),
#              RPACText("fax", label_text="Fax"),
#              RPACText("email", label_text="E-mail")
#              ]
#billToUpdateFormInstance=BillToUpdateForm()
#
#class ShipToSearchForm(RPACForm):
#    customers=DBSession.query(JCPCustomer.id, JCPCustomer.name).all()
#    options=[]
#    for v in customers:
#        options.append((unicode(v[0]), unicode(v[1])))
#
#    options.append(('', ''))
#    options.reverse()
#    fields=[RPACSelect("customer_id", label_text="Customer", options=options),
#              RPACText("company", label_text="Company"),
#              RPACText("address", label_text="Address"),
#              RPACText("attn", label_text="Attn"),
#              RPACText("tel", label_text="Tel"),
#              RPACText("fax", label_text="Fax"),
#              RPACText("email", label_text="E-mail")
#              ]
#shipToSearchFormInstance=ShipToSearchForm()
#
#class ShipToUpdateForm(RPACForm):
#    customers=DBSession.query(JCPCustomer.id, JCPCustomer.name).all()
#    options=[]
#    for v in customers:
#        options.append((unicode(v[0]), unicode(v[1])))
#
#    options.append(('', ''))
#    options.reverse()
#    fields=[RPACSelect("customer_id", label_text="Customer", options=options),
#              RPACText("company", label_text="Company"),
#              RPACText("address", label_text="Address"),
#              RPACText("attn", label_text="Attn"),
#              RPACText("tel", label_text="Tel"),
#              RPACText("fax", label_text="Fax"),
#              RPACText("email", label_text="E-mail")
#              ]
#shipToUpdateFormInstance=ShipToUpdateForm()
#
#class CountryCodeSearchForm(RPACForm):
#    fields=[RPACText("countryName", label_text="Country Name"),
#              RPACText("countryCode", label_text="Country Code")]
#countryCodeSearchFormInstance=CountryCodeSearchForm()
#
#class CountryCodeUpdateForm(RPACForm):
#    fields=[RPACText("countryName", label_text="Country Name"),
#              RPACText("countryCode", label_text="Country Code")]
#countryCodeUpdateFormInstance=CountryCodeUpdateForm()
#
#class ItemInfoSearchForm(RPACForm):
#    fields=[RPACText("item_code", label_text="Item Code"),
#              RPACText("packaging_code", label_text="Packaging Code"),
#              RPACRadio("washing_instruction", label_text="Washing Instruction", options=[(True, "True"), (False, "False")]),
#              RPACRadio("fiber_content", label_text="Fiber Content", options=[(True, "True"), (False, "False")]),
#              RPACRadio("country_of_origin", label_text="Country of Origin", options=[(True, "True"), (False, "False")]),
#              RPACRadio("special_value", label_text="Special Value", options=[(True, "True"), (False, "False")]),
#              RPACText("path", label_text="Path"),
#              RPACSelect("status", label_text="Status", options=[(0, 'Active'), (1, 'Inactive')]),
#              ]
#itemInfoSearchFormInstance=ItemInfoSearchForm()
#
#class ItemInfoUpdateForm(RPACForm):
#    fields=[RPACText("item_code", label_text="Item Code"),
#              RPACText("packaging_code", label_text="Packaging Code"),
#              RPACRadio("washing_instruction", label_text="Washing Instruction", options=[(True, "True"), (False, "False")]),
#              RPACRadio("fiber_content", label_text="Fiber Content", options=[(True, "True"), (False, "False")]),
#              RPACRadio("country_of_origin", label_text="Country of Origin", options=[(True, "True"), (False, "False")]),
#              RPACRadio("special_value", label_text="Special Value", options=[(True, "True"), (False, "False")]),
#              RPACText("path", label_text="Path"),
#              RPACSelect("status", label_text="Status", options=[(0, 'Active'), (1, 'Inactive')]),
#              ]
#itemInfoUpdateFormInstance=ItemInfoUpdateForm()
#
#class CustomerSearchForm(RPACForm):
#    fields=[RPACText("name", label_text="Customer Name")]
#customerSearchFormInstance=CustomerSearchForm()
#
#class CustomerUpdateForm(RPACForm):
#    fields=[RPACText("name", label_text="Customer Name")]
#customerUpdateFormInstance=CustomerUpdateForm()
