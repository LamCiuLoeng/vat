# coding: utf-8
from datetime import date,time
from datetime import datetime as dt
from decimal import Decimal
import logging
import os
import random
import traceback
import zipfile
from itertools import *

from repoze.what import authorize
from repoze.what import predicates
from repoze.what.predicates import has_permission
from repoze.what.predicates import in_group
from repoze.what.predicates import not_anonymous
from sqlalchemy import not_
from tg import config
from tg import expose
from tg import flash
from tg import override_template
from tg import redirect
from tg import request
from tg import url
from tg.decorators import paginate
from vatsystem.lib.base import BaseController
from vatsystem.model import *
from vatsystem.util.const import *
from vatsystem.util.common import *
from vatsystem.util.excel_helper import *
from vatsystem.widgets.report import *
from vatsystem.model.erp import PiDetail

from py4j.java_gateway import JavaGateway

__all__=["ReportController"]
 
 
 
class Bridge(object):
    
    def __init__(self):
        gateway = JavaGateway()
        self.point = gateway.entry_point
        
    def format(self, obj):
        
        if obj != 0 and not obj:
            return ''
            
        if isinstance(obj, (int, float, long, basestring)):
            return obj
        
        elif isinstance(obj, dt):
            return str(obj)
        
        elif isinstance(obj, decimal.Decimal):
            return float(obj)
        
        elif isinstance(obj, list):
            jlist = self.point.create_list()
            for obj1 in obj:
                jlist.add(self.format(obj1))
            return jlist
        
        elif isinstance(obj, dict):
            jhashmap = self.point.create_hashmap()
            for key, obj1 in obj.iteritems():
                jhashmap.put(key, self.format(obj1));
            return jhashmap
        
    def report(self, im, ou, header, style):
        return self.point.report(im, ou, header, style)
    


