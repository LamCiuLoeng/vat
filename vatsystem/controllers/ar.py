# -*- coding: utf-8 -*-
import copy
import traceback
import datetime
import transaction
from repoze.what import authorize
from tg import expose
from tg import flash
from tg import override_template
from tg import redirect
from tg import request
from vatsystem.lib.base import BaseController
from vatsystem.model import *
from vatsystem.model.erp import getOnlyVatNo,_fetch_sql_to_dict,_check_cn_rewrite_charges,Decimal,merge
from vatsystem.util import const
from vatsystem.util.common import *
from vatsystem.util.excel_helper import *
from vatsystem.widgets.ar import *

__all__ = ["ARController"]

class ARController(BaseController):
    
    allow_only = authorize.has_permission('ar')
    @expose('vatsystem.templates.ar.index')
    @tabFocus(tab_type='main')
    def index(self, ** kw):
        collections = [[], 1, 1]
        viewPager, cust, display = 1, 0, 0
        if kw.get("viewPager"):viewPager = kw.get("viewPager")
        if kw.get("customer_code") or kw.get("customer_name"):
            cust = 1
        if kw.get('type') == const.SEARCH_TYPE_SI:
            collections = SI.find( ** kw)
            override_template(self.index, 'mako:vatsystem.templates.ar.list_si')
        if kw.get('type') == const.SEARCH_TYPE_SO:
            collections = SO.find( ** kw)
            override_template(self.index, 'mako:vatsystem.templates.ar.list_so')
        if kw.get('type') == const.SEARCH_TYPE_MSIMSO:
            cust = 0
            collections = THead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.ar.list_thead')
        if kw.get('type') == const.SEARCH_TYPE_MCN:
            cust = 0
            collections = CHead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.ar.list_chead')
        if kw.get('type') == const.SEARCH_TYPE_GROUP_SI:
            collections = Customer.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.ar.list_customer')
        if kw.get('type') == const.SEARCH_TYPE_GROUP_SO:
            collections = Customer.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.ar.list_customer')
        if cust ==0:
            display = 1
        else:
            if viewPager == 1:display = 1           
        results = dict(
                       collections=collections[0],
                       si_search_form=si_search_form,
                       so_search_form=so_search_form,
                       thead_search_form=thead_search_form,
                       chead_search_form=chead_search_form,
                       si_group_search_form = si_group_search_form,
                       so_group_search_form = so_group_search_form,
                       kw=kw,
                       cust = cust,
                       display=display,
                       limit = collections[2],
                       offset = collections[1]
                       )
        return results
    
    @expose('vatsystem.templates.ar.view_si')
    def ajax_view_si(self, ** kw):
        try:
            si_list = SID.find(** kw)
            si = SI.get(kw['invoice_no'])
            mso = THead.find_mso(kw['invoice_no'])
            other_charge = RICharge.search_charge_erp(**{'customer_code':si.customer})
            return  dict(flag=0, si=si, mso=mso, theads=THead.find('detail', ** kw), cheads=CHead.find('detail', ** kw),
                            collections=si_list[0], si_charges=si_list[1], ri_charges=si_list[3],
                            other_charges=other_charge,cn_charges = si_list[3],cn_details=si_list[2] , ** kw)
            
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag=1, ** kw)

    @expose('vatsystem.templates.ar.view_so')
    def ajax_view_so(self, ** kw):
        print '*' * 80
        print 'ajax_view_so: %s' % kw
        print '*' * 80
        try:
            so_list = SOD.find(** kw)
            return dict(flag=0, so=SO.get(kw['sales_contract_no']), theads=THead.find('detail', ** kw), cheads=CHead.find('detail', ** kw),
                        collections=so_list[0], so_charges=so_list[1], ** kw)
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag=1, ** kw)

    @expose()
    def ajax_view_thead(self, ** kw):
        print '*' * 80
        print 'ajax_view_thead: %s' % kw
        print '*' * 80
        try:
            thead = THead.get(kw['id'])
            other_charges_from_vat = Charge.find_Other_Charges_From_vat(kw['id'], const.ERP_HEAD_TYPE_THEAD)
            if thead.head_type == const.ERP_HEAD_TYPE_SI:
                override_template(self.ajax_view_thead, 'mako:vatsystem.templates.ar.view_thead_si')
                return dict(flag=0, tHead=thead, other_charges_from_vat=other_charges_from_vat, ** kw)
            else:
                si_list = []
                relation_si = thead.relation_si.split(",") if thead.relation_si else []
                for invoice_no in relation_si:
                    si = SI.find(**{'invoice_no':invoice_no,'redirct':const.ERP_HEAD_TYPE_THEAD})
                    if len(si[0])>0: si_list.append(si[0][0])
                override_template(self.ajax_view_thead, 'mako:vatsystem.templates.ar.view_thead_so')
                return dict(flag=0, tHead=thead, other_charges_from_vat=other_charges_from_vat, si_list = si_list, ** kw)
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag=1, ** kw)

    @expose()
    def ajax_view_chead(self, ** kw):
        print '*' * 80
        print 'ajax_view_chead: %s' % kw
        print '*' * 80
        try:
            collections = []
            chead = CHead.get(kw['id'])
            sql = '''select tnh.NOTE_NO,tnh.NOTE_TYPE,tnh.STATUS,tnc.LINE_NO,tnc.CHG_DISCOUNT_CODE,tnc.TOTAL,tnh.NOTE_DATE,tnh.REMARK 
                    From t_cust_note_charges tnc,t_cust_note_hdr tnh 
                    where tnh.COMPANY_CODE='RPACSZ' and tnh.SC_NO is null and
                     tnh.INVOICE_NO is null and tnh.CUSTOMER='%s' and tnh.NOTE_NO=tnc.NOTE_NO''' % (chead.customer_code)
            other_charges_from_erp = []
            t_head_id = DBSession.execute('''SELECT t_head_id FROM "public"."vat_c_head" WHERE id='%s' ''' %(kw['id'])).fetchone()[0]
            other_charges_from_vat = Charge.find_Other_Charges_From_vat(t_head_id, const.ERP_HEAD_TYPE_CHEAD, kw['id'])
            if chead.head_type == const.ERP_HEAD_TYPE_SI:
                override_template(self.ajax_view_chead, 'mako:vatsystem.templates.ar.view_chead_si')
            else:
                relation_si = chead.relation_si.split(',') if chead.relation_si else []
                for invoice_no in relation_si:
                    si_details = SID.find(** {'invoice_no':invoice_no})
                    if len(si_detail[0]) > 0:
                        for si_detail in si_details[0]: collections.append(si_detail)
                override_template(self.ajax_view_chead, 'mako:vatsystem.templates.ar.view_chead_so')
            return dict(flag = 0, cHead = chead, collections = collections, other_charges_from_erps = other_charges_from_erp, other_charges_from_vat = other_charges_from_vat, ** kw)
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag=1, ** kw)

    @expose('json')
    def save_all_to_thead(self, ** kw):
        print '*' * 80
        print 'save_all_to_thead: %s' % kw
        print '*' * 80
        try:
            thead = THead.create(user=request.identity["user"], ** kw)
            invo = ",".join([i.split('$')[0] for i in kw.get("ids").split(",")])
            remark = {
                    "t_head_id":thead.id,
                    "action_type":"SAVE",
                    "remark":"Save %s %s" % (kw.get("head_type",'SI'), invo)
            }
            if kw.get("t_head_id"):
                remark.update({"action_type":"ADD","remark":"Add %s %s" % (kw.get("head_type",'SI'), invo)})
            ARLog.insert(** remark)
            message = "Successfully!<br/>The MSI/MSO No is: <a onclick=viewAll('/ar?type=%s&ref=%s')  href='javascript:void(0)' >%s<a>" % (const.SEARCH_TYPE_MSIMSO, thead.ref, thead.ref)
            if kw.get('t_head_id'):message = "Save Success!"
            type = 0
        except:
            message, type = "Save Failure!", 1
            traceback.print_exc()
        return dict(messages = message, types = type)
    
    @expose('json')
    def save_all_to_thead_by_customer(self, ** kw):
        try:
            customers, error_customers = [], []
            head_type = kw.get('head_type')
            customer_codes = [i for i in kw.get('ids').split(',')]
            for customer_code in customer_codes:
                follow = None
                kw.update({'customer_code':customer_code})
                if head_type == const.ERP_HEAD_TYPE_SI:
                    headers = SI.find_invoice_no_by_customer_code(** kw)
                    for header in headers:
                        check_mos = SI.check_hava_related(header)
                        if check_mos  == 1:
                            follow = True
                            error_customers.append(customer_code)
                            break
                    if not follow:
                        customers.append(customer_code)
                else:
                    headers = SO.find_so_no_by_customer_code(** kw)
                if len(headers) == 0 or follow: 
                    continue
                args = {
                        'head_type': head_type,'customer_code':customer_code,
                        'ids':",".join(["%s$%s" % (i, customer_code) for i in headers])
                        }
                thead = THead.create(user=request.identity["user"], ** args)
            if len(error_customers) > 0:
                message = "The customer(%s) SI has MSO, please relate the SI for MSO!" % ','.join(error_customers) 
                return dict(messages = message, types = 1, customers = ".".join(customers))
            else:
                return dict(messages = "Successfully!", types = 0, customers = ".".join(customers) )
        except:
            traceback.print_exc()
            return dict(message = "Save Failure!", type = 1)

    @expose('json')
    def save_to_chead(self, ** kw):
        print '*' * 80
        print 'save_to_chead: %s' % kw
        print '*' * 80       
        try:
            chead = CHead.create(** kw)
            ARLog.insert(**{
                            "c_head_id":chead.id,
                            "action_type":"CREATE",
                            "remark":"Create MCN"
            })
            other_charges = Charge.find_Other_Charges_From_vat(kw['id'],const.ERP_HEAD_TYPE_THEAD)
            if len(other_charges)>0:
                for other_charge  in other_charges:
                    if other_charge.type == "T_ERP": 
                        types = "C_ERP"
                    if other_charge.type == "T_Manual": 
                        types = "C_Manual"
                    mcn_total = other_charge.vat_total
                    if other_charge.vat_total != 0:
                        charge = Charge(
                                         create_time = other_charge.create_time,
                                         create_by_id = other_charge.create_by_id,
                                         update_time = other_charge.update_time,
                                         update_by_id = other_charge.update_by_id,
                                         active = other_charge.active,
                                         log = other_charge.log,
                                         t_head_id = other_charge.t_head_id,
                                         c_head_id = chead.id,
                                         so_head_id = other_charge.so_head_id,
                                         si_head_id = other_charge.si_head_id,
                                         company_code = other_charge.company_code,
                                         line_no = other_charge.line_no,
                                         charge_code = other_charge.charge_code,
                                         total = mcn_total,
                                         vat_total = 0,
                                         type = types,
                                         invoice_no = other_charge.invoice_no,
                                         sales_contract_no = other_charge.sales_contract_no,
                                         note_no = other_charge.note_no,
                                         cust_code = other_charge.cust_code,
                                         uuid = other_charge.uuid
                                        )
                        DBSession.add(charge)  
            message = "Successfully!<br/>The MCN No is: <a onclick=viewAll('/ar?type=%s&ref=%s')  href='javascript:void(0)' >%s<a>" % (const.SEARCH_TYPE_MCN, chead.ref, chead.ref)
            type = 0
        except:
            message,type = "Save Failure!", 1
            traceback.print_exc()            
        return dict(messages = message, types = type)

    @expose('json')
    def update_thead_details(self, ** kw):
        print '*' * 80
        print 'update_thead_details: %s' % kw
        print '*' * 80
        try:
            head_type = kw['head_type']
            if head_type == const.ERP_HEAD_TYPE_SI:
                siHead = SiHead.get(kw['id'])
                detailRemark = siHead.update_details( ** kw)
                chargeRemark = siHead.update_charges( ** kw)
                remark = {
                            "t_head_id":siHead.t_head_id,
                            "action_type":"UPDATE",
                            "remark":"Update "
                        }
                if detailRemark or chargeRemark:
                    if detailRemark:remark['remark'] +=" Detail %s" % detailRemark
                    if chargeRemark:remark['remark'] +=" Charge %s" % chargeRemark
                    ARLog.insert( **remark)
            else:
                soHead = SoHead.get(kw['id'])
                detailRemark = soHead.update_details( ** kw)
                chargeRemark = soHead.update_charges( ** kw)
                remark = {
                    "t_head_id":soHead.t_head_id,
                    "action_type":"UPDATE",
                    "remark":"Update"
                }
                if detailRemark or chargeRemark:
                    if detailRemark:remark['remark'] +="Detail %s" % detailRemark
                    if chargeRemark:remark['remark'] +="Charge %s" % chargeRemark
                    ARLog.insert( **remark)
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type)
       
    @expose('json')
    def update_chead_details(self, ** kw):
        print '*' * 80
        print 'update_chead_details: %s' % kw
        print '*' * 80
        try:
            head_type = kw['head_type']
            if head_type == const.ERP_HEAD_TYPE_SI:
                siHead = SiHead.get(kw['id'])
                detailRemark = siHead.update_details( ** kw)
                chargeRemark = siHead.update_charges( ** kw)
                remark = {
                        "c_head_id":siHead.c_head_id,
                        "action_type":"UPDATE",
                        "remark":"Update "
                        }
                if detailRemark or chargeRemark:
                    if detailRemark:remark['remark'] +=" Detail %s" % detailRemark
                    if chargeRemark:remark['remark'] +=" Charge %s" % chargeRemark
                    ARLog.insert( **remark)
            else:
                soHead = SoHead.get(kw['id'])
                detailRemark = soHead.update_details( ** kw)
                chargeRemark = soHead.update_charges( ** kw)
                remark = {
                    "c_head_id":soHead.c_head_id,
                    "action_type":"UPDATE",
                    "remark":"Update "
                }
                if detailRemark or chargeRemark:
                    if detailRemark:remark['remark'] +="Detail %s" % detailRemark
                    if chargeRemark:remark['remark'] +="Charge %s" % chargeRemark
                    ARLog.insert( **remark)
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type)

    @expose('json')
    def update_all_thead_vat_info(self, ** kw):
        print '*' * 80
        print 'update_all_thead_vat_info: %s' % kw
        print '*' * 80
        try:
            if getOnlyVatNo(kw['vat_no']):
                message,type = "Repeated VAT No.",1
            else:
                THead.update_all_vat_info(user=request.identity["user"], ** kw)
                message,type = "Successfully!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages = message, types = type, kws = kw)

    @expose('json')
    def update_all_chead_vat_info(self, ** kw):
        print '*' * 80
        print 'update_all_chead_vat_info: %s' % kw
        print '*' * 80
        try:
            if getOnlyVatNo(kw['vat_no']):
                message, type = "Repeated VAT No.",1
            else:
                CHead.update_all_vat_info(user=request.identity["user"], ** kw)
                message, type = "Successfully!",0
        except:
            message, type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages = message,types = type, kws = kw)

    @expose('json')
    def update_all_thead_status(self, ** kw):
        print '*' * 80
        print 'update_all_thead_status: %s' % kw
        print '*' * 80
        try:
            thead = THead.update_all_status(user=request.identity["user"], ** kw)
            if thead:
                message,type = "The MSI/MSO has issued the CST, you can't cancel it!",1
            else:
                message,type = "Saved Successfully!",0
            for i in kw.get("ids").split(","):
                print "i", i
                ARLog.insert(**{
                    "t_head_id":i,
                    "action_type":"UPDATE",
                    "remark":"Update Status %s" % kw.get("status")
                })
        except:
            traceback.print_exc()
            message,type = "Save Failure!",1
        return dict(messages = message, types = type, kws = kw)

    @expose('json')
    def update_all_chead_status(self, ** kw):
        print '*' * 80
        print 'update_all_chead_status: %s' % kw
        print '*' * 80
        try:
            chead = CHead.update_all_status(user=request.identity["user"], ** kw)
            if chead: 
                message,type = "The MCN has issued the CCN, you can't cancel it!", 1
            else:
                message,type = "Saved Successfully!",0
            for i in kw.get("ids").split(","):
                ARLog.insert(**{
                    "c_head_id":i,
                    "action_type":"UPDATE",
                    "remark":"Update Status %s" % kw.get("status")
                })
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages = message, types = type, kws = kw)
      
    @expose('json')
    def add_other_charges_from_manual(self,** kw):
        try:
            if kw.get('select_id'):
                selectId = kw.get('select_id').split(",");
                for i in selectId:
                    if i:
                        id = kw.get('id_%s' % i)
                        if id:
                            charge = Charge.get(id)
                            total= float(kw.get('total_%s' % i, 0))
                            charge_total = float(charge.total)
                            if abs(total - charge_total) <= 0.05:
                                charge.pending = None
                                charge.note_no = kw.get('note_no_%s' % i )
                                DBSession.merge(charge)
                            else:
                                message,type = "Save Failure, the total is not equal!", 1
                                return dict(messages=message,types=type)
                        else:
                            Charge.insert(
                                        active=kw.get('active_%s' % i),
                                        charge_code=kw.get('charge_code_%s' % i ),
                                        company_code=getCompanyCode(),
                                        line_no=kw.get('line_no_%s' % i ),
                                        note_no=kw.get('note_no_%s' % i ),
                                        t_head_id=kw.get('t_head_%s' % i ),
                                        total= kw.get('total_%s' % i),
                                        type=kw.get('type_%s' % i ),
                                        vat_total = kw.get('vat_total_%s' % i)
                                        )
                            ARLog.insert(**{
                                "t_head_id":kw.get('t_head_%s' % i ),
                                "action_type":"ADD",
                                "remark":"Add Other Charge %s:%s" % (kw.get('charge_code_%s' % i ),-Decimal(kw.get('total_%s' % i )))
                            })
            else:
                if kw.get("type")=="T_Manual":
                    kw['vat_total'] = kw['total']
                    Charge.insert(** kw)
                    ARLog.insert(**{
                            "t_head_id":kw.get("t_head_id"),
                            "action_type":"ADD",
                            "remark":"Add Other Charge %s:%s" % (kw.get("charge_code"),kw.get("total"))
                    })
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type)
         
    @expose('vatsystem.templates.ar.search_charge_erp')
    def search_charge_erp(self,**kw):
        try:
            other_charges_from_erp = RICharge.search_charge_erp(**kw)
            thead = THead.get(kw['tHead_id'])
            return dict(other_charges_from_erp=other_charges_from_erp,kws=kw,tHead=thead)
        except:
            traceback.print_exc()
   
    @expose('json')
    def update_other_charges_vat_total(self, ** kw):
        id = kw.get('id')
        head_type = kw.get('head_type')
        if head_type == const.ERP_HEAD_TYPE_THEAD:
            header = THead.get(id)
        else:
            header = CHead.get(id)
        charges = header.charges
        if kw.get('save'):
            for charge in charges:
                vat_total = float(kw.get('vat_total_%s' % charge.id, 0))
                query = {"c_head_id":charge.c_head_id,"action_type":"UPDATE"}
                mg =  merge([charge.vat_total,charge.line_no],
                            [vat_total],
                            ['Vat Total','Line NO'])
                if mg: query['remark'] = "Update Other Charge %s" % mg
                if charge.type == 'T_Manual' or charge.type == 'T_ERP':
                    del query['c_head_id']
                    query.update({"t_head_id":charge.t_head_id})
                    charge.total = vat_total
                charge.vat_total = vat_total
                charge.pending = kw.get('pending_%s' % charge.id)
                DBSession.merge(charge)
                if query.get('remark'):
                    ARLog.insert(**query)      
            message, type = "Save Success!", 0
                    
        if kw.get('delete'):
            for charge in charges:
                if kw.get('checkbox_%s' % charge.id):
                    DBSession.delete(charge)
                    ARLog.insert(**{
                        "t_head_id":charge.t_head_id,
                        "action_type":"DELETE",
                        "remark":"Delete Other Charge %s %s" % (charge.charge_code,round(charge.total,2))
                    })
            message, type = "Delete Success!", 0
        return dict(messages=message,types=type)
    
    @expose('json')
    def autocomplete(self,** kw):
        if kw.get("form") == "_form0": 
            DB  = DBSession2
            db_dict = {
                       "t_invoice_hdr":["invoice_no"]
                       }
        if kw.get("form") == "_form1": 
            DB  = DBSession2
            db_dict = {
                       "t_sales_contract_hdr":["sales_contract_no"]
                       }
        if kw.get("form") == "_form2": 
            DB  = DBSession
            db_dict = {
               "vat_si_head":["invoice_no"],
               "vat_so_head":["sales_contract_no"],
               "vat_t_head":["ref", "vat_no"],
               "vat_so_detail":["item_no"],
               "vat_si_detail":["item_no"]
               }
        if kw.get("form") == "_form3": 
            DB  = DBSession
            db_dict = {
               "vat_si_head":["invoice_no", "item_code"],
               "vat_so_head":["sales_contract_no", "item_code"],
               "vat_c_head":["thead_ref", "ref", "vat_no"],
               "vat_so_detail":["item_no"],
               "vat_si_detail":["item_no"]
               }
        if kw.get("form") == "_form4": 
            DB  = DBSession2
            db_dict = {
               "t_cust_hdr":["cust_code", "cust_name", "cust_type"]
               }
        if kw.get("form") == "_form5": 
            DB  = DBSession2
            db_dict = {
               "t_cust_hdr":["cust_code", "cust_name", "cust_type"]
               }
        if kw.get("type") == 'display_name':
            DB  = DBSession
            db_dict = {
                       "tg_user":["display_name"]
                       }
        type, q = kw.get("type"), kw.get("q",'').strip()
        arr = SI.auto_complete(DB, db_dict, type, q)
        return dict(users=arr)
    
    @expose('vatsystem.templates.ar.add_si_so_erp')
    def add_si_so_erp(self,**kw):
        if kw.get('type') == '1':
            collections = SI.find( ** kw)
        else:
            collections = SO.find( ** kw)
        return dict(
                    kws=kw,
                    collections=collections[0],
                    limit = collections[2],
                    offset = collections[1]
                ) 
    
    @expose('vatsystem.templates.ar.add_related_si_erp')
    def add_related_si_erp(self, **kw):
        thead = THead.get(kw['tHead_id'])
        soheads = thead.so_heads
        si_list, si_detail_list, relation_si = [],[],[]
        for a in soheads:
            soheads = SoHead.get_by_so(a.sales_contract_no)
            for c in soheads:
                if c.t_head and c.t_head.relation_si:
                    for d in c.t_head.relation_si.split(","):  
                        relation_si.append(d) 
            siheads = SI.find_si_by_sc_no(a.sales_contract_no)
            for b in siheads:
                if b.invoice_no in relation_si:continue
                queryDict = {"cate":"thead"}
                if kw.get("date_from"):queryDict.update({"date_from":kw.get("date_from")})
                if kw.get("date_to"):queryDict.update({"date_to":kw.get("date_to")})
                if kw.get("invoice_no"):
                    if kw.get("invoice_no") == b.invoice_no:
                        queryDict.update({"invoice_no":b.invoice_no})
                        si =  SI.find(**queryDict)
                else:
                    queryDict.update({"invoice_no":b.invoice_no})
                    si =  SI.find(**queryDict)
                if len(si[0])>0 and si[0][0] not in si_list:
                    si_list.append(si[0][0])        
        return dict(
                    kws=kw,
                    collections=si_list,
                    limit = 0,
                    offset = len(si_list)
                ) 
        
    @expose('json')
    def ajax_check_mcn(self,** kw):
        check = 0
        thead = THead.get(kw.get('id'))
        if thead.head_type == const.ERP_HEAD_TYPE_SI:
            for si in thead.si_heads:
                siDetails = si.si_details
                for sid in siDetails:
                    self_msn_qty = 0
                    msn_details = SiDetail.get_details(sid.invoice_no,sid.line_no,sid.item_no) 
                    for b in msn_details:
                        if b.c_head_id:
                            if b.uuid == sid.uuid: self_msn_qty += pn(b.vat_qty)
                    vat_qty = sid.vat_qty - self_msn_qty
                    if not vat_qty == 0:
                        check = 1
                        break
                        
        elif thead.head_type == const.ERP_HEAD_TYPE_SO:
            for so in thead.so_heads:
                soDetails = so.so_details
                for sod in soDetails:
                    self_msn_qty = 0
                    msn_details = SoDetail.get_details(sod.sales_contract_no,sod.line_no,sod.item_no) 
                    for b in msn_details:
                        if b.c_head_id:
                            if b.uuid == sod.uuid: self_msn_qty += pn(b.vat_qty)
                    vat_qty = sod.vat_qty - self_msn_qty
                    if not vat_qty == 0:
                        check = 1
                        break
        return dict(Msg = check)

    @expose('json')
    def ajax_delete_item(self,** kw):
        type   = kw.get("type")
        id     = [kw.get("id")] if kw.get("id").find(",")<0 else kw.get("id").split(",")
        remark = {
                "action_type":"DELETE",
                "remark":"Delete SI"
                }
        if type == const.ERP_HEAD_TYPE_SI:
            for i in id:
                si = SiHead.get_by_id(i)
                for a in si.si_details: DBSession.delete(a)
                for b in si.charges: DBSession.delete(b)
                DBSession.delete(si)
                remark['t_head_id'] = si.t_head_id
                remark['remark'] += " "+si.invoice_no
        elif type == const.ERP_HEAD_TYPE_SO:
            remark['remark'] = "Delete SO"
            for i in id:
                so = SoHead.get_by_id(i)
                for a in so.so_details: DBSession.delete(a)
                for b in so.charges: DBSession.delete(b)
                DBSession.delete(so)
                remark['t_head_id'] = so.t_head_id
                remark['remark'] += " "+so.sales_contract_no
        ARLog.insert(**remark)
        return dict(Msg = "sucees" )
                    
    @expose('vatsystem.templates.ar.view_history')
    def view_history(self, ** args):
        return dict(historys = ARLog.find(** args))
    
    @expose("json")
    def relation_si(self, **kw):
        try:
            (relation, t_head_id, type) = (kw.get(i, '') for i in ('relation', 't_head_id', 'type')) 
            queryDict = {"t_head_id":t_head_id}
            if type == 'save':
                queryDict.update({"action_type":"SAVE","remark":"Save related SI %s " % relation})
            if type == 'delete':
                if not relation: 
                    theads = THead.get(t_head_id)
                    relation = theads.relation_si
                queryDict.update({"action_type":"DELETE","remark":"Delete related SI %s " % relation})
            result = THead.update_relation_si(**kw)
            if result == 1 and type == 'save':
                return dict(status = 1)
            else:
                ARLog.insert(** queryDict)
            statu=0
        except:
            statu=1
        return dict(status = statu)
       
    @expose("json")
    def ajax_check_hava_mso(self, **kw):
        try:
            name = kw.get("name")
            return SI.check_hava_mso(name)
        except:
            traceback.print_exc()

            
    @expose("json")
    def check_amount(self, ** kw):
        ids = kw.get('id', '').split(',')
        for id in ids:
            thead = THead.get(id)
            other_charges = thead.charges
            other_charge_amounts = {}
            for other_charge in other_charges:
                if not other_charge.so_head_id and other_charge.sales_contract_no:
                    if other_charge_amounts.get(other_charge.sales_contract_no):
                        other_charge_amounts[other_charge.sales_contract_no] += float(other_charge.vat_total)
                    else:
                        other_charge_amounts.update({other_charge.sales_contract_no:float(other_charge.vat_total)})
            if thead.head_type != const.ERP_HEAD_TYPE_SO:
                continue
            so_heads = thead.so_heads
            for so_head in so_heads:
                p = []
                so_amount = 0
                other_charge_amount = other_charge_amounts.get(so_head.sales_contract_no, 0)
                so_details = so_head.find_details()
                so_charges = so_head.find_charges()
                for so_detail in so_details:
                    so_amount += float(int(so_detail.vat_qty) * float(so_detail.unit_price))
                    if int(so_detail.available_qty) - int(so_detail.vat_qty) != 0:
                        p.append(int(so_detail.available_qty))
                for so_charge in so_charges:
                    so_amount += float(so_charge.vat_total)
                so_amount += other_charge_amount
                if len(p) == 0:
                    ava_amount = so_head.available_amount()[1]
                    if abs(ava_amount - so_amount) > 0.05:
                        return dict(status = 0)
        return dict(status = 1)
            
    
