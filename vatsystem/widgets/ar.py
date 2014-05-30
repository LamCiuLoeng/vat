# coding: utf-8

from vatsystem.model import *
from vatsystem.util import const
from vatsystem.widgets.components import *

__all__ = [
           "si_search_form",
           "so_search_form",
           "thead_search_form",
           "chead_search_form",
           "si_group_search_form",
           "so_group_search_form"
           ]

class SiSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"),
        RPACAjaxText("customer_name", label_text="Customer Name"),
        RPACAjaxText("invoice_no", label_text="SI Number"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'siStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'siEndDate'}, label_text="Date To"),
    ]

class SoSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"),
        RPACAjaxText("customer_name", label_text="Customer Name"),
        RPACAjaxText("sales_contract_no", label_text="SO Number"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'soStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'soEndDate'}, label_text="Date To"),
    ]

class TheadSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"),
        RPACAjaxText("customer_name", label_text="Customer Name"),
        RPACSelect("status",attrs={'VISIBILITY':'visible'}, label_text="Status", options=const.VAT_THEAD_STATUS_LIST),
        RPACSelect("pending",attrs={'VISIBILITY':'visible'}, label_text="Pending", options=('', 'YES', 'NO')),
        RPACAjaxText("invoice_no", label_text="SI Number"),
        RPACAjaxText("sales_contract_no", label_text="SO Number"),
        RPACAjaxText("ref", label_text="Reference No"),
        RPACAjaxText("vat_no", label_text="VAT No"),
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACSelect("related_si",attrs={'VISIBILITY':'visible'}, label_text="Related SI", options=('', 'YES', 'NO')),
        RPACAjaxText("create_by_id", label_text="Created By"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'theadStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'theadEndDate'}, label_text="Date To"),
    ]

class CHeadSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"),
        RPACAjaxText("customer_name", label_text="Customer Name"),
        RPACSelect("status", attrs={'VISIBILITY':'visible'}, label_text="Status", options=const.VAT_CHEAD_STATUS_LIST),
        RPACAjaxText("invoice_no", label_text="SI Number"),
        RPACAjaxText("sales_contract_no", label_text="SO Number"),
        RPACAjaxText("thead_ref", label_text="MSI/MSO Ref"),
        RPACAjaxText("ref", label_text="MCN Ref"),
        RPACAjaxText("vat_no", label_text="VAT No"),
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACAjaxText("create_by_id", label_text="Created By"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'cheadStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'cheadEndDate'}, label_text="Date To"),
    ]

class SiGroupSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"),
        RPACAjaxText("customer_name", label_text="Customer Name"),
        RPACAjaxText("customer_type", label_text="Customer Type"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'siGroupStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'siGroupEndDate'}, label_text="Date To"),
    ]

class SoGroupSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"),
        RPACAjaxText("customer_name", label_text="Customer Name"),
        RPACAjaxText("customer_type", label_text="Customer Type"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'soGroupStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'soGroupEndDate'}, label_text="Date To"),
    ]
    
si_search_form = SiSearchForm()
so_search_form = SoSearchForm()
thead_search_form = TheadSearchForm()
chead_search_form = CHeadSearchForm()
si_group_search_form = SiGroupSearchForm()
so_group_search_form = SoGroupSearchForm()
