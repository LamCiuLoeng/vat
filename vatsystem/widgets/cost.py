# coding: utf-8

from vatsystem.model import *
from vatsystem.util import const
from vatsystem.widgets.components import *

__all__ = [
           "ohead_search_form", 
           "nhead_search_form",
           "po_search_form",
           "charge_search_form",
           "variance_search_form"
           ]

class OheadSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Supplier Code"),
        RPACAjaxText("customer_name", label_text="Supplier Name"),
        RPACSelect("status",attrs={'VISIBILITY':'visible'}, label_text="Status", options=const.VAT_THEAD_STATUS_LIST),
        RPACAjaxText("invoice_no", label_text="SI Number"),
        RPACAjaxText("sales_contract_no", label_text="SO Number"),
        RPACAjaxText("thead_ref", label_text="MSI/MSO Ref"),
        RPACAjaxText("ref", label_text="Reference No"),
        RPACAjaxText("vat_no", label_text="VAT No"),
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACAjaxText("create_by_id", label_text="Created By"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'theadStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'theadEndDate'}, label_text="Date To"),
    ]

class NHeadSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Supplier Code"),
        RPACAjaxText("customer_name", label_text="Supplier Name"),
        RPACSelect("status", attrs={'VISIBILITY':'visible'}, label_text="Status", options=const.VAT_CHEAD_STATUS_LIST),
        RPACAjaxText("invoice_no", label_text="SI Number"),
        RPACAjaxText("sales_contract_no", label_text="SO Number"),
        RPACAjaxText("chead_ref", label_text="MCN Ref"),
        RPACAjaxText("ref", label_text="Reference No"),
        RPACAjaxText("vat_no", label_text="VAT No"),
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACAjaxText("create_by_id", label_text="Created By"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'cheadStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'cheadEndDate'}, label_text="Date To"),
    ]
    
class POSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"), 
        RPACAjaxText("customer_name", label_text="Customer Name"), 
        RPACAjaxText("ref", label_text="Ref"),
        RPACAjaxText("item_no", label_text="Item Code"),
        RPACAjaxText("po_no", label_text="PO NO"),
        RPACAjaxText("pi_no", label_text="PI NO"),
        RPACAjaxText("sales_contract_no", label_text="SO Number"),
        RPACAjaxText("invoice_no", label_text="SI Number"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'poStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'poEndDate'}, label_text="Date To"),
    ]
    
class ChargeSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"), 
        RPACAjaxText("customer_name", label_text="Customer Name"), 
        RPACAjaxText("ref", label_text="Ref"),
        RPACAjaxText("item_no", label_text="Item Code"),
        RPACAjaxText("po_no", label_text="PO NO"),
        RPACAjaxText("pi_no", label_text="PI NO"),
        RPACAjaxText("sales_contract_no", label_text="SO Number"),
        RPACAjaxText("invoice_no", label_text="SI Number"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'chargeStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'chargeEndDate'}, label_text="Date To"),
    ]

class VarianceSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("pi_no", label_text="PI No"),
        RPACAjaxText("note_no", label_text="Note No"),
        #RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'varianceStartDate'}, label_text="Date From"),
        #RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'varianceEndDate'}, label_text="Date To"),
    ]
    
ohead_search_form = OheadSearchForm()
nhead_search_form = NHeadSearchForm()
po_search_form = POSearchForm()
charge_search_form = ChargeSearchForm()
variance_search_form = VarianceSearchForm()
