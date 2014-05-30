# coding: utf-8

from vatsystem.model import *
from vatsystem.util import const
from vatsystem.widgets.components import *

__all__ = [
           "pi_search_form",
           "po_search_form",
           "phead_search_form",
           "shead_search_form",
           "mhead_search_form",
           "excel_search_form",
           "dzd_pi_search_form",
           "dzd_dn_search_form",
           "dzd_set_date_form"
           ]

def getOptions(obj, query_field="name", to = None, order_by_field="name", active=0):
    def fun():
        if active==None:
            data = DBSession.query(obj).order_by(getattr(obj, order_by_field))
        else:
            data = DBSession.query(obj).filter(obj.active == active).order_by(getattr(obj, order_by_field))
        if to:
            data = data.filter(obj.type == to)
        return  [("", ""), ] + [(str(row.id), str(getattr(row, query_field))) for row in data.all()]
    return fun

def getsupplier():
    def fun():
        getsupplier  = DBSession.query(distinct(STDetail.supplier_code)) 
        getsupplier1 = DBSession.query(distinct(DNDetail.supplier_code)) 
        getsupplierall  = getsupplier.union(getsupplier1).all()
        return  [("", ""), ] + [(str(row[0]), str(row[0])) for row in getsupplierall]
    return fun

class ExcelSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("supplier_code", label_text="Supplier Code"), 
        RPACAjaxText("po_no", label_text="PO Number"),
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACSelect("status", attrs={'VISIBILITY':'visible'}, label_text="Status", options=const.SEARCH_TYPE_EXCEL_STATUS),
        RPACAjaxText("ref", label_text="Ref"),
        RPACAjaxText("reconciliation_lot", label_text='Statement NO'),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'siStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'siEndDate'}, label_text="Date To"),
    ]

class PiSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("supplier", label_text="Supplier Code"), 
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACAjaxText("purchase_invoice_no", label_text="PI Number"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'siStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'siEndDate'}, label_text="Date To"),
    ]

class PoSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("customer_code", label_text="Customer Code"),
        RPACAjaxText("customer_name", label_text="Customer Name"),
        RPACAjaxText("sales_contract_no", label_text="SO Number"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'soStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'soEndDate'}, label_text="Date To"),
    ]

class PheadSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("supplier", label_text="Supplier Code"),
        RPACAjaxText("supplier_name", label_text="Supplier Name"),
        RPACSelect("status",attrs={'VISIBILITY':'visible'}, label_text="Status", options=const.VAT_THEAD_STATUS_LIST),
        RPACAjaxText("invoice_no", label_text="PI Number"),
        RPACAjaxText("po_no", label_text="PO Number"),
        RPACAjaxText("ref", label_text="Reference No"),
        RPACAjaxText("dzd", label_text="DZD Ref"),
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACAjaxText("create_by_id", label_text="Created By"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'theadStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'theadEndDate'}, label_text="Date To"),
    ]

class SHeadSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("supplier", label_text="Supplier Code"),
        RPACAjaxText("supplier_name", label_text="Supplier Name"),
        RPACSelect("status", attrs={'VISIBILITY':'visible'}, label_text="Status", options=const.VAT_CHEAD_STATUS_LIST),
        RPACAjaxText("invoice_no", label_text="PI Number"),
        RPACAjaxText("po_no", label_text="PO Number"),
        RPACAjaxText("phead_ref", label_text="MPI/MPO Ref"),
        RPACAjaxText("ref", label_text="MSN Ref"),
        RPACAjaxText("dzd", label_text="DZD Ref"),
        RPACAjaxText("vat_no", label_text="VAT No"),
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACAjaxText("create_by_id", label_text="Created By"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'cheadStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'cheadEndDate'}, label_text="Date To"),
    ]
class MHeadSearchForm(RPACNoForm):
    fields = [
        RPACAjaxText("supplier", label_text="Supplier Code"),
        RPACAjaxText("supplier_name", label_text="Supplier Name"),
        RPACSelect("status", attrs={'VISIBILITY':'visible'}, label_text="Status", options=const.VAT_CHEAD_STATUS_LIST),
        RPACAjaxText("invoice_no", label_text="PI Number"),
        RPACAjaxText("po_no", label_text="PO Number"),
        RPACAjaxText("phead_ref", label_text="MPI/MPO Ref"),
        RPACAjaxText("ref", label_text="MSN Ref"),
        #RPACAjaxText("vat_no", label_text="VAT No"),
        RPACAjaxText("item_code", label_text="Item Code"),
        RPACAjaxText("create_by_id", label_text="Created By"),
        RPACCalendarPicker("date_from", attrs={'style':'width:80px','id':'cheadStartDate'}, label_text="Date From"),
        RPACCalendarPicker("date_to", attrs={'style':'width:80px','id':'cheadEndDate'}, label_text="Date To"),
    ]
    
