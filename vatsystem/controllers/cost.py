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
from vatsystem.model import *
from vatsystem.model.erp import *
from vatsystem.util import const
from vatsystem.util.common import *
from vatsystem.widgets.ar import *
from vatsystem.widgets.cost import *
from vatsystem.util.excel_helper import *
from vatsystem.lib.base import BaseController


__all__ = ["COSTController"]

class COSTController(BaseController):
    
    allow_only = authorize.has_permission('cst')
    
    @expose('vatsystem.templates.cost.index')
    @tabFocus(tab_type='main')
    def index(self, ** kw):
        cust = 0
        collections = [[], 1, 1]
        viewPager, cust, display = 1, 0, 0
        if kw.get("viewPager"):
            viewPager = kw.get("viewPager")
        if kw.get("customer_code") or kw.get("customer_name"):
            cust = 1
        if kw.get('type') == const.SEARCH_TYPE_MSIMSO:
            kw.update({
                       'status':[const.VAT_THEAD_STATUS_POST, const.VAT_THEAD_STATUS_CONFIRMED], 
                       'co':'cost'
                       })
            collections = THead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.cost.list_thead')
        if kw.get('type') == const.SEARCH_TYPE_MCN:
            kw.update({
                       'status':[const.VAT_THEAD_STATUS_POST, const.VAT_THEAD_STATUS_CONFIRMED], 
                       'co':'cost'
                       })
            collections = CHead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.cost.list_chead')
        if kw.get('type') == const.SEARCH_TYPE_CST:
            collections = OHead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.cost.list_ohead')
        if kw.get('type') == const.SEARCH_TYPE_CCN:
            collections = NHead.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.cost.list_nhead')
        if kw.get('type') == const.SEARCH_TYPE_PI:
            collections = CpDetail.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.cost.list_pi')
        if kw.get('type') == const.SEARCH_TYPE_CHARGE:
            collections = CpCharge.find(** kw)
            override_template(self.index, 'mako:vatsystem.templates.cost.list_charge')
        if kw.get('type') == const.SEARCH_TYPE_VARIANCE:
            collections = CpDetail.find_variance(** kw)
            override_template(self.index, 'mako:vatsystem.templates.cost.list_variance')
        if cust ==0:
            display = 1
        else:
            if viewPager == 1:
                display = 1           
        results = dict(
                       kw = kw,
                       cust = cust,
                       display = display,
                       limit  = collections[2],
                       offset = collections[1],
                       collections = collections[0],
                       thead_search_form = thead_search_form,
                       chead_search_form = chead_search_form,
                       ohead_search_form = ohead_search_form,
                       nhead_search_form = nhead_search_form,
                       po_search_form = po_search_form,
                       charge_search_form = charge_search_form,
                       variance_search_form = variance_search_form
                       )
        return results
    
    @expose()
    def ajax_view_ohead(self, ** kw):
        print '*' * 80
        print 'ajax_view_ohead: %s' % kw
        print '*' * 80
        try:
            ohead = OHead.get(kw['id'])
            override_template(self.ajax_view_ohead, 'mako:vatsystem.templates.cost.view_ohead')
            return dict(flag = 0, oHead = ohead, ** kw)
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag = 1, ** kw)

    @expose()
    def ajax_view_nhead(self, ** kw):
        print '*' * 80
        print 'ajax_view_nhead: %s' % kw
        print '*' * 80
        try:
            nhead = NHead.get(kw['id'])
            override_template(self.ajax_view_nhead, 'mako:vatsystem.templates.cost.view_nhead')
            return dict(flag = 0, 
                        nHead = nhead, 
                        Other_Charges_From_Erps = [], 
                        Other_Charges_From_vats = [], 
                        ** kw
                        )
        except:
            flash("Error!")
            traceback.print_exc()
            return dict(flag = 1, ** kw)
    
    @expose('vatsystem.templates.cost.view_charge')
    def ajax_view_charge(self, ** kw):
        try:
            uicharges = []
            suppliers = []
            curr_charges = []
            head_type = kw.get('head_type')
            if head_type == const.ERP_HEAD_TYPE_CST:
                ohead = OHead.get(kw['id'])
                for co_detail in ohead.co_details:
                    relation_pi = co_detail.cp_details
                    for pi in relation_pi:
                        if pi.supplier not in suppliers:
                            suppliers.append(pi.supplier)       
                for supplier in suppliers:
                    kw.update({"supplier":supplier})
                    uicharge = UICharge.search_charge_erp(** kw)
                    for uic in uicharge:
                        uic_key = "%s_%s" % (uic.get('note_no'), uic.get('line_no'))
                        other_charge = CpCharge.get_charge_by_like(uic.get('note_no'), uic.get('line_no'))
                        if len(other_charge) > 0: continue
                        if not uic in uicharges:
                            uicharges.append(uic)
                return dict(flag = 0, oHead = ohead, uicharges = uicharges, ** kw)
        except:
            traceback.print_exc()

    @expose('vatsystem.templates.cost.view_new_pi')
    def ajax_view_new_pi(self, ** kw):
        try:
            rs = []
            id = kw.get('id')
            codetail = CoDetail.get(id)
            pidetails, picharges = CpDetail.find_pi_charge([codetail])
            for pidetail in pidetails:
                rs.append(pidetail)   
            return dict(id = id, oHead = codetail.o_head, pidetails = rs)
        except:
            traceback.print_exc()
    
    @expose('vatsystem.templates.cost.view_new_charge')
    def ajax_view_new_charge(self, ** kw):
        id = kw.get('id')
        ohead = OHead.get(id)
        codetails = ohead.co_details
        pidetails, picharges = CpDetail.find_pi_charge(codetails)
        return dict(id = id, oHead = ohead, picharges = picharges)
    
    @expose('json')
    def ajax_add_new_pi(self, ** kw):
        try:
            result = []
            ids = kw.get('ids').split(',')
            for id in ids:
                pro = id.split('_')
                codetail = CoDetail.get(pro[0])
                codetail.create_type = const.CREATE_NEW_PI
                pidetails = CpDetail.find_new_pi([codetail])
                for pidetail in pidetails:
                    if hasattr(pidetail, 'grn_no') and pidetail.co_detail_id == codetail.id and hasattr(pidetail, 'grn_line_no') and "%s_%s" % (pidetail.grn_no, pidetail.grn_line_no) == "%s_%s" % (pro[1], pro[2]):
                        pidetail.co_detail_id = codetail.id
                        cpdetails = CpDetail.findRelatePOPI(pidetail)
                        if cpdetails:
                            if cpdetails.pi_qty + pidetail.pi_qty <= cpdetails.po_qty:
                                cpdetails.pi_qty += pidetail.pi_qty
                            else:
                                cpdetails.pi_qty = cpdetails.po_qty
                            DBSession.merge(cpdetails) 
                        else:
                            pidetail.bridge_qty = pidetail.ava_pi_qty
                            cpdetails = CpDetail.find_detail_by_po_all(codetail.id, pidetail.po_no, pidetail.po_line_no)
                            for cpdetail in cpdetails:
                                if not cpdetail.grn_no and not cpdetail.grn_line_no:
                                    if cpdetail.po_qty >= pidetail.bridge_qty:
                                        if cpdetail.po_qty == pidetail.bridge_qty:
                                            DBSession.delete(cpdetail)
                                        else:
                                            cpdetail.po_qty = cpdetail.po_qty - pidetail.ava_pi_qty
                                            DBSession.merge(cpdetail)
                                        pidetail.pi_qty = pidetail.ava_pi_qty
                                        pidetail.po_qty = pidetail.ava_pi_qty
                                        pidetail.o_head_id = cpdetail.o_head_id
                                        pidetail.ae        = cpdetail.ae
                                        pidetail.unit_price = cpdetail.unit_price
                                        pidetail.description = cpdetail.description
                                        pidetail.pi_unit_price = cpdetail.unit_price
                                        pidetail.sales_contract_no = cpdetail.sales_contract_no
                                        result.append(pidetail)
                                        break
                                    else:
                                        pidetail.bridge_qty = pidetail.bridge_qty - cpdetail.po_qty 
                                        pidetail.pi_qty = cpdetail.po_qty
                                        pidetail.po_qty = cpdetail.po_qty
                                        pidetail.ae     = cpdetail.ae
                                        pidetail.o_head_id = cpdetail.o_head_id
                                        pidetail.unit_price = cpdetail.unit_price
                                        pidetail.pi_unit_price = cpdetail.unit_price
                                        pidetail.sales_contract_no = cpdetail.sales_contract_no
                                        pidetail.description = cpdetail.description
                                        result.append(pidetail)
                                        DBSession.delete(cpdetail)
            CpDetail.create(result, **kw)
            message, type = "Successfully!", 0
        except:
            message, type = "Save Failure!", 1
            traceback.print_exc()
        return dict(messages = message, types = type)

    @expose('json')
    def ajax_add_new_charge(self, ** kw):
        try:
            rs = []
            ids = kw.get('ids').split(',')
            for id in ids:
                pro = id.split('_')
                ohead = OHead.get(pro[0])
                kw.update({'o_head_id':ohead.id})
                cpcharges = ohead.cp_charges
                picharges = CpCharge.find_new_charge(ohead.co_details)
                for picharge in picharges:
                    if "%s_%s" % (picharge.pi_no, picharge.line_no) == "%s_%s" % (pro[1], pro[2]):
                        p = None
                        for cpcharge in cpcharges:
                            if picharge.cpcharge_id == cpcharge.id  and pf(cpcharge.po_total) > (cpcharge.total):
                                if cpcharge.pi_no and (picharge.pi_no != cpcharge.pi_no or picharge.pi_line_no != picharge.pi_line_no):
                                    continue
                                if pf(cpcharge.total) + pf(picharge.ava_total) > pf(cpcharge.po_total):
                                    cpcharge.total = cpcharge.po_total
                                else:
                                    cpcharge.total = float(cpcharge.total) + float(picharge.ava_total)
                                cpcharge.pi_no = picharge.purchase_invoice_no
                                cpcharge.pi_line_no = picharge.line_no
                                DBSession.merge(cpcharge)
                                p = True
                                break
                        if not p:
                            header = ohead
                            picharge.o_head_id = ohead.id
                            cpcharge = CpCharge.get(picharge.cpcharge_id)
                            picharge.ref           = header.ref
                            picharge.customer_code = header.customer_code
                            picharge.customer_name = header.customer_name
                            picharge.type     = const.CHARGE_TYPE_P_MAN
                            picharge.pi_no    = picharge.purchase_invoice_no
                            picharge.total    = float(picharge.ava_total)
                            picharge.ae       = cpcharge.ae
                            picharge.so_no    = cpcharge.so_no
                            CpCharge.create([picharge], **kw)
            message, type = "Successfully!", 0
        except:
            traceback.print_exc()
            message, type = "Save Failure!", 1
        return dict(messages = message, types = type)
                  
    @expose()
    def ajax_add_other_charge(self, ** kw):
        head_type = kw.get('head_type')
        if head_type == const.ERP_HEAD_TYPE_CST:
            select = kw.get('select_id')
            selects = [i.split(':') for i in select.split(',')] if select else None
            if selects:
                for s in selects:
                    if len(s) < 2:continue 
                    uidescrip = UI.find_by_note(s[0])
                    if not uidescrip:
                        continue
                    uicharges = UICharge.find_details_by_note_no(s[0], s[1])
                    for uicharge in uicharges:
                        if uidescrip.note_type == 'D':
                            uicharge.total   = - float(s[3])
                        uicharge.charge_code = uicharge.chg_discount_code
                        uicharge.supplier    = uidescrip.supplier
                        uicharge.note_no     = uidescrip.note_no
                        uicharge.note_type   = uidescrip.note_type
                        uicharge.status      = uidescrip.status
                        uicharge.note_date   = uidescrip.create_date
                        uicharge.remark      = uidescrip.remark
                        CpCharge.create([uicharge], **{'o_head_id':kw.get('id')})
                              
    @expose('json')
    def save_to_othead(self, ** kw):
        print '*' * 80
        print 'save_to_othead: %s' % kw
        print '*' * 80       
        try:
            if not THead._check_related(** kw):
                message, type = "You can't generate the CST cause the MSO hasn't been related SI!", 1
                return dict(messages = message, types = type) 
            if not OHead.check_po_by_so(** kw):
                message, type = "You can't generate the CST without the PO!", 1
                return dict(messages = message, types = type)
            ohead = OHead.create(** kw)
            ARLog.insert(**{
                            "o_head_id":ohead.id,
                            "action_type":"CREATE",
                            "remark":"Create CST"
                            })
            message = "Successfully!<br/>The CST No is: <a onclick=viewAll('/cost?type=%s&ref=%s')  href='javascript:void(0)' >%s<a>" % \
                            (const.SEARCH_TYPE_CST, ohead.ref, ohead.ref)
            type = 0
        except:
            message, type = "Save Failure!", 1
            traceback.print_exc()            
        return dict(messages = message, types = type)
    
    @expose('json')
    def update_to_othead(self, ** kw):
        try:
            rq = {}
            head_type = kw.get('head_type')
            if head_type == const.ERP_HEAD_TYPE_CST:
                head = OHead.get(kw.get('id'))
                rq.update({'o_head_id':head.id})
            else:
                head = NHead.get(kw.get('id'))
                rq.update({'n_head_id':head.id})
            remark = head.update_charges(** kw)
            rq.update({
                       "action_type":"DELETE" if kw.get('type') == 'Delete' else 'UPDATE',
                       "remark":remark
                       })
            ARLog.insert(** rq)
            message,type = "Successfully!", 0
        except:
            traceback.print_exc()
            message,type = "Save Failure!", 1
        return dict(messages = message, types = type)
    
    @expose('json')
    def save_to_nthead(self, ** kw):
        print '*' * 80
        print 'save_to_nthead: %s' % kw
        print '*' * 80       
        try:
            chead = CHead.find_thead_cst(** kw)
            if not chead:
                return dict(messages = "Save Failure!", types = 1)
            nhead = NHead.create(** kw)
            ARLog.insert(**{
                            "n_head_id":nhead.id,
                            "action_type":"CREATE",
                            "remark":"Create CNN"
                            })
            message = "Successfully!<br/>The CCN No is: <a onclick=viewAll('/cost?type=%s&ref=%s')  href='javascript:void(0)' >%s<a>" % \
                                        (const.SEARCH_TYPE_CCN, nhead.ref, nhead.ref)
            type = 0
        except:
            message,type = "Save Failure!", 1
            traceback.print_exc()            
        return dict(messages = message, types = type)

    @expose('json')
    def update_ohead_details(self, ** kw):
        print '*' * 80
        print 'update_thead_details: %s' % kw
        print '*' * 80
        try:
            oHead = OHead.get(kw['id'])
            detailRemark = oHead.update_details( ** kw)
            remark = {
                        "o_head_id":oHead.id,
                        "action_type":"UPDATE",
                        "remark":"Update "
                    }
            if detailRemark:
                remark['remark'] = detailRemark
                ARLog.insert( **remark)
            message, type = "Successfully!", 0
        except:
            message, type = "Failure!", 1
            traceback.print_exc()
        return dict(messages = message, types = type)
       
    @expose('json')
    def update_nhead_details(self, ** kw):
        print '*' * 80
        print 'update_chead_details: %s' % kw
        print '*' * 80
        try:
            nHead = NHead.get(kw['id'])
            detailRemark = nHead.update_details( ** kw)
            remark = {
                        "n_head_id":nHead.id,
                        "action_type":"UPDATE",
                        "remark":"Update "
                    }
            if detailRemark:
                if detailRemark:remark['remark'] += " Detail %s" % detailRemark
                ARLog.insert( **remark)
            message, type = "Successfully!", 0
        except:
            message, type = "Failure!", 1
            traceback.print_exc()
        return dict(messages = message, types = type)

    @expose('json')
    def update_all_ohead_vat_info(self, ** kw):
        print '*' * 80
        print 'update_all_thead_vat_info: %s' % kw
        print '*' * 80
        try:
            if getOnlyVatNo(kw['vat_no']):
                message, type = "Repeated VAT No.", 1
            else:
                OHead.update_all_vat_info(user=request.identity["user"], ** kw)
                message, type = "Successfully!", 0
        except:
            message,type = "Save Failure!", 1
            traceback.print_exc()
        return dict(messages = message, types = type, kws = kw)

    @expose('json')
    def update_all_nhead_vat_info(self, ** kw):
        print '*' * 80
        print 'update_all_chead_vat_info: %s' % kw
        print '*' * 80
        try:
            if getOnlyVatNo(kw['vat_no']):
                message, type = "Repeated VAT No.", 1
            else:
                NHead.update_all_vat_info(user=request.identity["user"], ** kw)
                message, type = "Successfully!", 0
        except:
            message, type = "Save Failure!", 1
            traceback.print_exc()
        return dict(messages = message, types = type, kws = kw)

    @expose('json')
    def update_all_ohead_status(self, ** kw):
        print '*' * 80
        print 'update_all_thead_status: %s' % kw
        print '*' * 80
        try:
            ids = kw.get("ids").split(",")
            OHead.update_all_status(user=request.identity["user"], ** kw)
            message, type = "Saved Successfully!", 0
            for i in ids:
                ARLog.insert(**{
                    "o_head_id":i,
                    "action_type":"UPDATE",
                    "remark":"Update Status %s" % kw.get("status")
                })
        except:
            traceback.print_exc()
            message, type = "Save Failure!", 1
        return dict(messages = message, types = type, kws = kw)

    @expose('json')
    def update_all_nhead_status(self, ** kw):
        print '*' * 80
        print 'update_all_chead_status: %s' % kw
        print '*' * 80
        try:
            ids = kw.get("ids").split(",")
            NHead.update_all_status(user=request.identity["user"], ** kw)
            message, type = "Save Successfully!", 0
            for i in ids:
                ARLog.insert(**{
                    "n_head_id":i,
                    "action_type":"UPDATE",
                    "remark":"Update Status %s" % kw.get("status")
                })
        except:
            message, type = "Save Failure!", 1
            traceback.print_exc()
        return dict(messages = message, types = type, kws = kw)
    
    @expose('vatsystem.templates.ar.view_history')
    def view_history(self, ** args):
        historys = ARLog.find(** args)
        return dict(historys = historys)
    
    @expose('json')
    def ajax_delete_item(self,** kw):
        type = kw.get("type")
        id   = list(set([kw.get("id")] if kw.get("id").find(",")<0 else kw.get("id").split(",")))
        remark = {
                "action_type":"DELETE",
                "remark":"Delete CST"
        }
        for i in id:
            coHead = CoHead.get(i)
            for a in coHead.co_details: 
                DBSession.delete(a)
            for b in coHead.charges: 
                DBSession.delete(b)
            remark['o_head_id'] = coHead.o_head_id
            remark['remark'] += " " + coHead.sales_contract_no
            DBSession.delete(coHead)
        ARLog.insert(**remark)
        return dict(Msg = "sucees" )
    
    @expose('json')
    def autocomplete(self, ** kw):
        db_dict = {}
        DB = DBSession
        if kw.get("form") == "_form0": 
            db_dict = {
                   "vat_t_head":["customer_code", "customer_name", "status", "ref", "vat_no" ],
                   "vat_si_head":["invoice_no"],
                   "vat_so_head":["sales_contract_no"],
                   "vat_si_detail":["item_no"],
                   "vat_so_detail":["item_no"]
                    }
        elif kw.get("form") == "_form1": 
            db_dict = {
                    "vat_c_head":["customer_code", "customer_name", "status", "ref", "thead_ref", "vat_no" ],
                    "vat_si_head":["invoice_no"],
                    "vat_so_head":["sales_contract_no"],
                    "vat_si_detail":["item_no"],
                    "vat_so_detail":["item_no"]
           }
        elif kw.get("form") == "_form2": 
            db_dict = {
                    "vat_o_head":["customer_code", "customer_name", "status", "ref", "thead_ref", "vat_no" ],
                    "vat_co_head":["invoice_no", "sales_contract_no"],
                    "vat_co_detail":["item_no"]
           }
        elif kw.get("form") == "_form3": 
            db_dict = {
                    "vat_n_head":["customer_code", "customer_name", "status", "ref", "chead_ref", "vat_no" ],
                    "vat_co_head":["invoice_no",  "sales_contract_no" ],
                    "vat_co_detail":["item_no"]
           }
        elif kw.get("form") == "_form4":
            db_dict = {
                    "vat_o_head":["customer_code", "customer_name", "ref", "ref", "chead_ref", "vat_no" ],
                    "vat_co_detail":["item_no", "sales_contract_no", "invoice_no"],
                    "vat_cp_detail":["po_no", "pi_no"]
           }
        elif kw.get("form") == "_form5":
            db_dict = {
                    "vat_o_head":["customer_code", "customer_name", "status", "ref", "chead_ref", "vat_no" ],
                    "vat_co_detail":["item_no", "sales_contract_no", "invoice_no"],
                    "vat_cp_detail":["po_no", "pi_no"]
           }
        elif kw.get("form") == "_form6":
            db_dict = {
                    "vat_cp_detail":["pi_no"],
                    "t_supl_note_charges":["note_no"]
           }
        
        if kw.get("type") == 'display_name':
            db_dict = {"tg_user":["display_name"]}
        type, q  = kw.get("type"), kw.get("q",'').strip()
        arr = OHead.auto_complete(DB, db_dict, type, q)
        return {"users": arr}
    
    @expose('json')
    def update_other_charges_vat_total(self,** kw):
        if kw.get('save'):
            for v in kw:
                if not v == "save" and not v == "checkbox_list":
                    charge = DBSession.query(OCharge).filter_by(id=int(v)).one()
                    query  = {"o_head_id":charge.o_head_id,"action_type":"UPDATE"}
                    mg = merge([charge.vat_total,charge.line_no],
                                [int(float(kw[v]))],
                                ['Vat Total','Line NO'])
                    if mg: query['remark'] = "Update Charge %s" % mg
                    charge.vat_total = int(float(kw[v]))
                    DBSession.merge(charge)
                    if query.get('remark'):
                        ARLog.insert( ** query)      
            message, type = "Save Success!", 0
                    
        if kw.get('delete'):
            if isinstance(kw['checkbox_list'],list):
                for i in  kw['checkbox_list']:
                    charge = DBSession.query(OCharge).filter_by(id=int(i)).one()
                    DBSession.delete(charge)
                    ARLog.insert(**{
                        "o_head_id":charge.o_head_id,
                        "action_type":"DELETE",
                        "remark":"Delete Other Charge %s %s" % (charge.charge_code,round(charge.total,2))
                    })
            else:
                    charge = DBSession.query(OCharge).filter_by(id=int(kw['checkbox_list'])).one()
                    DBSession.delete(charge)
                    ARLog.insert(**{
                        "o_head_id":charge.o_head_id,
                        "action_type":"DELETE",
                        "remark":"Delete Other Charge %s %s" % (charge.charge_code,round(charge.total,2))
                    })
            message, type = "Delete Success!", 0
        return dict(messages = message, types = type)
       
    
    @expose('json')
    def update_variance(self, ** kw):
        try:
            ids = kw.get('ids', '').split(',')
            for id in ids:
                variance, grn_no, grn_line_no ,pi_no, charge_code, line_no, type, note_no = None, None, None, None, None, None, None, None
                if len(id.split('$')) == 2:
                    type = const.ERP_TYPE_DETAIL
                    grn_no, grn_line_no = id.split('$')
                elif len(id.split('$')) == 3:
                    no, type, line_no = id.split('$')
                    if type == const.ERP_TYPE_CHARGE:
                        pi_no = no
                    else:
                        note_no = no 
                else:
                    continue
                args = {
                        'grn_no':grn_no,
                        'grn_line_no':grn_line_no,
                        'pi_no':pi_no,
                        'line_no':line_no, 
                        'type':int(type),
                        'note_no':note_no,
                        'currency':kw.get('currency_%s' % id),
                        'designation':kw.get('designation_%s' % id),
                        'exchange_rate':kw.get('exchange_rate_%s' % id),
                        'supplier_short_name':kw.get('supplier_short_name_%s' % id),
                        'so_no':kw.get('so_no_%s' % id),
                        'po_no':kw.get('po_no_%s' % id),
                        'pi_no':kw.get('pi_no_%s' % id),
                        'item_no':kw.get('item_no_%s' % id),
                        'billing_month':kw.get('billing_month_%s' % id),
                        'change_project':kw.get('change_project_%s' % id),
                        'variance_date':kw.get('variance_date_%s' % id),
                        'related':kw.get('related_%s' % id)
                        }
                with_out_amount = kw.get('with_out_amount_%s' % id)
                variance_price =  kw.get('variance_price_%s' % id)
                with_out_price =  kw.get('with_out_price_%s' % id)
                variance_amount = kw.get('variance_amount_%s' % id)
                change_with_out_amount = kw.get('change_with_out_amount_%s' % id)
                change_with_out_price  = kw.get('change_with_out_price_%s' % id)
                po_qty = kw.get('po_qty_%s' % id)
                if po_qty:
                    args.update({'po_qty':po_qty})
                if with_out_amount:
                    args.update({'with_out_amount':with_out_amount})
                if change_with_out_amount:
                    args.update({'change_with_out_amount':change_with_out_amount})
                if variance_amount:
                    args.update({'variance_amount':variance_amount})
                if variance_price:
                    args.update({'variance_price':variance_price})
                if with_out_price:
                    args.update({'with_out_price':with_out_price})
                if change_with_out_price:
                    args.update({'change_with_out_price':change_with_out_price})
                variance = Variance(**args)  
                DBSession.add(variance)
            DBSession.flush()
            message, type = "Save Successfully!", 0
        except:
            traceback.print_exc()
            message, type = "Save Failure!", 1
        return dict(messages = message, types = type)
    
    @expose('json')
    def add_charge_variance(self, ** kw):
        try:
            pi_no = kw.get('pi_no')
            vid = kw.get('vid')
            if not isinstance(vid, list):
                vid = [vid]
            for line_no in vid:
                charges = PICharge.find_charge_by_item_code(pi_no, None, None, line_no)
                for charge in charges:
                    args = {
                            'pi_no':charge.purchase_invoice_no,
                            'total':charge.total,
                            'line_no':charge.line_no,
                            'charge_code':charge.charge_code
                            }
                    charge = Variance_Charge(**args)
                    DBSession.add(charge)
            DBSession.flush()
            message, type = "Save Successfully!", 0
        except:
            traceback.print_exc()
            message, type = "Save Failure!", 1
        return dict(messages = message, types = type)

            
    @expose('json')
    def delete_variance_charge(self, ** kw):
        try:
            vid = kw.get('vid')
            if vid:
                if not isinstance(vid, list):
                    vid = [vid]
                for id in vid:
                    charge = Variance_Charge.get(id)
                    DBSession.delete(charge)
            message, type = "Save Successfully!", 0
        except:
            traceback.print_exc()
            message, type = "Save Failure!", 1
        return dict(messages = message, types = type)
    
    

        
            
        
        
            
         
            
          