class ReportController(BaseController):
    
    allow_only=authorize.not_anonymous()

    @expose('vatsystem.templates.report.index')
    @paginate('collections', items_per_page=25)
    @tabFocus(tab_type='main')
    def index(self, **kw):
        results=dict( 
                       kw=kw,
                       stock_withOut_item_search_form = stockWithOutItem_search_form,
                       stock_with_Item_search_form    = stockWithItem_search_form,
                       invoice_withOut_cost_search_form = invoiceWithOutCost_search_form,
                       invoice_with_Cost_search_form    = invoiceWithCost_search_form,
                       msi_list_one_form = msi_list_one_form
                       )
        return results
    
    @expose()
    def stock_without_item(self, **kw):
        header, details = self._stock_without_item(**kw)
        filename = self._set_file_name()
        templatePath = os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/Report_Stock_WithOut_Item_Template.xls")
        header = [
                 [2, 1, kw.get('date_from')], 
                 [2, 3, kw.get('date_to')], 
                 [6, 7, str(header.get('befor_qty'))], 
                 [6, 8, str(header.get('befor_amount'))], 
                 [7, 0, details], 
                 [8+len(details), 2, u'本月累计'],
                 [9+len(details), 2, u'本年累计'],
                 
                 [9+len(details), 4, str(header.get('year_qty'))], 
                 [9+len(details), 6, str(header.get('year_amount'))], 
                 [9+len(details), 7, str(header.get('year_lave_qty'))], 
                 [9+len(details), 8, str(header.get('year_lave_amount'))],
                 
                 [8+len(details), 4, str(header.get('month_qty'))], 
                 [8+len(details), 6, str(header.get('month_amount'))], 
                 [8+len(details), 7, str(header.get('month_lave_qty'))], 
                 [8+len(details), 8, str(header.get('month_lave_amount'))],
                 ]
                            
        style = {
                "A8:I%s" % str(10+len(details)):{"border":"solid", "borderColor":"black"}
                 }
        bridge = Bridge()
        header = bridge.format(header)
        style = bridge.format(style)
        bridge.report(templatePath, filename, header, style)
        return serveFile(unicode(filename))
    
    def _stock_without_item(self, **kw):
        from itertools import *
        result = []
        date_from = kw.get('date_from') 
        date_to   = kw.get('date_to') 
        item_no   = kw.get('item_code')
        
        date_from   = dt.strptime(date_from + "00:00:00", "%Y-%m-%d%H:%M:%S")
        date_to     = dt.strptime(date_to   + "23:59:59", "%Y-%m-%d%H:%M:%S")
        
        cst_details = OHead.find_detail_charge_by_date(date_from, date_to, item_no)
        mpi_details = PHead.find_detail_charge_by_date(date_from, date_to, item_no)
        
        period_qty, period_amount = Period.find_all_by_item(item_no, str(date_from.year - 1))
        
        cst_detail_all = []
        variances = Variance.find()
        for variance in variances:
            if variance.variance_amount == 0:
                continue
            if variance.type not in [const.ERP_TYPE_CHARGE, const.ERP_TYPE_OTHER_CHARGE, const.ERP_TYPE_PO_CHARGE]:
                '''
                variance.cn = []
                variance.curr_qty = None
                variance.unit_price = ''
                variance.amount  = - variance.variance_amount
                variance.date_time = variance.variance_date
                variance.head_type = const.SEARCH_TYPE_CHARGE
                cst_detail_all.append(variance)
            else:
            '''
                if item_no and variance.item_no != item_no:continue
                variance.cn = []
                variance.head_type = const.SEARCH_TYPE_CST
                variance.amount =  -variance.variance_amount
                variance.curr_qty = ''
                variance.unit_price = - variance.variance_price
                variance.date_time = variance.variance_date
                cst_detail_all.append(variance)
                
        csts, cst_charges = {}, {}
        befor_qty, befor_amount, year_qty, year_amount, month_qty, month_amount, \
                                    year_lave_qty, year_lave_amount, month_lave_qty, month_lave_amount = period_qty, period_amount, 0, 0, 0, 0, 0, 0, 0, 0
        cst_details.extend(cst_detail_all)
        for detail in chain(cst_details, mpi_details):
            if isinstance(detail.date_time, date):
                detail.date_time = dt.combine(detail.date_time, time())
            if detail.__tablename__ in ['vat_pcharge', 'vat_cp_charge']:continue
            if detail.date_time < date_from:
                befor_cn_qty = 0
                befor_cn_amount = 0
                for c in detail.cn:
                    cn_qty    = c.get('qty', 0)
                    date_time = c.get('date_time')
                    if date_time and date_time < date_from:
                        befor_cn_qty += cn_qty
                        befor_cn_amount += befor_cn_qty*detail.unit_price
                if detail.curr_qty:
                    befor_qty += detail.curr_qty
                befor_qty -= befor_cn_qty
                befor_amount  += detail.amount
                befor_amount  -= befor_cn_amount
                
            if date_from <= detail.date_time <= date_to:
                month_cn_qty = 0
                month_cn_amount = 0
                for c in detail.cn:
                    cn_qty = c.get('qty', 0)
                    date_time = c.get('date_time')
                    if date_time and date_from <= date_time <= date_to:
                        month_cn_qty += cn_qty
                        month_cn_amount += month_cn_qty*detail.unit_price
                if detail.curr_qty:
                    month_qty += detail.curr_qty
                month_qty -= month_cn_qty
                month_amount  += detail.amount
                month_amount -= month_cn_amount
            if date_from.year == detail.date_time.year and date_to.month >= detail.date_time.month:
                year_cn_qty = 0
                year_cn_amount = 0
                for c in detail.cn:
                    cn_qty = c.get('qty', 0)
                    date_time = c.get('date_time')
                    if date_time and date_from.year == date_time.year and date_to.month >= date_time.month:
                        year_cn_qty += cn_qty
                        year_cn_amount += year_cn_qty*detail.unit_price
                if detail.curr_qty:
                    year_qty += detail.curr_qty
                year_qty -= year_cn_qty
                year_amount  += detail.amount
                year_amount  -= year_cn_amount
                   
            if date_from <= detail.date_time <= date_to:
                item_cn_qty = 0
                item_cn_amount = 0
                for c in detail.cn:
                    cn_qty = c.get('qty', 0)
                    date_time = c.get('date_time')
                    if date_time and date_from <= date_time <= date_to:
                        item_cn_qty += cn_qty
                        item_cn_amount += item_cn_qty*detail.unit_price
                if detail.curr_qty or detail.curr_qty == 0:
                    detail.curr_qty = detail.curr_qty - item_cn_qty
                detail.amount = detail.amount - item_cn_amount
                if (detail.__tablename__ != 'vat_cp_charge' or detail.__tablename__ != 'vat_pcharge') and detail.curr_qty == 0:
                    continue 
                if item_no:
                    l = [detail.date_time, detail.po_no, detail.so_no, detail.curr_qty, str(detail.unit_price), detail.amount]
                    result.append(l)
                else:
                    l = [detail.date_time, detail.item_no, detail.po_no, detail.so_no, detail.curr_qty, str(detail.unit_price), detail.amount]
                    if detail.head_type == const.SEARCH_TYPE_CHARGE:
                        if cst_charges.get(detail.item_no):
                            cst_charges[detail.item_no].append(l)
                        else:
                            cst_charges.update({detail.item_no:[l]})
                    else:
                        if csts.get(detail.item_no):
                            csts[detail.item_no].append(l)
                        else:
                            csts.update({detail.item_no:[l]})
        curr_lave_qty, curr_lave_amount = 0, 0
        if not item_no:
            detail, charge = [], []
            csts = csts.values()
            csts.extend(cst_charges.values())
            for values in csts:
                for value in values:
                    if value[4]:
                        curr_lave_qty += value[4]
                    curr_lave_amount  += value[6]
                    value.extend([curr_lave_qty + befor_qty, curr_lave_amount + befor_amount])
                    detail.append(value)
            result = detail
            
        else:
            detail = []
            for rs in result:
                if rs[3]:
                    curr_lave_qty += rs[3]
                curr_lave_amount  += rs[5]
                rs.extend([curr_lave_qty+befor_qty, curr_lave_amount+befor_amount])
                detail.append(rs)
            result = detail

        year_lave_qty     = befor_qty + year_qty
        year_lave_amount  = befor_amount + year_amount
        month_lave_qty    = befor_qty + month_qty
        month_lave_amount = befor_amount + month_amount
        header = {
                  'item_code':item_no, 'start_date':date_from, 'end_date':date_to, 
                  'befor_qty':befor_qty, 'befor_amount':befor_amount, 'year_qty':year_qty, 'year_amount':year_amount,
                  'month_qty':month_qty, 'month_amount':month_amount, 'year_lave_qty':year_lave_qty, 'year_lave_amount':year_lave_amount,
                  'month_lave_qty':month_lave_qty, 'month_lave_amount':month_lave_amount
                  }
        return [header, result]
    
    @expose()
    def stock_with_item(self, **kw):
        additionInfo = []
        header, details = self._stock_without_item(**kw)
        filename = self._set_file_name()
        templatePath = os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/Report_Stock_With_Item_Template.xls")
        additionInfo.extend(
                            [
                             header.get('item_code'), header.get('start_date'), header.get('end_date'), 
                             header.get('befor_qty'), header.get('befor_amount'), 
                             header.get('year_qty'), header.get('year_amount'), header.get('year_lave_qty'), header.get('year_lave_amount'),
                             header.get('month_qty'), header.get('month_amount'), header.get('month_lave_qty'), header.get('month_lave_amount'),
                             ]
                            )
        header = [
                 [0, 0, "_".join([kw.get('item_code'), u'库存商品明细账(不包含费用金额)'])],
                 [2, 1, kw.get('date_from')], 
                 [2, 3, kw.get('date_to')], 
                 [6, 6, str(header.get('befor_qty'))], 
                 [6, 7, str(header.get('befor_amount'))], 
                 [7, 0, details, {'border':"*"}], 
                  
                 [8+len(details), 2, u'本月累计'],
                 [9+len(details), 2, u'本年累计'],
                 
                 [9+len(details), 3,str(header.get('year_qty'))], 
                 [9+len(details), 5,str(header.get('year_amount'))], 
                 [9+len(details), 6,str(header.get('year_lave_qty'))], 
                 [9+len(details), 7,str(header.get('year_lave_amount'))],
                 [8+len(details), 3,str(header.get('month_qty'))], 
                 [8+len(details), 5,str(header.get('month_amount'))], 
                 [8+len(details), 6,str(header.get('month_lave_qty'))], 
                 [8+len(details), 7,str(header.get('month_lave_amount'))],
                 ]
                            
        style = {
                "A8:H%s" % str(10+len(details)):{"border":"solid", "borderColor":"black"}
                 }
        bridge = Bridge()
        header = bridge.format(header)
        style  = bridge.format(style)
        bridge.report(templatePath, filename, header, style)
        return serveFile(unicode(filename))
    
    @expose()
    def invoice_without_cost(self, **kw):
        additionInfo=[]
        header, details = self._invoice_without_cost(**kw)
        filename = self._set_file_name()
        templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/Report_Invoice_WithOut_Cost_Template.xls")
        additionInfo.extend([u'已收票未做成本'])
        header = [
                  [5, 0, details],
                  [7 + len(details), 0, 'Total']
                  ]
                            
        style = {
                "E%s" % str(8+len(details)):{'excute':"SUM(""E6:E%s"")" % str(7+len(details))},
                "G%s" % str(8+len(details)):{'excute':"SUM(""G6:G%s"")" % str(7+len(details))},
                "A6:N%s" % str(9+len(details)):{"border":"solid", "borderColor":"black"}
                }
        bridge = Bridge()
        header = bridge.format(header)
        style = bridge.format(style)
        bridge.report(templatePath, filename, header, style)
        return serveFile(unicode(filename))
    
    def _invoice_without_cost(self, **kw):
        result = []
        details = OHead.find_invoice_without_cost(kw.get('date_from', '').strip(), kw.get('date_to', '').strip(), kw.get('item_code', '').strip())
        for detail in details:
            if detail.st_detail_id:
                st_detail = detail.st_detail
                l = [detail.item_no, detail.pi_head.supplier, detail.po_no, detail.invoice_no, detail.base_curr_qty, str(detail.unit_price), detail.base_curr_qty*detail.unit_price, \
                            st_detail.po_date, st_detail.pi_date, st_detail.so_date, st_detail.billing_month, st_detail.kingdee_date, st_detail.so_no, st_detail.customer_code]
                result.append(l)
        return [[], result]
    
    @expose()
    def invoice_with_cost(self, **kw):
        additionInfo=[]
        header , details = self._invoice_with_cost(**kw)
        filename = self._set_file_name()
        templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/Report_Invoice_With_Cost_Template.xls")
        additionInfo.extend([u'已做成本未收票'])
        header = [
                  [5, 0, details],
                  [7+len(details), 0, 'Total']
                  ]
                            
        style = {
                "E%s" % str(8+len(details)):{'excute':"SUM(E6:E%s)" % str(6+len(details))},
                "G%s" % str(8+len(details)):{'excute':"SUM(G6:G%s)" % str(6+len(details))},
                "A6:J%s" % str(9+len(details)):{"border":"solid", "borderColor":"black"}
                }
        
        bridge = Bridge()
        header = bridge.format(header)
        style  = bridge.format(style)
        bridge.report(templatePath, filename, header, style)
        return serveFile(unicode(filename))
    
    def _invoice_with_cost(self, **kw):
        result = []
        details = OHead.invoice_with_cost(kw.get('date_from'), 
                                                  kw.get('date_to'), 
                                                  kw.get('item_code', ' ').strip())
         
        for detail in details:
            if detail.__tablename__ == 'vat_cp_charge':
                continue
            l = [detail.item_no, detail.supplier, detail.po_no, detail.pi_no, detail.base_curr_qty, detail.unit_price, detail.base_curr_qty*detail.unit_price, detail.so_no,\
                  detail.customer, detail.vat_date]
            result.append(l)
        return [[], result]
    
    @expose()
    def export_dzd(self, **kw):
        additionInfo=[]
        head_type=kw.get('head_type', '')
        header , details_data = self._dzd_data(id = kw.get('id'), type = head_type)
        filename= self._set_file_name()
        details = details_data[0]
        fowllow, fowllow1 = 6+len(details), 5+len(details)
        if head_type == 'pi':
            templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/AP_DZD_PI_Template.xls")
            style = {
                "H%s" % fowllow:{'excute':"SUM(H6:H%s)" % fowllow1},
                "J%s" % fowllow:{'excute':"SUM(J6:J%s)" % fowllow1},
                "A6:L%s" % fowllow:{"border":"solid", "borderColor":"black"}
                }
        else:
            templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/AP_DZD_DN_Template.xls")
            style = {
                "I%s" % fowllow:{'excute':"SUM(I6:I%s)" % fowllow1},
                "K%s" % fowllow:{'excute':"SUM(K6:K%s)" % fowllow1},
                "A6:M%s"  % (fowllow + 1):{"border":"solid", "borderColor":"black"}
                }
        
        header = [
                  [5, 0, details],
                  [5+len(details), 6, u"合计"]
                  ]
                    
        bridge = Bridge()
        header = bridge.format(header)
        style = bridge.format(style)
        bridge.report(templatePath, filename, header, style)
        return serveFile(unicode(filename))
        
    def _dzd_data(self, id, type):
        result = []
        st_head = STHead.get(id)
        if type == 'pi':
            st_details = st_head.st_details
            for i in st_details:
                if not i.mpi_id:continue
                if i.type == const.ERP_TYPE_DETAIL:
                    detail = PiDetail.find_details_by_dzd(i.id, 'pi')
                else:
                    detail = PCharge.find_details_by_dzd(i.id, 'pi')
                if not detail:
                    i.p_head = PHead.get(i.mpi_id)
                    pidetail = PiDetail.find_s_head_id_by_category(i.category, i.invoice_no, const.ERP_HEAD_TYPE_ST)
                    i.pi_head_id = pidetail.id
                    i.charge_code = i.item_code
                    i.total = i.item_amount
                    i.st_detail = i
                    detail = i
                result.append(detail)
        else:
            dn_details = st_head.dn_details
            for i in dn_details:
                if not i.msn_id:continue
                if i.type == const.ERP_TYPE_DETAIL:
                    detail = PiDetail.find_details_by_dzd(i.id)
                else:
                    detail = PCharge.find_details_by_dzd(i.id)
                if not detail:
                    i.s_head = SHead.get(i.msn_id)
                    pidetail = PiDetail.find_s_head_id_by_category(i.category, i.other_ref)
                    i.pi_head_id = pidetail.id
                    i.charge_code = i.item_code
                    i.total = i.amount
                    i.note_no = i.number
                    i.invoice_no = i.other_ref
                    i.vat_total = i.amount
                    i.dn_detail = i
                    detail = i
                result.append(detail)           
        return st_head, self._data_parse_data(result, type)
    
    def _data_parse_data(self, data, type):
        datas = {}
        qty, total = 0, 0
        if type == 'pi':
            for i in data:
                p_head = i.p_head
                if not datas.get(p_head.id):
                    datas.update({p_head.id:{'detail':{i.invoice_no:[]},'charge':{i.invoice_no:[]}, 'other_charge':{None:[]}}})
                else:
                    datas_detail = datas[p_head.id]['detail']
                    datas_charge = datas[p_head.id]['charge']
                    datas_other_charge = datas[p_head.id]['other_charge']
                    if not datas_detail.get(i.invoice_no):
                        datas_detail.update({i.invoice_no:[]})
                    if not datas_charge.get(i.invoice_no):
                        datas_charge.update({i.invoice_no:[]})
                    if not datas_other_charge.get(i.invoice_no):
                        datas_other_charge.update({i.invoice_no:[]})
                detail = datas[p_head.id]['detail'][i.invoice_no]
                charge = datas[p_head.id]['charge'][i.invoice_no]
                other_charge = datas[p_head.id]['other_charge'][None]
                
                if i.__tablename__ == 'vat_pi_detail':
                    detail.append([ p_head.dzd, p_head.ref, i.invoice_no, i.po_no, p_head.supplier, p_head.supplier_name, i.item_no,
                                   int(i.qty), i.unit_price, i.item_total, i.st_detail.reconciliation_lot, i.st_detail.issue_date ])
                    qty += int(i.qty)
                    total += i.item_total
                else:
                    if i.pi_head_id:
                        charge.append([ p_head.dzd,  p_head.ref, i.invoice_no, i.po_no, p_head.supplier, p_head.supplier_name, i.charge_code,
                                       None, None, i.total, i.st_detail.reconciliation_lot, i.st_detail.issue_date ])
                    else:
                        other_charge.append([ p_head.dzd,  p_head.ref, i.invoice_no, i.po_no, p_head.supplier, p_head.supplier_name, i.charge_code,
                                       None, None, i.total, i.st_detail.reconciliation_lot, i.st_detail.issue_date ])
                    total += i.total

        else:
            for i in data:
                s_head = i.s_head
                if not datas.get(s_head.id):
                    datas.update({s_head.id:{'detail':{i.note_no:[]},'charge':{i.note_no:[]}, 'other_charge':{None:[]}}})
                else:
                    datas_detail = datas[s_head.id]['detail']
                    datas_charge = datas[s_head.id]['charge']
                    datas_other_charge = datas[s_head.id]['other_charge']
                    if not datas_detail.get(i.note_no):
                        datas_detail.update({i.note_no:[]})
                    if not datas_charge.get(i.note_no):
                        datas_charge.update({i.note_no:[]})
                    if not datas_other_charge.get(i.note_no):
                        datas_other_charge.update({i.note_no:[]})
                detail = datas[s_head.id]['detail'][i.note_no]
                charge = datas[s_head.id]['charge'][i.note_no]
                other_charge = datas[s_head.id]['other_charge'][None]
                if i.__tablename__ == 'vat_pi_detail':
                    detail.append([ s_head.dzd, s_head.ref, i.note_no, i.invoice_no,  i.po_no, s_head.supplier, s_head.supplier_name, i.item_no,
                                  int(i.vat_qty), i.unit_price, i.vat_qty*i.unit_price, i.dn_detail.reconciliation_lot, i.dn_detail.issue_date  ])
                    qty += int(i.vat_qty)
                    total += i.vat_qty*i.unit_price
                else:
                    if i.pi_head_id:
                        charge.append([ s_head.dzd,  s_head.ref, i.note_no, i.invoice_no, i.po_no, s_head.supplier, s_head.supplier_name, i.charge_code,
                                       None, None, i.vat_total, i.dn_detail.reconciliation_lot, i.dn_detail.issue_date])
                    else:
                        other_charge.append([ s_head.dzd,  s_head.ref, i.note_no, i.invoice_no, i.po_no, s_head.supplier, s_head.supplier_name, i.charge_code,
                                       None, None, i.vat_total, i.dn_detail.reconciliation_lot, i.dn_detail.issue_date])
                    total += i.vat_total
        rs = []
        for a, b in datas.iteritems():
            datas_details = b['detail']
            datas_charges = b['charge']
            datas_other_charge = b['other_charge'][None]
            for c, d in datas_details.iteritems():
                rs.extend(d)
                rs.extend(datas_charges.get(c, []))
            rs.extend(datas_other_charge)
        return rs, qty, total
    
    @expose()
    def export_cst(self, **kw):
        additionInfo=[]
        head_type = kw.get('head_type', '')
        header, thead_data, details = self._data_parse_cst(id = kw.get('id'), head_type = head_type)
        filename= self._set_file_name()
        customer=Customer.get(**{'customer_code':header.customer_code})
        if customer:
            additionInfo =[customer.cust_code,
                          customer.cust_name,
                          customer.cust_short_name,
                          customer.tel_no,
                          customer.fax_no,
                          customer.contact_sales,
                          customer.cust_short_name
                          ]
        else:
            additionInfo = ['']*6
        username=request.identity['repoze.who.userid']
        if head_type == const.ERP_HEAD_TYPE_CST:
            additionInfo.append(''.join(['(CST-', header.status, ')']))
        else:
            additionInfo.append(''.join(['(CCN-', header.status, ')']))
        templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/CST_Account_Template.xls")
        
        additionInfo.extend([
                             "Venus", 
                             "Jeffy.ling@r-pac.com.cn", 
                             "0755-25317037/25317075", 
                             "0755-25317137/7175"])
        header = [
                  [3, 1, additionInfo[0] if len(additionInfo)>1 else ''],
                  [4, 1, additionInfo[3] if len(additionInfo)>6 else ''],
                  [4, 5, additionInfo[4] if len(additionInfo)>6 else ''],
                  [5, 1, additionInfo[5] if len(additionInfo)>6 else ''],
                  [0, 2, u'美皇贸易（深圳）有限公司'+additionInfo[7] if len(additionInfo)>6 else ''],
                  [12,0, thead_data],
                  [12 + len(thead_data), 1, 'Total'],
                  [14 + len(thead_data), 0, u'核对人签名：'],
                  [14 + len(thead_data), 10, u'单位公章：'],
                  [15 + len(thead_data), 0, u'日期：'],
                  [16 + len(thead_data), 0, u'请在核对后签名盖章并传真到美皇贸易（深圳）有限公司'],
                  [17 + len(thead_data), 0, u'如有问题，请联系以下：'],
                  [18 + len(thead_data), 0, u'Tel:'+additionInfo[10] if additionInfo[10] else u'Tel:'],
                  [18 + len(thead_data), 5, u'Fax:'+additionInfo[11] if additionInfo[11] else u'Fax:'],
                  [19 + len(thead_data), 0, u'Email:'+additionInfo[9] if additionInfo[9] else u'Email:'],
                  [20 + len(thead_data), 0, u'联系人：'+additionInfo[8] if additionInfo[8] else u'联系人：'],
                  [21 + len(thead_data), 0, [["SO#","PO#","Supplier Short Name", "VAT号码", "designation","Set Item","PO Qty","币别","汇率","未税单价","未税金额",'remark']]],
                  [22 + len(thead_data), 0, details],
                  [22 + len(thead_data) + len(details), 1, "Total"],
                  ]
        
        follow, fowllow0, fowllow1, fowllow2 = 12 + len(thead_data), 13+len(thead_data), 21 + len(thead_data), 22 + len(thead_data) + len(details)
        style = {
                "A%s" % str(15 + len(thead_data)):{'fontBold':'bold', 'fontColor':'black', 'fontSize':'13'},
                "K%s" % str(15 + len(thead_data)):{'fontBold':'bold', 'fontColor':'black', 'fontSize':'13'},
                 
                "G%s" % fowllow0:{'excute':"SUM(G%s:G%s)" % (12, follow)},
                "K%s" % fowllow0:{'excute':"SUM(K%s:K%s)" % (12, follow)},
                "M%s" % fowllow0:{'excute':"SUM(M%s:M%s)" % (12, follow)},
                "N%s" % fowllow0:{'excute':"SUM(N%s:N%s)" % (12, follow)},
                "L%s" % fowllow0:{'excute':"SUM(L%s:L%s)" % (12, follow)},
                "O%s" % fowllow0:{'excute':"SUM(O%s:O%s)" % (12, follow)},
                "P%s" % fowllow0:{'excute':"SUM(P%s:P%s)" % (12, follow)},
                "Q%s" % fowllow0:{'excute':"SUM(Q%s:Q%s)" % (12, follow)},
                "G%s" % str(fowllow2+1):{'excute':"SUM(G%s:G%s)" % (fowllow1, fowllow2)},
                "K%s" % str(fowllow2+1):{'excute':"SUM(K%s:K%s)" % (fowllow1, fowllow2)},
                "A12:Q%s" %  str(fowllow0 + 1):{"border":"solid", "borderColor":"black"},
                "A%s:L%s" % (str(fowllow1 + 1), str(fowllow2+2)):{"border":"solid", "borderColor":"black"}
                }
        bridge = Bridge()
        header = bridge.format(header)
        style = bridge.format(style)
        bridge.report(templatePath, filename, header, style)
        
        return serveFile(unicode(filename))
            
    def _data_parse_cst(self, id, head_type):
        if id:
            if head_type == const.ERP_HEAD_TYPE_CST:
                head  = OHead.get(id)
                thead = THead.get(head.thead_id)
                header, thead_data = self._report_data('tHead', thead.id)
            else:
                head  = NHead.get(id)
                chead = CHead.get(head.chead_id)
                header, thead_data = self._report_data('cHead', chead.id)
        details, details_dict = [], {}
        for co_head in head.co_heads:
            for co_detail in co_head.co_details:
                cpdetails = co_detail.cp_details
                for det in cpdetails:
                    key = "%s_%s_%s" % (det.po_no, det.sales_contract_no, det.item_no)
                    if details_dict.get(key):
                        curr_qty = details_dict[key][6]+ det.po_qty
                        curr_amount = details_dict[key][10] + det.po_qty*det.unit_price
                    else:
                        curr_qty = det.po_qty
                        curr_amount = det.po_qty * det.unit_price
                    details_dict.update({key:[
                                              det.sales_contract_no,
                                              det.po_no,
                                              det.supplier_name,
                                              "",
                                              det.ae,
                                              det.item_no,
                                              curr_qty,
                                              det.currency,
                                              str(det.exchange_rate),
                                              str(det.unit_price),
                                              curr_amount,
                                              ""
                                              ]})
        charges_dict = {}
        other_charge_list = []
        charges = head.cp_charges
        for charge in charges:
            app_list = [
              charge.so_no,
              charge.po_no,
              charge.supplier_name,
              "",
              charge.ae,
              charge.charge_code,
              "",
              charge.currency,
              str(charge.exchange_rate),
              "",
              charge.total if charge.pi_no else charge.po_total,
              ""
              ]
            if charge.po_no  and  charge.so_no:
                key = "%s_%s_%s" % (charge.po_no, charge.so_no, charge.charge_code)
                if charges_dict.get(key):
                    charges_dict[key][10] += charge.po_total
                else:
                    charges_dict.update({key:app_list})
            else:
                other_charge_list.append(app_list)
        charges = charges_dict.values()
        return header, thead_data, self._sort_data(details_dict.values(), charges, other_charge_list)
    
    def _sort_data(self, details, charges, other_charges):
        rs, result = {}, []
        for det in details:
            det_key = "%s_%s" % (det[0], det[1])
            if rs.get(det_key):
                rs[det_key].append(det)
            else:  
                rs.update({det_key:[det]})
 
        for cha in charges:
            cha_key = "%s_%s" % (cha[0], cha[1])
 
            if rs.get(cha_key):
                rs[cha_key].append(cha)
            else:
                rs.update({cha_key:[cha]}) 
        for oth in other_charges:
            supplier = oth[2]
            for rs_key in rs.keys():
                if supplier and supplier in rs_key:
                    break
            rs[rs_key].append(oth)
 
        for key, value in rs.iteritems():
            key = key[0: key.index("_")]
            index = 0
            for index, res in enumerate(result):
                if key == res[0]:
                    break
            for c, i in enumerate(value):
                result.insert(index + c + 1, i)
        return result
        
    @expose()
    def export(self, **kw):
        try:
            filename = self._export(** kw)
            return serveFile(unicode(filename))
        except:
            traceback.print_exc()

    def _export(self, ** kw):
        additionInfo=[]
        head_type = kw.get('head_type', '')
        header, detail_datas = self._report_data(id=kw.get('id', ''), type=head_type)
        header.export_time=dt.now()
        DBSession.add(header)
        if head_type in ['tHead', 'cHead']:
            user = request.identity["user"]
            customer=Customer.get(**{'customer_code':header.customer_code})
            if customer:
                additionInfo=[customer.cust_code,
                              customer.cust_name,
                              customer.cust_short_name,
                              user.phone,
                              user.fax,
                              customer.contact_sales
                              ]
            else:
                additionInfo=['']*6
        elif head_type in ['pHead', 'sHead']:
            additionInfo=[header.supplier_short_name]

        additionInfo.append(header.ref)

        if head_type=='tHead' and header.head_type=='SI':
            additionInfo.append(''.join(['(MSI-', header.status, ')']))
        elif head_type=='tHead' and header.head_type=='SO':
            additionInfo.append(''.join(['(MSO-', header.status, ')']))
        elif head_type=='cHead':
            additionInfo.append(''.join(['(MCN-', header.status, ')']))
        elif head_type=='pHead' and header.head_type=='P_PI':
            additionInfo.append(''.join(['(MPI-', header.status, ')']))
        elif head_type=='sHead' and header.head_type=='S_PI':
            additionInfo.append(''.join(['(MSN-', header.status, ')']))

        current=dt.now()
        dateStr=current.today().strftime("%Y%m%d")
        fileDir=os.path.join(os.path.abspath(os.path.curdir), "report_download", "%s"%dateStr)

        if not os.path.exists(fileDir): os.makedirs(fileDir)
        
        timeStr = header.create_time.strftime("%Y%m%d%H%M%S")
        rn=random.randint(0, 10000)
        username=request.identity['repoze.who.userid']
        filename=os.path.join(fileDir, "%s_%s_%d.xls"%(username, timeStr, rn))
        #filename=os.path.join(fileDir, "%s.xls" % customer.cust_short_name)
        details = self._format_value(detail_datas)
        if head_type in ['cHead', 'tHead']:
            if head_type == 'tHead' and kw.get('export'):
                filename=os.path.join(fileDir, "%s.xls" % customer.cust_short_name)
            templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/AR_account_Template.xls")

            additionInfo.extend([username, request.identity["user"].email_address, request.identity["user"].phone, request.identity["user"].fax])
            if const.COMPANY_CODE_SZ in getCompanyCode():
                header_title = u'美皇贸易（深圳）有限公司'+additionInfo[7] if len(additionInfo)>6 else ''
                header_contact = u'请在核对后签名盖章并传真到美皇贸易（深圳）有限公司'
            else:
                header_title = u'艾伯克包装品（深圳）有限公司'+additionInfo[7] if len(additionInfo)>6 else ''
                header_contact = u'请在核对后签名盖章并传真到艾伯克包装品（深圳）有限公司'
            datas = [
                  [3, 1, additionInfo[2] if len(additionInfo)>1 else ''],
                  [4, 1, additionInfo[0] if len(additionInfo)>6 else ''],
                  [5, 8, additionInfo[5] if len(additionInfo)>6 else ''],
                  [5, 1, additionInfo[3] if len(additionInfo)>6 else ''],
                  [5, 5, additionInfo[4] if len(additionInfo)>6 else ''],
                  [0, 2, header_title],
                  [12,0, details],
                  [12 + len(details), 1, 'Total'],
                  [14 + len(details), 0, u'核对人签名：'],
                  [14 + len(details), 10, u'单位公章：'],
                  [15 + len(details), 0, u'日期：'],
                  [16 + len(details), 0, header_contact],
                  [17 + len(details), 0, u'如有问题，请联系以下：'],
                  [18 + len(details), 0, u'Tel:'+additionInfo[10] if additionInfo[10] else u'Tel:'],
                  [18 + len(details), 5, u'Fax:'+additionInfo[11] if additionInfo[11] else u'Fax:'],
                  [19 + len(details), 0, u'Email:'+additionInfo[9] if additionInfo[9] else u'Email:'],
                  [20 + len(details), 0, u'联系人：'+additionInfo[8] if additionInfo[8] else u'联系人：'],
                  ]
        
            follow, fowllow0, fowllow1 = 12 + len(details), 13+len(details), 21 + len(details)
            style = {
                    "A%s" % str(15 + len(details)):{'fontBold':'bold', 'fontColor':'black', 'fontSize':'13'},
                    "K%s" % str(15 + len(details)):{'fontBold':'bold', 'fontColor':'black', 'fontSize': '13'},
                    "H%s" % fowllow0:{'excute':"SUM(H%s:H%s)" % (12, follow)},
                    "L%s" % fowllow0:{'excute':"SUM(L%s:L%s)" % (12, follow)},
                    "N%s" % fowllow0:{'excute':"SUM(N%s:N%s)" % (12, follow)},
                    "O%s" % fowllow0:{'excute':"SUM(O%s:O%s)" % (12, follow)},
                    "M%s" % fowllow0:{'excute':"SUM(M%s:M%s)" % (12, follow)},
                    "P%s" % fowllow0:{'excute':"SUM(P%s:P%s)" % (12, follow)},
                    "Q%s" % fowllow0:{'excute':"SUM(Q%s:Q%s)" % (12, follow)},
                    "R%s" % fowllow0:{'excute':"SUM(R%s:R%s)" % (12, follow)},
                    "A12:R%s" %  str(fowllow0 + 1):{"border":"solid", "borderColor":"black", "align":"center"},
                    "sheet":{0:header.ref}
                    }
        elif head_type in ['pHead', 'sHead']:
            templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/AP_account_Template.xls")
            follow0, follow = 12 + len(details), 11 + len(details)
            datas = [
                      [3, 1, additionInfo[0] if len(additionInfo)>1 else ''],
                      [11, 0, details],
                      ["A%s" % follow0, 'Total']
                      ]
            style  = {
                      "E%s" % follow0:{'excute':"SUM(E%s:E%s)" % (12, follow)},
                      "H%s" % follow0:{'excute':"SUM(H%s:H%s)" % (12, follow)},
                      "J%s" % follow0:{'excute':"SUM(J%s:J%s)" % (12, follow)},
                      "K%s" % follow0:{'excute':"SUM(K%s:K%s)" % (12, follow)},
                      "A%s:K%s" % (11, str(13 + len(details))):{"border":"solid", "borderColor":"black"}
                      }
        bridge = Bridge()
        datas = bridge.format(datas)
        style = bridge.format(style)
        bridge.report(templatePath, filename, datas, style)
        
        exportName = "%s_%s_%d.xls" %(username, timeStr, rn)
        remark = {
                  "action_type":"EXPORT",
                  "remark":"Export %s " % exportName
                  }
        
        if head_type=='tHead':
            remark['t_head_id'] = header.id
        elif head_type=='cHead':
            remark['c_head_id'] = header.id
        elif head_type=='pHead':
            remark['p_head_id'] = header.id
        elif head_type=='sHead':
            remark['s_head_id'] = header.id
            
        ARLog.insert(** remark )
        return filename

    def _format_value(self, datas):
        for data_list in datas:
            for item in data_list:
                if item and isinstance(item, basestring):
                    pass
                elif item and isinstance(item, dt):
                    item=Date2Text(item).decode("utf8")
        return datas

    def _report_data(self, type, id):
        if type=='tHead':
            header=THead.get(id)
        elif type=='cHead':
            header=CHead.get(id)
        elif type=='pHead':
            header=PHead.get(id)
        elif type=='sHead':
            header=SHead.get(id)
        detail_datas=self._generate_data(header=header,
                                         type=header.head_type,
                                         head_type=type
                                         )
        return (header, detail_datas)
    

    def _generate_data(self, header, type, head_type):
        detail_datas=[]
        header_charges=[]
        
        if getattr(header, 'charges', '') != '':
            header_charges=[charge for charge in header.charges if charge.active==0]
        if getattr(header, 'pcharges', '') != '':
            header_charges=[charge for charge in header.pcharges if charge.active==0]
        ref=header.ref[:3]
        if type=='SI':
            for si_info in header.si_heads:
                dns = DN.find_dn(si_info.sc_no)
                si_info.create_date = si_info.create_date.strftime("%Y-%m-%d")
                active_charges=[charge for charge in si_info.charges if charge.active==0]
                for item_detail in si_info.si_details:
                    fax_unit_price=item_detail.unit_price*Decimal('1.17')
                    total=item_detail.vat_qty*fax_unit_price
                    no_fax_unit_price=item_detail.unit_price
                    no_fax_total=item_detail.vat_qty*no_fax_unit_price
                    fax=no_fax_total*Decimal('0.17')
                    total_sum=fax+no_fax_total

                    if item_detail.vat_qty!=0:
                        detail_datas.append([item_detail.invoice_no,
                                             item_detail.si_head.cust_po_no,
                                             ','.join(dns) if len(dns) > 0 else '',
                                             si_info.create_date,
                                             si_info.so_sales_contact,
                                             item_detail.si_head.sc_no,
                                             item_detail.item_no,
                                             item_detail.vat_qty if ref!='MCN' else-1*item_detail.vat_qty,
                                             item_detail.desc_zh,
                                             item_detail.unit,
                                             item_detail.si_head.currency,
                                             fax_unit_price,
                                             '',
                                             total if ref!='MCN' else-1*total,
                                             no_fax_unit_price,
                                             no_fax_total if ref!='MCN' else-1*no_fax_total,
                                             fax if ref!='MCN' else-1*fax,
                                             total_sum if ref!='MCN' else-1*total_sum
                                             ])
                    if item_detail==si_info.si_details[-1]:
                        for charge in active_charges:
                            if (charge.t_head or charge.c_head) and charge.si_head and charge.vat_total:
                                charge_no_fax_total = charge.vat_total*Decimal('1.17')
                                detail_datas.append([item_detail.invoice_no,
                                                     item_detail.si_head.cust_po_no,
                                                     None,
                                                     None,
                                                     si_info.so_sales_contact,
                                                     item_detail.si_head.sc_no,
                                                     None,
                                                     None,
                                                     charge.charge_code,
                                                     None,
                                                     item_detail.si_head.currency,
                                                     None,
                                                     charge.vat_total if ref!='MCN' else-1*charge.vat_total,
                                                     charge_no_fax_total if ref!='MCN' else -1*charge_no_fax_total,
                                                     None,
                                                     charge.vat_total if ref!='MCN' else -1*charge.vat_total,
                                                     charge_no_fax_total - charge.vat_total if ref!='MCN' else -1*(charge_no_fax_total - charge.vat_total),
                                                     charge_no_fax_total if ref!='MCN' else-1*charge_no_fax_total
                                                     ])
        elif type=='SO':
            for so_info in header.so_heads:
                dns = DN.find_dn(so_info.sales_contract_no)
                so_info.create_date = so_info.create_date.strftime("%Y-%m-%d")
                active_charges=[charge for charge in so_info.charges if charge.active==0]
                for item_detail in so_info.so_details:
                    fax_unit_price=item_detail.unit_price*Decimal('1.17')
                    total=item_detail.vat_qty*fax_unit_price
                    no_fax_unit_price=item_detail.unit_price
                    no_fax_total=item_detail.vat_qty*no_fax_unit_price
                    fax=no_fax_total*Decimal('0.17')
                    total_sum=fax+no_fax_total

                    if item_detail.vat_qty!=0:
                        detail_datas.append([None,
                                             item_detail.so_head.cust_po_no,
                                             ','.join(dns) if len(dns) > 0 else '',
                                             so_info.create_date,
                                             so_info.ae,
                                             item_detail.sales_contract_no,
                                             item_detail.item_no,
                                             item_detail.vat_qty if ref!='MCN' else-1*item_detail.vat_qty,
                                             item_detail.desc_zh,
                                             item_detail.unit,
                                             item_detail.so_head.currency,
                                             fax_unit_price,
                                             '',
                                             total if ref!='MCN' else-1*total,
                                             no_fax_unit_price,
                                             no_fax_total if ref!='MCN' else-1*no_fax_total,
                                             fax if ref!='MCN' else-1*fax,
                                             total_sum if ref!='MCN' else-1*total_sum
                                             ])

                    if item_detail==so_info.so_details[-1]:
                        for charge in active_charges:
                            if (charge.t_head or charge.c_head) and charge.so_head and charge.vat_total:
                                charge_no_fax_total = charge.vat_total*Decimal('1.17')
                                detail_datas.append([None,
                                                     item_detail.so_head.cust_po_no,
                                                     None,
                                                     None,
                                                     so_info.ae,
                                                     item_detail.so_head.sales_contract_no,
                                                     None,
                                                     None,
                                                     charge.charge_code,
                                                     None,
                                                     item_detail.so_head.currency,
                                                     None,
                                                     charge.vat_total if ref!='MCN' else-1*charge.vat_total,
                                                     charge_no_fax_total if ref!='MCN' else -1*charge_no_fax_total,
                                                     None,
                                                     charge.vat_total if ref!='MCN' else -1*charge.vat_total,
                                                     charge_no_fax_total - charge.vat_total if ref!='MCN' else -1*(charge_no_fax_total - charge.vat_total),
                                                     charge_no_fax_total if ref!='MCN' else-1*charge_no_fax_total
                                                     ])
        elif type in ['P_PI', 'S_PI']:
            item_origin_list = []
            po_list = []
            item_list = []
            active_charges = []
            
            for pi_info in header.pi_heads:
                for charge in pi_info.pcharges:
                    if not charge.charge_code in const.CHARGE_CODES.get(u'\u589e\u503c\u7a0e'):
                        active_charges.append(charge)
                    
                for item_detail in pi_info.pi_details:
                    item_origin_list.append([item_detail.invoice_no,
                                             item_detail.po_no,
                                             item_detail.desc_zh,
                                             item_detail.item_no,
                                             item_detail.vat_qty,
                                             item_detail.unit,
                                             item_detail.pi_head.currency,
                                             None,
                                             float(item_detail.unit_price),
                                             ])
                                
                    po_list.append(item_detail.po_no)
                    item_list.append(item_detail.item_no)
            
            po_set = set(po_list)
            item_set = set(item_list)
            
            for po_no in po_set:
                item_temp_list = []
                
                for item_detail in item_origin_list:
                    if po_no == item_detail[1]:
                        item_temp_list.append(item_detail)
                
                for item in item_set:
                    item_detail_temp_list = []
                    item_total_qty = 0
                    
                    for item_detail in item_temp_list:
                        if item_detail in item_origin_list:
                            item_origin_list.remove(item_detail)
                        
                        if item == item_detail[3]:
                            item_total_qty += item_detail[4]
                            item_detail_temp_list.append(item_detail)
                    
                    for tmp_item in item_detail_temp_list:
                        tmp_item[4] = item_total_qty
                    
                    if len(item_detail_temp_list) > 0:
                        item_detail_temp_list[0].append(float(item_detail_temp_list[0][4] * item_detail_temp_list[0][8]))
                        item_detail_temp_list[0].append(float(item_detail_temp_list[0][4] * item_detail_temp_list[0][8]))
                        detail_datas.append(item_detail_temp_list[0])
                
                for charge in active_charges:
                    if len(detail_datas) > 0  and charge.vat_total:
                        detail_datas.append([None,
                                             None,
                                             charge.charge_code,
                                             None,
                                             None,
                                             None,
                                             None,
                                             charge.vat_total,
                                             None,
                                             None,
                                             charge.vat_total
                                             ])
        
        item=detail_datas[-1] if detail_datas else None
        type_list=[[CHARGE_TYPE_T_ERP, CHARGE_TYPE_T_HAND],
                   [CHARGE_TYPE_C_ERP, CHARGE_TYPE_C_HAND],
                   [CHARGE_TYPE_P_MAN, CHARGE_TYPE_P_ERP, CHARGE_TYPE_S_ERP],
                   ]

        if ref in ['MSI', 'MSO']:
            charge_type=type_list[0]
        elif ref=='MCN':
            charge_type=type_list[1]
        else:
            charge_type=type_list[2]

        if type in ['SI', 'SO']:
            for charge in header_charges:
                if charge.type in charge_type and int(charge.vat_total)!=0:
                    other_charge_no_fax_total = charge.vat_total*Decimal('1.17')
                    detail_datas.append([None,
                                         None,
                                         None,
                                         None,
                                         None,
                                         None,
                                         None,
                                         None,
                                         charge.charge_code if item else None,
                                         None,
                                         item[9] if item else None,
                                         None,
                                         (ref=='MCN' and item) and-1*charge.vat_total or ((item is None) and None or charge.vat_total),
                                         (ref=='MCN' and item) and-1*other_charge_no_fax_total or ((item is None) and None or other_charge_no_fax_total),
                                         None,
                                         (ref=='MCN' and item) and-1*charge.vat_total or ((item is None) and None or charge.vat_total),
                                         (ref=='MCN' and item) and-1*(other_charge_no_fax_total - charge.vat_total) or \
                                            ((item is None) and None or (other_charge_no_fax_total - charge.vat_total)),
                                         (ref=='MCN' and item) and-1*other_charge_no_fax_total or ((item is None) and None or other_charge_no_fax_total)
                                         ])
        elif type in ['P_PI', 'S_PI']:
            for charge in header_charges:
                if charge.type in charge_type and int(charge.vat_total)!=0:
                    detail_datas.append([None,
                                         None,
                                         charge.charge_code,
                                         None,
                                         None,
                                         None,
                                         None,
                                         charge.vat_total,
                                         None,
                                         None,
                                         charge.vat_total
                                         ])
        
        return detail_datas

    def _set_file_name(self):
        current=dt.now()
        dateStr=current.today().strftime("%Y%m%d")
        fileDir=os.path.join(os.path.abspath(os.path.curdir), "report_download", "%s"%dateStr)
        if not os.path.exists(fileDir): os.makedirs(fileDir)
        timeStr=current.time().strftime("%H%M%S")
        rn=random.randint(0, 10000)
        username=request.identity['repoze.who.userid']
        return os.path.join(fileDir, "%s_%s_%d.xls"%(username, timeStr, rn))
    
    @expose()
    def export_mpi(self, **kw):
        st_head = STHead.get(kw.get('id'))
        st_details = st_head.st_details
        data = []
        for st_detail in st_details:
            pi_details, pcharges  =  st_detail.pi_details, st_detail.pcharges
            print len(pi_details), len(pcharges)
            for pi_detail in pi_details:
                data.append(
                            [pi_detail.invoice_no,
                             pi_detail.po_no,
                             pi_detail.desc_zh,
                             pi_detail.item_no,
                             pi_detail.vat_qty,
                             pi_detail.unit,
                             pi_detail.pi_head.currency,
                             None,
                             float(pi_detail.unit_price),
                             float(pi_detail.unit_price) * pi_detail.vat_qty,
                             float(pi_detail.unit_price) * pi_detail.vat_qty * float('1.17')
                             ]
                            )
            
            for pcharge in pcharges:
                data.append(
                            [None,
                             None,
                             pcharge.charge_code,
                             None,
                             None,
                             None,
                             None,
                             pcharge.vat_total,
                             None,
                             None,
                             pcharge.vat_total
                             ])
        additionInfo=[]
        filename = self._set_file_name()
        templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/AP_DZD_MPI_Template.xls")
        header = [
                  [10, 0, data],
                  ]
        style = {
                "A%s:K%s" % (str(10), str(10+len(data))):{"border":"solid", "borderColor":"black"}
                }
        bridge = Bridge()
        header = bridge.format(header)
        style = bridge.format(style)
        bridge.report(templatePath, filename, header, style)
        return serveFile(unicode(filename))
            
    
    @expose()
    def export_msn(self, **kw):
        st_head = STHead.get(kw.get('id'))
        dn_details = st_head.dn_details
        data = []
        for dn_detail in dn_details:
            pi_details, pcharges = dn_detail.pi_details, dn_detail.pcharges
            for pi_detail in pi_details:
                data.append(
                            [pi_detail.invoice_no,
                             pi_detail.po_no,
                             pi_detail.desc_zh,
                             pi_detail.item_no,
                             pi_detail.vat_qty,
                             pi_detail.unit,
                             pi_detail.pi_head.currency,
                             None,
                             float(pi_detail.unit_price),
                             float(pi_detail.unit_price) * pi_detail.vat_qty,
                             float(pi_detail.unit_price) * pi_detail.vat_qty * float('1.17')
                             ])
            for pcharge in pcharges:
                data.append(
                            [None,
                             None,
                             pcharge.charge_code,
                             None,
                             None,
                             None,
                             None,
                             pcharge.vat_total,
                             None,
                             None,
                             pcharge.vat_total
                             ])
        additionInfo=[]
        filename = self._set_file_name()
        templatePath=os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/AP_DZD_MPI_Template.xls")
        header = [
                  [10, 0, data],
                  ]
        style = {
                "A%s:K%s" % (str(10), str(10+len(data))):{"border":"solid", "borderColor":"black"}
                }
        bridge = Bridge()
        header = bridge.format(header)
        style = bridge.format(style)
        bridge.report(templatePath, filename, header, style)
        return serveFile(unicode(filename))
      
    @expose()
    def export_variance(self, **kw):
        try:
            ou=self._set_file_name()
            result = []
            variances = Variance.find()
            po_qty, with_out_amount, change_with_out_amount, variance_amount = 0, 0, 0, 0
            for variance in variances:
                if variance.variance_amount == 0:
                    continue
                if variance.po_qty:
                    po_qty += int(variance.po_qty) 
                with_out_amount += variance.with_out_amount
                change_with_out_amount += variance.change_with_out_amount
                variance_amount += variance.variance_amount
                d = [
                    variance.so_no, variance.po_no, variance.supplier_short_name, variance.designation, variance.item_no, variance.po_qty,
                    variance.currency, variance.exchange_rate, variance.with_out_price, variance.with_out_amount,
                    variance.billing_month, variance.change_project, variance.change_with_out_price, variance.change_with_out_amount, variance.variance_amount
                    ]
                result.append(d)
            im = os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/COST_VARIANCE_Template.xls")
            header = [
                      [2, 0,  result],
                      [2+len(result), 0, 'Total'],
                      [2+len(result), 5,  po_qty],
                      [2+len(result), 9,  with_out_amount],
                      [2+len(result), 13, change_with_out_amount],
                      [2+len(result), 14, variance_amount],
                      ]
            style = {
                    "A%s:O%s" % (3, str(3+len(result))):{"border":"solid", "borderColor":"black"}
                    }
            bridge = Bridge()
            header = bridge.format(header)
            style = bridge.format(style)
            bridge.report(im, ou, header, style)
            return serveFile(unicode(ou))
        except:
            traceback.print_exc()
            
       
    @expose()
    def export_ar_all(self, **kw):
        try:
            myzip = self._set_file_name().replace('xls', 'zip')
            f = zipfile.ZipFile(myzip, 'w')
            ids = kw.get('ids', '').split(',')
            for id in ids:
                filename = self._export(**{
                                           'id':id, 
                                           'head_type':'tHead', 
                                           'export':'all'
                                        })
                path, ext = os.path.split(filename)
                f.write(filename, ext.encode('gbk'))
            f.close()
            return serveFile(unicode(myzip))
        except:
            traceback.print_exc()
            
    @expose()
    def export_ar_one(self, **kw):
        try:
            theads, details, result = None, [], []
            customer_code, invoice_no, sales_contract_no, rec_month, payment_status, status, vat_date_from, vat_date_to, create_date_from, create_date_to = \
                (kw.get(i, '').strip() for i in ['customer_code', 'invoice_no', 'sales_contract_no', 'rec_month', 'payment_status', 'status', 'vat_date_from', 'vat_date_to', 'create_date_from', 'create_date_to'])
            
            if (customer_code or rec_month or payment_status or status or vat_date_from or vat_date_to or create_date_from or create_date_to) or len([i for i in kw.values() if i == '']) == len(kw):
                theads = THead.find_details_by_keys(customer_code, rec_month, payment_status, status, vat_date_from, vat_date_to, create_date_from, create_date_to)
                if theads and len(theads) > 0:
                    for thead in theads:
                        sidetails = thead.si_details
                        sodetails = thead.so_details
                        charges   = thead.charges
                        if invoice_no:
                            for sidetail in sidetails:
                                if sidetail.invoice_no == invoice_no:
                                    details.append(sidetail)
                        else:
                            details.extend(sidetails)
                        if sales_contract_no:
                            for sodetail in sodetails:
                                if sodetail.sales_contract_no == sales_contract_no:
                                    details.append(sodetail)
                        else:
                            details.extend(sodetails)
                        details.extend(charges)
            else:
                if invoice_no:
                    sidetails = [i for i in SiDetail.get_details(invoice_no) if not i.c_head_id]
                    for sidetail in sidetails:
                        if sidetail not in details:
                            details.append(sidetail)
                    theads = list(set([i.t_head for i in sidetails]))
                    for thead in theads:
                        for charge in thead.charges:
                            if charge not in details:
                                details.append(charge)
                    related_thead = THead.find_mso(invoice_no)
                    if related_thead:
                        si_head = SI.get(invoice_no)
                        sodetails = related_thead.so_details
                        for sodetail in sodetails:
                            if si_head.sc_no and sodetail.sales_contract_no == si_head.sc_no:
                                if sodetail not in details:
                                    sodetail.invoice_no = invoice_no
                                    details.append(sodetail)
                        charges = related_thead.charges
                        for charge in charges:
                            if si_head.sc_no and charge.sales_contract_no == si_head.sc_no:
                                if charge not in details:
                                    charge.invoice_no = invoice_no
                                    details.append(charge)
                            if not charge.sales_contract_no and not charge.invoice_no:
                                if charge not in details:
                                    details.append(charge)
                    
                if sales_contract_no:
                    sodetails = [i for i in SoDetail.get_details(sales_contract_no) if not i.c_head_id]
                    sidetails = [i for i in SiDetail.get_details_by_so(sales_contract_no) if not i.c_head_id]
                    for sodetail in sodetails:
                        if sodetail not in details:
                            details.append(sodetail)
                    theads = list(set([i.t_head for i in sodetails]))
                    for thead in theads:
                        for charge in thead.charges:
                            if charge not in details:
                                details.append(charge)
                    for sidetail in sidetails:
                        if sidetail not in details:
                            details.append(sidetail)
                    theads = list(set([i.t_head for i in sidetails]))
                    for thead in theads:
                        for charge in thead.charges:
                            if charge not in details:
                                details.append(charge)
                    
            for detail in details:
                shead, desc_zh = None, None
                thead = detail.t_head
                if hasattr(detail, 'si_head_id'):
                    shead = detail.si_head
                    if hasattr(detail, 'desc_zh') or hasattr(detail, 'item_desc'):
                        desc_zh = detail.desc_zh if detail.desc_zh else detail.item_desc
                elif hasattr(detail, 'so_head_id'):
                    shead = detail.so_head
                    if hasattr(detail, 'desc_zh') or hasattr(detail, 'description'): 
                        desc_zh = detail.desc_zh if hasattr(detail, 'desc_zh') and detail.desc_zh else detail.description
                if shead:
                    create_date = shead.create_date
                result.append([
                               thead.customer_code,
                               thead.customer_name,
                               thead.customer_short_name,
                               thead.ref,
                               thead.status,
                               thead.vat_no,
                               thead.vat_date.strftime("%Y-%m-%d") if thead.vat_date else '',
                               detail.sales_contract_no if hasattr(detail, 'sales_contract_no') else detail.sc_no,
                               detail.invoice_no,
                               detail.charge_code if hasattr(detail, 'charge_code') else desc_zh,
                               shead.currency if shead else '',
                               detail.vat_qty*detail.unit_price*Decimal(1+const.TAX_PERCENTAGE) if hasattr(detail, 'vat_qty') else detail.vat_total*Decimal(1+const.TAX_PERCENTAGE),
                               thead.rec_month,
                               thead.payment_remark
                               ])
            ou=self._set_file_name()
            im = os.path.join(os.path.abspath(os.path.curdir), "report_download/TEMPLATES/AR_acount_list_Template.xls")
            header = [
                      ["A4", result],
                      ]
            style = {
                    "A%s:N%s" % (4, str(4+len(result))):{"border":"solid", "borderColor":"black"}
                    }
            bridge = Bridge()
            header = bridge.format(header)
            style = bridge.format(style)
            bridge.report(im, ou, header, style)
            return serveFile(unicode(ou))
        except:
            traceback.print_exc()
         
    