class DZDPiSearchForm(RPACForm):
    fields = [
        RPACAjaxText("supplier_code", label_text="Supplier Code" , attrs={'cid':'piSearch'}), 
        RPACAjaxText("invoice_no", label_text="Invoice Number", attrs={'cid':'piSearch'}),
        RPACAjaxText("mpi_ref", label_text="MPI No", attrs={'cid':'piSearch'}),
        RPACAjaxText("billing_month", label_text=u'\u5f00\u7968\u6708\u4efd', attrs={'cid':'piSearch'}),
        RPACAjaxText("kingdee_date", label_text=u'\u5165\u91d1\u8776\u6708\u4efd', attrs={'cid':'piSearch'}),
        RPACAjaxText("reconciliation_lot", label_text=u'\u5bf9\u5e10\u6279\u53f7', attrs={'cid':'piSearch'}),
        RPACAjaxText("payment_date", label_text=u'\u4ed8\u6b3e\u65e5\u671f', attrs={'cid':'piSearch'}),
        RPACSelect("status", attrs={'VISIBILITY':'visible', 'cid':'piSearch'}, label_text="Status", options=const.SEARCH_TYPE_EXCEL_STATUS),
    ]
    
class DZDDnSearchForm(RPACForm):
    fields = [
        RPACAjaxText("supplier_code", label_text="Supplier Code", attrs={'cid':'dnSearch'}), 
        RPACAjaxText("number", label_text="Note No", attrs={'cid':'dnSearch'}),
        RPACAjaxText("msn_ref", label_text="MSN No", attrs={'cid':'dnSearch'}),
        RPACAjaxText("billing_month", label_text=u'\u5f00\u7968\u6708\u4efd', attrs={'cid':'dnSearch'}),
        RPACAjaxText("kingdee_date", label_text=u'\u5165\u91d1\u8776\u6708\u4efd', attrs={'cid':'dnSearch'}),
        RPACAjaxText("reconciliation_lot", label_text=u'\u5bf9\u5e10\u6279\u53f7', attrs={'cid':'dnSearch'}),
        RPACAjaxText("payment_date", label_text=u'\u4ed8\u6b3e\u65e5\u671f', attrs={'cid':'dnSearch'}),
        RPACSelect("status", attrs={'VISIBILITY':'visible', 'cid':'dnSearch'}, label_text="Status", options=const.SEARCH_TYPE_EXCEL_STATUS),
    ]
class DZDSetDateForm(RPACForm):
    fields = [
        HiddenField("billing_month_complete", attrs={'cid':'dzd_search'}),
        HiddenField("kingdee_date_complete", attrs={'cid':'dzd_search'}),
        HiddenField("payment_date_complete", attrs={'cid':'dzd_search'}),
        RPACSelect("supplier_code", label_text="Supplier Code", attrs={'cid':'dzd_search'}),
        RPACAjaxText("kingdee_date", label_text=u'\u5165\u91d1\u8776\u6708\u4efd', attrs={'cid':'dzd_search'}),
        RPACSelect("reconciliation_lot", label_text=u'\u5bf9\u5e10\u6279\u53f7', attrs={'cid':'dzd_search'}),
        RPACAjaxText("payment_date", label_text=u'\u4ed8\u6b3e\u65e5\u671f', attrs={'cid':'dzd_search'}), 
        RPACAjaxText("billing_month", label_text=u'\u5f00\u7968\u6708\u4efd', attrs={'cid':'dzd_search'}),
    ]
 
pi_search_form = PiSearchForm()
po_search_form = PoSearchForm()
phead_search_form = PheadSearchForm()
shead_search_form = SHeadSearchForm()
mhead_search_form = MHeadSearchForm()
excel_search_form = ExcelSearchForm()
dzd_pi_search_form = DZDPiSearchForm()
dzd_dn_search_form = DZDDnSearchForm()
dzd_set_date_form = DZDSetDateForm()
