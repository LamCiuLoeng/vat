# coding: utf-8

from vatsystem.model import *
from vatsystem.util import const
from vatsystem.widgets.components import *

__all__ = [
           "msi_search_form",
           "msi_hidden_form",
           "stockWithOutItem_search_form", 
           "stockWithItem_search_form", 
           "invoiceWithOutCost_search_form", 
           "invoiceWithCost_search_form",
           "msi_list_one_form"
           ]



class MSISearchForm(RPACNoForm):
    fields = [RPACAjaxText("ref_no", label_text="MSI/MSO Number"),
              RPACAjaxText("customer_name", label_text="Customer Name"),
              RPACCalendarPicker("date_from", label_text="Date From"),
              RPACCalendarPicker("date_to", label_text="Date To"),]

class MSIHiddenForm(RPACHiddenForm):
    fields = []

class ExportSearchForm(RPACNoForm):
    fields = [RPACAjaxText("ref_no", label_text="MSI/MSO Number"),]

class ExportHiddenForm(RPACHiddenForm):
    fields = []
    

class StockWithOutItemSearchForm(RPACNoForm):
        fields = [
              RPACCalendarPicker("date_from", attrs={'id':'StockWithOutItemStartDate'}, label_text="Date From"),
              RPACCalendarPicker("date_to", attrs={'id':'StockWithOutItemEndDate'}, label_text="Date To"),]
    
class StockWithItemSearchForm(RPACNoForm):
      fields = [
              RPACAjaxText("item_code", label_text="Item Code"),
              RPACCalendarPicker("date_from", attrs={'id':'StockWithItemStartDate'}, label_text="Date From"),
              RPACCalendarPicker("date_to", attrs={'id':'StockWithItemEndDate'}, label_text="Date To"),]
    
class InvoiceWithOutCostSearchForm(RPACNoForm):
        fields = [
              RPACCalendarPicker("date_from", attrs={'id':'InvoiceWithOutCostStartDate'}, label_text="Date From"),
              RPACCalendarPicker("date_to", attrs={'id':'InvoiceWithOutCostEndDate'}, label_text="Date To"),]
    
class InvoiceWithCostSearchForm(RPACNoForm):
    fields = [
              RPACCalendarPicker("date_from", attrs={'id':'InvoiceWithCostStartDate'}, label_text="Date From"),
              RPACCalendarPicker("date_to", attrs={'id':'InvoiceWithCostEndDate'}, label_text="Date To"),]

class MSIListOneForm(RPACForm):
    fields = [
              RPACAjaxText("customer_code", label_text="Customer Code"),
              RPACAjaxText("invoice_no", label_text="SI Number"),
              RPACAjaxText("sales_contract_no", label_text="SO Number"),
              RPACSelect("rec_month",attrs={'VISIBILITY':'visible'}, label_text=u"对账月份", options=(('',''),(1,1),(2,2),(3,3),(4,4),(5,5),(6,6),(7,7),(8,8),(9,9),(10,10),(11,11),(12,12))),
              RPACSelect("payment_status",attrs={'VISIBILITY':'visible'}, label_text=u"是否付款", options=(('', ''), (1, u'未付'), (2, u'已付'), (3, u'部分付款'))),
              RPACSelect("status",attrs={'VISIBILITY':'visible'}, label_text="MSI/MSO Status", options=const.VAT_THEAD_STATUS_LIST),
              RPACCalendarPicker("vat_date_from", attrs={'style':'width:80px','id':'vatStartDate'}, label_text="VAT Date From"),
              RPACCalendarPicker("vat_date_to", attrs={'style':'width:80px','id':'vatEndDate'}, label_text="VAT Date To"),
              RPACCalendarPicker("create_date_from", attrs={'style':'width:80px','id':'createStartDate'}, label_text="Create Date From"),
              RPACCalendarPicker("create_date_to", attrs={'style':'width:80px','id':'createEndDate'}, label_text="Create Date To"),
              ]
msi_search_form = MSISearchForm()
msi_hidden_form = MSIHiddenForm()
stockWithOutItem_search_form = StockWithOutItemSearchForm()
stockWithItem_search_form = StockWithItemSearchForm()
invoiceWithOutCost_search_form = InvoiceWithOutCostSearchForm()
invoiceWithCost_search_form = InvoiceWithCostSearchForm()
msi_list_one_form = MSIListOneForm()
#export_search_form = ExportSearchForm()
#export_hidden_form = ExportHiddenForm()