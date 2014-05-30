# -*- coding: utf-8 -*-
import uuid
import copy
import random
import traceback
import datetime
import transaction
from itertools import *
from repoze.what import authorize
from tg import config
from tg import expose
from tg import flash
from tg import override_template
from tg import redirect
from tg import request
from vatsystem.lib.base import BaseController
from vatsystem.model import *
from vatsystem.model.erp import getOnlyVatNo,_fetch_sql_to_dict,_check_cn_rewrite_charges,Decimal
from vatsystem.util import const
from vatsystem.util.common import *
from vatsystem.util.excel_helper import *
from vatsystem.widgets.ap import *

__all__ = ["APController"]

class APController(BaseController):
    allow_only = authorize.has_permission('ap')
    @expose('vatsystem.templates.ap.index')
    @tabFocus(tab_type='main')
    def index(self, ** kw):
        viewPager, cust, display, collections = 1, 0, 0, [[], 1, 1]
        if kw.get("viewPager"):viewPager = kw.get("viewPager")
        if kw.get("supplier_name") or kw.get("supplier"):
            cust = 1
        if kw.get('type') == const.SEARCH_TYPE_PI:
            collections = PI.find( ** kw)
            override_template(self.index, 'mako:vatsystem.templates.ap.list_si')
        if kw.get('type') == const.SEARCH_TYPE_PSIPSO:
            cust = 0
            collections = PHead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.ap.list_thead')
        if kw.get('type') == const.SEARCH_TYPE_MSN:
            cust = 0
            collections = SHead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.ap.list_chead')
        if kw.get("type") == const.SEARCH_TYPE_EXCEL:
            cust = 0
            collections = STHead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.ap.list_statement')
        if kw.get("type") == const.SEARCH_TYPE_MF:
            cust = 0
            collections = MHead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.ap.list_mf')
        if cust ==0:display = 1
        else:
            if viewPager == 1:display = 1  
        results = dict(
                       collections = collections[0],
                       pi_search_form = pi_search_form,
                       po_search_form = po_search_form,
                       phead_search_form = phead_search_form,
                       shead_search_form = shead_search_form,
                       mhead_search_form = mhead_search_form,
                       excel_search_form = excel_search_form,
                       kw = kw,
                       cust = cust,
                       display = display,
                       limit = collections[2],
                       offset = collections[1]
                       )
        return results

    @expose('vatsystem.templates.ap.view_si')
    def ajax_view_pi(self, ** kw):
        try:
            si_list = PID.find(** kw)
            si = PI.get(kw['invoice_no'])
            args = {"supplier":si.supplier}
            other_charge = UICharge.search_cust_charge_erp(** args)
            return  dict(flag=0, type = si_list[4], si=si, pheads=PHead.find('detail', ** kw), sheads=SHead.find('detail', ** kw),
                        collections=si_list[0], si_charges=si_list[1], ri_charges=si_list[3],
                        other_charges=other_charge,cn_charges = si_list[3],cn_details=si_list[2] , ** kw)
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag=1, ** kw)

    @expose()
    def ajax_view_phead(self, ** kw):
        print '*' * 80
        print 'ajax_view_phead: %s' % kw
        print '*' * 80
        try:
            phead = PHead.get(kw['id'])
            Other_Charges_From_vat = PCharge.find_other_charges_from_vat(kw['id'], [const.CHARGE_TYPE_P_MAN, const.CHARGE_TYPE_P_ERP], 'p_head_id')
            override_template(self.ajax_view_phead, 'mako:vatsystem.templates.ap.view_thead_si')
            return dict(flag = 0, pHead = phead, Other_Charges_From_vats = Other_Charges_From_vat, ** kw)
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag=1, ** kw)

    @expose()
    def ajax_view_shead(self, ** kw):
        print '*' * 80
        print 'ajax_view_shead: %s' % kw
        print '*' * 80
        try:
            shead = SHead.get(kw['id'])
            Other_Charges_From_vat = PCharge.find_other_charges_from_vat(kw['id'],[const.CHARGE_TYPE_S_ERP,const.CHARGE_TYPE_S_MAN],'s_head_id')
            override_template(self.ajax_view_shead, 'mako:vatsystem.templates.ap.view_chead_si')
            return dict(flag=0, sHead=shead, Other_Charges_From_Erps = [], Other_Charges_From_vats = Other_Charges_From_vat, ** kw)
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag=1, ** kw)
    
    @expose('vatsystem.templates.ap.view_thead_mf')
    def ajax_view_mhead(self, ** kw):
        print '*' * 80
        print 'ajax_view_mhead: %s' % kw
        print '*' * 80
        try:
            mhead = MHead.get(kw['id'])
            Other_Charges_From_vat = PCharge.find_other_charges_from_vat(kw['id'], const.CHARGE_TYPE_M_MAN, 'm_head_id')
            return dict(flag = 0, mHead = mhead , Other_Charges_From_Erps = [], Other_Charges_From_vats=Other_Charges_From_vat, ** kw)
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag=1, ** kw)

    @expose('json')
    def save_all_to_phead(self, ** kw):
        print '*' * 80
        print 'save_all_to_phead: %s' % kw
        print '*' * 80
        try:
            phead = PHead.create(user=request.identity["user"], ** kw)
            invo = ",".join([i.split('$')[0] for i in kw.get("ids").split(",")])
            remark = {
                    "p_head_id":phead.id,
                    "action_type":"SAVE",
                    "remark":"Save %s %s" % ('PI',invo)
                    }
            if kw.get("p_head_id"):remark.update({"action_type":"ADD","remark":"Add %s %s" % ('PI',invo)})
            ARLog.insert(** remark)
            message = "Successfully!<br/>The MPI/MPO No is: <a onclick=viewAll('/ap?type=%s&ref=%s')  href='javascript:void(0)' >%s<a>" % (const.SEARCH_TYPE_MSIMSO, phead.ref, phead.ref)
            if kw.get('p_head_id'):message = "Save Success!"
            type = 0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages = message, types = type)
    
    @expose('json')
    def save_to_phead_statement(self, ** kw):
        print '*' * 80
        print 'save_all_to_phead: %s' % kw
        print '*' * 80
        try:
            invo = [int(i.split('$')[0]) for i in kw.get("ids").split(",")]
            print invo
            for a in invo:
                STHead.parse_match2(a)
                STHead.parse_dndetails(a)
            message = "Save Success!"
            type = 0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages = message,types = type)

    @expose('json')
    def save_to_shead(self, ** kw):
        print '*' * 80
        print 'save_to_shead: %s' % kw
        print '*' * 80       
        try:
            shead = SHead.create(** kw)
            ARLog.insert(**{
                            "s_head_id":shead.id,
                            "action_type":"CREATE",
                            "remark":"Create MSN"
                        })
            Other_Charges = PCharge.find_other_charges_from_vat(kw['id'],[const.CHARGE_TYPE_P_MAN, const.CHARGE_TYPE_P_ERP], 'p_head_id')
            if len(Other_Charges)>0:
                for i  in Other_Charges:
                    if i.type == const.CHARGE_TYPE_P_ERP: 
                        types = const.CHARGE_TYPE_S_ERP
                    if i.type == const.CHARGE_TYPE_P_MAN: 
                        types = const.CHARGE_TYPE_S_MAN
                    msn_total = i.vat_total
                    if i.vat_total != 0:
                        sql_execute = PCharge(create_time=i.create_time,create_by_id=i.create_by_id,update_time=i.update_time,update_by_id=i.update_by_id,active=i.active,log=i.log,s_head_id=shead.id,po_head_id=i.po_head_id,pi_head_id=i.pi_head_id,company_code=i.company_code,line_no=i.line_no,charge_code=i.charge_code,total=msn_total,vat_total=0,type=types,invoice_no=i.invoice_no,note_no=i.note_no,uuid=i.uuid,uuid2=str(uuid.uuid4()))
                        DBSession.add(sql_execute)  
            message = "Successfully!<br/>The MSN No is: <a onclick=viewAll('/ap?type=%s&ref=%s')  href='javascript:void(0)' >%s<a>" % (const.SEARCH_TYPE_MCN, shead.ref, shead.ref)
            type = 0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type)
    
    @expose('json')
    def save_to_mf(self, ** kw):
        print '*' * 80
        print 'save_to_mf: %s' % kw
        print '*' * 80      
        try:
            mfhead = MHead.create(** kw)
            remark = {
                        "action_type":"CREATE",
                        "remark":"Create MF"
                     }
            if kw.get("type") == "t_head_id":
                remark.update({"p_head_id":kw.get('id')})
                Other_Charges = PCharge.find_other_charges_from_vat(kw['id'],const.CHARGE_TYPE_P,'p_head_id')
            else:
                remark.update({"s_head_id":kw.get('id')})
                Other_Charges = PCharge.find_other_charges_from_vat(kw['id'],const.CHARGE_TYPE_S,'s_head_id')
            ARLog.insert(** remark)
            print "Other_Charges", Other_Charges
            if len(Other_Charges)>0:
                for i  in Other_Charges:
                    if i.type == const.CHARGE_TYPE_P_ERP: 
                        types = const.CHARGE_TYPE_PM_ERP
                    if i.type == const.CHARGE_TYPE_P_MAN: 
                        types = const.CHARGE_TYPE_PM_MAN
                    if i.type == const.CHARGE_TYPE_S_ERP: 
                        types = const.CHARGE_TYPE_SM_ERP
                    if i.type == const.CHARGE_TYPE_S_MAN: 
                        types = const.CHARGE_TYPE_SM_MAN
                    msn_total = i.vat_total
                    if i.vat_total != 0:
                        charge = {
                                'create_time':i.create_time, 'create_by_id':i.create_by_id,
                                'update_time':i.update_time, 'update_by_id':i.update_by_id,
                                'active':i.active, 'log':i.log, 'm_head_id': mfhead.id, 'po_head_id':i.po_head_id,
                                'pi_head_id':i.pi_head_id, 'company_code':i.company_code, 'line_no':i.line_no,
                                'charge_code':i.charge_code, 'total':msn_total, 'vat_total':i.ava_total2,
                                'type':types, 'invoice_no':i.invoice_no, 'note_no':i.note_no, 'uuid':i.uuid, 'uuid2':i.uuid2
                                }
                        sql_execute = PCharge(** charge)
                        DBSession.add(sql_execute)  
            message = "Successfully!<br/>The MF No is: <a onclick=viewAll('/ap?type=%s&ref=%s')  href='javascript:void(0)' >%s<a>" % (const.SEARCH_TYPE_MF, mfhead.ref, mfhead.ref)
            type = 0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type)

    @expose('json')
    def update_phead_details(self, ** kw):
        print '*' * 80
        print 'update_phead_details: %s' % kw
        print '*' * 80
        try:
            head_type = kw['head_type']
            if head_type == const.CHARGE_TYPE_P_PI:
                piHead = PiHead.get(kw['id'])
                detailRemark = piHead.update_details( ** kw)
                chargeRemark = piHead.update_charges( ** kw)
                remark = {
                         "p_head_id":piHead.p_head_id,
                         "action_type":"UPDATE",
                         "remark":"Update "
                        }
                if detailRemark or chargeRemark:
                    if detailRemark:remark['remark'] +=" Detail %s" % detailRemark
                    if chargeRemark:remark['remark'] +=" Charge %s" % chargeRemark
                    ARLog.insert( **remark)
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type)
       
    @expose('json')
    def update_shead_details(self, ** kw):
        print '*' * 80
        print 'update_shead_details: %s' % kw
        print '*' * 80
        try:
            head_type = kw['head_type']
            if head_type == const.CHARGE_TYPE_S_PI:
                piHead = PiHead.get(kw['id'])
                detailRemark = piHead.update_details( ** kw)
                chargeRemark = piHead.update_charges( ** kw)
                remark = {
                         "s_head_id":piHead.s_head_id,
                         "action_type":"UPDATE",
                         "remark":"Update "
                        }
                if detailRemark or chargeRemark:
                    if detailRemark:remark['remark'] +=" Detail %s" % detailRemark
                    if chargeRemark:remark['remark'] +=" Charge %s" % chargeRemark
                    ARLog.insert( **remark)
            else:
                poHead = PoHead.get(kw['id'])
                poHead.update_details( ** kw)
                poHead.update_charges( ** kw)
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type)
    
    @expose('json')
    def update_mhead_details(self, ** kw):
        print '*' * 80
        print 'update_phead_details: %s' % kw
        print '*' * 80
        try:
            piHead = PiHead.get(kw['id'])
            detailRemark = piHead.update_details( ** kw)
            chargeRemark = piHead.update_charges( ** kw)
            remark = {
                    "m_head_id":piHead.m_head_id,
                    "action_type":"UPDATE",
                    "remark":"Update "
                    }
            if detailRemark or chargeRemark:
                if detailRemark:remark['remark'] +=" Detail %s" % detailRemark
                if chargeRemark:remark['remark'] +=" Charge %s" % chargeRemark
                ARLog.insert( **remark)
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type)

    @expose('json')
    def update_all_phead_vat_info(self, ** kw):
        print '*' * 80
        print 'update_all_thead_vat_info: %s' % kw
        print '*' * 80
        try:
            if getOnlyVatNo(kw['vat_no']):
                message,type = "Repeated VAT No.",1
            else:
                PHead.update_all_vat_info(user=request.identity["user"], ** kw)
                message,type = "Successfully!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type,kws=kw)

    @expose('json')
    def update_all_shead_vat_info(self, ** kw):
        print '*' * 80
        print 'update_all_shead_vat_info: %s' % kw
        print '*' * 80
        try:
            if getOnlyVatNo(kw['vat_no']):
                message,type = "Repeated VAT No.",1
            else:
                SHead.update_all_vat_info(user=request.identity["user"], ** kw)
                message,type = "Successfully!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type,kws=kw)
    
    @expose('json')
    def update_all_mhead_vat_info(self, ** kw):
        print '*' * 80
        print 'update_all_mhead_vat_info: %s' % kw
        print '*' * 80
        try:
            if getOnlyVatNo(kw['vat_no']):
                message,type = "Repeated VAT No.",1
            else:
                MHead.update_all_vat_info(user=request.identity["user"], ** kw)
                message,type = "Successfully!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type,kws=kw)

    @expose('json')
    def update_all_phead_status(self, ** kw):
        print '*' * 80
        print 'update_all_thead_status: %s' % kw
        print '*' * 80
        try:
            PHead.update_all_status(user=request.identity["user"], ** kw)
            message,type = "Save Success!",0
            for i in kw.get("ids").split(','):
                ARLog.insert(**{
                    "p_head_id":i,
                    "action_type":"UPDATE",
                    "remark":"Update Status %s" % kw.get("status")
                })
        except:
            traceback.print_exc()
            message,type = "Save Failure!",1
        return dict(messages=message,types=type,kws=kw)

    @expose('json')
    def update_all_shead_status(self, ** kw):
        print '*' * 80
        print 'update_all_shead_status: %s' % kw
        print '*' * 80
        try:
            SHead.update_all_status(user=request.identity["user"], ** kw)
            message, type = "Save Success!", 0
            for i in kw.get("ids").split(','):
                ARLog.insert(**{
                    "s_head_id":i,
                    "action_type":"UPDATE",
                    "remark":"Update Status %s" % kw.get("status")
                })
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type,kws=kw)
    
    @expose('json')
    def update_all_mhead_status(self, ** kw):
        print '*' * 80
        print 'update_all_mhead_status: %s' % kw
        print '*' * 80
        try:
            MHead.update_all_status(user=request.identity["user"], ** kw)
            message, type = "Save Success!", 0
            for i in kw.get("ids").split(','):
                ARLog.insert(**{
                    "m_head_id":i,
                    "action_type":"UPDATE",
                    "remark":"Update Status %s" % kw.get("status")
                })
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages=message,types=type,kws=kw)
      
    @expose('json')
    def add_other_charges_from_manual(self,** kw):
        try:
            if kw.get('select_id'):
                selectId = kw.get('select_id').split(",")
                for i in selectId:
                    if i == "," or not i: 
                        continue
                    charge = {
                                'active':kw.get("active_%s" % i, ''),
                                'charge_code':kw.get('charge_code_%s' % i, ''),
                                'company_code':kw.get('company_code_%s' % i, '' ),
                                'line_no':kw.get('line_no_%s' % i, '' ),
                                'note_no':kw.get('note_no_%s' % i, '' ),
                                'p_head_id':kw.get('p_head'),
                                'total':-Decimal(kw.get('total_%s' % i, '')),
                                'type':kw.get('type_%s' % i, ''),
                                'vat_total':-Decimal(kw.get('total_%s' % i, ''))
                             }
                    #result  = PCharge.insert(active=kw.get("active_%s" % i),charge_code=kw.get('charge_code_%s' % i ),company_code=kw.get('company_code_%s' % i ),line_no=kw.get('line_no_%s' % i ),note_no=kw.get('note_no_%s' % i ),p_head_id=kw.get('p_head_%s' % i),total=-Decimal(kw.get('total_%s' % i )),type=kw.get('type_%s' % i ),vat_total=-Decimal(kw.get('total_%s' % i )))
                    pcharge = PCharge(** charge)
                    DBSession.add(pcharge)
                    ARLog.insert(**{
                        "p_head_id":kw.get('p_head_%s' % i ),
                        "action_type":"ADD",
                        "remark":"Add Other Charge %s:%s" % (kw.get('charge_code_%s' % i ),-Decimal(kw.get('total_%s' % i )))
                    })
            else:
                if kw.get("type") == const.CHARGE_TYPE_P_MAN: 
                    kw['vat_total'] = kw['total']
                ARLog.insert(**{
                        "p_head_id":kw.get("p_head_id"),
                        "action_type":"ADD",
                        "remark":"Add Other Charge %s:%s" % (kw.get("charge_code"),kw.get("total"))
                })
                result  = PCharge.insert(** kw)
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages = message, types = type)
         
    @expose('vatsystem.templates.ap.search_charge_erp')
    def search_charge_erp(self, ** args):
        phead = PHead.get(args.get('pHead_id'))
        charges = UICharge.search_charge_erp(** args)
        return dict(charges=charges, kws=args, pHead=phead)   
   
    @expose('json')
    def update_other_charges_vat_total(self,** kw):
        if kw.get('save'):
            for v in kw:
                if not v == "save" and not v=="checkbox_list":
                    vat_detail = DBSession.query(PCharge).filter_by(id=int(v)).one() 
                    if vat_detail.type == 'P_Manual' or vat_detail.type == 'P_ERP':
                        query = {
                                 "p_head_id":vat_detail.p_head_id, 
                                 "action_type":"UPDATE"
                        }
                        vat_detail.total = int(float(kw[v]))
                    if vat_detail.type == 'S_Manual' or vat_detail.type == 'S_ERP':
                        query = {
                                 "s_head_id":vat_detail.s_head_id, 
                                 "action_type":"UPDATE"
                        }
                    if vat_detail.type == 'PM_Manual' or vat_detail.type == 'SM_Manual':
                        query = {
                                 "m_head_id":vat_detail.m_head_id, 
                                 "action_type":"UPDATE"
                        }
                    if len(query) >0 :
                        mg = merge([vat_detail.vat_total,vat_detail.line_no],[int(float(kw[v]))],['Vat Total','Line NO'])
                        if mg: query['remark'] = "Update Other Charge %s" % mg
                    vat_detail.vat_total = int(float(kw[v]))
                    DBSession.merge(vat_detail)
                    DBSession.flush()
                    if query.get('remark'):ARLog.insert(**query)
            message,type = "Save Success!",0
                    
        if kw.get('delete'):
            if isinstance(kw['checkbox_list'],list):
                for i in  kw['checkbox_list']:
                    vat_detail = DBSession.query(PCharge).filter_by(id=int(i)).one()
                    DBSession.delete(vat_detail)
                    ARLog.insert(**{
                        "p_head_id":vat_detail.p_head_id,
                        "action_type":"DELETE",
                        "remark":"Delete Other Charge %s %s" % (vat_detail.charge_code,round(vat_detail.total,2))
                    })
            else:
                    vat_detail = DBSession.query(PCharge).filter_by(id=int(kw['checkbox_list'])).one()
                    DBSession.delete(vat_detail)
                    ARLog.insert(**{
                        "p_head_id":vat_detail.p_head_id,
                        "action_type":"DELETE",
                        "remark":"Delete Other Charge %s %s" % (vat_detail.charge_code,round(vat_detail.total,2))
                    })
            message,type = "Delete Success!",0
        return dict(messages=message,types=type)
    
    @expose('json')
    def autocomplete(self,** kw):
        db_dict = {}
        if kw.get("form") == "_form0": 
            DB = DBSession
            db_dict = {
                       "vat_t_sthead":["status", "ref" ],
                       "vat_t_stdetail":["supplier_code", "po_no", "item_code", "qty", "unit", "reconciliation_lot"],
                       "vat_t_dndetail":["supplier_code"]
                       }
        if kw.get("form") == "_form1": 
            DB  = DBSession2
            db_dict = {
                       "t_purchase_invoice_hdr":["supplier", "purchase_invoice_no"],
                       "t_purchase_invoice_dtl":["item_code"]
                       }
        if kw.get("form") == "_form2": 
            DB  = DBSession
            db_dict = {
                       "vat_pi_head":["supplier", "supplier_name", "status", "po_no", "invoice_no"],
                       "vat_p_head":["ref", 'dzd'], "vat_pi_detail":["item_code"]
                       }
        if kw.get("form") == "_form3": 
            DB  = DBSession
            db_dict = {
                       "vat_pi_head":["supplier", "supplier_name", "status", "po_no", "invoice_no"],
                       "vat_s_head":["ref","phead_ref","vat_no","dzd"], "vat_pi_detail":["item_code"]
                       }
        if kw.get("form") == "_form4": 
            DB  = DBSession
            db_dict = {
                       "vat_pi_head":["supplier", "supplier_name", "status", "po_no", "invoice_no", "ref"],
                       "vat_m_head":["ref", "phead_ref", "vat_no"], "vat_pi_detail":["item_code"]
                       }
        if kw.get("type") == 'display_name':
            DB  = DBSession
            db_dict = {
                       "tg_user":["display_name"]
                       }
        type, q  = kw.get("type"), kw.get("q",'').strip()
        arr = PI.auto_complete(DB, db_dict, type, q)
        return {"users":arr}
    
    @expose('vatsystem.templates.ap.add_si_so_erp')
    def add_pi_po_erp(self,**kw):
        if kw.get('type') == '1':
            collections = PI.find( ** kw)
        else:
            collections = SO.find( ** kw)
        return dict(
                    kws = kw,
                    collections = collections[0],
                    limit = collections[2],
                    offset = collections[1]
                ) 
        
    @expose('json')
    def ajax_check_msn(self,** kw):
        check = 0
        phead = PHead.get(kw.get('id'))
        if phead.head_type == const.CHARGE_TYPE_P_PI:
            for si in phead.pi_heads:
                piDetails = si.pi_details
                for pid in piDetails:
                    vat_total = 0
                    for i in pid.find_details(pid.invoice_no,const.CHARGE_TYPE_S_PI,pid.item_no):
                        if i.uuid == pid.uuid: 
                            vat_total += pn(i.vat_qty) 
                    vat_qty = pid.vat_qty -  vat_total 
                    if not vat_qty == 0:
                        check = 1
                        break   
        return dict(Msg = check)
    
    @expose('json')
    def ajax_check_mf(self, ** args):
        check = 0
        type  = args.get('type')
        head = PHead.get(args.get('id')) if type == const.CHARGE_TYPE_P_PI else SHead.get(args.get('id'))
        pi_heads = head.pi_heads
        m_heads  = head.m_heads                    
        m_pi_detail_dict = {}           
        for m_head in m_heads:
            for m_pi_heads in m_head.pi_heads:
                for m_pi_detail in m_pi_heads.pi_details:
                    if m_pi_detail.active == 0:
                        if m_pi_detail_dict.get(m_pi_detail.uuid):
                            m_pi_detail_dict[m_pi_detail.uuid] += m_pi_detail.vat_total
                        else:
                            m_pi_detail_dict.update({m_pi_detail.uuid:m_pi_detail.vat_total})
                        
        for pi_head in pi_heads:
            for pi_detail in pi_head.pi_details:
                if pi_detail.active == 0:
                    if not "%.2f" % m_pi_detail_dict.get(pi_detail.uuid,0) == "%.2f" % float(pi_detail.vat_qty*pi_detail.unit_price*(1+pi_detail.tax_rate)):
                        check = 1
                        break
        return dict(Msg = check, type = type)
    
    @expose('json')
    def update_payment_date(self, **args):
        try:
            ids = ",".join([a.split("-")[1] for a in args.get('ids').split(",")])
            payment_date = args.get('payment_date');
            m_heads = MHead.find_by_ids(ids)
            for a in m_heads:
                a.payment_date = dt.strptime('%s00:00:00' % payment_date, "%Y-%m-%d%H:%M:%S")
                DBSession.merge(a)
                DBSession.flush()
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages = message, types = type , ids = ids, payment_date = payment_date)
            
    @expose('json')
    def ajax_delete_item(self,** kw):
        type = kw.get("type")
        id   = [kw.get("id")] if kw.get("id").find(",")<0 else kw.get("id").split(",")
        remark = {
                "action_type":"DELETE",
                "remark":"Delete PI"
        }
        if type in [const.ERP_HEAD_TYPE_PI, const.CHARGE_TYPE_S_MF, const.CHARGE_TYPE_S_NMF]:
            for i in id:
                pi = PiHead.get_by_id(i)
                for a in pi.pi_details: 
                    DBSession.delete(a)
                for b in pi.pcharges: 
                    DBSession.delete(b)
                DBSession.delete(pi)
                if type in [const.CHARGE_TYPE_S_MF, const.CHARGE_TYPE_S_NMF]:
                    remark['m_head_id'] = pi.m_head_id
                else: remark['p_head_id'] = pi.p_head_id
                remark['remark'] += " "+pi.invoice_no
        ARLog.insert(** remark)
        return dict(Msg = "sucees" )

                
    @expose('vatsystem.templates.ap.import_statement')
    def import_statement(self, ** kw):
        try:
            message = STHead.upload_file(** kw)
            if message: 
                flash(message)
        except:
            flash("Error!")
            traceback.print_exc()
        return dict(flag=1, kw = kw)
    
    @expose('json')
    def import_statement_dzd(self, ** kw):
        id = kw.get("id")
        try:
            type = 0
            STHead.scheduled_tasks()
            message = "Save Success!"
        except:
            type = 1
            message = "Error!"
            traceback.print_exc()
        return dict(type = type, message = "Save Success!")
    
    @expose('vatsystem.templates.ap.view_statement')
    def ajax_view_statement(self, ** args):
        start, end = 0, 0
        id = args.get('id')
        initPage  = 15
        pi_pager  = int(args.get('pi_pager', 0))
        dn_pager  = int(args.get('dn_pager', 0))
        st_head   = STHead.get(id) if id else None
        pi_amount = st_head.find_pi_amount()
        dn_amount = st_head.find_dn_amount()
        data = {}
        stdetails   = STHead.search_query(st_head.id, const.ERP_HEAD_TYPE_ST, **args)
        dndetails   = STHead.search_query(st_head.id, const.ERP_HEAD_TYPE_DN, **args)
        c_pi_amount = st_head.find_pi_amount(stdetails)
        c_dn_amount = st_head.find_dn_amount(dndetails)
        stdetails   = stdetails[pi_pager*initPage:(pi_pager+1)*initPage]
        dndetails   = dndetails[dn_pager*initPage:(dn_pager+1)*initPage]
        return dict(
                    st_head = st_head, 
                    stdetails = stdetails, 
                    dndetails = dndetails,
                    pi_pager = pi_pager,
                    dn_pager = dn_pager,
                    pi_amount = pi_amount,
                    dn_amount = dn_amount,
                    c_pi_amount = c_pi_amount,
                    c_dn_amount = c_dn_amount,
                    dzd_set_date_form = dzd_set_date_form,
                    dzd_pi_search_form = dzd_pi_search_form,
                    dzd_dn_search_form = dzd_dn_search_form
                    )  
    
    @expose('json')
    def ajax_get_date(self, ** args):
        rs, kws  = {}, {}
        id    = args.get('id')
        value = args.get('value').split('&')
        for a in value:
            k = a.split("=")
            if len(k) > 0:
                kws.update({k[0]:k[1]})
        supplier_code = kws.get('supplier_code')
        reconciliation_lot = kws.get('reconciliation_lot')
        nextChangeObj = args.get('nextChangeObj').split(",") if args.get('nextChangeObj') else []
        if args.get('type').upper() == const.ERP_HEAD_TYPE_PI:
            db = STDetail
        else:
            db = DNDetail
        for i in nextChangeObj:
            data = DBSession.query(distinct(getattr(db, i))).filter(db.st_head_id == id)
            if supplier_code:
                data = data.filter(db.supplier_code == supplier_code)
            if reconciliation_lot:
                data = data.filter(db.reconciliation_lot == reconciliation_lot)
            data = data.all()
            rs.update({i:[a[0] for a in data if a[0]]})
        return rs
    
    @expose('json')
    def ajax_update_dzd(self, ** args):
        try:
            id = args.get('id')
            complete = ['billing_month', 'kingdee_date', 'payment_date']
            if args.get('type').upper() == const.ERP_HEAD_TYPE_PI:
                db = STDetail
            else:
                db = DNDetail
            data = DBSession.query(db).filter(db.active == 0).filter(db.st_head_id == id)\
                    .filter(db.supplier_code == args.get('supplier_code')).filter(db.reconciliation_lot == args.get('reconciliation_lot')).all()
            for d in data:
                for i in complete:
                    k = args.get(i)
                    if k and not getattr(d, i):
                        if i == 'kingdee_date':
                            pidetails = DBSession.query(PiDetail).filter(PiDetail.st_detail_id == d.id).all()
                            for pidetail in pidetails:
                                pidetail.kingdee_date =  _get_lastday_Of_month(k.kingdee_date)
                                DBSession.merge(pidetail)
                        setattr(d, i, k)
                DBSession.merge(d)
            DBSession.flush()
            message,type = "Save Success!",0
        except:
            message,type = "Save Failure!",1
            traceback.print_exc()
        return dict(messages = message, types = type)
        
    
    @expose('json')
    def update_statement(self, ** args):
        id = args.get('st_head')
        category = args.get('category')
        if id:
            head  = STHead.get(id) if id else None
            if args.get('type') == 'Save':
                selects = args.get('select_id')
                selects = selects if isinstance(selects,list) else [selects]
                for a in selects:
                    if category == const.ERP_HEAD_TYPE_ST:
                        details = STDetail.get(a)
                    else:
                        details = DNDetail.get(a)
                    details = [details] if details else []
                    for a in  details:
                        keys = a.__table__.columns.keys()
                        for columnName in keys:
                            if category == const.ERP_HEAD_TYPE_DN:
                                if columnName == 'order_qty':
                                    obj = args.get('qty_%s_' % a.id)
                                elif columnName == 'unit_price':
                                    obj = args.get('unit_%s_' % a.id) 
                                else:
                                    obj = args.get('%s_%s_' % (columnName,a.id))
                            else:
                                if columnName == 'unit_price':
                                    obj = args.get('unit_%s' % a.id)
                                elif columnName in ['item_amount', 'item_base_amount'] and args.get('unit_%s' % a.id) and args.get('qty_%s' % a.id):
                                    obj = Decimal(args.get('unit_%s' % a.id, 0))* int(args.get('qty_%s' % a.id, 0))
                                else:
                                    obj = args.get('%s_%s' % (columnName,a.id))
                            if obj:
                                setattr(a, columnName, obj)
                                DBSession.merge(a)
                                DBSession.flush()
                        if a.status == "uncomplete" and category == const.ERP_HEAD_TYPE_ST:
                            STHead.update_invoice(a)
            elif args.get('type') == 'Delete':
                selects = args.get('select_id')
                selects = selects if isinstance(selects,list) else [selects]
                for a in selects:
                    if category == const.ERP_HEAD_TYPE_ST:
                        result = STDetail.get(a)
                    else:
                        result = DNDetail.get(a)
                    if hasattr(result, 'mpi_id') and result.mpi_id:
                        continue
                    if hasattr(result, 'msn_id') and result.msn_id:
                        continue
                    DBSession.delete(result)
                    DBSession.flush()
            else:
                if category == const.ERP_HEAD_TYPE_ST:
                    STHead.parse_match2(id)
                if category == const.ERP_HEAD_TYPE_DN:
                    STHead.parse_dndetails(id)
            message,type = "Save Success!",0
            
            st_head_status = 'complete'
            dn_details = DNDetail.find_details_by_status(id, "uncomplete")
            st_details = STDetail.find_details_by_status(id, "uncomplete")
            for g in chain(dn_details, st_details):
                if g.status == 'uncomplete':
                    st_head_status = 'uncomplete'
                    break
            head.status = st_head_status
            DBSession.merge(head)
            DBSession.flush()
        return dict(messages = message, types = type)
    
    @expose('json')
    def import_excel(self, ** args):
        result, periods = {}, {}
        from vatsystem.util.excel_helper import PIProceedsExcel, DNProceedsExcel, PICostExcel, DNCostExcel
        fileDir = os.path.join(os.path.abspath(os.path.curdir), "report_download")
        if not os.path.exists(fileDir): os.makedirs(fileDir)
        paths = [os.path.join(fileDir, 'PIProceedsExcel.xls'), os.path.join(fileDir, 'DNProceedsExcel.xls'), os.path.join(fileDir, 'PICostExcel.xls'), os.path.join(fileDir, 'DNCostExcel.xls')]
        excels = [PIProceedsExcel, DNProceedsExcel, PICostExcel, DNCostExcel]
        databases = [PIProceeds, DNProceeds, PICost, DNCost]
        period_keys = [['piproceeds_qty','piproceeds_amount' ], ['dnproceeds_qty', 'dnproceeds_amount'] , ['picost_qty', 'picost_amount'], ['dncost_qty', 'dncost_amount']]
        for index, path in enumerate(paths):
            excel = excels[index](templatePath = path)
            datas = excel.outputData()
            database = databases[index]
            period_key = period_keys[index]
            for data in datas:
                print data
                company_code = data['company_code']
                item_code    = data['item_code']
                date         = data['date']
                qty          = data.get('qty', 0) if data.has_key('qty') else data.get('order_qty', 0)
                amount       = data.get('base_amount', 0) if data.has_key('base_amount') else data.get('item_base_amount', 0)
                if not date or (index == 0 and item_code in const.CHARGE_CODES[u'\u589e\u503c\u7a0e']) or (index == 1 and item_code in const.CHARGE_CODES[u'\u589e\u503c\u7a0e']):continue
                date = int(date)
                key = '%s$%s$%s' % (company_code, item_code, date)
                if not qty:
                    qty = 0
                if periods.get(key):
                    if periods[key].get(period_key[0]):
                        periods[key][period_key[0]] += qty
                    else:
                        periods[key].update({period_key[0]:qty})
                    if periods[key].get(period_key[1]):
                        periods[key][period_key[1]] += amount
                    else:
                        periods[key].update({period_key[1]:amount})
                else:
                    periods.update({key:{period_key[0]:qty, period_key[1]:amount}})
                DBSession.add(database(**data))
                
        header = {}       
        for key1, value in periods.iteritems():
            company_code, item_code, date = key1.split('$')
            header_key = '%s$%s' % (company_code, date)
            if not header.get(header_key):
                header.update({header_key:{}})
            for period_key, period_value in value.iteritems():
                if not period_value:period_value = 0
                header[header_key].update({period_key:header[header_key].get(period_key, 0) + period_value})

            detail = PeriodDetail.get(item_code, date, company_code)
            if detail:
                for period_key, period_value in value.iteritems():
                    if hasattr(detail, period_key):
                        setattr(detail, period_key, getattr(detail, period_key) + Decimal(period_value))
                        DBSession.merge(detail)
            else:
                value.update({'item_code':item_code, 'date':date, 'company_code':company_code})
                DBSession.add(PeriodDetail(**value))
                
        for key2, value in header.iteritems():
            company_code, date = key2.split('$')
            detail = Period.get(date, company_code)
            if detail:
                for period_key, period_value in value.iteritems():
                    if hasattr(detail, period_key):
                        setattr(detail, period_key, getattr(detail, period_key) + Decimal(period_value))
                        DBSession.merge(detail) 
            else:
                value.update({'date':date, 'company_code':company_code})
                DBSession.add(Period(**value))
          
