#-*- coding: utf-8 -*-
import os
import uuid
import operator
import decimal,copy
import datetime
import random
from chardet import detect
from itertools import *  
from datetime import datetime as dt
from pylons.decorators.cache import beaker_cache
from sqlalchemy import *
from sqlalchemy import or_
from sqlalchemy.sql import and_
from vatsystem.model import *
from vatsystem.util import const
from vatsystem.util.common import *
from vatsystem.util.db_extend import *
from vatsystem.util.mako_filter import *
from copy import deepcopy

os.environ["NLS_LANG"] = "american_america.al32utf8"

def Decimal(i):
    return decimal.Decimal(str(i)) if i else 0
    
def merge(mod, obj, cat):
    a = []
    for k,v in enumerate(obj):
        if mod[k] or v:
            check = comp(mod[k] , v)
            if check[0]:
                a.append(cat[k]+" '"+check[1]+"' to '"+check[2]+"'")
    return "["+cat[-1]+str(mod[-1])+": "+",".join(a)+"]" if len(a)>0 else None


def getOnlyVatNo(vatNo):
    vatList = []
    if vatNo.find(",") > -1: 
        for i in vatNo.split(","):
            if i.find("~") > -1:
                i = i.split("~")
                for v in range(int(i[0]), int(i[1]) + 1):
                    vatList.append(v)
            else:
                vatList.append(int(i))
    else:
        if vatNo.find("~") > -1:
            i = vatNo.split("~")
            for i in range(int(i[0]), int(i[1]) + 1):
                vatList.append(i)
        else:
            vatList.append(int(vatNo))
    getVatNoList1 = DBSession.query(distinct(CHead.vat_no))
    getVatNoList2 = DBSession.query(distinct(THead.vat_no))
    getVatNoList3 = DBSession.query(distinct(PHead.vat_no))
    getVatNoList4 = DBSession.query(distinct(SHead.vat_no))
    getVatNoList5 = DBSession.query(distinct(OHead.vat_no))
    getVatNoList6 = DBSession.query(distinct(NHead.vat_no))
    getVatNoList  = getVatNoList1.union(getVatNoList2, getVatNoList3, getVatNoList4, getVatNoList5, getVatNoList6).all()
    for c in vatList:
        for d, a in enumerate(getVatNoList):
            if a[0] and a[0].find(",") > -1:
                for b in a[0].split(","):
                    if b.find("~") > -1:
                        bsp = b.split("~")
                        if (int(bsp[0]) < c or int(bsp[0]) == c) and (int(bsp[1]) > c or int(bsp[1]) == c):
                            return True
                    else:
                        if int(b) == c:
                            return True
            else:
                if a[0] and a[0].find("~") > -1:
                    asp = a[0].split("~")
                    if (int(asp[0]) < c or int(asp[0]) == c) and (int(asp[1]) > c or int(asp[1]) == c):
                        return True
                else:
                    if a[0] and int(a[0]) == c:
                        return True
                    
def _get_charge_code(charge):
    if charge.__tablename__ in ['t_supl_note_charges', 't_cust_note_charges']:
        charge_code = charge.chg_discount_code
    else:
        charge_code = charge.charge_code
    return charge_code

 
def _all_rewrite_price_and_filter_charges(charge_list, detail_list):
       
    rate =  1.17
    tax_rate = 0.17
    include_tax = 0
    detail_total, charge_total, curr_charge, per_charge = 0, 0, 0, 0
    res_details, res_charges, curr_charges, tax_charges  = [], [], [], []
    charge_list = copy.deepcopy(charge_list)
    detail_list = copy.deepcopy(detail_list)
    
    for charge in charge_list:
        if not _get_charge_code(charge) in const.CHARGE_CODES.get(u'\u589e\u503c\u7a05-\u61c9\u4ed8'):
            curr_charges.append(charge)
            charge_total += float(charge.total)
            if hasattr(charge, 'percentage') and charge.percentage:
                per_charge += float(charge.total)
        else:
            tax_charges.append(charge)
            
    for detail in detail_list:
        if hasattr(detail, 'supplier') and detail.supplier in const.TAX_PERCENTAGE_SUPPLIER:
            rate = 1.03
            tax_rate = 0.03
        if hasattr(detail, 'supplier') and detail.supplier in const.TAX_PERCENTAGE_SUPPLIER_0: 
            rate = 1
            tax_rate = 0
            
        if detail.__tablename__ in ['t_supl_note_dtl', 't_cust_note_dtl']:
            detail_total += float(detail.note_qty * detail.unit_price)
        else:
            detail_total += float(detail.qty * detail.unit_price)
  
    if len(tax_charges) == 0:
        for detail in detail_list:
            detail.is_rate = 0
            detail.tax_rate = tax_rate
            print "?"*30, detail.unit_price,rate
            detail.unit_price = pf(float(detail.unit_price)/rate)
            res_details.append(detail)
        for charge in charge_list:
            charge.is_rate = 0
            charge.tax_rate = tax_rate
            charge.total = float(charge.total)/rate
            res_charges.append(charge)
    else:
        if len(tax_charges) > 2:
            tax_charge_total = 0
            for tax_charge in tax_charges:
                tax_charge_total += float(tax_charge.total)
            all_no_vat = charge_total + detail_total - per_charge
            for ctax_rate in const.TAX_PERCENTAGE_LIST:
                if  -0.01 <= ctax_rate * all_no_vat/tax_charge_total - 1 <= 0.01:
                    include_tax = 2
                    break
            if include_tax == 2:
                res_details = detail_list
                res_charges = curr_charges
            else:
                res_details = detail_list
                res_charges = charge_list 
        else:
            type = []
            for tax_charge in tax_charges:
                total = float(tax_charge.total)
                for ctax_rate in const.TAX_PERCENTAGE_LIST:
                    if total != 0 and  -0.01 <= ctax_rate * detail_total/total - 1 <= 0.01:
                        include_tax = 2
                        type.append(1)
                        tax_rate = float(ctax_rate)
                        rate = 1 + tax_rate
                        break
                    elif  total != 0 and -0.01<= ctax_rate * (charge_total - per_charge)/total - 1 <= 0.01:
                        include_tax = 2
                        type.append(2)
                        tax_rate = float(ctax_rate)
                        rate = 1 + tax_rate
                        break
                    else:
                        if tax_charge not in res_charges:
                            res_charges.append(tax_charge)
            
            if 1 not in type and len(type) == 1 and len(res_charges) == 0:
                for detail in detail_list:
                    detail.is_rate = 0
                    detail.tax_rate = tax_rate
                    detail.unit_price = pf(float(detail.unit_price)/rate)
                    res_details.append(detail)
            else:
                res_details.extend(detail_list)
                 
            if 2 not in type and len(type) == 1 and len(res_charges) == 0:
                for charge in curr_charges:
                    charge.is_rate = 0
                    charge.tax_rate = tax_rate
                    charge.total = float(charge.total)
                    if hasattr(charge, 'percentage') and not charge.percentage:
                        charge.total = charge.total/rate
                    res_charges.append(charge)
            else:
                if 2 in type and len(type) == 1:
                    for charge in curr_charges:
                        charge.total = float(charge.total)
                        if hasattr(charge, 'percentage') and charge.percentage:
                            charge.total = charge.total/rate
                        res_charges.append(charge)
                else:
                    res_charges.extend(curr_charges) 
               
            if len(type) == 0:
                tax_charge_total = 0
                for tax_charge in tax_charges:
                    tax_charge_total += float(tax_charge.total)
                all_no_vat = charge_total + detail_total
                for ctax_rate in const.TAX_PERCENTAGE_LIST:
                    if  tax_charge_total != 0 and -0.01 <= ctax_rate * all_no_vat/tax_charge_total - 1 <= 0.01:
                        include_tax = 2
                        break
                if include_tax == 2:
                    res_details = detail_list
                    res_charges = curr_charges
                else:
                    res_details = detail_list
                    res_charges = charge_list 
               
    return res_details, res_charges, include_tax
    

def _check_cn_rewrite_charges(invoice_no, si_details, cn_details): 
    type = []
    if len(si_details) == len(cn_details):
        for a in si_details:
            for b in cn_details:
                if a.item_no == b.item_no:
                    if  a.qty == b.note_qty:
                        type.append(1)
                    else:return 0         
    else:
        return 0   
    return 1 if 1 in type else 0

def _ap_check_cn_rewrite_charges(invoice_no, si_details, cn_details):
    type = []
    if len(si_details) == len(cn_details):
        for a in si_details:
            for b in cn_details:
                if a.item_no == b.item_no and a.line_no == b.pi_line_no:
                    if  a.qty == b.note_qty:
                        type.append(1)
                    else:return 0         
    else:
        return 0   
    return 1 if 1 in type else 0                

def _fetch_sql_to_dict(sql, _DBSession = DBSession, start = 0, end = 0):
    result_dict = {}
    for i in _DBSession.execute(sql).fetchall():
        key = int(i[0]) if str(i[0]).isdigit() else str(i[0])
        if start == 0 and end == 0:
            result_dict.update({key:i[1]})
        else:
            result_dict.update({key:i[start:end]})
    return result_dict

def _row2dict(row):
    d = {}
    for columnName in row.__table__.columns.keys():
        d[columnName] = getattr(row, columnName)
    return d


class SO(Table_SO):

    customer_short_name, qty, invoiced_qty, available_qty, mso_qty, mcn_qty, charge_total, available_total, mso_total, mcn_total  = ('', 0, 0, 0, 0, 0, 0, 0, 0, 0)

    @classmethod
    def get(cls, sales_contract_no):
        return DBSession2.query(cls).filter(cls.sales_contract_no == sales_contract_no).filter(cls.company_code.in_(getCompanyCode())).first()
    
    @classmethod
    def find(cls, ** args):
        args['status'] = ['C','N','D']
        page, limit, cate = 500, 0, const.VAT_PAGE_NEXT
        queryExtend = QueryExtend(cls, ** args)
        customer_name = args.get('customer_name', '')
        if args.get("page"):
            limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == const.VAT_PAGE_PRE:
            cate, limit, offset = const.VAT_PAGE_PRE, int(args.get("limit")), int(args.get("offset"))
        return cls.paset_result(queryExtend, limit, offset, [], limit, cate, customer_name, args)

    @classmethod
    def paset_result(cls, QueryExtend, limit, offset, results, flimit, cate, customer_name, args):
        tax_total, next_page = 0, limit
        QueryExtend.query_all(False if args.get('all') else True, DBSession2, True, limit,offset, ** {
                      const.QUERY_TYPE_NOT_EQ: ['status'],
                      const.QUERY_TYPE_LIKE: ['sales_contract_no', 'customer_code'],
                      const.QUERY_TYPE_DATE: [('create_date', 'date_from', 'date_to')],
                      const.QUERY_TYPE_ORDER_BY: ['create_date'],
                      const.QUERY_TYPE_COMPANY_CODE: ['company_code']
                    })
        
        queryExtend_result = QueryExtend.result
        
        if len(queryExtend_result)==0:return results, next_page, flimit
        
        for i in QueryExtend.result:
            next_page += 1
            i = cls.find_by_so_no(i.sales_contract_no, i)
            if i.available_qty > 0 and (not customer_name or (i.customer_name + i.customer_short_name).find(customer_name) > -1):
                results.append(i)
            if len(results) > 24  and not args.get('all'):break

        if len(results) < 25 and cate == 'next' and not args.get('all'):
            limit = offset
            offset = offset+500
            return cls.paset_result(QueryExtend, limit, offset, results, flimit, cate, customer_name, args)
        else:
            return results, next_page, flimit
        
    @classmethod
    def find_by_so_no(cls, so_no, i = None):
        if not i:
            i = cls.get(so_no)
        so_details = SOD.find_sod(so_no)
        so_charges = SOCharge.find(so_no)
        so_details, so_charges, include_tax = _all_rewrite_price_and_filter_charges(so_charges, so_details)
        
        qty, invoiced_qty = 0, 0
        for so_detail in so_details:
            qty += int(so_detail.qty)
            if so_detail.invoiced_qty:
                invoiced_qty += int(so_detail.invoiced_qty)
                
        charge_total = 0
        for so_charge in so_charges:
            charge_total += so_charge.total
        
        i.qty = qty
        i.invoiced_qty = invoiced_qty
        i.charge_total  = charge_total
        i.mso_qty = SoHead.find_t_so_head_qty_key(so_no).get(so_no, 0)
        sid_msod = THead.base_mos_mcn_si_qty(so_no)
        mso_mcn_si_qty = THead.get_mso_mcn(sid_msod[0], sid_msod[1])
        i.available_qty = int(i.qty - i.invoiced_qty - (mso_mcn_si_qty[0] - mso_mcn_si_qty[2]) + (mso_mcn_si_qty[1] - mso_mcn_si_qty[4]))
        i.mcn_qty = mso_mcn_si_qty[1]
        i.mso_total = Charge.find_t_so_charge_total_dict(so_no).get(so_no, 0)
        i.mcn_total = Charge.find_c_so_charge_total_dict(so_no).get(so_no, 0)
        i.available_total = Decimal(i.charge_total) - Decimal(i.mso_total) + Decimal(i.mcn_total)
        i.customer_short_name = Customer.get(i.customer_code).cust_short_name
        return i
    
    
    @classmethod
    def find_so_head_qty_dict(cls):
        sql = '''
                SELECT TSH.SALES_CONTRACT_NO, so_dtl.QTY, so_dtl.Invoice_Qty FROM T_SALES_CONTRACT_HDR tsh,
                    (SELECT tsd.SALES_CONTRACT_NO,SUM(tsd.BASE_QTY) Qty,SUM(decode(tsd.INVOICED_QTY,null,0,tsd.INVOICED_QTY)) Invoice_Qty FROM T_SALES_CONTRACT_DTL tsd WHERE tsd.company_code in %s GROUP BY tsd.SALES_CONTRACT_NO ) so_dtl
                    WHERE tsh.company_code in %s AND tsh.STATUS NOT IN ('C','N','D')
                    AND tsh.SALES_CONTRACT_NO=so_dtl.SALES_CONTRACT_NO
                    AND so_dtl.Invoice_Qty<>so_dtl.Qty
                ''' % (getCompanyCode(1), getCompanyCode(1))
        return _fetch_sql_to_dict(sql, DBSession2, start=1, end=3)
    
    @classmethod
    def find_so_head_qty(cls, sale_no):
        sql = '''
                SELECT so_dtl.SALES_CONTRACT_NO, so_dtl.QTY, so_dtl.Invoice_Qty FROM (SELECT tsd.SALES_CONTRACT_NO,SUM(tsd.BASE_QTY) Qty,SUM(decode(tsd.INVOICED_QTY,null,0,tsd.INVOICED_QTY)) Invoice_Qty 
                    FROM T_SALES_CONTRACT_DTL tsd WHERE tsd.company_code in %s GROUP BY tsd.SALES_CONTRACT_NO ) so_dtl WHERE   so_dtl.Invoice_Qty<>so_dtl.Qty  AND so_dtl.SALES_CONTRACT_NO='%s'
                    ''' % (getCompanyCode(1),sale_no)
        return _fetch_sql_to_dict(sql, DBSession2, start=1, end=3)
    
    @classmethod
    def find_qty_to_dict(cls, ** args):
        sql = '''
                SELECT TSH.SALES_CONTRACT_NO, so_dtl.QTY, so_dtl.Invoice_Qty FROM T_SALES_CONTRACT_HDR tsh,
                    (SELECT tsd.SALES_CONTRACT_NO,SUM(tsd.BASE_QTY) Qty,SUM(tsd.INVOICED_QTY) Invoice_Qty FROM T_SALES_CONTRACT_DTL tsd WHERE tsd.company_code in %s GROUP BY tsd.SALES_CONTRACT_NO ) so_dtl
                    WHERE tsh.company_code in %s AND tsh.STATUS NOT IN ('C','N','D')
                    AND tsh.SALES_CONTRACT_NO=so_dtl.SALES_CONTRACT_NO
                    AND so_dtl.Invoice_Qty<>so_dtl.Qty
                ''' % (getCompanyCode(1), getCompanyCode(1))
        result_dict = {}
        for i in DBSession2.execute(sql).fetchall():
            result_dict.update({i[0]:i[1:3]})
        return result_dict
    
    @classmethod
    def customer_codes(cls, ** args):
        customer_code, customer_type, customer_name, date_from, date_to = (args.get(i, '').strip() for i in ['customer_code', 'customer_type', 'customer_name', 'date_from', 'date_to'])
        customers = Customer.find_all_customer_by_type(customer_type)
        data = DBSession2.query(distinct(cls.customer_code)).filter(cls.create_date <= dt.strptime(date_to + " 23:59:59", "%Y-%m-%d %H:%M:%S"))\
                            .filter(cls.create_date >= dt.strptime(date_from + " 00:00:00", "%Y-%m-%d %H:%M:%S")).filter(cls.company_code.in_(getCompanyCode()))
        if customer_code:
            data = data.filter(cls.customer_code == customer_code)
        if customer_name:
            data = data.filter(cls.customer_name == customer_name)
        customer_codes = data.all()
        return [i[0] for i in customer_codes if (customer_type and i[0] in customers) or not customer_type]
    
    @classmethod
    def find_so_no_by_customer_code(cls, ** args):
        result = []
        customer_code, date_from, date_to = (args.get(i, '').strip() for i in ['customer_code', 'date_from', 'date_to'])
        so_nos  = DBSession2.query(distinct(cls.sales_contract_no)).filter(cls.customer_code == customer_code).filter(cls.create_date <= dt.strptime(date_to + " 23:59:59", "%Y-%m-%d %H:%M:%S"))\
                            .filter(cls.create_date >= dt.strptime(date_from + " 00:00:00", "%Y-%m-%d %H:%M:%S")).filter(cls.company_code.in_(getCompanyCode())).all()
        for so_no in so_nos:
            so = cls.find_by_so_no(so_no[0])
            if so and so.available_qty > 0:
               result.append(so) 
        return [i.sales_contract_no for i in result]
    

class SOD(Table_SOD):

    mso_qty, mcn_qty, available_qty, available_total, mso_total, mcn_total = (0, 0, 0, 0, 0, 0)

    @classmethod
    def find(cls, sales_contract_no):
        detail_list, charge_list = [], []
        tax_total = 0
        tdetail_qty_dict = SoDetail.find_t_so_detail_qty_dict(sales_contract_no)
        cdetail_qty_dict = SoDetail.find_c_so_detail_qty_dict(sales_contract_no)
        total_dict = SICharge.find_si_charge_total_dict()
        sid_msod = THead.base_mos_mcn_si_qty(sales_contract_no)
        so_result = _all_rewrite_price_and_filter_charges(SOCharge.find(sales_contract_no), cls.find_sod(sales_contract_no))
        sods = so_result[0]
        socharges = so_result[1]
        for i in sods:
            key = i.line_no
            i.mso_qty = tdetail_qty_dict.get(key, 0)
            if not i.invoiced_qty: i.invoiced_qty = 0
            mso_mcn_si_qty = THead.get_mso_mcn(sid_msod[0], sid_msod[1], i.line_no, i.item_no)
            i.available_qty = i.base_qty - i.invoiced_qty - (mso_mcn_si_qty[0] - mso_mcn_si_qty[2]) + (mso_mcn_si_qty[1] - mso_mcn_si_qty[4])
            i.mcn_qty = mso_mcn_si_qty[1]
            unit_prices = Decimal(i.unit_price)
            tax_total += Decimal(const.TAX_PERCENTAGE) * (Decimal(i.unit_price) * Decimal(i.base_qty))
            if i.available_qty > 0: 
                detail_list.append(i)
        tcharge_total_dict = Charge.find_t_so_charge_total_dict(sales_contract_no)
        ccharge_total_dict = Charge.find_c_so_charge_total_dict(sales_contract_no)
        for i in socharges:
            key = i.line_no
            i.mso_total = tcharge_total_dict.get(key, 0)
            i.mcn_total = ccharge_total_dict.get(key, 0)
            i.available_total = float(i.total) - float(i.mso_total) + float(i.mcn_total)
            if pf(i.available_total) != 0:
                charge_list.append(i)
        return detail_list, charge_list

    @classmethod
    def find_so_detail_qty_dict(cls, sales_contract_no):
        result_dict = {}
        for i in DBSession2.query(cls).filter(cls.sales_contract_no == sales_contract_no).filter(cls.company_code.in_(getCompanyCode())).all():
            result_dict.update({i.line_no:[i.base_qty, i.invoiced_qty]})
        return result_dict
    
    @classmethod
    def find_sod(cls, sales_contract_no):
        return DBSession2.query(cls).filter(cls.sales_contract_no == sales_contract_no).filter(cls.company_code.in_(getCompanyCode())).all()

class SOCharge(Table_SOCharge):

    type = 'SO'
    mso_total, mcn_total, available_total = (0, 0, 0)

    @classmethod
    def find(cls, sales_contract_no):
        return DBSession2.query(cls).filter(cls.sales_contract_no == sales_contract_no).filter(cls.company_code.in_(getCompanyCode())).all()

    @classmethod
    def find_so_charge_total_dict(cls, sales_contract_no=None):
        if not sales_contract_no:
            sql = '''
                        select tsc.SALES_CONTRACT_NO,sum(tsc.TOTAL) Total from t_sales_contract_charges tsc
                            where tsc.company_code in %s
                            group by tsc.SALES_CONTRACT_NO
                            having sum(tsc.TOTAL)<>0
                    ''' % getCompanyCode(1)
            return _fetch_sql_to_dict(sql, DBSession2)
        else:
            result_dict = {}
            for i in cls.find(sales_contract_no):
                result_dict.update({i.line_no:i.total})
            return result_dict
        
    @classmethod
    def get_so_vat_charge_total(cls, sales_contract_no = None):
        get_item_sql = '''SELECT "SUM"(TOTAL_AMT)*0.17 FROM "RPAC"."T_SALES_CONTRACT_DTL" where SALES_CONTRACT_NO='%s' ''' % (sales_contract_no)
        get_item = DBSession2.execute(get_item_sql).fetchone()
        get_charge_sql = '''SELECT "SUM"(TOTAL) FROM "RPAC"."T_SALES_CONTRACT_CHARGES" where SALES_CONTRACT_NO='%s' and CHARGE_CODE like '%s' ''' % (sales_contract_no,u'增值稅%')
        get_charge = DBSession2.execute(get_charge_sql).fetchone()
        get_charge2_sql = '''SELECT "SUM"(TOTAL) FROM "RPAC"."T_SALES_CONTRACT_CHARGES" where SALES_CONTRACT_NO='%s' and CHARGE_CODE not like '%s' ''' % (sales_contract_no,u'增值稅%')
        get_charge2 = DBSession2.execute(get_charge2_sql).fetchone()
        get_item = float(get_item[0]) if len(get_item)>0 else 0
        if len(get_charge)>0: get_charge = float(get_charge[0]) if get_charge[0] else 0
        else: get_charge = 0
        if len(get_charge2)>0: get_charge2 = float(get_charge2[0]) if get_charge2[0] else 0
        else: get_charge2 = 0
        if -0.5 <= get_item-get_charge and 0.5 >= get_item-get_charge: get_charge = 0  
        return get_charge2+get_charge
    
    @classmethod
    def get_so_vat_charge_parse(cls,sales_contract_no=None):
        other_charge_sql = "SELECT DECODE(SUM(TCC.TOTAL),NULL,0,SUM(TCC.TOTAL)) sale_no2 FROM T_SALES_CONTRACT_CHARGES TCC WHERE TCC.CHARGE_CODE not like '%s' AND TCC.company_code in %s AND TCC.SALES_CONTRACT_NO='%s'" % ( u'增值稅%', getCompanyCode(1), sales_contract_no )
        other_charge_sql = DBSession2.execute(other_charge_sql).fetchone()[0]
        sql = '''
                SELECT TSCD.sTotal,TSCC.cTotal,
                    CASE
                    WHEN 0.5>abs(TSCD.sTotal-TSCC.cTotal)
                    THEN 0
                    ELSE TSCC.cTotal 
                    end result
                    FROM 
                    (SELECT SUM(TSC.TOTAL_AMT)*0.17 sTotal,TSC.SALES_CONTRACT_NO sale_no1 FROM T_SALES_CONTRACT_DTL TSC WHERE TSC.company_code in %s GROUP BY SALES_CONTRACT_NO) TSCD,
                    (SELECT SUM(TCC.TOTAL) cTotal,TCC.SALES_CONTRACT_NO sale_no2  FROM T_SALES_CONTRACT_CHARGES TCC WHERE TCC.CHARGE_CODE like '%s' AND TCC.company_code in %s GROUP BY TCC.SALES_CONTRACT_NO) TSCC
                    where TSCC.SALE_NO2 = TSCD.SALE_NO1 
                    AND TSCC.SALE_NO2='%s'
        ''' % (getCompanyCode(1), u'增值稅%', getCompanyCode(1), sales_contract_no )
        res = DBSession2.execute(sql).fetchone()
        return  other_charge_sql + res[2] if res else other_charge_sql
               
               
class SI(Table_SI):

    qty, available_qty,ri_qty, msi_qty, mcn_qty, charge_total, ri_total, available_total, msi_total, mcn_total = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
    
    @classmethod
    def get(cls, invoice_no):
        return DBSession2.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.company_code.in_(getCompanyCode())).first()

    @classmethod
    def find(cls,** args):
        tax_total, page, limit, cate, args['status'] = 0, 25, 0, const.VAT_PAGE_NEXT, 'C'
        queryExtend = QueryExtend(cls, ** args)
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == const.VAT_PAGE_PRE:
            cate, limit, offset  = const.VAT_PAGE_PRE, int(args.get("limit", 0)), int(args.get("offset", 0))
        return cls.paset_result(queryExtend, limit, offset, [], limit, cate, args)

    @classmethod
    def paset_result(cls, QueryExtend, limit, offset, results, flimit, cate, args):
        type = args.get('type')
        tax_total, next_page = 0, limit
        QueryExtend.query_all(False if (type == const.SEARCH_TYPE_GROUP_SI or args.get('all')) else True, DBSession2, True, limit, offset, ** {
                      const.QUERY_TYPE_NOT_EQ: ['status'],
                      const.QUERY_TYPE_LIKE: ['invoice_no', ('customer', 'customer_code')],
                      const.QUERY_TYPE_LIKE_AND_OR: [('customer_name', 'customer_name', 'customer_short_name')],
                      const.QUERY_TYPE_DATE: [('create_date', 'date_from', 'date_to')],
                      const.QUERY_TYPE_ORDER_BY: ['create_date'],
                      const.QUERY_TYPE_COMPANY_CODE: ['company_code']
                      })
        queryExtend_result = QueryExtend.result
        
        if len(queryExtend_result)==0:
            return results, next_page, flimit
        
        for i in queryExtend_result:
            next_page += 1
            if args.get(const.SI_HEAD_REDIRCT):
                i = cls.find_by_invoice_no(i.invoice_no, i, const.SI_HEAD_REDIRCT)
            else:
                i = cls.find_by_invoice_no(i.invoice_no, i)
                
            if i and i.available_qty > 0 or args.get(const.SI_HEAD_REDIRCT): 
                results.append(i)
                 
            if not args.get('all') and  type != const.SEARCH_TYPE_GROUP_SI and len(results) > 24:
                break
                    
        if not args.get('all') and type != const.SEARCH_TYPE_GROUP_SI and len(results) < 25 and cate == const.VAT_PAGE_NEXT:
            limit = offset
            offset = offset+25
            return cls.paset_result(QueryExtend, limit, offset, results, flimit, cate, args)
        else:
            return results, next_page, flimit
    
    @classmethod
    def find_by_invoice_no(cls, invoice_no, i = None, redirct = None):
        if not i:
            i = cls.get(invoice_no)
        relations =  SoDetail.find_relation_si(invoice_no)[0]  
        i.mso_qty, i.moc_qty = 0, 0
        if not redirct:
            mso_tree =  THead.get_mso_mcn_qty(invoice_no)
            if mso_tree[0]!=0 and mso_tree[0] - mso_tree[1] -  mso_tree[2] == 0:
                return
            else: 
                i.mso_qty = mso_tree[0]                 
        mso_detail = SoDetail.get_details(i.sc_no)
        si_detail = SID.get_details(invoice_no)
        si_charge = SICharge.find(invoice_no)
        cn_detail = RID.get_details(invoice_no)
        cn_charge = RICharge.find_all_charges(invoice_no)
        si_result = _all_rewrite_price_and_filter_charges(si_charge, si_detail)
        cn_result = _all_rewrite_price_and_filter_charges(cn_charge, cn_detail)
        if not  _check_cn_rewrite_charges(invoice_no, si_detail, cn_detail) == 1:
            if si_result[-1] == 2 and cn_result[-1]==2: 
                si_Detail_list = []
                si_charge_list = []
                for a in si_result[0]:
                    for b in cn_result[0]:
                        if a.item_no == b.item_no and a.line_no == b.invoice_item_line_no:
                            a.available_qty = a.qty - b.note_qty
                    si_Detail_list.append(a)
                    
                for c in si_result[1]:
                    for d in cn_result[1]:
                        if d.chg_discount_code.decode("utf-8") == c.charge_code:
                            c.total = Decimal(c.total)
                            c.available_total = Decimal(c.total) - Decimal(d.total)
                    si_charge_list.append(c)
                    
                si_Detail, si_charge, cn_detail, cn_charge = si_Detail_list, si_charge_list, cn_result[0], cn_result[1]
            
            if len(cn_result[0])==0:
                si_detail = si_result[0]
                si_charge = si_result[1]
            i.qty, i.charge_total, i.ri_qty, i.ri_total = 0, 0, 0, 0
            for a in si_detail: i.qty  += int(a.qty)
            for b in si_charge: i.charge_total += b.total 
            for c in cn_detail: i.ri_qty += int(c.note_qty)   
            for d in cn_charge: i.ri_total += d.total
            thead_qty_dict = SiHead.find_t_si_head_qty_dict(invoice_no)
            chead_qty_dict = SiHead.find_c_si_head_qty_dict(invoice_no)
            thead_total_dict = Charge.find_t_si_charge_total_dict(invoice_no)
            chead_total_dict = Charge.find_c_si_charge_total_dict(invoice_no)
            i.msi_qty = thead_qty_dict.get(invoice_no, 0)
            i.mcn_qty = chead_qty_dict.get(invoice_no, 0)
            i.msi_total = thead_total_dict.get(invoice_no, 0)
            i.mcn_total = chead_total_dict.get(invoice_no, 0)
            if i.mso_qty == 0 and not redirct:
                i.available_qty = int(i.qty  - Decimal(i.ri_qty)- Decimal(i.msi_qty) + Decimal(i.mcn_qty)) 
            else:
                i.available_qty  = int(i.qty  - Decimal(i.ri_qty)- Decimal(i.msi_qty) + Decimal(i.mcn_qty) - i.qty + relations)
                i.mso_qty = i.qty
                i.moc_qty = relations
            i.available_total = Decimal(i.charge_total) - Decimal(i.ri_total)- Decimal(i.msi_total) + Decimal(i.mcn_total) 
            return i
                
    @classmethod
    def check_hava_mso(cls, name):
        type, sc_no, si_ava_qty, so_ava_qty, pass_sc_nos, pass_item_nos, sub_type, ref  = 0, None, 0, 0, [], [], 0,None
        data = [i.split("$")[0] for i in name.split(",")] if name else []
        invoice_dict = {}
        sc_dict = {}
        for a in data:
            sidetails = SID.find(a)
            sidetails = sidetails[0] if len(sidetails)> 0 else []
            for c in sidetails:
                sc_no = c.sc_no
                if sc_no:
                    si_qty = c.available_qty + c.msi_qty - c.mcn_qty
                    if not sc_dict.get(sc_no):
                        sc_dict.update({sc_no:{
                                               "si_qty" : si_qty, 
                                               "so_qty" : 0 , 
                                               "mso_qty" : 0,
                                               "mcn_qty" : 0,
                                               "so_item" : {"%s_%s" % (c.item_no,c.sc_item_line_no):0},
                                               "si_item" : {"%s_%s" % (c.item_no,c.sc_item_line_no):si_qty},
                                               "mso_item" : {"%s_%s" % (c.item_no,c.sc_item_line_no):0},
                                               "mcn_item" : {"%s_%s" % (c.item_no,c.sc_item_line_no):0}}
                                        })
                    else:
                        sc_dict[sc_no]['si_qty'] += si_qty
                        if sc_dict[sc_no]['si_item'].get("%s_%s" % (c.item_no,c.sc_item_line_no)):
                            sc_dict[sc_no]['si_item']["%s_%s" % (c.item_no,c.sc_item_line_no)]+= si_qty
                        else:
                            sc_dict[sc_no]['si_item']["%s_%s" % (c.item_no,c.sc_item_line_no)] = si_qty
                            
            soheads = SoHead.get_by_so(sc_no) if sc_no else []
            for b in soheads:
                if b.sales_contract_no not in pass_sc_nos:
                    pass_sc_nos.append(b.sales_contract_no)
                    so = SoDetail.get_details(b.sales_contract_no)
                    if len(so)>0:
                        for e in so:
                            if e.t_head_id: 
                                so_ava_qty += e.vat_qty
                                if "%s_%s" % (e.item_no,e.line_no) not in pass_item_nos:sc_dict[b.sales_contract_no]['so_qty'] += e.qty
                                sc_dict[b.sales_contract_no]['mso_qty'] += e.vat_qty
                                if sc_dict[sc_no]['so_item'].get("%s_%s" % (e.item_no,e.line_no)):
                                    sc_dict[sc_no]['so_item']["%s_%s" % (e.item_no,e.line_no)]+= e.qty
                                else:
                                    sc_dict[sc_no]['so_item']["%s_%s" % (e.item_no,e.line_no)] = e.qty
                                    
                                if sc_dict[sc_no]['mso_item'].get("%s_%s" % (e.item_no,e.line_no)):
                                    sc_dict[sc_no]['mso_item']["%s_%s" % (e.item_no,e.line_no)]+= e.vat_qty
                                else:
                                    sc_dict[sc_no]['mso_item']["%s_%s" % (e.item_no,e.line_no)] = e.vat_qty
                                pass_item_nos.append("%s_%s" % (e.item_no,e.line_no))
                                    
                            elif e.c_head_id:
                                sc_dict[b.sales_contract_no]['mcn_qty'] += e.vat_qty
                                if sc_dict[sc_no]['mcn_item'].get("%s_%s" % (e.item_no,e.line_no)):
                                    sc_dict[sc_no]['mcn_item']["%s_%s" % (e.item_no,e.line_no)]+= e.vat_qty
                                else:
                                    sc_dict[sc_no]['mcn_item']["%s_%s" % (e.item_no,e.line_no)] = e.vat_qty
                                 
                if b.t_head and b.t_head.relation_si:
                    relation_si = b.t_head.relation_si.split(",")
                    if a in relation_si:
                        type = 2
                        ref = b.t_head.ref
                        break
                    else: type = 1
                else:type = 1
        for k, v in sc_dict.iteritems():
            if v.get("si_qty", 0) + v.get("mso_qty", 0) - v.get("mcn_qty", 0) > v.get("so_qty", 0):
                sub_type = 1
                break
            for i, q  in v.get("so_item").iteritems():
                if v.get("si_item").get(i, 0) + v.get("mso_item").get(i, 0) - v.get("mcn_item").get(i, 0) > q:
                    sub_type = 1
                    break 
        return dict(type = type, sc_no = sc_no, ref = ref, sub_type = sub_type)
        
     
    @classmethod
    def check_hava_related(cls, invoice_no):
        f = 0
        si = SI.get(invoice_no)
        so_no = si.sc_no if si.sc_no else None
        if so_no:
            theads  = list(set([s.t_head for s in SoHead.get_by_so(so_no) if s.t_head_id]))
            for thead in theads:
                f = 1
                if thead.relation_si:
                    sids = []
                    si_nos = thead.relation_si.split(',')
                    for si_no in si_nos:
                        sid = SID.find(si_no)
                        sids.extend(sid[0])
                    sods  = SoDetail.get_details(so_no)
                    so_qty, si_qty = 0, 0
                    for sod in sods:
                        so_qty += sod.vat_qty
                    for sid in sids:
                        si_qty += sid.vat_qty
                    if int(so_qty) == int(si_qty): f = 0
        return f
                        
        
    @classmethod
    def find_si_head_qty_dict(cls):
        sql = '''
            SELECT b.invoice_no, SUM(b.qty) Qty FROM (
                SELECT a.invoice_no,a.invoice_line_no,a.item_no ,SUM(a.qty) Qty  FROM (
                    SELECT tid.INVOICE_NO,tid.SC_NO,tid.line_no invoice_line_no,tid.ITEM_NO, tid.QTY QTY FROM T_INVOICE_DTL tid WHERE tid.company_code in %s
                    UNION ALL
                    SELECT tnd.INVOICE_NO,tnd.SC_NO,tnd.invoice_item_line_no invoice_line_no,tnd.ITEM_NO,tnd.NOTE_QTY*(-1) QTY  FROM T_CUST_NOTE_DTL tnd WHERE tnd.company_code in %s
                ) a GROUP BY a.invoice_no,a.invoice_line_no,a.item_no) b
            GROUP BY b.invoice_no ORDER BY b.invoice_no
            ''' % (getCompanyCode(1), getCompanyCode(1))
        return _fetch_sql_to_dict(sql, DBSession2)
     
    @classmethod
    def auto_complete(cls, DB, db_dict, type, q):
        result = []
        for k, v in db_dict.iteritems():
            if(type in ['cust_code', 'cust_name']):
                k = 't_cust_hdr'
                sql = "SELECT  distinct %s FROM %s where COMPANY_CODE in %s AND %s LIKE '%s' AND ROWNUM<=10 " % (type, k, getCompanyCode(1),type,q.upper()+'%')
                return DBSession2.execute(sql).fetchall()
            else:
                if type in v:
                    if DB == DBSession2:
                        sql = "SELECT  distinct %s FROM %s where COMPANY_CODE in %s AND %s LIKE '%s' AND ROWNUM<=10 " % (type, k, getCompanyCode(1),type,q.upper()+'%')
                    else:
                        sql = "SELECT  distinct %s FROM %s where %s LIKE '%s'  limit 10 offset 0 " % (type, k, type, q.upper()+'%')
                    rrs = DB.execute(sql).fetchall()
                    for rr in rrs:
                        if rr not in result:
                            result.append(rr)
        return result
    
    @classmethod
    def find_si_by_sc_no(cls,sc_no):
        return DBSession2.query(cls).filter(cls.sc_no == sc_no).filter(cls.company_code.in_(getCompanyCode())).all()
    
    
    @classmethod
    def customer_codes(cls, ** args):
        customer_code, customer_type, customer_name, date_from, date_to = (args.get(i, '').strip() for i in ['customer_code', 'customer_type', 'customer_name', 'date_from', 'date_to'])
        customers = Customer.find_all_customer_by_type(customer_type)
        data = DBSession2.query(distinct(cls.customer)).filter(cls.create_date <= dt.strptime(date_to + " 23:59:59", "%Y-%m-%d %H:%M:%S"))\
                            .filter(cls.create_date >= dt.strptime(date_from + " 00:00:00", "%Y-%m-%d %H:%M:%S")).filter(cls.company_code.in_(getCompanyCode()))
        if customer_code:
            data = data.filter(cls.customer == customer_code)
        if customer_name:
            data = data.filter(cls.customer_short_name == customer_name)
        customer_codes = data.all()
        return [i[0] for i in customer_codes if (customer_type and i[0] in customers) or not customer_type]
    
    @classmethod
    def find_invoice_no_by_customer_code(cls, ** args):
        result = []
        customer_code, date_from, date_to = (args.get(i, '').strip() for i in ['customer_code', 'date_from', 'date_to'])
        if not customer_code: return []
        invoice_nos = DBSession2.query(distinct(cls.invoice_no)).filter(cls.customer == customer_code).filter(cls.create_date <= dt.strptime(date_to + " 23:59:59", "%Y-%m-%d %H:%M:%S"))\
                            .filter(cls.create_date >= dt.strptime(date_from + " 00:00:00", "%Y-%m-%d %H:%M:%S")).filter(cls.company_code.in_(getCompanyCode())).all()
        for invoice_no in invoice_nos:
            si = cls.find_by_invoice_no(invoice_no[0])
            if si and si.available_qty > 0:
                result.append(si)
        return [i.invoice_no for i in result]
    
      
class SID(Table_SID):

    ri_qty, msi_qty, mcn_qty, available_qty, available_total, msi_total, mcn_total = (0, 0, 0, 0, 0, 0, 0)

    @classmethod
    def find(cls,invoice_no):
        tax_total = 0
        tdetail_qty_dict = SiDetail.find_t_si_detail_qty_dict(invoice_no)
        cdetail_qty_dict = SiDetail.find_c_si_detail_qty_dict(invoice_no)
        total_dict = SICharge.find_si_charge_total_dict()
        tcharge_total_dict = Charge.find_t_si_charge_total_dict(invoice_no)
        ccharge_total_dict = Charge.find_c_si_charge_total_dict(invoice_no)
        si_charge = SICharge.find(invoice_no)
        cn_charge = RICharge.find_all_charges(invoice_no)
        si_detail = cls.get_details(invoice_no)
        cn_detail = RID.get_details(invoice_no)
        si_result = _all_rewrite_price_and_filter_charges(si_charge, si_detail)
        cn_result = _all_rewrite_price_and_filter_charges(cn_charge, cn_detail)
        
        si_Detail_list = []
        si_charge_list = []
        for a in si_result[0]:
            for b in cn_result[0]:
                if a.item_no == b.item_no and a.line_no == b.invoice_item_line_no:
                    a.available_qty = int(a.qty) - int(b.note_qty)
            si_Detail_list.append(a)

        for c in si_result[1]:
            for d in cn_result[1]:
                if d.chg_discount_code.decode("utf-8") == c.charge_code:
                    c.total = Decimal(c.total)
                    c.available_total = Decimal(c.total) - Decimal(d.total)
            si_charge_list.append(c)
        si_detail, si_charge = si_Detail_list, si_charge_list
        si_detail_d, si_charge_d = [], []
        for e in si_detail:
            key = e.line_no
            e.ri_qty = 0
            e.mso_qty = 0
            relations_qty =  SoDetail.find_relation_si(e.invoice_no, e.item_no, e.sc_item_line_no)              
            for g in cn_detail:
                if e.item_no == g.item_no and e.line_no == g.invoice_item_line_no:   
                    e.ri_qty = int(g.note_qty)
            e.msi_qty = tdetail_qty_dict.get(key, 0)
            e.mcn_qty = cdetail_qty_dict.get(key, 0)
            if relations_qty[0] == 0:
                e.available_qty = e.qty - e.ri_qty  - e.msi_qty + e.mcn_qty
            else:
                e.available_qty = e.qty - e.ri_qty  - e.msi_qty + e.mcn_qty - e.qty + relations_qty[1]
                e.base_ava_qty = e.available_qty
                e.mso_qty = relations_qty[2]
            e.vat_qty = e.available_qty
            if e.available_qty > 0:
                si_detail_d.append(e)
            
        si_detail = si_detail_d   
        for f in si_charge:
            key = f.line_no
            ri_total = get_cn_total(f.invoice_no,f.charge_code)
            f.msi_total = tcharge_total_dict.get(key, 0)
            f.mcn_total = ccharge_total_dict.get(key, 0)
            f.available_total = Decimal(f.total)- Decimal(ri_total) - Decimal(f.msi_total) + Decimal(f.mcn_total)
            if pf(f.available_total) != 0:
                si_charge_d.append(f)
            
        si_charge = si_charge_d   
        return [si_detail, si_charge, cn_detail, cn_charge]
        
    @classmethod
    def find_si_detail_qty_dict(cls, invoice_no):
        result_dict = {}
        for i in DBSession2.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.company_code.in_(getCompanyCode())).all():
            result_dict.update({i.line_no:i.qty})
        return result_dict
    
    @classmethod
    def get_unit_price(cls,invoice_no):
        sql = "select UNIT_PRICE from T_INVOICE_DTL where invoice_no='%s'" % (invoice_no)
        return DBSession2.execute(sql).fetchone()
    
    @classmethod
    def get_details(cls,invoice_no):
        return DBSession2.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.company_code.in_(getCompanyCode())).all()
    
    @classmethod
    def get_sum_details(cls, sc_no):
        details_list =  DBSession2.query(cls).filter(cls.sc_no == sc_no).filter(cls.company_code.in_(getCompanyCode())).all()
        sum_details = 0
        for a in details_list:sum_details += a.item_total
        return sum_details
            
    @classmethod
    def get_sum_total_vat(cls,invoice_no):
        sql = '''SELECT SUM(ITEM_TOTAL)*0.17 FROM "RPAC"."T_INVOICE_DTL" where INVOICE_NO='%s' ''' % (invoice_no)
        sum_total=DBSession2.execute(sql).fetchone()
        return sum_total[0] if sum_total else 0
    
    
class SICharge(Table_SICharge):

    type = 'SI'
    mso_total, mcn_total, available_total = (0, 0, 0)

    @classmethod
    def find(cls, invoice_no):
        return DBSession2.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.company_code.in_(getCompanyCode())).all()
    
    @classmethod
    def find_charge(cls,invoice_no):
        return DBSession2.query(cls).filter(cls.company_code.in_(getCompanyCode())).filter(cls.invoice_no == invoice_no).filter(cls.charge_code==u'增值稅' or cls.charge_code==u'增值稅應付' or cls.charge_code==u'增值稅-應付').all()

    @classmethod
    def find_other_charge_total(cls,invoice_no=None):
        get_item_sql = '''SELECT sum(item_total)*0.17 FROM "RPAC"."T_INVOICE_DTL" WHERE INVOICE_NO='%s' ''' % (invoice_no)
        get_item = DBSession2.execute(get_item_sql).fetchone()
        get_charge_sql = '''SELECT sum(TOTAL) FROM "RPAC"."T_INVOICE_CHARGES" WHERE INVOICE_NO='%s' and CHARGE_CODE like '%s' ''' % (invoice_no,u'增值稅%')
        get_charge = DBSession2.execute(get_charge_sql).fetchone()
        get_charge2_sql = '''SELECT sum(TOTAL) FROM "RPAC"."T_INVOICE_CHARGES" WHERE INVOICE_NO='%s' and CHARGE_CODE not like '%s' ''' % (invoice_no,u'增值稅%')
        get_charge2 = DBSession2.execute(get_charge2_sql).fetchone()
        get_cn_totas = RICharge.get_sum_total_charges(invoice_no)

        get_item = Decimal(get_item[0]) if len(get_item)>0 else 0   
        if len(get_charge)>0:
                get_charge = Decimal(get_charge[0]) if get_charge[0] else 0 
        else: get_charge = 0 
        if len(get_charge2)>0:
            get_charge2 = Decimal(get_charge2[0]) if get_charge2[0] else 0
        else:
            get_charge2 = 0
        if 0.05 >= abs(get_item-get_charge-get_cn_totas):
            get_charge = 0
            get_cn_totas = 0
        return get_charge2+get_charge+get_cn_totas
        
    @classmethod
    def find_si_charge_total_dict(cls, invoice_no=None):
        if not invoice_no:
            sql = '''
                select tic.INVOICE_NO, sum(tic.TOTAL) Total from t_invoice_charges tic
                    where tic.company_code in %s
                    group by tic.INVOICE_NO
                    having sum(tic.TOTAL)<>0
            ''' % getCompanyCode(1)
            return _fetch_sql_to_dict(sql, DBSession2)
        else:
            result_dict = {}
            for i in cls.find(invoice_no):
                result_dict.update({i.line_no:i.total})
            return result_dict
        
    @classmethod
    def get_charge_list(cls,invoice_no):
        sql = '''
            SELECT total FROM "RPAC"."T_INVOICE_CHARGES" WHERE INVOICE_NO='%s' and CHARGE_CODE like '%s'
        ''' % (invoice_no,u'增值稅%')
        return DBSession2.execute(sql).fetchall()
    
    @classmethod
    def get_sum_charge(cls,invoice_no):
        get_charge_sql = '''SELECT sum(TOTAL) FROM "RPAC"."T_INVOICE_CHARGES" WHERE INVOICE_NO='%s' ''' % (invoice_no)
        get_charge = DBSession2.execute(get_charge_sql).fetchone()[0]
        return get_charge if get_charge else 0
    

class RI(Table_RI):

    @classmethod
    def find(cls, customer):
        return DBSession2.query(cls).filter(cls.customer == customer).filter(cls.company_code.in_(getCompanyCode())).all()
    
    @classmethod
    def find_by_note_no(cls, note_no):
        return DBSession2.query(cls).filter(cls.note_no == note_no).filter(cls.company_code.in_(getCompanyCode())).first()
    
class RID(Table_RIDetail):

    @classmethod
    def find(cls, invoice_no, ** args):
        detail_list = DBSession2.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.company_code.in_(getCompanyCode())).all()
        tax_total = 0
        detail_dict = {}
        for i in detail_list:
            detail_dict.update({i.invoice_item_line_no:i.note_qty})
            tax_total += Decimal(const.TAX_PERCENTAGE) * (Decimal(i.unit_price) * Decimal(i.note_qty))
        ri_result = _all_rewrite_price_and_filter_charges(RICharge.find_ri_charges(invoice_no), detail_list)
        ri_result.append(detail_dict)
        return ri_result
    
    @classmethod
    def find_by_so(cls, sc_no):
        detail_list = DBSession2.query(cls).filter(cls.sc_no == sc_no).filter(cls.company_code.in_(getCompanyCode())).all()
        return _all_rewrite_price_and_filter_charges(RICharge.fin_ri_by_sc_no(sc_no), detail_list)
    
    @classmethod
    def find_ri_detail_qty_dict(cls, invoice_no):
        result_dict = {}
        for i in DBSession2.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.company_code.in_(getCompanyCode())).all():
            result_dict.update({i.line_no:i.item_total})
        return result_dict
    
    @classmethod
    def get_details(cls,invoice_no):
        return DBSession2.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.company_code.in_(getCompanyCode())).all()
    
    @classmethod
    def get_sum_total_vat(cls,invoice_no):
        sql = '''SELECT sum(ITEM_TOTAL)*0.17 FROM "RPAC"."T_CUST_NOTE_DTL" WHERE INVOICE_NO='%s' ''' % (invoice_no)
        total_vat  = DBSession2.execute(sql).fetchone()
        return total_vat[0] if total_vat[0] else 0
    
    @classmethod
    def get_details_by_note_no(cls, note_no):
        return DBSession2.query(cls).filter(cls.note_no == note_no).filter(cls.company_code.in_(getCompanyCode())).all()

            
class RICharge(Table_RICharge):

    type = 'CN'
    mso_total, mcn_total, available_total = (0, 0, 0)

    @classmethod
    def fin_ri_by_sc_no(cls, sc_no):
        sql = '''
            select tnc.* from T_CUST_NOTE_CHARGES tnc inner join T_CUST_NOTE_HDR tnh on tnh.NOTE_NO=tnc.NOTE_NO
                where tnh.SC_NO IS NOT NULL AND tnh.company_code in %s AND tnh.SC_NO='%s'
            ''' % (getCompanyCode(1), sc_no)
        return DBSession2.query(cls).from_statement(sql).all()
    
    
    @classmethod
    def find_ri_charges(cls, invoice_no):
        sql = '''
            select tnc.* from T_CUST_NOTE_CHARGES tnc inner join T_CUST_NOTE_HDR tnh on tnh.NOTE_NO=tnc.NOTE_NO
                where tnh.INVOICE_NO IS NOT NULL AND tnh.company_code in %s AND tnh.INVOICE_NO='%s'
            ''' % (getCompanyCode(1), invoice_no)
        return DBSession2.query(cls).from_statement(sql).all()

    @classmethod
    def find_ri_cust_charges(cls, cust_code):
        sql = '''
            select tnh.NOTE_NO,tnh.NOTE_TYPE,tnh.STATUS,tnc.LINE_NO,tnc.CHG_DISCOUNT_CODE,tnc.TOTAL,tnh.CREATE_DATE,tnh.REMARK From t_cust_note_charges tnc,t_cust_note_hdr tnh where tnh.COMPANY_CODE in %s and tnh.SC_NO is null and tnh.INVOICE_NO is null and tnh.CUSTOMER='%s' and tnh.NOTE_NO=tnc.NOTE_NO
            ''' % (getCompanyCode(1), cust_code)
        return DBSession2.execute(sql).fetchall()
    
            
    @classmethod
    def get_sum_total_charges(cls,invoice_no):
        sql ='''
         select sum(tnc.TOTAL) from T_CUST_NOTE_CHARGES tnc inner join T_CUST_NOTE_HDR tnh on tnh.NOTE_NO=tnc.NOTE_NO 
             where TNC.CHG_DISCOUNT_CODE like '%s' and  tnh.INVOICE_NO IS NOT NULL AND  tnh.INVOICE_NO='%s' ''' % (u'增值稅%',invoice_no)
        get_cn_total = DBSession2.execute(sql).fetchone()[0]
        if get_cn_total:
            return float(get_cn_total)
        else:
            return 0
        
    @classmethod
    def get_charges_list(cls,invoice_no):
        sql ='''
         select tnc.TOTAL from T_CUST_NOTE_CHARGES tnc inner join T_CUST_NOTE_HDR tnh on tnh.NOTE_NO=tnc.NOTE_NO 
             where TNC.CHG_DISCOUNT_CODE like '%s' and  tnh.INVOICE_NO IS NOT NULL AND  tnh.INVOICE_NO='%s' ''' % (u'增值稅%',invoice_no)
        return DBSession2.execute(sql).fetchall()
    
    @classmethod
    def find_ri_charge_total_dict(cls, invoice_no=None):
        if not invoice_no:
            sql = '''
                select tch.INVOICE_NO, sum(tcc.TOTAL) Total from t_cust_note_charges tcc,t_cust_note_hdr tch
                    where tch.company_code in %s and tch.NOTE_NO=tcc.NOTE_NO
                    group by tch.INVOICE_NO
                    having sum(tcc.TOTAL)<>0
            ''' % getCompanyCode(1)
            return _fetch_sql_to_dict(sql, DBSession2)
        else:
            result_dict = {}
            for i in cls.find_ri_charges(invoice_no):
                result_dict.update({i.line_no:i.total})
            return result_dict
        
    @classmethod
    def get_sum_charge(cls, invoice_no=None):
        sql ='''
         select sum(tnc.TOTAL) from T_CUST_NOTE_CHARGES tnc inner join T_CUST_NOTE_HDR tnh on tnh.NOTE_NO=tnc.NOTE_NO 
             where tnh.INVOICE_NO IS NOT NULL AND  tnh.INVOICE_NO='%s'
        ''' % (invoice_no)
        get_cn_total = DBSession2.execute(sql).fetchone()[0]
        return float(get_cn_total) if get_cn_total else 0
    
    @classmethod
    def get_sum_other_charge(cls,invoice_no):
        sql = '''SELECT sum(tnc.TOTAL) FROM "RPAC"."T_CUST_NOTE_CHARGES" tnc,"RPAC"."T_INVOICE_CHARGES" tic,T_CUST_NOTE_HDR tnh 
            WHERE  TNH.NOTE_NO= TNC.NOTE_NO and TNH.INVOICE_NO = TIC.INVOICE_NO and tnc.CHG_DISCOUNT_CODE = tic.CHARGE_CODE and tic.CHARGE_CODE not like '%s' and tnh.INVOICE_NO='%s' ''' % (u'增值稅%',invoice_no)
        sum_other_charge = DBSession2.execute(sql).fetchone()[0]
        return sum_other_charge if sum_other_charge else 0
        
    @classmethod
    def find_all_charges(cls, invoice_no,desc=None):
        sql = '''
            select tnc.* from T_CUST_NOTE_CHARGES tnc inner join T_CUST_NOTE_HDR tnh on tnh.NOTE_NO=tnc.NOTE_NO
                where  tnh.INVOICE_NO='%s' ''' % (invoice_no)
        if desc:
            sql = sql + "order by line_no desc"
        return DBSession2.query(cls).from_statement(sql).all()
    
    @classmethod
    def search_charge_erp(cls, **kw):
        sql = '''select tnh.NOTE_NO,tnh.NOTE_TYPE,tnh.STATUS,tnc.LINE_NO,tnc.CHG_DISCOUNT_CODE,tnc.TOTAL,tnh.CREATE_DATE,tnh.REMARK 
                            From t_cust_note_charges tnc,t_cust_note_hdr tnh 
                                where tnh.COMPANY_CODE in %s and tnh.SC_NO is null and tnh.INVOICE_NO is null and tnh.CUSTOMER='%s' 
                and tnh.NOTE_NO=tnc.NOTE_NO''' % (getCompanyCode(1), kw['customer_code'])            
        data = DBSession2.execute(sql).fetchall()
        ns, cc = [], []
        for d in data:
            if d[0] not in ns: ns.append(d[0])
        for n in ns:
            date_from = kw.get('date_from')
            date_to = kw.get('date_to')
            if date_from:
                date_from = dt.strptime(date_from + "00:00:00", "%Y-%m-%d%H:%M:%S")
            if kw.get('note_no') and n != kw.get('note_no'):
                date_to = dt.strptime(date_to + "23:59:59", "%Y-%m-%d%H:%M:%S")
            charges = cls.search_charge_by_note_no(n)
            details, charges, tax = _all_rewrite_price_and_filter_charges(charges, [])
            for charge in charges:
                vat_total = 0
                vat_charges = Charge.find_other_charge_by_note_no(n)
                for vat_charge in vat_charges:
                    vat_total += vat_charge.vat_total
                ri = RI.find_by_note_no(n)
                if date_from and date_from>ri.note_date:
                    continue
                if date_to and date_to>ri.note_date:
                    continue
                charge.note_type = ri.note_type
                if charge.note_type == 'C':
                    charge.total = - charge.total
                if pf(charge.total.__abs__()) > pf(vat_total.__abs__()):
                    charge.status = ri.status
                    charge.note_date = ri.note_date
                    charge.remark = ri.remark
                    charge.vat_total = charge.total - vat_total
                    cc.append(charge)
        return cc
    
    @classmethod
    def search_charge_by_note_no(cls, note_no):
        return DBSession2.query(cls).filter(cls.note_no == note_no).filter(cls.company_code.in_(getCompanyCode())).all()
 
        
class Customer(Table_Customer):
    
    @classmethod
    def find(cls, ** args):
        result =  []
        date_from, date_to, head_type, customer_code = (args.get(i, '').strip() for i in ('date_from', 'date_to', 'type', 'customer_code'))
        if head_type == const.SEARCH_TYPE_GROUP_SI:
            customer_codes = SI.customer_codes(**args)
            qtys = SiHead.find_all_customer_si_qty_dict(date_from, date_to, customer_code)
            customer_qtys = cls.find_all_customer_si_qty_dict(date_from, date_to, customer_code)
        else:
            customer_qtys = cls.find_all_customer_so_qty_dict(date_from, date_to, customer_code)
            qtys = SoHead.find_all_customer_so_qty_dict(date_from, date_to, customer_code)
            customer_codes = SO.customer_codes(**args)
        for customer_code in customer_codes:
            if customer_qtys.get(customer_code) and customer_qtys.get(customer_code) > qtys.get(customer_code, 0):
                result.append(cls.get(customer_code))
        return result, 0, 25

    @classmethod
    @beaker_cache(expire=600, type='memory', query_args=True)
    def find_all_customer_dict(cls):
        result = {}
        for i in DBSession2.query(cls.cust_code, cls.cust_short_name).all():
            result.update({i.cust_code:i.cust_short_name})
        return result

    @classmethod
    def get(cls, customer_code):
        return DBSession2.query(cls).filter(cls.cust_code == customer_code).filter(cls.company_code.in_(getCompanyCode())).first()
    
    @classmethod
    def find_all_customer_si_qty_dict(cls, date_from, date_to, customer_code):
        sql = '''
                        SELECT tih.CUSTOMER,SUM(tid.QTY) Cust_Qty FROM t_invoice_dtl tid, t_invoice_hdr tih  
                WHERE tid.COMPANY_CODE IN %s
                AND tid.CREATE_DATE>=TO_DATE('%s 00:00:00','YYYY-MM-DD HH24:MI:SS') 
                AND tid.CREATE_DATE<=TO_DATE('%s 23:59:59','YYYY-MM-DD HH24:MI:SS') 
                AND tid.INVOICE_NO=tih.INVOICE_NO %s
              GROUP BY tih.CUSTOMER
            ''' % (getCompanyCode(1), date_from, date_to, "AND tih.CUSTOMER='%s' " % customer_code if customer_code else '')
        return _fetch_sql_to_dict(sql, DBSession2)
    
    @classmethod
    def find_all_customer_so_qty_dict(cls, date_from, date_to, customer_code):
        sql = '''
                        SELECT tsh.customer_code, SUM(tsd.QTY) Cust_Qty FROM t_sales_contract_dtl tsd, t_sales_contract_hdr tsh  
                WHERE tsd.COMPANY_CODE IN %s
                AND tsd.CREATE_DATE>=TO_DATE('%s 00:00:00','YYYY-MM-DD HH24:MI:SS') 
                AND tsd.CREATE_DATE<=TO_DATE('%s 23:59:59','YYYY-MM-DD HH24:MI:SS') 
                AND tsd.sales_contract_no=tsh.sales_contract_no %s
              GROUP BY tsh.customer_code
            ''' % (getCompanyCode(1), date_from, date_to, "AND tsh.customer_code='%s' " % customer_code if customer_code else '')
        return _fetch_sql_to_dict(sql, DBSession2)
    
    @classmethod
    def find_all_customer_by_type(cls, customer_type):
        return [i[0] for i in DBSession2.query(distinct(cls.cust_code)).filter(cls.cust_type == customer_type).filter(cls.company_code.in_(getCompanyCode())).all()]
        

class THead(Table_THead):

    @classmethod
    def find(cls, category=None, ** args):
        ids = [0]
        page, limit, cate = 25, 0, 'next'
        status = args.get('status')
        item_code, invoice_no, sales_contract_no, vat_no, create_by_id, co, pending, related_si = \
                                (args.get(i, '').strip() for i in ('item_code', 'invoice_no', 'sales_contract_no', 'vat_no', 'create_by', 'co', 'pending', 'related_si'))
        if item_code:
            ids.extend(SiDetail.get_thead_ids(item_code))
            ids.extend(SoDetail.get_thead_ids(item_code))
        if sales_contract_no:
            ids.extend(SiHead.get_thead_ids(invoice_no, sales_contract_no))
            ids.extend(SoHead.get_thead_ids(sales_contract_no))
        elif invoice_no:
            ids.extend(SiHead.get_thead_ids(invoice_no, sales_contract_no))
        if args.get('create_by_id'):
            users =  cls.user_name_id(args['create_by_id'])
            if len(users)>0:
                args['create_by_id'] = users[0].user_id
            else:
                return []
        if len(ids) > 1: args['ids'] = list(set(ids))
        arr_not_null = []
        if vat_no: arr_not_null.append('vat_no')
        params = {
            const.QUERY_TYPE_LIKE: ['ref', 'customer_code'],
            const.QUERY_TYPE_LIKE_AND_OR: [('customer_name', 'customer_name', 'customer_short_name')],
            const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
            const.QUERY_TYPE_IN: [('id', 'ids')],
            const.QUERY_TYPE_ORDER_BY: ['create_time'],
            const.QUERY_TYPE_CREATE_BY: ['create_by_id'],
            const.QUERY_TYPE_COMPANY_CODE: ['company_code'],
            const.QUERY_TYPE_NOT_NULL: arr_not_null
            
        }
        if isinstance(status, list):
            params[const.QUERY_TYPE_IN].append('status')
        else:
            params.update({const.QUERY_TYPE_EQ: ['status']})
        queryExtend = QueryExtend(cls, ** args)
        if args.get("page"):
            limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == const.VAT_PAGE_PRE:
            cate, limit, offset = const.VAT_PAGE_PRE, int(args.get("limit")), int(args.get("offset"))
        if category:offset = None   
        queryExtend.query_all(True, DBSession, True, limit, offset, ** params)
        query_result = cls._format_related(queryExtend.result, ** args) if related_si else queryExtend.result
        query_result = cls._format_pending(query_result, ** args) if pending else query_result
        if vat_no or co:
            results = []
            for i in query_result:
                if co == 'cost' and i.o_head_id:
                    continue
                if vat_no:
                    for j in i.vat_no.split(','):
                        if len(j.split('~')) == 1 and vat_no == j:
                            results.append(i)
                            break
                        elif len(j.split('~')) == 2:
                            kk = j.split('~')
                            if int(kk[0]) <= int(vat_no) and int(kk[1]) >= int(vat_no):
                                results.append(i)
                                break
                else:
                    results.append(i)
            if category:
                return results
            else:
                return results, offset, limit
        else:
            if category:
                return query_result
            else:
                return query_result, offset, limit

    @classmethod
    def _format_related(cls, theads, ** args):
        yes_result, no_result = [], []
        head_type = args.get('related_si')
        for thead in theads:
            if thead.relation_si:
                sids_qty = {}
                sods = thead.so_details
                relation_si = thead.relation_si.split(",") if thead.relation_si else []
                for b in relation_si:
                    sids = SID.find(b)
                    if len(sids[0])>0: 
                        sids = sids[0]
                        for sid in sids:
                            key = "%s_%s" % (sid.item_no, sid.sc_item_line_no) 
                            if sids_qty.get(key):
                                sids_qty[key] += sid.available_qty
                            else:
                                sids_qty.update({key:sid.available_qty})
                sod_type = True
                for sod in sods:
                    key = "%s_%s" % (sod.item_no, sod.line_no)
                    if not sids_qty.get(key) or (sids_qty.get(key) and int(sids_qty[key]) != int(sod.vat_qty)):
                        no_result.append(thead)
                        sod_type = False
                        break
                if sod_type:
                    yes_result.append(thead)
            else:
                if thead.head_type == const.ERP_HEAD_TYPE_SO:
                    no_result.append(thead)           
        return yes_result if head_type and head_type == 'YES' else no_result
    
    @classmethod
    def _check_related(cls, **args):
        theads = []
        ids = args.get('ids').split(',')
        for id in ids:
            id = id.split('$')[0]
            thead = THead.get(id)
            theads.append(thead)
        result = cls._format_related(theads, **{'related_si':'NO'})
        return False if len(result) > 0 else True
            
    @classmethod
    def _format_pending(cls, theads, ** args):
        yes_result, no_result  = [], []
        head_type = args.get('pending')
        for thead in theads:
            charges = thead.charges
            follow = None
            for charge in charges:
                if charge.pending:
                    yes_result.append(thead)
                    follow = True
                    break
            if follow:
                continue
            no_result.append(thead)
        return yes_result if head_type == 'YES' else no_result
    
    @classmethod
    def create(cls, ** args):
        mCRef = CRef()
        ids, head_type, customer_code, t_head_id = (args.get(i, '') for i in ('ids', 'head_type', 'customer_code', 't_head_id'))
        refTime = dt.now().strftime('%Y%m')[2:]
        ref = 'MSI' if head_type == const.ERP_HEAD_TYPE_SI else 'MSO'
        max = mCRef.get(ref)
        customer = Customer.get(customer_code)
        thArgs = {
            'head_type':head_type,
            'customer_code':customer.cust_code,
            'customer_name':customer.cust_name,
            'customer_type':customer.cust_type,
            'customer_short_name':customer.cust_short_name,
            'company_code':getCompanyCode()[0],
            'status':const.VAT_THEAD_STATUS_NEW,
            'ref':'%s%s' % (ref, max),
        }
        if t_head_id:
            thead = THead.get(t_head_id)
        else:
            thead = THead( ** thArgs)
            DBSession.add(thead)
            DBSession.flush()
        if ids:
            for id in ids.split(','):
                shArgs = {'t_head_id':thead.id}
                if head_type == const.ERP_HEAD_TYPE_SI:
                    invoice_no = id.split('$')[0]
                    sidResult = SID.find(invoice_no)
                    shArgs.update({'invoice_no':invoice_no})
                    siHead = SiHead.create( ** shArgs)
                    shArgs.update({'si_head_id':siHead.id, 'currency':siHead.currency, 'cust_po_no':siHead.cust_po_no, 'sales_contract_no': siHead.sc_no})
                    SiDetail.create(sidResult[0], ** shArgs)
                    Charge.create(const.CHARGE_TYPE_T_SI, sidResult[1], ** shArgs)
                    Charge.create(const.CHARGE_TYPE_T_RI, sidResult[3], ** shArgs)
                elif head_type == const.ERP_HEAD_TYPE_SO:
                    sales_contract_no = id.split('$')[0]
                    sodResult = SOD.find(sales_contract_no)
                    shArgs.update({'sales_contract_no':sales_contract_no})
                    soHead = SoHead.create( ** shArgs)
                    shArgs.update({'so_head_id':soHead.id, 'currency':soHead.currency, 'cust_po_no':soHead.cust_po_no, 'sales_contract_no': soHead.sales_contract_no})
                    SoDetail.create(sodResult[0], ** shArgs)
                    Charge.create(const.CHARGE_TYPE_T_SO, sodResult[1], ** shArgs)
        return thead

    @classmethod
    def update_all_status(cls, ** args):
        (status, ids) = (args.get(i, '') for i in ('status', 'ids'))
        theads = cls.find_by_ids(ids)
        for i in theads:
            i.remark = args.get("remark-%s" % i.id)
            i.express_no = args.get("express_no-%s" % i.id)
            i.express_date = args.get("express_date-%s" % i.id)
            i.rec_month   = args.get("rec_month-%s" % i.id)
            i.payment_status = args.get("payment_status-%s" % i.id)
            i.payment_remark  = args.get("payment_remark-%s" % i.id)
            if status == const.VAT_THEAD_STATUS_CANCELLED:
                if i.o_head_id and i.o_head.status != const.VAT_THEAD_STATUS_CANCELLED:
                    return True
                    break
                else:i.status = status
                i.active = 1
                if i.head_type == const.ERP_HEAD_TYPE_SI:
                    for q in i.si_heads:
                        q.active = 1
                        DBSession.merge(q)
                    for j in i.si_details:
                        j.active = 1
                        DBSession.merge(j)
                else:
                    for q in i.so_heads:
                        q.active = 1
                        DBSession.merge(q)
                    for j in i.so_details:
                        j.active = 1
                        DBSession.merge(j)
                for j in i.charges:
                    j.active = 1
                    DBSession.merge(j)
            else:
                if status and not status == const.VAT_CHEAD_STATUS_SAVE:
                    i.status = status
                  
            if not status == const.VAT_THEAD_STATUS_NEW:
                if i.head_type == const.ERP_HEAD_TYPE_SO:
                    so_details = []
                    for q in i.so_heads:
                        so_detail = q.find_details()
                        for v in so_detail: so_details.append(v)
                    for j in i.so_details:
                        for u in so_details:
                            if j.active == u.active and j.uuid == u.uuid:
                                #j.ava_qty = u.available_qty + u.vat_qty
                                j.ava_qty = u.available_qty
                                DBSession.merge(j)           
            DBSession.merge(i)
            DBSession.flush()
    
    @classmethod
    def update_all_vat_info(cls, ** args):
        vat_no, vat_date, ids = (args.get(i, '').strip() for i in ('vat_no', 'vat_date', 'ids'))
        theads = cls.find_by_ids(ids)
        for i in theads:
            i.vat_no = vat_no
            i.vat_date = dt.strptime('%s00:00:00' % vat_date, "%Y-%m-%d%H:%M:%S")
            DBSession.merge(i)

    @classmethod
    def update_relation_si(cls, ** args):
        (relation, t_head_id, type, head_type) = (args.get(i, '') for i in ('relation', 't_head_id', 'type', 'head_type'))
        sid_dict = {}
        theads = cls.find_by_ids(t_head_id)
        if type == 'save':
            total_amount = 0
            if len(theads)>0:
                thead_relation = theads[0].relation_si
                if thead_relation:
                    relation = ",".join([relation, thead_relation])
            relations = list(set(relation.split(",")))
            for rela in relations:
                if rela:
                    sids = SID.get_details(rela)
                    sicharges = SICharge.find(rela)
                    sids, sicharges, include_tax = _all_rewrite_price_and_filter_charges(sicharges, sids)
                    for sid in sids:
                        if sid_dict.get("%s_%s" % (sid.sc_item_line_no,sid.item_no)):
                            sid_dict["%s_%s" % (sid.sc_item_line_no,sid.item_no)] += int(sid.qty)
                        else:
                            sid_dict.update({"%s_%s" % (sid.sc_item_line_no,sid.item_no):int(sid.qty)})
                        total_amount += float(sid.unit_price)*int(sid.qty)
                    for sicharge in sicharges:
                        total_amount += float(sicharge.amount)
        so_total_amount = 0                    
        for i in theads:
            if type == 'save':
                for socharge in i.charges:
                    so_total_amount += float(socharge.vat_total)
                for sodetail in i.so_details:
                    so_total_amount += float(sodetail.unit_price) * int(sodetail.vat_qty)
                    if not int(sodetail.vat_qty) >= int(sid_dict.get("%s_%s" % (sodetail.line_no,sodetail.item_no),0)):
                        return 1
                if float(total_amount - so_total_amount) > 0.05 and not head_type:
                    return 1
                i.relation_si = ",".join([i.relation_si, relation]) if i.relation_si else relation
                i.relation_si = ",".join(list(set(i.relation_si.split(","))))
            if type == 'delete':
                i.relation_si = relation
                for a in i.c_heads:
                    a.relation_si = None
                    for b in a.so_details:
                        b.invoice_no = None
                        b.invoice_qty = None
                        DBSession.merge(b)
            DBSession.merge(i)
            return 0
    
    @classmethod
    def find_mso(cls, invoice_no):
        return DBSession.query(cls).filter(cls.relation_si.like('%s' % "%"+invoice_no+"%")).filter(cls.active == 0).first()
    
    @classmethod
    def get_mso_mcn(cls, sid, mosd, line_no = None, item_no = None):
        mso_qty, mso_mcn_qty, si_qty, msi_qty, msi_mcn_qty  = 0, 0, 0, 0, 0
        sids = []
        for a in sid:
            for d in a[0]:sids.append(d)
        for e in sids:
            if line_no:
                if line_no == e.sc_item_line_no and item_no == item_no:
                    si_qty += e.qty
                    msi_qty += e.msi_qty
                    msi_mcn_qty += e.mcn_qty
            else:
                si_qty += e.qty
                msi_qty += e.msi_qty
                msi_mcn_qty += e.mcn_qty
                    
        for c in mosd:
            if c.c_head_id and c.invoice_no == None:
                if line_no and item_no:
                    if line_no == c.line_no and item_no == item_no:
                        mso_mcn_qty += pn(c.vat_qty)
                else: 
                    mso_mcn_qty += pn(c.vat_qty)
                    
            if c.t_head_id and c.invoice_no == None:
                if line_no and item_no:
                    if line_no == c.line_no and item_no == item_no:
                        mso_qty += pn(c.vat_qty)
                else:  
                    mso_qty += pn(c.vat_qty)    
        if si_qty>0:
            msi_mcn_qty = 0 
        return mso_qty, mso_mcn_qty, si_qty, msi_qty, msi_mcn_qty 
    
    @classmethod
    def get_mso_mcn_qty(cls, invoice_no):
        mso_qty, mcn_qty, msn_details, relation_si, invoice_qty, self_si_qty, mso_ava_qty, all_ava_qty, self_ava_qty = 0, 0, [], None, 0, 0, 0, 0, 0
        mso = cls.find_mso(invoice_no)
        soheads = mso.so_heads if mso else []
        for d in soheads:
            if d.t_head_id:
                sodetails = d.find_details(invoice_no)
                for e in sodetails:
                    mcn_qty += e.mcn_qty
                    mso_qty += e.vat_qty
                    mso_ava_qty += e.available_qty
                    
        if mso:relation_si = mso.relation_si
        
        if relation_si:relation_si = relation_si.split(",")
        else: relation_si = []
        all_qty, out_qty, self_qty = 0, 0, 0
        for a in relation_si:
            sid =  SID.find(a)
            if sid[0]:
                for b in sid[0]:
                    all_qty += pi(b.qty)
                    all_ava_qty += pi(b.available_qty)
                    if invoice_no == a:
                        self_ava_qty = pi(b.available_qty)
                        self_si_qty = pi(b.qty)
                    if not invoice_no == a:out_qty += pi(b.available_qty) 
        return mso_qty, mcn_qty, all_qty, out_qty, self_ava_qty, mcn_qty, self_si_qty, mso_ava_qty, all_ava_qty
    
    @classmethod
    def base_mos_mcn_si_qty(cls, sales_contract_no = None, invoice_no = None):
        relation_si, sid, mosd = [], [], []
        if invoice_no:
            mso = SiHead.get_by_invoice(invoice_no)
            sales_contract_no = mso.sc_no
        soheads = SoHead.get_by_so(sales_contract_no)
        for a in soheads:
            b = a.t_head
            mso_details = a.so_details
            for c in mso_details: 
                mosd.append(c)    
            if b and a.t_head_id:
                relation_si = b.relation_si
                if relation_si and len(relation_si)>0:
                    if isinstance(relation_si,list):
                        relation_si = ",".join(relation_si).split(",")
                    else:relation_si = relation_si.split(",")
                    for d in relation_si: sid.append(SID.find(d))
        return sid, mosd
            
    @classmethod
    def get_mso_mcn_si_qty(cls, sid, mosd, line_no=None, item_no=None, t_head_id=None):
        mcn_qty, mso_qty, all_qty, self_qty, self_out_qty, invoice_qty, relation_si= 0, 0, 0, 0, 0, 0, None
        for a in sid:
            for e in a[0]:
                t_head = cls.find_mso(e.invoice_no)
                t_head = t_head.id if t_head else None
                if line_no == e.sc_item_line_no and t_head != t_head_id:
                    self_out_qty += pi(e.qty)
                if line_no == e.sc_item_line_no and t_head == t_head_id:
                    self_qty += pi(e.qty)
                all_qty += pi(e.qty)
                    
        for c in mosd:
            if c.c_head_id:
                relation_si = c.c_head.relation_si.split(",") if c.c_head.relation_si else []
                if line_no and item_no:
                    if line_no == c.line_no and item_no == item_no:
                        mcn_qty += pn(c.vat_qty)
                        if c.invoice_qty and len(relation_si) > 0:
                            relations_dic = {}
                            relation_li = [li for li in c.invoice_qty.split(",") if len(li) > 0]
                            for di in relation_li: 
                                dic = di.split(":") 
                                if len(dic) > 0:relations_dic.update({dic[0]:dic[1]})
                            for key_line, values in relations_dic.iteritems():
                                invoice_qty += pi(values) 
                else: 
                    mcn_qty += pn(c.vat_qty)
                    if c.invoice_qty and len(relation_si) > 0:
                        relations_dic = {}
                        relation_li = [li for li in c.invoice_qty.split(",") if len(li) > 0]
                        for di in relation_li: 
                            dic = di.split(":") 
                            if len(dic) > 0:relations_dic.update({dic[0]:dic[1]})
                        for key_line, values in relations_dic.iteritems():
                            invoice_qty += pi(values)  
            else:
                if line_no and item_no:
                    if line_no == c.line_no and item_no == item_no:
                        mso_qty += pn(c.vat_qty)
                else: mso_qty += pn(c.vat_qty)
        return mso_qty, mcn_qty - invoice_qty  if relation_si and len(relation_si) >0 else mcn_qty , all_qty, self_out_qty, self_qty
    
    @classmethod
    def find_details_by_keys(cls, customer_code, rec_month, payment_status, status, vat_date_from, vat_date_to, create_date_from, create_date_to):
        data = DBSession.query(cls).filter(cls.active == 0).filter(cls.company_code.in_(getCompanyCode())).order_by(asc(cls.id))
        if customer_code:
            data = data.filter(cls.customer_code == customer_code)
        if rec_month:
            data = data.filter(cls.rec_month == rec_month)
        if payment_status:
            data = data.filter(cls.payment_status == payment_status)
        if status:
            data = data.filter(cls.status == status)
        if vat_date_from:
            data = data.filter(cls.vat_date >= dt.strptime(vat_date_from + "00:00:00", "%Y-%m-%d%H:%M:%S"))
        if vat_date_to:
            data = data.filter(cls.vat_date <= dt.strptime(vat_date_to + "23:59:59", "%Y-%m-%d%H:%M:%S"))
        if create_date_from:
            data = data.filter(cls.create_time >= dt.strptime(create_date_from + "00:00:00", "%Y-%m-%d%H:%M:%S"))
        if create_date_to:
            data = data.filter(cls.create_time <= dt.strptime(create_date_to + "23:59:59", "%Y-%m-%d%H:%M:%S"))
        return data.all()
    
                       
class CHead(Table_CHead):

    @classmethod
    def find(cls, category=None, ** args):
        ids = [0]
        page, limit, cate = 25, 0, 'next'
        status = args.get('status')
        item_code, invoice_no, sales_contract_no, vat_no, create_by_id, co = (args.get(i, '').strip() for i in ('item_code', 'invoice_no', 'sales_contract_no', 'vat_no',  'create_by_id', 'co'))
        if item_code:
            ids.extend(SiDetail.get_chead_ids(item_code))
            ids.extend(SoDetail.get_chead_ids(item_code))
        if sales_contract_no:
            ids.extend(SiHead.get_chead_ids(invoice_no, sales_contract_no))
            ids.extend(SoHead.get_chead_ids(sales_contract_no))
        elif invoice_no:
            ids.extend(SiHead.get_chead_ids(invoice_no, sales_contract_no))
        if args.get('create_by_id'):
            users =  cls.user_name_id(args['create_by_id'])
            if len(users)>0:
                args['create_by_id'] = users[0].user_id
            else:
                return []
        if len(ids) > 1: args['ids'] = list(set(ids))
        arr_not_null = []
        if vat_no: arr_not_null.append('vat_no')
        
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit")) 
            offset = int(args.get("offset"))
        
        if category:offset = None
        params = {
            const.QUERY_TYPE_LIKE: ['thead_ref', 'ref', 'customer_code'],
            const.QUERY_TYPE_LIKE_AND_OR: [('customer_name', 'customer_name', 'customer_short_name')],
            const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
            const.QUERY_TYPE_IN: [('id', 'ids')],
            const.QUERY_TYPE_ORDER_BY: ['create_time'],
            const.QUERY_TYPE_CREATE_BY: ['create_by_id'],
            const.QUERY_TYPE_COMPANY_CODE: ['company_code'],
            const.QUERY_TYPE_NOT_NULL: arr_not_null
        }
        if isinstance(status, list):
            params[const.QUERY_TYPE_IN].append('status')
        else:
            params.update({const.QUERY_TYPE_EQ: ['status']})
        queryExtend = QueryExtend(cls, ** args)
        queryExtend.query_all(True, DBSession, False, limit, offset, ** params)
        if vat_no or co:
            results = []
            for i in queryExtend.result:
                if co == 'cost':
                    if i.n_head_id or i.subtraction == 1:
                        continue
                    thead = i.t_head
                    ohead = OHead.get_ohead_by_thead(thead.id)
                    if len(ohead) == 0:
                        continue
                if vat_no:
                    for j in i.vat_no.split(','):
                        if len(j.split('~')) == 1 and vat_no == j:
                            results.append(i)
                            break
                        elif len(j.split('~')) == 2:
                            kk = j.split('~')
                            if int(kk[0]) <= int(vat_no) and int(kk[1]) >= int(vat_no):
                                results.append(i)
                                break
                else:
                    results.append(i)
            if category:            
                return results
            else:
                return results, offset, limit
        else:
            if category: 
                return queryExtend.result
            else:
                return queryExtend.result, offset, limit


    @classmethod
    def create(cls, ** args):
        mCRef = CRef()
        ref = 'MCN'
        max = mCRef.get(ref) 
        thead = THead.get(args['id'])
        keys = ['head_type', 'customer_code', 'customer_name', 'customer_type', 'company_code', 'customer_short_name', ('thead_vat_no', 'vat_no'), ('thead_ref', 'ref'), ('t_head_id', 'id'),
            {'status':const.VAT_CHEAD_STATUS_NEW}, {'ref':'%s%s' % (ref, max)},'relation_si']
        params = _get_params_from_args_and_obj(keys, thead, ** args)
        chead = CHead( ** params)
        chead.o_head_id = thead.o_head_id
        DBSession.add(chead)
        DBSession.flush()

        shArgs = {'c_head_id': chead.id}
        if chead.head_type == const.ERP_HEAD_TYPE_SI:
            for si in thead.si_heads:
                siHead = SiHead.create(si, ** shArgs)
                shArgs.update({'si_head_id':siHead.id})
                SiDetail.create(si.si_details, ** shArgs)
                Charge.create(const.CHARGE_TYPE_C_SI, Charge.find_t_si_t_si_charges(thead.id, si.invoice_no), ** shArgs)
        elif chead.head_type == const.ERP_HEAD_TYPE_SO:
            for so in thead.so_heads:
                soHead = SoHead.create(so, ** shArgs)
                shArgs.update({'so_head_id':soHead.id})
                SoDetail.create(so.so_details, ** shArgs)
                Charge.create(const.CHARGE_TYPE_C_SO, Charge.find_t_so_charges(thead.id, so.sales_contract_no), ** shArgs)
        return chead

    @classmethod
    def update_all_status(cls, ** args):
        (status, ids) = (args.get(i, '') for i in ('status', 'ids'))
        cheads = cls.find_by_ids(ids)
        for i in cheads:
            i.remark = args.get("remark-%s" % i.id)
            if status == const.VAT_CHEAD_STATUS_CANCELLED:
                if i.n_head_id and i.n_head.status != const.VAT_CHEAD_STATUS_CANCELLED:
                    return True
                    break
                else:i.status = status
                if i.head_type == const.ERP_HEAD_TYPE_SI:
                    for j in i.si_heads:
                        j.active = 1
                        for u in j.si_details:
                            u.active = 1
                            DBSession.merge(u)
                        DBSession.merge(j)
                else:
                    for j in i.so_heads:
                        j.active = 1
                        for u in  j.so_details:
                            u.active = 1
                            DBSession.merge(u)
                        DBSession.merge(j)
                for j in i.charges:
                    j.active = 1
                    DBSession.merge(j)
            else:i.status = status
            
            if status == const.VAT_CHEAD_STATUS_RESERVE:
                if i.head_type == const.ERP_HEAD_TYPE_SI:
                    for j in i.si_heads:
                        msi_qty_only_self_dict = SiDetail.find_t_si_detail_qty_only_self_dict(j.invoice_no, j.c_head.t_head_id)
                        for u in j.si_details:
                            key = u.line_no
                            self_msn_qty = 0
                            msn_details = SiDetail.get_details(u.invoice_no, u.line_no, u.item_no) 
                            for b in msn_details:
                                if b.c_head_id:
                                    if b.uuid == u.uuid and b.id != u.id: self_msn_qty += pn(b.vat_qty)
                            u.base_ava_qty = msi_qty_only_self_dict.get(key, 0) - self_msn_qty
                            DBSession.merge(u)
                else: 
                    for j in i.so_heads:
                        mso_qty_only_self_dict = SoDetail.find_t_so_detail_qty_only_self_dict(j.sales_contract_no, j.c_head.t_head_id)
                        for u in  j.so_details:
                            key = u.line_no
                            self_msn_qty = 0
                            msn_details = SoDetail.get_details(u.sales_contract_no,u.line_no,u.item_no) 
                            for b in msn_details:
                                if b.c_head_id:
                                    if b.uuid == u.uuid and b.id != u.id: self_msn_qty += pn(b.vat_qty)
                            u.ava_qty = mso_qty_only_self_dict.get(key, 0) - self_msn_qty
                            DBSession.merge(u)

    @classmethod
    def update_all_vat_info(cls, ** args):
        (vat_no, vat_date, ids) = (args.get(i, '').strip() for i in ('vat_no', 'vat_date', 'ids'))
        cheads = cls.find_by_ids(ids)
        for i in cheads:
            i.vat_no = vat_no
            i.vat_date = dt.strptime('%s00:00:00' % vat_date, "%Y-%m-%d%H:%M:%S")
            DBSession.merge(i)

    @classmethod
    def find_thead_cst(cls, ** args):
        rs = True
        ids = args.get('ids')
        if ids:
            for id in ids.split(','):
                id = id.split('$')[0]
                chead = CHead.get(id)
                if chead:
                    thead = chead.t_head
                    ohead = OHead.get_ohead_by_thead(thead.id)
                    if len(ohead) == 0:
                        rs = False
                else:
                    rs = False
        return rs

    @classmethod
    def find_chead_by_ref(cls, ref):
        return DBSession.query(cls).filter(cls.ref == ref).filter(cls.active == 0).first()
        
        
class SiHead(Table_SiHead):

    @classmethod
    def create(cls, si=None, ** args):
        if args.has_key('c_head_id'):
            keys = ['c_head_id',
                'invoice_no', 'company_code', 'sc_no', 'department', 'create_date',
                'status', 'customer', 'customer_short_name', 'cust_po_no',
                'currency', 'order_amt', 'item_amt', 'so_sales_contact', 'erp_create_date']
        else:
            keys = ['t_head_id',
                'invoice_no', 'company_code', 'sc_no', 'department', ('create_date', 'invoice_date'),
                'status', 'customer', 'cust_po_no', 'customer_short_name',
                'currency', 'order_amt', 'item_amt', 'so_sales_contact']
            si = SI.get(args['invoice_no'])
        params = _get_params_from_args_and_obj(keys, si, ** args)
        siHead = cls(** params)
        siHead.erp_create_date = si.create_date
        DBSession.add(siHead)
        DBSession.flush()
        return siHead
    
    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).get(id)
    
    @classmethod
    def get_by_invoice(cls, invoice):
        return DBSession.query(cls).filter(cls.invoice_no == invoice).first()
    
    def find_details(self):
        results = []
        if self.t_head_id:
            si_detail = SID.get_details(self.invoice_no)
            cn_detail = RID.get_details(self.invoice_no)
            for i in self.si_details:
                msn_qty, self_msn_qty, vat_qty, sid_qty, rid_qty, msc_qty, re_msn_qty = 0, 0, 0, 0, 0, 0, 0
                key = i.line_no
                relation_si_qty = SoDetail.find_relation_si(self.invoice_no, i.item_no, i.sc_item_line_no)
                for a in si_detail:
                    if a.item_no == i.item_no and i.line_no == a.line_no:
                        sid_qty = a.qty      
                for b in cn_detail:
                    if b.item_no == i.item_no and i.line_no == b.invoice_item_line_no:
                        rid_qty = b.note_qty      
                msn_details = SiDetail.get_details(i.invoice_no, i.line_no, i.item_no) 
                for b in msn_details:
                    if b.c_head_id:
                        msn_qty += pn(b.vat_qty)
                        if b.uuid == i.uuid: self_msn_qty += pn(b.vat_qty)
                    else:
                        if self.t_head.status == const.VAT_THEAD_STATUS_NEW:
                            if b.id != i.id: vat_qty += pn(b.vat_qty)
                        else:vat_qty += pn(b.vat_qty)   
                msc_qty =  relation_si_qty[1]  
                i.msc_qty = msc_qty
                i.cn_qty  = rid_qty
                i.mcn_qty = self_msn_qty
                if relation_si_qty[0] == 0:
                    i.available_qty = sid_qty - rid_qty - vat_qty + msn_qty
                else:
                    i.available_qty = sid_qty - rid_qty - vat_qty + msn_qty - sid_qty + msc_qty
                results.append(i)
                
        elif self.c_head_id:
            mcn_qty_except_self_dict = SiDetail.find_c_si_detail_qty_except_self_dict(self.invoice_no, self.c_head_id)
            msi_qty_only_self_dict = SiDetail.find_t_si_detail_qty_only_self_dict(self.invoice_no, self.c_head.t_head_id)
            for i in self.si_details:
                key = i.line_no
                self_msn_qty = 0
                msn_details = SiDetail.get_details(i.invoice_no,i.line_no,i.item_no) 
                for b in msn_details:
                    if b.c_head_id:
                        if b.uuid == i.uuid and b.id != i.id: self_msn_qty += pn(b.vat_qty)
                i.available_qty = msi_qty_only_self_dict.get(key, 0) - self_msn_qty
                results.append(i)
        
        return sorted(results.__iter__(), key=lambda x:x.line_no)


    def find_charges(self):

        results = []
        if self.t_head_id:
            si_charge = self.charges
            cn_charge = RICharge.find_all_charges(self.invoice_no, 'desc')
            for a in si_charge:
                vat_total, msn_total, self_msn_total = 0, 0, 0
                key = a.line_no
                msn_charge = Charge.find_details(a.invoice_no, a.line_no) 
                for b in msn_charge:
                    if b.c_head_id:
                        msn_total += pn(b.vat_total)
                        if b.uuid == a.uuid: self_msn_total += pn(b.vat_total)
                    elif b.t_head_id:
                        if self.t_head.status == const.VAT_THEAD_STATUS_NEW:
                            if b.id != a.id: vat_total += pn(b.vat_total)
                        else:vat_total += pn(b.vat_total) 
                a.msi_total = vat_total
                a.mcn_total = self_msn_total
                a.available_total = Decimal(a.total) - Decimal(a.msi_total) + Decimal(msn_total)
                for b in cn_charge:
                    if b.chg_discount_code.decode("utf-8") == a.charge_code:
                        a.available_total = Decimal(a.total) - Decimal(b.total) - Decimal(a.msi_total) + Decimal(msn_total)
                a.vat_total = a.vat_total
                a.id = a.id
                if a.type == const.CHARGE_TYPE_T_SI:
                    results.append(a)
                
        elif self.c_head_id:
            mcn_total_except_self_dict = Charge.find_c_si_charge_except_self_dict(self.invoice_no, self.c_head_id)
            msi_total_only_self_dict = Charge.find_t_si_charge_only_self_dict(self.invoice_no, self.c_head.t_head_id)
            for i in self.charges:
                key = i.line_no
                i.available_total = msi_total_only_self_dict.get(key, 0) - mcn_total_except_self_dict.get(key, 0)
                if i.total != 0:
                    results.append(i)
        return results

    def update_details(self, ** args):
        remark = []
        for i in self.find_details():
            if args.get('qty_%s' % i.id):
                mg = merge([i.remark, i.vat_qty,i.desc_zh if i.desc_zh else i.item_desc,str(i.unit_price),i.line_no],[args.get('remark_%s' % i.id,None), int(args.get('qty_%s' % i.id, 0)),args.get('desc_%s' % i.id, ''),args.get('price_%s' % i.id,0) if args.get('price_%s' % i.id,0) else str(i.unit_price)],['Remark', 'VAT Qty','Description','Unit Price','Line NO'])
                if mg: remark.append(mg)
            i.vat_qty = int(args.get('qty_%s' % i.id, 0))
            i.desc_zh = args.get('desc_%s' % i.id, '')
            i.remark  = args.get('remark_%s' % i.id, '')
            if args.get('price_%s' % i.id, 0): i.unit_price = str(args.get('price_%s' % i.id, 0))
            ItemDesc.save(** {'code':self.customer, 'item_no':i.item_no, 'description':i.desc_zh})
        return ",".join(remark) if len(remark)>0 else None   

    def update_charges(self, ** args):
        remark = []
        for i in self.find_charges():
            if args.get('total_%s' % i.id):
                mg = merge([i.vat_total,i.line_no],[args.get('total_%s' % i.id)],['VAT Qty','Line NO'])
                if mg: remark.append(mg)
            i.vat_total = args.get('total_%s' % i.id)
            DBSession.merge(i)
        return ",".join(remark) if len(remark)>0 else None 
    
    @classmethod
    def find_t_si_head_qty_dict(cls, invoice_no = None):
        if invoice_no:
            sql = "select INVOICE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where T_HEAD_ID is not NULL and invoice_no='%s' and company_code in %s and active='0' GROUP BY INVOICE_NO" % (invoice_no, getCompanyCode(1))
        else:
            sql = "select INVOICE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where T_HEAD_ID is not NULL and company_code in %s and active='0' GROUP BY INVOICE_NO" % getCompanyCode(1)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_si_head_qty_dict(cls, invoice_no = None):
        if invoice_no:
            sql = "select INVOICE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where C_HEAD_ID is not NULL and invoice_no='%s' and company_code in %s and active='0' GROUP BY INVOICE_NO" % (invoice_no, getCompanyCode(1))
        else:
            sql = "select INVOICE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where C_HEAD_ID is not NULL and company_code in %s and active='0' GROUP BY INVOICE_NO" % getCompanyCode(1)
        return _fetch_sql_to_dict(sql)
    
    @classmethod
    def find_t_si_head_qty_key(cls, invoice_no):
        sql = "select INVOICE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where T_HEAD_ID is not NULL and company_code in %s and invoice_no='%s' and active='0' GROUP BY INVOICE_NO" % (getCompanyCode(1), invoice_no)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_si_head_qty_key(cls, invoice_no):
        sql = "select INVOICE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where C_HEAD_ID is not NULL and company_code in %s and invoice_no='%s' and active='0' GROUP BY INVOICE_NO" % (getCompanyCode(1), invoice_no)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_all_customer_si_qty_dict(cls, date_from, date_to, customer_code):
        sql = '''
                         SELECT vsh.customer, sum(vsd.qty) FROM vat_si_head vsh, vat_si_detail vsd  
                WHERE vsh.COMPANY_CODE IN ('PRACSZ','RPACPACK')
                AND vsh.CREATE_DATE>='%s 00:00:00'
                AND vsh.CREATE_DATE<='%s 23:59:59'
                AND vsh.id=vsd.si_head_id AND vsh.t_head_id=vsd.t_head_id %s
              GROUP BY vsh.customer
            ''' % (date_from, date_to, "AND vsh.customer='%s' " % customer_code if customer_code else '')
        return _fetch_sql_to_dict(sql)
    
    @classmethod
    def get_thead_ids(cls, invoice_no, sales_contract_no):
        data = DBSession.query(distinct(cls.t_head_id))
        if invoice_no:
            data = data.filter(cls.invoice_no == invoice_no)
        if sales_contract_no:
            data = data.filter(cls.sc_no == sales_contract_no)
        results = [i[0] for i in data]
        return results if results else [0]

    @classmethod
    def get_chead_ids(cls, invoice_no, sales_contract_no):
        data = DBSession.query(distinct(cls.c_head_id))
        if invoice_no:
            data = data.filter(cls.invoice_no == invoice_no)
        if sales_contract_no:
            data = data.filter(cls.sc_no == sales_contract_no)
        results = [i[0] for i in data]
        return results if results else [0]


class SiDetail(Table_SiDetail):

    available_qty, mcn_qty = (0, 0)

    @classmethod
    def create(cls, siDetails, ** args):
        if args.has_key('c_head_id'):
            for sid in siDetails:
                keys = ['c_head_id', 'si_head_id', ('qty', 'vat_qty'),
                    'invoice_no', 'sc_no', 'company_code', 'line_no',
                    'item_no', 'item_desc', 'desc_zh', 'unit_price', 'unit', {'vat_qty':0}, 'uuid', 'remark', 'sc_item_line_no']
                params = _get_params_from_args_and_obj(keys, sid, ** args)
                siDetail = cls( ** params)
                DBSession.add(siDetail)
        else:
            for sid in siDetails:
                sihead = SiHead.get(args.get('si_head_id'))
                keys = ['t_head_id', 'si_head_id', 'qty', ('vat_qty', 'available_qty'),
                    'invoice_no', 'sc_no', 'company_code', 'line_no',
                    'item_no', 'item_desc', ('desc_zh', 'item_desc'), 'unit_price', 'unit', 'sc_item_line_no', 'base_ava_qty']
                params = _get_params_from_args_and_obj(keys, sid, ** args)
                siDetail = cls( ** params)
                item_desc = ItemDesc.get(sihead.customer, siDetail.item_no)
                if item_desc:
                    siDetail.desc_zh = item_desc.description
                siDetail.uuid = str(uuid.uuid4())
                DBSession.add(siDetail)

    @classmethod
    def find_t_si_detail_qty_dict(cls, invoice_no):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where T_HEAD_ID is not NULL and  INVOICE_NO='%s' and active='0' GROUP BY LINE_NO" % (invoice_no)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_si_detail_qty_dict(cls, invoice_no):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where C_HEAD_ID is not NULL and INVOICE_NO='%s' and active='0' GROUP BY LINE_NO" % (invoice_no)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_si_detail_qty_except_self_dict(cls, invoice_no, t_head_id):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where T_HEAD_ID is not NULL and INVOICE_NO='%s' and active='0' and T_HEAD_ID!='%s' GROUP BY LINE_NO" % (invoice_no, t_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_si_detail_qty_except_self_dict(cls, invoice_no, c_head_id):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where C_HEAD_ID is not NULL and INVOICE_NO='%s' and active='0' and C_HEAD_ID!='%s' GROUP BY LINE_NO" % (invoice_no, c_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_si_detail_qty_only_self_dict(cls, invoice_no, t_head_id):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SI_DETAIL where T_HEAD_ID is not NULL and INVOICE_NO='%s' and active='0' and T_HEAD_ID='%s' GROUP BY LINE_NO" % (invoice_no, t_head_id)
        return _fetch_sql_to_dict(sql)
    
    @classmethod
    def find_c_si_detail_qty_out_self_val(cls, invoice_no, item_no, id, line_no):
        sql = "select sum(VAT_QTY)  from VAT_SI_DETAIL where  INVOICE_NO='%s' and active='0' and item_no='%s' and id !='%s' and line_no='%s' GROUP BY LINE_NO" % (invoice_no, item_no, id, line_no)
        result = DBSession.execute(sql).fetchone()
        return result[0] if result else 0
    
    @classmethod
    def get_thead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.t_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]

    @classmethod
    def get_chead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.c_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]

    @classmethod
    def get_details(cls,invoice_no, line_no = None, item_no = None, uuid = None):
        data = DBSession.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.active == 0).filter(cls.company_code.in_(getCompanyCode()))
        if line_no: data = data.filter(cls.line_no == line_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if uuid:data = data.filter(cls.uuid == uuid)
        return data.all()
    
    @classmethod
    def get_details_by_so(cls, sc_no):
        return DBSession.query(cls).filter(cls.sc_no == sc_no).filter(cls.active == 0).filter(cls.company_code.in_(getCompanyCode())).all()
    
    @classmethod
    def get_qty_mso_mcn(cls,invoice_no, line_no = None,item_no= None, uuid = None):
        qty, mso, mcn = 0, 0, 0
        siDetails = cls.get_details(invoice_no, line_no , item_no, uuid )
        for a in siDetails:
            if a.t_head_id:
                qty += a.qty
                mso += a.vat_qty
            elif a.c_head_id:
                if a.c_head.status == const.VAT_THEAD_STATUS_POST:
                    c_head = a.c_head               
                    c_head.subtraction = 1
                    DBSession.merge(c_head)
                    mcn += a.vat_qty
        return qty, mso, mcn
    
    
        
class SoHead(Table_SoHead):

    @classmethod
    def create(cls, so=None, ** args):
        if args.has_key('c_head_id'):
            keys = ['c_head_id', 'sales_contract_no', 'company_code', 'order_dept', 'status',
                'customer_code', 'customer_name', 'currency', 'create_date',
                'ae', 'cust_po_no', 'order_amt', 'item_amt', 'erp_create_date']
        else:
            keys = ['t_head_id', 'sales_contract_no', 'company_code', 'order_dept', 'status',
                'customer_code', 'customer_name', 'currency', ('create_date', 'issue_date'),
                'ae', 'cust_po_no', 'order_amt', 'item_amt']
            so = SO.get(args['sales_contract_no'])
        params = _get_params_from_args_and_obj(keys, so, ** args)
        soHead = cls(** params)
        soHead.erp_create_date = so.create_date
        DBSession.add(soHead)
        DBSession.flush()
        return soHead

    @classmethod
    def find_all_customer_so_qty_dict(cls, date_from, date_to, customer_code):
        sql = '''
                         SELECT vsh.customer_code, sum(vsd.qty) FROM vat_so_head vsh, vat_so_detail vsd  
                WHERE vsh.COMPANY_CODE IN ('PRACSZ','RPACPACK')
                AND vsh.CREATE_DATE>='%s 00:00:00'
                AND vsh.CREATE_DATE<='%s 23:59:59'
                AND vsh.id=vsd.so_head_id AND vsh.t_head_id=vsd.t_head_id %s
              GROUP BY vsh.customer_code
            ''' % (date_from, date_to, "AND vsh.customer_code='%s' " % customer_code if customer_code else '')
        return _fetch_sql_to_dict(sql)
    
    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).get(id)
    
    @classmethod
    def get_by_so(cls, so_no):
        return DBSession.query(cls).filter(cls.sales_contract_no == so_no).filter(cls.active == 0).all()
    
    def find_details(self, si_type = None):
        results = []
        if self.t_head_id:
            relation_si = self.t_head.relation_si if self.t_head else None
            relation_si = relation_si.split(",") if relation_si else []
            sod_qty_dict = SOD.find_so_detail_qty_dict(self.sales_contract_no)
            mcn_qty_dict = SoDetail.find_c_so_detail_qty_dict(self.sales_contract_no)
            mso_qty_except_self_dict = SoDetail.find_t_so_detail_qty_except_self_dict(self.sales_contract_no, self.t_head_id)
            for i in self.so_details:
                msn_qty, self_msn_qty, vat_qty  =  0, 0, 0
                key = i.line_no
                if not sod_qty_dict.get(key):sod_qty_dict[key] = [0,0]
                msn_details = SoDetail.get_details(i.sales_contract_no,i.line_no,i.item_no) 
                for b in msn_details:
                    if b.t_head_id and si_type == None:
                        if b.t_head.relation_si:continue
                    if b.c_head_id and si_type == None:
                        if b.c_head.relation_si:continue
                        
                    if b.c_head_id:
                        msn_qty += pn(b.vat_qty)
                        if b.uuid == i.uuid: 
                            self_msn_qty += pn(b.vat_qty)
                    elif b.t_head_id:
                        if self.t_head.status == const.VAT_THEAD_STATUS_NEW:
                            if not b.id == i.id: vat_qty += pn(b.vat_qty)
                        else:
                            vat_qty += pn(b.vat_qty)
                i.mso_qty = mso_qty_except_self_dict.get(key, 0)
                i.mcn_qty = self_msn_qty
                i.available_qty = Decimal(sod_qty_dict.get(key, [0, 0])[0]) - Decimal(sod_qty_dict.get(key, [0, 0])[1]) + msn_qty - vat_qty
                results.append(i)
                
        elif self.c_head_id:
            mso_qty_only_self_dict = SoDetail.find_t_so_detail_qty_only_self_dict(self.sales_contract_no, self.c_head.t_head_id)
            for i in self.so_details:
                key = i.line_no
                self_msn_qty = 0
                msn_details = SoDetail.get_details(i.sales_contract_no,i.line_no,i.item_no) 
                for b in msn_details:
                    if b.c_head_id:
                        if b.uuid == i.uuid and b.id != i.id: self_msn_qty += pn(b.vat_qty)
                i.available_qty = mso_qty_only_self_dict.get(key, 0) - self_msn_qty
                results.append(i)
                
        results = sorted(results.__iter__(), key=lambda x:x.line_no)
        return results

    def find_charges(self):
        results = []
        if self.t_head_id:
            socharge_total_dict = SOCharge.find_so_charge_total_dict(self.sales_contract_no)
            mcn_total_dict = Charge.find_c_so_charge_total_dict(self.sales_contract_no)
            mso_total_except_self_dict = Charge.find_t_so_charge_except_self_dict(self.sales_contract_no, self.t_head_id)
            for i in self.charges:
                key = i.line_no
                i.mso_total = mso_total_except_self_dict.get(key, 0)
                i.mcn_total = mcn_total_dict.get(key, 0)
                i.available_total = i.total - i.mso_total + i.mcn_total
                results.append(i)
        elif self.c_head_id:
            mcn_total_except_self_dict = Charge.find_c_so_charge_except_self_dict(self.sales_contract_no, self.c_head_id)
            mso_total_only_self_dict = Charge.find_t_so_charge_only_self_dict(self.sales_contract_no, self.c_head.t_head_id)
            for i in self.charges:
                key = i.line_no
                i.available_total = mso_total_only_self_dict.get(key, 0) - mcn_total_except_self_dict.get(key, 0)
                results.append(i)
        return results
    
    @classmethod
    def find_sum_ava_detail(cls, sales_contract_no):
        soheads = DBSession.query(cls).filter(cls.sales_contract_no == sales_contract_no).filter(cls.active == 0).all()
        sum_details = 0
        for a in soheads:
            if a.t_head_id:
                sodetails = a.find_details()
                for b in sodetails:
                    sum_details += b.available_qty
        return sum_details
        
    def update_details(self, ** args):
        remark, invoice_qty = [], []
        for i in self.find_details():
            if args.get('qty_%s' % i.id):
                mod,obj,cat = [i.vat_qty, i.desc_zh if i.desc_zh else i.description, str(i.unit_price), i.line_no],[int(args.get('qty_%s' % i.id, 0)), args.get('desc_%s' % i.id, ''), args.get('price_%s' % i.id,0) if args.get('price_%s' % i.id,0) else str(i.unit_price)],['VAT Qty','Description','Unit Price','Line NO']
                if i.t_head_id:
                    mod.insert(0, i.remark)
                    obj.insert(0, args.get('remark_%s' % i.id, None))
                    cat.insert(0, 'Remark')
                mg = merge( mod, obj, cat)
                if mg:remark.append(mg)
            i.vat_qty = int(args.get('qty_%s' % i.id, 0))
            i.desc_zh = args.get('desc_%s' % i.id, '')
            i.remark  = args.get('remark_%s' % i.id, '')
            if args.get('invoice_no_%s' % i.id): 
                invoice_no = args.get('invoice_no_%s' % i.id)
                invoice_no = list(set(invoice_no if isinstance(invoice_no,list) else [invoice_no]))
                for a in invoice_no: 
                    for k, v in args.iteritems():
                        if k.find(a) > -1 and v:
                            cate_invoice = "%s:%s" % (k, v)
                            if cate_invoice not in invoice_qty:invoice_qty.append("%s:%s" % (k, v))
                i.invoice_no = ",".join(invoice_no)
                i.invoice_qty = ",".join(invoice_qty)
            if args.get('price_%s' % i.id, 0): i.unit_price = str(args.get('price_%s' % i.id, 0))
            ItemDesc.save(** {'code':self.customer_code, 'item_no':i.item_no, 'description':i.desc_zh})
        return ','.join(remark) if len(remark)>0 else None
        
    def update_charges(self, ** args):
        remark = []
        for i in self.find_charges():
            if args.get('total_%s' % i.id):
                mg = merge([i.vat_total,i.line_no],[args.get('total_%s' % i.id)],['VAT Qty','Line NO'])
                if mg: remark.append(mg)
            i.vat_total = args.get('total_%s' % i.id, 0)
            DBSession.merge(i)
        return ','.join(remark) if len(remark)>0 else None

    @classmethod
    def find_t_so_head_qty_dict(cls):
        sql = "select SALES_CONTRACT_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where T_HEAD_ID is not NULL  and active='0' GROUP BY SALES_CONTRACT_NO" 
        return _fetch_sql_to_dict(sql)
    
    @classmethod
    def find_t_so_head_qty_key(cls,sale_no):
        sql = "select SALES_CONTRACT_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where T_HEAD_ID is not NULL and active='0' and SALES_CONTRACT_NO='%s' GROUP BY SALES_CONTRACT_NO" % sale_no
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_so_head_qty_dict(cls):
        sql = "select SALES_CONTRACT_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where C_HEAD_ID is not NULL  and active='0' GROUP BY SALES_CONTRACT_NO" 
        return _fetch_sql_to_dict(sql)
    
    @classmethod
    def find_c_so_head_qty_key(cls,sale_no):
        sql = "select SALES_CONTRACT_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where C_HEAD_ID is not NULL  and active='0' and SALES_CONTRACT_NO='%s' GROUP BY SALES_CONTRACT_NO" % sale_no
        return _fetch_sql_to_dict(sql)

    @classmethod
    def get_thead_ids(cls, sales_contract_no):
        results = [i[0] for i in DBSession.query(distinct(cls.t_head_id)).filter(cls.sales_contract_no == sales_contract_no)]
        return results if results else [0]

    @classmethod
    def get_chead_ids(cls, sales_contract_no):
        results = [i[0] for i in DBSession.query(distinct(cls.c_head_id)).filter(cls.sales_contract_no == sales_contract_no)]
        return results if results else [0]
    
    def available_amount(self):
        so_amount = 0
        sales_contract_no = self.sales_contract_no
        so_details = SOD.find_sod(sales_contract_no)
        so_charges = SOCharge.find(sales_contract_no)
        so_details, so_charges, include_tax = _all_rewrite_price_and_filter_charges(so_charges, so_details)
        soheads = SoHead.get_by_so(sales_contract_no)
        si_details, si_charges = None, None
        for so_detail in so_details:
            so_amount += int(so_detail.qty) * float(so_detail.unit_price)
        for so_charge in so_charges:
            so_amount += float(so_charge.total)
        t_heads = []
        for sohead in soheads:
            if sohead.t_head_id and self.t_head.id != sohead.t_head_id:
                t_heads.append(sohead.t_head_id)
        mso_amount = 0
        for t_head_id in list(set(t_heads)):
            t_head = THead.get(t_head_id)
            msodetails = t_head.so_details
            msocharges = t_head.charges
            for msodetail in msodetails:
                mso_amount += float(msodetail.unit_price) * int(msodetail.vat_qty)
            for msocharge in msocharges:
                mso_amount += float(msocharge.vat_total)
        return so_amount, so_amount - mso_amount

class SoDetail(Table_SoDetail):

    invoiced_qty, available_qty, mcn_qty = (0, 0, 0)

    @classmethod
    def create(cls, soDetails, ** args):
        if args.has_key('c_head_id'):
            for sod in soDetails:
                keys = ['c_head_id', 'so_head_id', ('qty', 'vat_qty'),
                    'sales_contract_no', 'company_code', 'line_no',
                    'item_no', 'description', 'desc_zh', 'unit_price', 'unit', {'vat_qty':0},'uuid','remark']
                params = _get_params_from_args_and_obj(keys, sod, ** args)
                soDetail = cls( ** params)
                DBSession.add(soDetail)
        else:
            for sod in soDetails:
                soHead = SoHead.get(args.get('so_head_id'))
                keys = ['t_head_id', 'so_head_id', ('vat_qty', 'available_qty'), ('qty', 'base_qty'),
                    'sales_contract_no', 'company_code', 'line_no',
                    'item_no', 'description', 'desc_zh', 'unit_price', 'unit', 'invoiced_qty']
                params = _get_params_from_args_and_obj(keys, sod, ** args)
                soDetail = cls( ** params)
                item_desc = ItemDesc.get(soHead.customer_code, soDetail.item_no)
                if item_desc:
                    soDetail.desc_zh = item_desc.description
                soDetail.uuid = str(uuid.uuid4())
                DBSession.add(soDetail)
    
    @classmethod
    def find_relation_si(cls, invoice_no, item_no = None, line_no = None):
        invoice_qty, all_relations_qty = 0, 0
        data =  DBSession.query(cls).filter(cls.invoice_no.like('%s' % "%"+invoice_no+"%")).filter(cls.active == 0).all()
        mso_qty = 0
        relations_qty = 0
        relation_qty = {}
        post_invoice = []
        for a in data:
            if a.invoice_no and a.so_head_id not in post_invoice:
                relation_si = a.invoice_no.split(",")
                relations = [li for li in a.invoice_qty.split(",") if len(li) > 0] if a.invoice_qty else []
                for di in relations: 
                    dic = di.split(":") 
                    if len(dic) > 0:relation_qty.update({dic[0]:dic[1]})
                for key_line, values in relation_qty.iteritems():
                    if key_line.find(invoice_no) > -1:
                        all_relations_qty += pi(values)
                    if item_no and line_no:
                        if key_line.find("%s_%s_" % (invoice_no, line_no)) > -1:
                            relations_qty += pi(values)
                post_invoice.append(a.so_head_id)
            if a.invoice_no == invoice_no and a.item_no == item_no and a.line_no == line_no:
                mso_qty += a.qty
        return all_relations_qty, relations_qty, mso_qty

    @classmethod
    def find_t_so_detail_qty_dict(cls, sales_contract_no):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where T_HEAD_ID is not NULL and SALES_CONTRACT_NO='%s' and active='0' GROUP BY LINE_NO" % sales_contract_no
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_so_detail_qty_dict(cls, sales_contract_no):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where C_HEAD_ID is not NULL  and SALES_CONTRACT_NO='%s' and active='0' GROUP BY LINE_NO" % sales_contract_no
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_so_detail_qty_except_self_dict(cls, sales_contract_no, t_head_id):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where T_HEAD_ID is not NULL  and SALES_CONTRACT_NO='%s' and active='0' and T_HEAD_ID!='%s' GROUP BY LINE_NO" % (sales_contract_no, t_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_so_detail_qty_except_self_dict(cls, sales_contract_no, c_head_id):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where C_HEAD_ID is not NULL  and SALES_CONTRACT_NO='%s' and active='0' and C_HEAD_ID!='%s' GROUP BY LINE_NO" % (sales_contract_no, c_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_so_detail_qty_only_self_dict(cls, sales_contract_no, t_head_id):
        sql = "select LINE_NO, sum(VAT_QTY) as VAT_QTY from VAT_SO_DETAIL where T_HEAD_ID is not NULL  and SALES_CONTRACT_NO='%s' and active='0' and T_HEAD_ID='%s' GROUP BY LINE_NO" % (sales_contract_no, t_head_id)
        return _fetch_sql_to_dict(sql)
    
    @classmethod
    def find_c_so_detail_qty_out_self_val(cls, sales_contract_no, item_no, id,line_no):
        sql = "select sum(VAT_QTY)  from VAT_SO_DETAIL where  company_code in %s and sales_contract_no='%s' and active='0' and item_no='%s' and id !='%s' and line_no='%s' GROUP BY LINE_NO" % (sales_contract_no, item_no, id, line_no)
        result = DBSession.execute(sql).fetchone()
        return result[0] if result else 0

    @classmethod
    def get_thead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.t_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]

    @classmethod
    def get_chead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.c_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]
    
    @classmethod
    def get_details(cls, sales_contract_no, line_no = None,item_no= None, uuid = None):
        data =  DBSession.query(cls).filter(cls.sales_contract_no == sales_contract_no).filter(cls.active == 0).filter(cls.company_code.in_(getCompanyCode()))
        if line_no: data = data.filter(cls.line_no == line_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if uuid: data = data.filter(cls.uuid == uuid)
        return data.all()
    
    @classmethod
    def get_relate_details(cls,invoice_no,line_no = None,item_no= None):
        data =  DBSession.query(cls).filter(cls.invoice_no.ilike('%%%s%%' % invoice_no)).filter(cls.active == 0)
        if line_no: data = data.filter(cls.line_no == line_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        return data.first()
    
    @classmethod
    def get_qty_mso_mcn(cls,sales_contract_no, line_no = None,item_no= None, uuid = None):
        qty, mso, mcn = 0, 0, 0
        sodetails = cls.get_details(sales_contract_no, line_no , item_no, uuid )
        for a in sodetails:
            if a.t_head_id:
                qty += a.qty
                mso += a.vat_qty
            elif a.c_head_id:
                if a.c_head.status == const.VAT_THEAD_STATUS_POST:
                    c_head = a.c_head               
                    c_head.subtraction = 1
                    DBSession.merge(c_head)
                    mcn += a.vat_qty
        return qty, mso, mcn
                

class ItemDesc(Table_ItemDesc):

    @classmethod
    def get(cls, code, item_no):
        return DBSession.query(cls).filter(cls.code == code).filter(cls.item_no == item_no).first()

    @classmethod
    def save(cls, ** args):
        (code, item_no, description, desc_zh) = (args.get(i, '') for i in ('code', 'item_no', 'description', 'desc_zh'))
        itemDesc = cls.get(code, item_no)
        if itemDesc:
            itemDesc.description = desc_zh if desc_zh else description
            DBSession.merge(itemDesc)
        else:DBSession.add(ItemDesc( ** args))


class ItemCode(Table_ItemCode):
    
    @classmethod
    def find(cls, item_no):
        return DBSession2.query(cls).filter(cls.item_code == item_no).all()
    
    @classmethod
    def find_dict(cls, item_code, qty = None):
        result = {}
        if not qty: qty = 1
        itemcodes = cls.find(item_code)
        if len(itemcodes) > 0:
            for itemcode in itemcodes:
                result.update({itemcode.component_item_code: {
                                                              'qty': int(itemcode.qty) * int(qty),
                                                              'item_qty': int(itemcode.qty),
                                                              'all_qty':int(itemcode.qty) * int(qty),
                                                              'type':const.ITEM_CODE_YES
                                                              }})
        else:
            result.update({item_code: {
                                       'qty':int(qty),
                                       'item_qty':1,
                                       'all_qty':int(qty),
                                       'type':const.ITEM_CODE_NO
                                       }})
        return result
    
     
class Charge(Table_Charge):

    available_total, mcn_total, msi_total, mcn_total = (0, 0, 0, 0)

    @classmethod
    def create(cls, type, charges=[], ** args):
        args.update({'type':type})
        keys = []
        for charge in charges:
            if type == const.CHARGE_TYPE_T_SI:
                keys = ['type', 'company_code', 'currency', 'cust_po_no', 'line_no', 'charge_code', 'total', ('vat_total', 'available_total'), 't_head_id', 'si_head_id', 'invoice_no', 'sales_contract_no']
            elif type == const.CHARGE_TYPE_T_SO:
                keys = ['type', 'company_code', 'currency', 'cust_po_no', 'line_no', 'charge_code', 'total', ('vat_total', 'available_total'), 't_head_id', 'so_head_id', 'sales_contract_no']
            elif type == const.CHARGE_TYPE_T_RI:
                keys = ['type', 'company_code', 'line_no', ('charge_code', 'chg_discount_code'), 'total', ('vat_total', 'available_total'), 't_head_id', 'si_head_id', 'invoice_no']
            elif type == const.CHARGE_TYPE_T_CUSTOMER:
                keys = ['type', 'company_code', 'line_no', 'total', 'qty', 't_head_id', 'c_head_id', 'si_head_id', 'cust_code', ('charge_code', 'chg_discount_code')]
            elif type == const.CHARGE_TYPE_T_MANUAL:
                keys = ['type', 'company_code', 'line_no', 'charge_code', 'total', 'qty', 't_head_id', 'c_head_id', 'si_head_id']
            elif type == const.CHARGE_TYPE_C_SI:
                keys = ['type', 'company_code', 'currency', 'cust_po_no',  'line_no', 'charge_code', ('total', 'vat_total'), {'vat_total':0}, 'c_head_id', 'si_head_id', 'sales_contract_no' , 'invoice_no', 'uuid']
            elif type == const.CHARGE_TYPE_C_SO:
                keys = ['type', 'company_code', 'currency', 'cust_po_no',  'line_no', 'charge_code', ('total', 'vat_total'), {'vat_total':0}, 'c_head_id', 'so_head_id', 'sales_contract_no', 'uuid']
            elif type == const.CHARGE_TYPE_C_RI:
                keys = ['type', 'company_code', 'line_no', ('charge_code', 'chg_discount_code'), ('total', 'vat_total'), {'vat_total':0}, 'c_head_id', 'si_head_id', 'invoice_no', 'uuid']
            elif type == const.CHARGE_TYPE_C_CUSTOMER:
                keys = ['type', 'company_code', 'line_no', 'total', 'qty', 't_head_id', 'c_head_id', 'si_head_id', 'cust_code', ('charge_code', 'chg_discount_code'), 'uuid']
            elif type == const.CHARGE_TYPE_C_MANUAL:
                keys = ['type', 'company_code', 'line_no', 'charge_code', 'total', 'qty', 'c_head_id', 'si_head_id']
            params = _get_params_from_args_and_obj(keys, charge, ** args)
            detail = cls( ** params)
            if type in [const.CHARGE_TYPE_T_SI, const.CHARGE_TYPE_T_SO, const.CHARGE_TYPE_T_RI, const.CHARGE_TYPE_T_CUSTOMER, const.CHARGE_TYPE_T_MANUAL]:
                detail.uuid = str(uuid.uuid4())
            DBSession.add(detail)
    
    @classmethod
    def insert(cls, ** kw):
        charge = cls( ** kw)
        charge.uuid = str(uuid.uuid4())
        DBSession.add(charge)
    
    @classmethod
    def find_details(cls, invoice_no, line_no = None):
        data =  DBSession.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.active == 0)
        if line_no: data = data.filter(cls.line_no == line_no)
        return data.all()
    
    @classmethod
    def find_t_si_charges(cls, t_head_id, invoice_no):
        return DBSession.query(cls).filter(cls.t_head_id == t_head_id).filter(cls.invoice_no == invoice_no).all()
    
    @classmethod
    def find_t_si_t_si_charges(cls, t_head_id, invoice_no):
        return DBSession.query(cls).filter(cls.t_head_id == t_head_id).filter(cls.invoice_no == invoice_no).filter(cls.type == 'T_SI').filter(cls.vat_total != '0').all()
    
    @classmethod
    def find_t_si_t_ri_charges(cls, t_head_id, invoice_no):
        return DBSession.query(cls).filter(cls.t_head_id == t_head_id).filter(cls.invoice_no == invoice_no).filter(cls.type == 'T_RI').all()
    
    @classmethod
    def find_t_so_charges(cls, t_head_id, sales_contract_no):
        return DBSession.query(cls).filter(cls.t_head_id == t_head_id).filter(cls.sales_contract_no == sales_contract_no).all()

    @classmethod
    def find_t_si_charge_total_dict(cls, invoice_no=None):
        if invoice_no:
            sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  INVOICE_NO='%s' and type in ('%s','%s') and active='0' GROUP BY LINE_NO" % (invoice_no, const.CHARGE_TYPE_T_SI, const.CHARGE_TYPE_T_RI)
        else:
            sql = "select INVOICE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  type in ('%s','%s') and active='0' GROUP BY INVOICE_NO" % (const.CHARGE_TYPE_T_SI, const.CHARGE_TYPE_T_RI)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_si_charge_total_dict(cls, invoice_no=None):
        if invoice_no:
            sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  INVOICE_NO='%s' and type='%s' and active='0' GROUP BY LINE_NO" % (invoice_no, const.CHARGE_TYPE_C_SI)
        else:
            sql = "select INVOICE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  type='%s' and active='0' GROUP BY INVOICE_NO" % const.CHARGE_TYPE_C_SI
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_si_charge_except_self_dict(cls, invoice_no, t_head_id):
        sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  INVOICE_NO='%s' and type='%s' and active='0' and T_HEAD_ID!='%s' GROUP BY LINE_NO" % (invoice_no, const.CHARGE_TYPE_T_SI, t_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_si_charge_except_self_dict(cls, invoice_no, c_head_id):
        sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  INVOICE_NO='%s' and type='%s' and active='0' and C_HEAD_ID!='%s' GROUP BY LINE_NO" % (invoice_no, const.CHARGE_TYPE_C_SI, c_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_si_charge_only_self_dict(cls, invoice_no, t_head_id):
        sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  INVOICE_NO='%s' and type='%s' and active='0' and T_HEAD_ID='%s' GROUP BY LINE_NO" % (invoice_no, const.CHARGE_TYPE_T_SI, t_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_so_charge_total_dict(cls, sales_contract_no=None):
        if sales_contract_no:
            sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  SALES_CONTRACT_NO='%s' and type='%s' and active='0' GROUP BY LINE_NO" % (sales_contract_no, const.CHARGE_TYPE_T_SO)
        else:
            sql = "select SALES_CONTRACT_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE  where type='%s' and active='0' GROUP BY SALES_CONTRACT_NO" % (const.CHARGE_TYPE_T_SO)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_so_charge_total_dict(cls, sales_contract_no=None):
        if sales_contract_no:
            sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  SALES_CONTRACT_NO='%s' and type='%s' and active='0' GROUP BY LINE_NO" % (sales_contract_no, const.CHARGE_TYPE_C_SO)
        else:
            sql = "select SALES_CONTRACT_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  type='%s' and active='0' GROUP BY SALES_CONTRACT_NO" % (const.CHARGE_TYPE_C_SO)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_so_charge_except_self_dict(cls, sales_contract_no, t_head_id):
        sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  sales_contract_no='%s' and type='%s' and active='0' and T_HEAD_ID!='%s' GROUP BY LINE_NO" % (sales_contract_no, const.CHARGE_TYPE_T_SO, t_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_c_so_charge_except_self_dict(cls, sales_contract_no, c_head_id):
        sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  sales_contract_no='%s' and type='%s' and active='0' and C_HEAD_ID!='%s' GROUP BY LINE_NO" % (sales_contract_no, const.CHARGE_TYPE_C_SO, c_head_id)
        return _fetch_sql_to_dict(sql)

    @classmethod
    def find_t_so_charge_only_self_dict(cls, sales_contract_no, t_head_id):
        sql = "select LINE_NO, sum(VAT_TOTAL) as VAT_TOTAL from VAT_CHARGE where  sales_contract_no='%s' and type='%s' and active='0' and T_HEAD_ID='%s' GROUP BY LINE_NO" % (sales_contract_no, const.CHARGE_TYPE_T_SO, t_head_id)
        return _fetch_sql_to_dict(sql)
    
    @classmethod
    def find_Other_Charges_From_vat(cls, head_id, type, c_head_id=None):
        if type == const.ERP_HEAD_TYPE_THEAD:
            return DBSession.query(cls).filter(cls.type.in_(['T_ERP','T_Manual'])).filter(cls.t_head_id == head_id).order_by(asc(cls.line_no)).all()
        if type == const.ERP_HEAD_TYPE_CHEAD:
            data = DBSession.query(cls).filter(cls.type.in_(['C_ERP','C_Manual'])).filter(cls.t_head_id == head_id).order_by(asc(cls.line_no))
            if c_head_id:
                return data.filter(cls.c_head_id == c_head_id).all()
            else:
                return data.all()

    @classmethod
    def get_sum_vat_total(cls,invoice_no):
        sql = '''SELECT sum(vat_total) FROM "public"."vat_charge" WHERE invoice_no='%s' and type in('T_SI','T_SO','T_ERP','T_Manual') ''' % (invoice_no)
        return DBSession.execute(sql).fetchone()[0]
    
    @classmethod
    def get_sum_mcn_total(cls,invoice_no):    
        sql = '''SELECT sum(vat_total) FROM "public"."vat_charge" WHERE invoice_no='%s' and type in('C_SI','C_SO','C_ERP','C_Manual') ''' % (invoice_no)
        return DBSession.execute(sql).fetchone()[0]

    @classmethod
    def find_Other_Charges_From_Vat_bo(cls,head_id):
        not_back_other_charge = []
        c_erp_result     = DBSession.query(Charge).filter_by(type='C_ERP',t_head_id=head_id).all()
        c_manual_result  = DBSession.query(Charge).filter_by(type='C_Manual',t_head_id=head_id).all()
        t_erp_result     = DBSession.query(Charge).filter_by(type='T_ERP',t_head_id=head_id).all()
        t_manual_result  = DBSession.query(Charge).filter_by(type='T_Manual',t_head_id=head_id).all()
        if len(t_erp_result)>0:
            for a in t_erp_result:
                if len(c_erp_result)>0:
                    for b in  c_erp_result:
                        if  not a.line_no == b.line_no:
                            not_back_other_charge.append(a)
                else:
                    not_back_other_charge.append(a)
                    
        if len(t_manual_result)>0:            
            for c in t_manual_result:
                if len(c_manual_result)>0:
                    for d in c_manual_result:
                        if not c.line_no == d.line_no:
                            not_back_other_charge.append(c)
                else:
                        not_back_other_charge.append(c)
        return not_back_other_charge
    
    @classmethod
    def find_other_charge_by_note_no(cls, note_no):
        return DBSession.query(cls).filter(cls.note_no == note_no).filter(cls.active == 0).all()
    
    
class PI(Table_PI):

    qty, available_qty,ri_qty, msi_qty, mcn_qty, charge_total, ri_total, available_total, msi_total, mcn_total, po_no = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None)
    
    @classmethod
    def find(cls,** args):
        tax_total, page, limit, cate, args['status'] = 0, 25, 0, 'next', 'C'
        queryExtend = QueryExtend(cls, ** args)
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":cate, limit,offset = 'pre',int(args.get("limit")),int(args.get("offset"))
        return cls.paset_result(queryExtend,limit,offset,[],limit,cate)

    @classmethod
    def get(cls, purchase_invoice_no):
        return DBSession2.query(cls).filter(cls.purchase_invoice_no == purchase_invoice_no).first()
   
    @classmethod
    def paset_result(cls,QueryExtend,limit,offset,results,flimit,cate):
        tax_total, next_page = 0, limit
        QueryExtend.query_all(True, DBSession2, True, limit, offset, ** {                                                  
                      const.QUERY_TYPE_NOT_EQ: ['status'],
                      const.QUERY_TYPE_LIKE: ['purchase_invoice_no', ('supplier', 'supplier')],
                      const.QUERY_TYPE_LIKE_AND_OR: [('supplier_name', 'supplier_name', 'supplier_short_name')],
                      const.QUERY_TYPE_DATE: [('create_date', 'date_from', 'date_to')],
                      const.QUERY_TYPE_ORDER_BY: ['create_date'],
                      const.QUERY_TYPE_COMPANY_CODE: ['company_code']
                      })
        
        queryExtend_result = QueryExtend.result
        if len(queryExtend_result)==0:return results, next_page, flimit
        for i in queryExtend_result:
            next_page += 1 
            data = cls.parse_detail_charge(i.purchase_invoice_no)
            if data:
                i.po_no = data[10]
                i.qty = data[0]
                i.ri_qty = data[2]
                i.mpi_qty = data[3]
                i.mcn_qty = data[4]
                i.available_qty = data[1]
                i.charge_total  = data[5]
                i.ri_total = data[6]
                i.mpi_total = data[8]
                i.mcn_total = data[9]
                i.available_total = data[7]
                if i.available_qty > 0:results.append(i)
                if len(results) > 24:break
        if len(results) < 25 and cate == 'next':
            limit = offset
            offset = offset+25
            return cls.paset_result(QueryExtend,limit,offset,results,flimit,cate)
        else:
            return results, next_page, flimit
        
    @classmethod
    def parse_data(cls,invoice_no):
        pid = PID.get_details(invoice_no)
        picharge = PICharge.find(invoice_no)
        uid = UID.find_details(invoice_no)
        uicharge  = UICharge.find_details(invoice_no) if invoice_no else []
        pi_result = _all_rewrite_price_and_filter_charges(picharge, pid)
        sn_result = _all_rewrite_price_and_filter_charges(uicharge, uid)
        if not _ap_check_cn_rewrite_charges(invoice_no, pid, uid) == 1:
            pi_Detail_list = []
            pi_charge_list = []
            for a in pi_result[0]:
                for b in sn_result[0]:
                    if a.item_no == b.item_no and a.line_no == b.pi_line_no:
                        a.available_qty = a.qty - b.note_qty
                pi_Detail_list.append(a)
            for c in pi_result[1]:
                for d in sn_result[1]:
                    if d.chg_discount_code == c.charge_code:
                        c.total = Decimal(c.total)
                        c.available_total = Decimal(c.total) - Decimal(d.total)
                pi_charge_list.append(c)
            pid, picharge, uid, uicharge = pi_Detail_list, pi_charge_list, sn_result[0], sn_result[1]
            return pid, picharge, uid, uicharge, pi_result[2]
        else:
            return pid, picharge, sn_result[0], sn_result[1], 0
    
    @classmethod
    def parse_detail_charge(cls,invoice_no):
        qty, available_qty,ri_qty, mpi_qty, msn_qty, charge_total, ri_total, available_total, mpi_total, msn_total, po_no = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, None)
        data = cls.parse_data(invoice_no)
        if data:
            pDetail = PiDetail.find_details(invoice_no)
            pCharge = PCharge.find_details(invoice_no)
            pid, picharge, uid, uicharge = data[0], data[1], data[2], data[3]
            for e in uid:ri_qty += e.note_qty
            for f in uicharge:ri_total += f.total
            po_no = None 
            if len(pid)>0:
                for g in pid:qty += g.qty
                po_no = g.po_no                                                                                         
            for h in  pDetail:
                if h.head_type == const.CHARGE_TYPE_P_PI:mpi_qty += pn(h.vat_qty)
                if h.head_type == const.CHARGE_TYPE_S_PI:msn_qty += pn(h.vat_qty)
            available_qty = qty - mpi_qty + msn_qty - ri_qty
            for i in picharge:charge_total += i.total
            for j in pCharge:
                if j.type == const.CHARGE_TYPE_P_PI:mpi_total += pn(j.vat_total)
                if j.type == const.CHARGE_TYPE_S_PI:msn_total += pn(j.vat_total)
            available_total = charge_total - mpi_total + msn_total - ri_total
            return qty, available_qty,ri_qty, mpi_qty, msn_qty, charge_total, ri_total, available_total, mpi_total, msn_total, po_no
        else: return
        
    @classmethod
    def find_by_po(cls, po_no):
        return DBSession2.query(cls.po_no == po_no).all()
        
    @classmethod
    def auto_complete(cls, DB, db_dict, type, q):
        result = []
        for k, v in db_dict.iteritems():
            if type in v:
                if type == 'item_code' and  k in ['t_purchase_invoice_dtl','vat_pi_detail']: type = 'item_no'
                if type == 'supplier'  and  k in ['vat_t_stdetail', 'vat_t_dndetail']: type = 'supplier_code'
                if DB == DBSession2:
                    if type == 'item_code' and  k == 't_purchase_invoice_dtl': type = 'item_no'
                    sql = "SELECT  distinct %s FROM %s where COMPANY_CODE in %s AND %s LIKE '%s' AND ROWNUM<=10 " % (type, k, getCompanyCode(1),type,q.upper()+'%')
                else:
                    if type in ['qty','unit']:
                        sql = "SELECT  distinct %s FROM %s where  CAST(%s AS TEXT) LIKE '%s'  limit 10 offset 0 " % (type, k, type, q.upper()+'%')
                    else:
                        sql = "SELECT  distinct %s FROM %s where %s LIKE '%s'  limit 10 offset 0 " % (type, k, type, q.upper()+'%')
                rrs = DB.execute(sql).fetchall()
                for rr in rrs:
                    if rr not in result:
                        result.append(rr)
        return result
    

class PID(Table_PID):

    ri_qty, mpi_qty, msn_qty, ava_qty, ava_total, mpi_total, msn_total = (0, 0, 0, 0, 0, 0, 0)

    @classmethod
    def find(cls,invoice_no):
        ava_qty, cn_total, ava_total, pi_detail_result, pi_charge_resullt =  0, 0, 0, [], []
        data = PI.parse_data(invoice_no)
        pi_detail, pi_charge, ui_detail, ui_charge, type = data[0], data[1], data[2], data[3], data[4]
        
        for a in pi_detail:
            msn_qty, ri_qty, vat_qty, tax_rate = 0, 0, 0, 0
            msn_details = PiDetail.find_details(a.purchase_invoice_no, None , a.item_no, a.line_no)
            for b in ui_detail:
                if a.item_no == b.item_no and a.line_no == b.pi_line_no: ri_qty += b.note_qty
            for c in msn_details: 
                if c.head_type == const.CHARGE_TYPE_S_PI:msn_qty += pn(c.vat_qty)
                else:vat_qty += pn(c.vat_qty)
            a.cn_qty  = int(ri_qty)
            a.ava_qty = a.qty - vat_qty + msn_qty - int(ri_qty)
            a.msn_qty = msn_qty
            a.mpi_qty = vat_qty
            pi_detail_result.append(a) 
                
        for d in pi_charge:
            msn_total, ri_total, vat_total = 0, 0, 0
            msn_details = PCharge.find_details(d.purchase_invoice_no, None , d.line_no)
            for f in ui_charge:
                if d.charge_code == f.chg_discount_code:ri_total += f.total
            for g in msn_details:
                if g.type == const.CHARGE_TYPE_S_PI:msn_total += pn(g.vat_total)
                if g.type == const.CHARGE_TYPE_P_PI:vat_total += pn(g.vat_total)
            d.cn_total  = ri_total
            d.ava_total = d.total - vat_total + msn_total - ri_total
            d.mpi_total = vat_total
            d.msn_total =  msn_total
            pi_charge_resullt.append(d) 
                
        return [pi_detail_result, pi_charge_resullt, ui_detail, ui_charge, type]
        
    @classmethod
    def find_si_detail_qty_dict(cls, purchase_invoice_no):
        result_dict = {}
        for i in DBSession2.query(cls).filter(cls.purchase_invoice_no == purchase_invoice_no).filter(cls.company_code.in_(getCompanyCode())).all():
            result_dict.update({i.line_no:i.qty})
        return result_dict
    
    @classmethod
    def get_unit_price(cls,purchase_invoice_no):
        sql = "select UNIT_PRICE from T_INVOICE_DTL where invoice_no='%s'" % (purchase_invoice_no)
        return DBSession2.execute(sql).fetchone()
    
    @classmethod
    def get_details(cls,purchase_invoice_no):
        cn_qty,ava_qty,msn_qty,vat_qty,mpi_qty,results = 0, 0, 0, 0, 0, []
        for a in DBSession2.query(cls).filter(cls.purchase_invoice_no == purchase_invoice_no).all():
            msn_details = PiDetail.find_details(a.purchase_invoice_no, None, a.item_no)
            for b in msn_details:
                if b.head_type == const.CHARGE_TYPE_P_PI:mpi_qty += pn(b.vat_qty)
                if b.head_type == const.CHARGE_TYPE_S_PI:msn_qty += pn(b.vat_qty)
            a.cn_qty  = cn_qty
            a.mpi_qty = mpi_qty
            a.ava_qty = a.qty - mpi_qty + msn_qty - cn_qty
            a.msn_qty = msn_qty
            results.append(a)
        return results
    
    @classmethod
    def find_details_by_po_no(cls, po_no, item_no = None, line_no = None):
        data = DBSession2.query(cls).filter(cls.po_no == po_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if line_no: data = data.filter(cls.po_line_no == line_no)
        return data.all()
    
    @classmethod
    def find_details_by_po_no_keys(cls, po_no, item_no = None, line_no = None):
        data = DBSession2.query(cls.line_no, cls.po_line_no, cls.supplier, cls.supplier_name, cls.supplier_short_name, cls.item_no, cls.unit_price, cls.qty, cls.purchase_invoice_no).filter(cls.po_no == po_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if line_no: data = data.filter(cls.line_no == line_no)
        return data.all()
    
    @classmethod
    def find_details_by_pi_no(cls, pi_no, item_no = None, unit_price = None, qty = None, line_no = None):
        data = DBSession2.query(cls).filter(cls.purchase_invoice_no == pi_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if unit_price: data = data.filter(cls.unit_price == unit_price)
        if qty: data = data.filter(cls.qty == qty)
        if line_no: data = data.filter(cls.line_no == line_no)
        return data.all()
    
    @classmethod
    def find_details_in_pi_no(cls, pi_no_list, item_no = None, unit_price = None, qty = None):
        data = DBSession2.query(cls).filter(cls.purchase_invoice_no.in_(pi_no_list))
        if item_no: data = data.filter(cls.item_no == item_no)
        if unit_price: data = data.filter(cls.unit_price == unit_price)
        if qty: data = data.filter(cls.qty == qty)
        return data.all()
    
    @classmethod
    def get_details_by_pi_no(cls, pi_no):
        return DBSession2.query(cls).filter(cls.purchase_invoice_no == pi_no).first()
    
    @classmethod
    def find_details_by_grn_no(cls, grn_no, grn_line_no, po_no = None, item_no = None, line_no = None):
        data = DBSession2.query(cls)
        if po_no: data = data.filter(cls.po_no == po_no)
        if grn_no: data = data.filter(cls.grn_no == grn_no)
        if grn_line_no: data = data.filter(cls.grn_line_no == grn_line_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if line_no: data = data.filter(cls.po_line_no == line_no)
        return data.all()
    
        
class PICharge(Table_PICharge):

    type = 'PI'
    mso_total, mcn_total, available_total = (0, 0, 0)

    @classmethod
    def find(cls, purchase_invoice_no):
        cn_total,ava_total,vat_total,results =  0, 0,0, []
        charges = DBSession2.query(cls).filter(cls.purchase_invoice_no == purchase_invoice_no).filter(cls.company_code.in_(getCompanyCode())).all()
        for a in charges:
            mpi_total,msn_total = 0, 0
            msn_details = PCharge.find_details(a.purchase_invoice_no, None, a.line_no)
            cn_details  = UICharge.find_details(a.purchase_invoice_no, a.line_no) if a.purchase_invoice_no else []
            for b in msn_details:
                if b.type == const.CHARGE_TYPE_P_PI:mpi_total += pn(b.vat_total)
                if b.type == const.CHARGE_TYPE_S_PI:msn_total += pn(b.vat_total)
            a.cn_total  = 0
            a.mpi_total = mpi_total
            a.ava_total = a.total - mpi_total + msn_total + cn_total
            a.msn_total =  msn_total
            results.append(a)
        return results
    
    @classmethod
    def find_charge(cls,invoice_no, type = None):
        data = DBSession2.query(cls).filter(cls.company_code.in_(getCompanyCode())).filter(cls.purchase_invoice_no == invoice_no).filter(cls.charge_code==u'增值稅' or cls.charge_code==u'增值稅應付' or cls.charge_code==u'增值稅-應付')
        if type:
            return data.first()
        else:
            return data.all()
        
    @classmethod
    def find_charge_by_item_code(cls, invoice_no, charge_code = None, type = None, line_no = None):
        data = DBSession2.query(cls).filter(cls.purchase_invoice_no == invoice_no)
        if charge_code:
            data = data.filter(cls.charge_code == charge_code)
        if line_no:
            data = data.filter(cls.line_no == line_no)
        if type:
            return data.first()
        else:
            return data.all()

    @classmethod
    def find_details_by_po_no(cls, po_no):
        return DBSession2.query(cls).filter(cls.company_code.in_(getCompanyCode())).filter(cls.po_no == po_no).all()
    
    @classmethod
    def find_details_by_keys(cls, po_no):
        return DBSession2.query(cls.charge_code, cls.total,cls.line_no,cls.po_chrg_line_no,cls.purchase_invoice_no).filter(cls.company_code.in_(getCompanyCode())).filter(cls.po_no == po_no).all()
    
    @classmethod
    def find_details_by_pi(cls, pi_no):
        return DBSession2.query(cls).filter(cls.purchase_invoice_no == pi_no).all()
    
    @classmethod
    def get_details_by_pi(cls, pi_no, line_no = None):
        data = DBSession2.query(cls).filter(cls.purchase_invoice_no == pi_no)
        if line_no:
            data = data.filter(cls.line_no == line_no)
        return data.first()
    
    @classmethod                  
    def find_details_by_all(cls, pi, line_no = None, po = None, po_line_no = None):
        data = DBSession2.query(cls).filter(cls.purchase_invoice_no == pi).filter(cls.company_code.in_(getCompanyCode()))
        if line_no: data = data.filter(cls.line_no == line_no)
        if po: data = data.filter(cls.po_no == po)
        if po_line_no: data = data.filter(cls.po_chrg_line_no == po_line_no)
        return data.all()
    
    @classmethod                  
    def find_details_in_all(cls, pi_list, line_no = None, po = None, po_line_no = None):
        data = DBSession2.query(cls).filter(cls.purchase_invoice_no.in_(pi_list)).filter(cls.company_code.in_(getCompanyCode()))
        if line_no: data = data.filter(cls.line_no == line_no)
        if po: data = data.filter(cls.po_no == po)
        if po_line_no: data = data.filter(cls.po_chrg_line_no == po_line_no)
        return data.all()

class PO(Table_PO):
    
    @classmethod
    def find_detail(cls, po_no):
        return DBSession2.query(cls).filter(cls.purchase_order_no == po_no).first()
    
    
class POD(Table_POD):

    @classmethod
    def find_details(cls, po_no, item_no = None, line_no = None):
        result = []
        po = PO.find_detail(po_no)
        data = DBSession2.query(cls).filter(cls.purchase_order_no == po_no)
        if item_no: data = data.filter(cls.stock_item_no == item_no)
        if line_no: data = data.filter(cls.line_no == line_no)
        podetails = data.all()
        for podetail in podetails:
            podetail.supplier = po.supplier
            result.append(podetail)
        return result

    
class POCharge(Table_POCharge):
    
    @classmethod
    def find_details_by_all(cls, po, line_no = None):
        data = DBSession2.query(cls).filter(cls.purchase_order_no == po)
        if line_no:data = data.filter(cls.line_no == line_no)
        return data.all()
    
class PHead(Table_PHead):
    
    @classmethod
    def find(cls, category=None, ** args):
        ids, page, limit, cate =[0], 25, 0, 'next'
        item_code, supplier, supplier_name,invoice_no, po_no, status, create_by_id= (args.get(i, '').strip() for i in ('item_code', 'supplier', 'supplier_name', 'invoice_no', 'po_no', 'status', 'create_by'))
        if item_code:
            ids.extend(PiDetail.get_phead_ids(item_code))
        if supplier or supplier_name or invoice_no or  po_no:
            ids.extend(PiHead.get_phead_ids(invoice_no, po_no,supplier,supplier_name))
        if args.get('create_by_id'):
            users =  cls.user_name_id(args['create_by_id'])
            if len(users)>0: args['create_by_id'] = users[0].user_id
            else: return []
        if len(ids) > 1: args['ids'] = list(set(ids))
        arr_not_null = []
        params = {
            const.QUERY_TYPE_LIKE: ['ref','dzd'],
            const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
            const.QUERY_TYPE_IN: [('id', 'ids')],
            const.QUERY_TYPE_EQ: ['status'],
            const.QUERY_TYPE_ORDER_BY: ['create_time'],
            const.QUERY_TYPE_CREATE_BY: ['create_by_id'],
            const.QUERY_TYPE_COMPANY_CODE: ['company_code'],
            const.QUERY_TYPE_NOT_NULL: arr_not_null
        }
        queryExtend = QueryExtend(cls, ** args)
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit")) 
            offset = int(args.get("offset"))
        if category:offset = None   
        queryExtend.query_all(True, DBSession, False, limit, offset, ** params)
        
        if category:return queryExtend.result
        else:return queryExtend.result, offset, limit
        
    @classmethod
    def find_detail_charge_by_date(cls, date_from = None, date_to = None, item_code = None):
        result, is_post = [], []
        static_count = 10
        if date_from:
            year_date_from = dt.strptime("%s-01-0100:00:00" % date_from.year, "%Y-%m-%d%H:%M:%S")
        pidetails = DBSession.query(PiDetail).filter(PiDetail.active == 0).filter(PiDetail.p_head_id != None).filter(cls.company_code.in_(getCompanyCode()))
        if item_code:
            pidetails = pidetails.filter(PiDetail.item_no == item_code)
        if date_from:
            pidetails = pidetails.filter(PiDetail.kingdee_date >= year_date_from).filter(PiDetail.kingdee_date <= date_to)
        pidetails = pidetails.order_by(asc(PiDetail.id))
        pidetails = pidetails.all()
        for pidetail in pidetails:
            cn = []
            if pidetail.st_detail_id and pidetail.st_detail.kingdee_date:
                st_detail = pidetail.st_detail
                pidetail.kingdee_date =  _get_lastday_of_month(st_detail.kingdee_date)
            if not date_to or (pidetail.kingdee_date and pidetail.kingdee_date.year <= date_to.year and pidetail.kingdee_date.month <= date_to.month): 
                msn_details = PiDetail.find_details(pidetail.invoice_no, None, pidetail.item_no, None, pidetail.uuid)
                msn_qty = 0
                for msn_detail in msn_details:
                    if msn_detail.uuid == pidetail.uuid:
                        if msn_detail.dn_detail and msn_detail.s_head_id:
                            if msn_detail.dn_detail.kingdee_date:
                                dn_detail = msn_detail.dn_detail
                                msn_detail.kingdee_date =  _get_lastday_of_month(dn_detail.kingdee_date)
                                cn.append({
                                           'qty':msn_detail.vat_qty, 
                                           'date_time':msn_detail.kingdee_date if hasattr(msn_detail, 'kingdee_date') else None
                                           }) 
                                msn_qty += pn(msn_detail.vat_qty)

                pidetail.so_no = None
                pidetail.cn = cn
                pidetail.cn_qty = msn_qty
                pidetail.head_type = const.SEARCH_TYPE_PSIPSO
                pidetail.date_time = pidetail.kingdee_date
                pidetail.item_code = pidetail.item_no
                pidetail.curr_qty  = pidetail.vat_qty
                pidetail.amount    = pidetail.vat_qty * pidetail.unit_price
                pidetail.lave_qty  = 0
                pidetail.lave_amount = 0
                if pidetail.__tablename__ == 'vat_pi_detail':
                    if pidetail.st_detail_id:
                        pidetail.curr_billing_month = pidetail.st_detail.billing_month
                        pidetail.curr_kingdee_date = pidetail.st_detail.kingdee_date
                if pidetail.p_head_id and pidetail.p_head_id not in is_post:
                    is_post.append(pidetail.p_head_id)
                result.append(pidetail)
        for iss in is_post:
            phead = PHead.get(iss)
            picharges = phead.pcharges
            for picharge in picharges:
                st_detail = picharge.st_detail
                picharge.kingdee_date =  _get_lastday_of_month(st_detail.kingdee_date)
                picharge.head_type = const.SEARCH_TYPE_CHARGE
                picharge.date_time = picharge.kingdee_date
                picharge.item_no = picharge.charge_code
                picharge.amount    = picharge.total
                picharge.qty = None
                picharge.cn = []
                picharge.curr_qty = None
                picharge.unit_price = ''
                picharge.so_no = st_detail.so_no
                result.append(picharge)
                del picharge
            del phead
        return result
    
    @classmethod
    def create(cls, ** args):
        ids, head_type, supplier, p_head_id, dn = (args.get(i, '') for i in ('ids', 'head_type', 'supplier', 'p_head_id', 'dn'))
        refTime = dt.now().strftime('%Y%m')[2:]
        ref = 'MPI%s' % refTime if head_type == const.CHARGE_TYPE_P_PI else 'MPO%s' % refTime
        max = DBSession.query(func.max(cls.ref)).filter(cls.ref.like('%s%%' % ref)).first()[0]
        if max and len(max) == 13: max = int(max[7:]) + 1
        else: max = 1
        thArgs = {
            'head_type':head_type,
            'status':const.VAT_THEAD_STATUS_NEW,
            'ref':'%s%06d' % (ref, max),
            'company_code':getCompanyCode()[0]
        }
        if p_head_id:phead = cls.get(p_head_id)
        else:
            phead = cls( ** thArgs)
            DBSession.add(phead)
            DBSession.flush()
        if ids:
            for id in ids.split(','):
                shArgs = {'head_type':head_type, 'p_head_id':phead.id}
                if args.get('invoice_dict'):
                    shArgs.update({'invoice_dict':args.get('invoice_dict')})
                if head_type == const.CHARGE_TYPE_P_PI:
                    invoice_no = id.split('$')[0]
                    sidResult = PID.find(invoice_no)
                    shArgs.update({'invoice_no':invoice_no})
                    piHead = PiHead.create( ** shArgs)
                    shArgs.update({'pi_head_id':piHead.id})
                    if dn:
                        shArgs.update({'dn':dn})
                    PiDetail.create(sidResult[0], ** shArgs)
                    PCharge.create(const.CHARGE_TYPE_P_PI, sidResult[1], ** shArgs)
                    PCharge.create(const.CHARGE_TYPE_P_PRI, sidResult[3], ** shArgs)
                    phead.supplier            = piHead.supplier
                    phead.supplier_name       = piHead.supplier_name
                    phead.supplier_short_name = piHead.supplier_short_name
                    DBSession.merge(phead)
                    piHead.po_no  = sidResult[0][0].po_no if len(sidResult[0])>0 else None
                    piHead.charge_type = sidResult[4]
                    DBSession.merge(piHead)
                    
        if args.get("charge_dict") and len(args.get("charge_dict"))>0:
            if head_type == const.CHARGE_TYPE_P_PI:
                for k, v in args.get("charge_dict").iteritems():
                    shArgs = {'head_type':head_type, 'p_head_id':phead.id, 'charge_dict':args.get('charge_dict')}
                    piHead = PiHead.get_pihead_id(k, phead.id)
                    if piHead:
                        shArgs.update({'pi_head_id':piHead.id})
                        PCharge.create(const.CHARGE_TYPE_P_PI, PICharge.find(k), ** shArgs)
                    else:continue
        return phead
                    
    @classmethod
    def update_all_status(cls, ** args):
        (status, ids) = (args.get(i, '') for i in ('status', 'ids'))
        pheads = cls.find_by_ids(ids)
        for i in pheads:
            i.status = status
            if status == const.VAT_THEAD_STATUS_CANCELLED:
                i.remark = args.get("remark-%s" % i.id)
                if i.head_type == const.CHARGE_TYPE_P_PI:
                    for j in i.pi_heads:
                        j.active = 1
                        DBSession.merge(j)
                        for u in j.pi_details:
                            u.active = 1
                            DBSession.merge(u)
                else:
                    for j in i.po_details:
                        j.active = 1
                        DBSession.merge(j)
                        
                for j in i.pcharges:
                    j.active = 1
                    DBSession.merge(j) 
      
    @classmethod
    def update_all_vat_info(cls, ** args):
        vat_no, vat_date, ids = (args.get(i, '').strip() for i in ('vat_no', 'vat_date', 'ids'))
        pheads = cls.find_by_ids(ids)
        for i in pheads:
            i.vat_no = vat_no
            i.vat_date = dt.strptime('%s00:00:00' % vat_date, "%Y-%m-%d%H:%M:%S")
            DBSession.merge(i)
    
    @classmethod
    def get_category(cls, categroy):
        return DBSession.query(cls).filter(cls.active == 0).filter(cls.category == categroy).first()
        
    @classmethod
    def get_id_by_ref_category(cls, ref, categroy):
        data =  DBSession.query(distinct(cls.id)).filter(cls.active == 0).filter(cls.dzd == ref).filter(cls.category == categroy).first()
        return data[0] if data and len(data)>0 else None
    
    @classmethod
    def get_phead_by_ref_category(cls, ref, categroy):
        data =  DBSession.query(cls).filter(cls.active == 0).filter(cls.dzd == ref).filter(cls.category == categroy).first()
        return data
    
    @classmethod
    def get_supplier(cls, supplier):
        return DBSession.query(cls).filter(cls.active == 0).filter(cls.supplier == supplier).first()
    
                                     
class SHead(Table_SHead):
    
    @classmethod
    def find(cls, category=None, ** args):
        ids, page, limit, cate = [0], 25, 0, 'next'
        item_code, po_no, vat_no, status, create_by_id = (args.get(i, '').strip() for i in ('item_code', 'po_no', 'vat_no', 'status', 'create_by_id'))
        invoice_no = args.get('purchase_invoice_no') if args.get('purchase_invoice_no') else args.get('invoice_no')
        if item_code:
            ids.extend(PiDetail.get_shead_ids(item_code))
        if invoice_no or po_no:
            ids.extend(PiHead.get_shead_ids(invoice_no, po_no))
        if args.get('create_by_id'):
            users =  cls.user_name_id(args['create_by_id'])
            if len(users)>0:args['create_by_id'] = users[0].user_id
            else: return []
        if len(ids) > 1: args['ids'] = list(set(ids))
        arr_not_null = []
        if vat_no: arr_not_null.append('vat_no')
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit")) 
            offset = int(args.get("offset"))
        if category:offset = None
        params = {
            const.QUERY_TYPE_LIKE: ['purchase_invoice_no', 'phead_ref','ref','vat_no','supplier', 'supplier_name'],
            const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
            const.QUERY_TYPE_IN: [('id', 'ids')],
            const.QUERY_TYPE_EQ: ['status'],
            const.QUERY_TYPE_ORDER_BY: ['create_time'],
            const.QUERY_TYPE_CREATE_BY: ['create_by_id'],
            const.QUERY_TYPE_COMPANY_CODE: ['company_code'],
            const.QUERY_TYPE_NOT_NULL: arr_not_null
        }
        queryExtend = QueryExtend(cls, ** args)
        queryExtend.query_all(True, DBSession,False, limit, offset, ** params)
        if vat_no:
            results = []
            for i in queryExtend.result:
                for j in i.vat_no.split(','):
                    if len(j.split('~')) == 1 and vat_no == j:
                        results.append(i)
                        break
                    elif len(j.split('~')) == 2:
                        kk = j.split('~')
                        if int(kk[0]) <= int(vat_no) and int(kk[1]) >= int(vat_no):
                            results.append(i)
                            break
            if category:            
                return results
            else:
                return results, offset, limit
        else:
            if category: 
                return queryExtend.result
            else:
                return queryExtend.result, offset, limit

    @classmethod
    def create(cls, ** args):
        s_head_id = args.get("s_head_id")
        if s_head_id:
            shead = SHead.get(s_head_id)
            phead = shead.p_head
        else:
            ref = 'MSN%s' % dt.now().strftime('%Y%m')[2:]
            max = DBSession.query(func.max(cls.ref)).filter(cls.ref.like('%s%%' % ref)).first()[0]
            if max and len(max) == 13: max = int(max[7:]) + 1
            else: max = 1
            phead = PHead.get(args['id']) if not args.get('phead') else args.get('phead')
            if phead.head_type == const.CHARGE_TYPE_P_PI:
                type = const.CHARGE_TYPE_S_PI
            else:
                type = const.CHARGE_TYPE_S_PO
            args.update({'head_type':type})
            keys = ['head_type', 'customer_code', 'company_code', 'customer_name', 'customer_short_name', ('phead_vat_no', 'vat_no'), 
                    ('phead_ref', 'ref'), ('p_head_id', 'id'),'supplier','supplier_name','supplier_short_name',
                    {'status':const.VAT_CHEAD_STATUS_NEW}, {'ref':'%s%06d' % (ref, max)}]
            params = _get_params_from_args_and_obj(keys, phead, ** args)
            shead = SHead( ** params)
            DBSession.add(shead)
            DBSession.flush()
        if phead.head_type == const.CHARGE_TYPE_P_PI:
            type = const.CHARGE_TYPE_S_PI
        else:
            type = const.CHARGE_TYPE_S_PO
        shArgs = {'head_type':type,'s_head_id': shead.id}
        if shead.head_type == const.CHARGE_TYPE_S_PI and args.get('type') != const.CHARGE_TYPE_S_PRI:
            pi_heads = PiHead.find_details_by_phead(phead.id)
            for pi in pi_heads:
                d_invoice_dict = args.get('d_invoice_dict',{})
                d_charge_dict  = args.get('d_charge_dict',{})
                if d_invoice_dict and len(d_invoice_dict)>0:
                    if not d_invoice_dict.get(pi.invoice_no):
                        continue
                shArgs.update({
                               'd_invoice_dict':d_invoice_dict.get(pi.invoice_no)
                               })
                piHead = PiHead.create(pi, ** shArgs)
        return shead
    
    @classmethod
    def update_all_status(cls, ** args):
        (status, ids) = (args.get(i, '') for i in ('status', 'ids'))
        sheads = cls.find_by_ids(ids)
        for i in sheads:
            i.remark = args.get("remark-%s" % i.id)
            i.status = status
            if status == const.VAT_CHEAD_STATUS_CANCELLED:
                i.active = 1
                DBSession.merge(i)
                if i.head_type == const.CHARGE_TYPE_S_PI:
                    for j in i.pi_heads:
                        for u in j.pi_details:
                            u.active = 1
                            DBSession.merge(u)
                else:
                    for j in i.po_heads:
                        for u in  j.po_details:
                            u.active = 1
                            DBSession.merge(u)
                for j in i.pcharges:
                    j.active = 1
                    DBSession.merge(j)
                
    @classmethod
    def update_all_vat_info(cls, ** args):
        vat_no, vat_date, ids = (args.get(i, '').strip() for i in ('vat_no', 'vat_date', 'ids'))
        sheads = cls.find_by_ids(ids)
        for i in sheads:
            i.vat_no = vat_no
            i.vat_date = dt.strptime('%s00:00:00' % vat_date, "%Y-%m-%d%H:%M:%S")
            DBSession.merge(i)
             
    @classmethod
    def find_s_head_id(cls, p_head_id):
        return DBSession.query(cls).filter(cls.p_head_id == p_head_id).filter(cls.active == 0).first()


class MHead(Table_MHead):
    
    @classmethod
    def find(cls, category=None, ** args):
        ids, page, limit, cate = [0], 25, 0, 'next'
        item_code, po_no, vat_no, status, create_by_id = (args.get(i, '').strip() for i in ('item_code', 'po_no', 'vat_no', 'status', 'create_by_id'))
        invoice_no = args.get('purchase_invoice_no') if args.get('purchase_invoice_no') else args.get('invoice_no')
        if item_code:
            ids.extend(PiDetail.get_mhead_ids(item_code))
        if po_no or invoice_no:
            ids.extend(PiHead.get_mhead_ids(invoice_no, po_no))
        if args.get('create_by_id'):
            users =  cls.user_name_id(args['create_by_id'])
            if len(users)>0:args['create_by_id'] = users[0].user_id
            else: return []  
        if len(ids) > 1: args['ids'] = list(set(ids))
        arr_not_null = []
        if vat_no: arr_not_null.append('vat_no')
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit")) 
            offset = int(args.get("offset"))
        if category:offset = None
        params = {
            const.QUERY_TYPE_LIKE: ['purchase_invoice_no', 'phead_ref','ref','vat_no','supplier', 'supplier_name'],
            const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
            const.QUERY_TYPE_IN: [('id', 'ids')],
            const.QUERY_TYPE_EQ: ['status'],
            const.QUERY_TYPE_ORDER_BY: ['create_time'],
            const.QUERY_TYPE_CREATE_BY: ['create_by_id'],
            const.QUERY_TYPE_NOT_NULL: arr_not_null
        }
        
        queryExtend = QueryExtend(cls, ** args)
        queryExtend.query_all(True, DBSession,False, limit, offset, ** params)
        result = []
        for a in queryExtend.result:
            payment = 0
            for b in a.pi_heads:
                for c in b.pi_details:
                    payment += c.vat_total
                    
            for d in a.pcharges:   payment += d.vat_total
            a.payment_total = payment
            result.append(a)      
        if category: 
            return result
        else:
            return queryExtend.result, offset, limit

    @classmethod
    def create(cls, ** args):
        ref = 'MF%s' % dt.now().strftime('%Y%m')[2:]
        max = DBSession.query(func.max(cls.ref)).filter(cls.ref.like('%s%%' % ref)).first()[0]
        if max and len(max) == 12: max = int(max[6:]) + 1
        else: max = 1
        type = const.CHARGE_TYPE_S_MF if args.get("type") == "t_head_id" else const.CHARGE_TYPE_S_NMF
        head = PHead.get(args['id']) if args.get("type") == "t_head_id" else SHead.get(args['id'])
        args.update({'head_type' : type})
        keys = ['head_type', 'customer_code', 'customer_name', 'customer_short_name', ('phead_vat_no', 'vat_no'), ('phead_ref', 'ref'),'supplier','supplier_name', 'supplier_short_name',
            {'status':const.VAT_CHEAD_STATUS_NEW}, {'ref':'%s%06d' % (ref, max)}]
        if args.get("type") == "t_head_id": 
            ptype = const.CHARGE_TYPE_S_MF
            ctype = const.CHARGE_TYPE_P_PI
            keys.append(('p_head_id', 'id')) 
        else:
            ptype = const.CHARGE_TYPE_S_NMF
            ctype = const.CHARGE_TYPE_S_PI
            keys.append(('s_head_id', 'id'))
        params = _get_params_from_args_and_obj(keys, head, ** args)
        mhead = cls( ** params)
        DBSession.add(mhead)
        DBSession.flush()
        head_dict = {}
        for pi in head.pi_heads:
            for pidetail in pi.pi_details:
                vat_total =  0
                msn_details = PiDetail.find_details(pidetail.invoice_no, ptype, pidetail.item_no, pidetail.line_no, pidetail.uuid, pidetail.uuid2)
                for b in msn_details:
                    if b.id != pidetail.id:
                        vat_total += pn(b.vat_total)
                if ptype == const.CHARGE_TYPE_S_MF:
                    ava_total = pidetail.item_total*(1+pidetail.tax_rate) - vat_total
                else:ava_total = pidetail.vat_qty * pidetail.unit_price * (1+pidetail.tax_rate) - vat_total
                if head_dict.get(pi.id):head_dict[pi.id] += ava_total
                else: head_dict.update({pi.id : ava_total})       
        for pi in head.pi_heads:
            if head_dict.get(pi.id) and round(head_dict.get(pi.id, 0), 2) > 0.05:
                shArgs = {'head_type':type, 'm_head_id': mhead.id}
                piHead = PiHead.create(pi, ** shArgs)
                shArgs.update({'pi_head_id':piHead.id})
                PiDetail.create(pi.pi_details, ** shArgs)
                if args.get("type") == "t_head_id": 
                    PCharge.create(const.CHARGE_TYPE_S_MF, PCharge.find_other_charges_from_vat(args['id'], const.CHARGE_TYPE_A,'p_head_id', pi.id), ** shArgs)
                else:
                    PCharge.create(const.CHARGE_TYPE_S_NMF, PCharge.find_other_charges_from_vat(args['id'],const.CHARGE_TYPE_B,'s_head_id', pi.id), ** shArgs)
        return mhead
    
    @classmethod
    def update_all_status(cls, ** args):
        (status, ids) = (args.get(i, '') for i in ('status', 'ids'))
        mheads = cls.find_by_ids(ids)
        for i in mheads:
            i.remark = args.get("remark-%s" % i.id)
            i.status = status
            if status == const.VAT_CHEAD_STATUS_CANCELLED:
                if i.head_type in [const.CHARGE_TYPE_S_MF, const.CHARGE_TYPE_S_NMF]:
                    for j in i.pi_heads:
                        for u in j.pi_details:
                            u.active = 1
                            DBSession.merge(u)
                for j in i.pcharges:
                    j.active = 1
                    DBSession.merge(j)
    
    @classmethod
    def update_all_vat_info(cls, ** args):
        vat_no, vat_date, ids = (args.get(i, '').strip() for i in ('vat_no', 'vat_date', 'ids'))
        mheads = cls.find_by_ids(ids)
        for i in mheads:
            i.vat_no = vat_no
            i.vat_date = dt.strptime('%s00:00:00' % vat_date, "%Y-%m-%d%H:%M:%S")
            DBSession.merge(i)         
                              
class PiHead(Table_PiHead):
    
    @classmethod
    def get_by_id(cls, id):
        return DBSession.query(cls).get(id)
    
    @classmethod
    def create(cls, pi=None, ** args):
        if args.has_key('s_head_id'):
            d_invoice_dict = args.get('d_invoice_dict', [])
            keys = ['s_head_id',
                'invoice_no', 'head_type', 'company_code', 'po_no', 'ref',
                'supplier', 'supplier_name', 'supplier_short_name', 'department',
                'status', 'currency', 'order_amt', 'item_amt', 'invoice_date']
            if pi:
                for i in d_invoice_dict:
                    keys.append({'note_no':i.get('note_no')})
                    break
        else:
            keys = ['invoice_no', 'head_type', 'company_code', 'po_no', 'ref',
                'supplier', 'supplier_name', 'supplier_short_name', 'department',
                'status', 'currency', 'order_amt', 'item_amt', 'invoice_date']
            if args.get("m_head_id"): keys.append("m_head_id") 
            else:keys.append("p_head_id")
            pi = PI.get(args['invoice_no']) if not pi else pi
        p_head_id = args.get('p_head_id')
        invoice_no = args.get('invoice_no')
        if p_head_id and invoice_no:
            p_head = PHead.get(p_head_id)
            for a in p_head.pi_heads:
                if a.invoice_no == invoice_no:
                    return a        
        params = _get_params_from_args_and_obj(keys, pi, ** args)
        piHead = cls(** params)
        DBSession.add(piHead)
        DBSession.flush()
        return piHead
    
    @classmethod
    def get_phead_ids(cls, invoice_no, po, supplier=None, supplier_name=None):
        data = DBSession.query(distinct(cls.p_head_id)).filter(cls.active == 0)
        if invoice_no:data = data.filter(cls.invoice_no == invoice_no)
        if po:data = data.filter(cls.po_no == po)
        if supplier:data = data.filter(cls.supplier == supplier)
        if supplier_name:data = data.filter(cls.supplier_name == supplier_name)
        results = [i[0] for i in data]
        return results if results else [0]
    
    @classmethod
    def get_pihead_id(cls, invoice_no, p_head_id):
        data = DBSession.query(cls).filter(cls.active == 0)
        if invoice_no:data = data.filter(cls.invoice_no == invoice_no)
        if p_head_id:data = data.filter(cls.p_head_id == p_head_id)
        return data.first()
    
    @classmethod
    def get_shead_ids(cls, invoice_no, po):
        data = DBSession.query(distinct(cls.s_head_id)).filter(cls.active == 0)
        if invoice_no: data = data.filter(cls.invoice_no == invoice_no)
        if po: data = data.filter(cls.po_no == po)
        results = [i[0] for i in data]
        return results if results else [0]
    
    @classmethod
    def get_mhead_ids(cls, invoice_no, po):
        data = DBSession.query(distinct(cls.m_head_id)).filter(cls.active == 0)
        if invoice_no: data = data.filter(cls.invoice_no == invoice_no)
        if po: data = data.filter(cls.po_no == po)
        results = [i[0] for i in data]
        return results if results else [0]
    
    @classmethod
    def get_phead_info(cls, invoice_no, po = None, p_head_id = None, s_head_id = None):
        data = DBSession.query(cls).filter(cls.active == 0)
        if invoice_no:data = data.filter(cls.invoice_no == invoice_no)
        if po:data = data.filter(cls.po_no == po)
        if p_head_id:data = data.filter(cls.p_head_id == p_head_id)
        if s_head_id:data = data.filter(cls.s_head_id == s_head_id)
        return data.first()
    
    @classmethod
    def find_details_by_phead(cls, id):
        return DBSession.query(cls).filter(cls.p_head_id == id).filter(cls.active == 0).all()
        
    def find_details(self, uid=None):
        ava_qty, results =    0, []
        if not uid:uid = PI.parse_data(self.invoice_no)[2]
        if self.p_head_id:
            status = self.p_head.status
            for a in self.pi_details:
                msn_qty, ri_qty, vat_qty,self_msn_qty = 0, 0, 0, 0
                msn_details = PiDetail.find_details(a.invoice_no, None, a.item_no, a.line_no, a.uuid)
                for e in uid:
                    if a.item_no == e.item_no and a.line_no == e.pi_line_no and status == const.VAT_THEAD_STATUS_NEW: 
                        ri_qty += e.note_qty
                for b in msn_details:
                    if b.head_type == const.CHARGE_TYPE_S_PI:
                        msn_qty += pn(b.vat_qty)
                        if b.uuid == a.uuid: self_msn_qty += pn(b.vat_qty)
                    elif b.head_type == const.CHARGE_TYPE_P_PI:
                        if status == const.VAT_THEAD_STATUS_NEW:
                            if b.id != a.id: vat_qty += pn(b.vat_qty)
                        else:
                            vat_qty += pn(b.vat_qty)
                a.cn_qty  = int(ri_qty)
                a.ava_qty = a.qty - vat_qty + msn_qty - a.cn_qty
                a.msn_qty = self_msn_qty
                results.append(a) 
        
        elif self.s_head_id:
            for a in self.pi_details:
                msn_qty, ri_qty = 0, 0
                msn_details = PiDetail.find_details(a.invoice_no, const.CHARGE_TYPE_S_PI, a.item_no, None, a.uuid)
                for e in uid:ri_qty += e.note_qty
                for b in msn_details:
                    if b.id != a.id and b.uuid == a.uuid: msn_qty += pn(b.vat_qty)
                a.cn_qty  = int(ri_qty)
                a.ava_qty = a.qty -  msn_qty 
                a.msn_qty = msn_qty
                results.append(a)
                
        elif self.m_head_id:
            status = self.m_head.status
            for a in self.pi_details:
                vat_total =  0
                msn_details = PiDetail.find_details(a.invoice_no, a.head_type, a.item_no, a.line_no, a.uuid, a.uuid2)
                for b in msn_details:
                    if status == const.VAT_THEAD_STATUS_NEW:
                        if b.id != a.id: vat_total += pn(b.vat_total)
                    else:
                        vat_total += pn(b.vat_total)
                a.ava_total = a.item_total*(1+a.tax_rate) - vat_total 
                a.msn_total = vat_total
                results.append(a) 
                
        return sorted(results.__iter__(), key=lambda x:x.line_no)
        
    def find_charges(self,uicharge=None):
        cn_total,ava_total,results =  0, 0, []
        if not uicharge:uicharge = PI.parse_data(self.invoice_no)[3]
        if self.p_head_id:
            status = self.p_head.status
            pi_charge = self.pcharges
            for a in pi_charge:
                msn_total,ri_total,vat_total = 0,0,0
                if a.type == const.CHARGE_TYPE_P_PI:
                    msn_details = PCharge.find_details(a.invoice_no, None, a.line_no, None, None, a.uuid, a.uuid2)
                    #uicharge = UICharge.find_details(a.invoice_no, a.line_no)
                    for f in uicharge:
                        if a.charge_code == f.chg_discount_code:ri_total += f.total
                    for b in msn_details:
                        if b.type == const.CHARGE_TYPE_S_PI:msn_total += pn(b.vat_total)
                        elif b.type == const.CHARGE_TYPE_P_PI:
                            if status == const.VAT_THEAD_STATUS_NEW:
                                if a.id != b.id:vat_total += pn(b.vat_total)
                            else:
                                vat_total += pn(b.vat_total)
                    a.cn_total  = ri_total
                    a.ava_total = a.total - vat_total + msn_total - ri_total
                    a.msn_total =  msn_total
                    results.append(a)   
                      
        elif self.s_head_id:
            for a in self.pcharges:
                msn_total,ri_total = 0,0
                msn_details = PCharge.find_details(a.invoice_no,const.CHARGE_TYPE_S_PI, a.line_no, None, None, a.uuid, a.uuid2)
                for f in uicharge:ri_total += f.total
                for b in msn_details:
                    if b.id != a.id: msn_total += pn(b.vat_total)
                a.cn_total  = ri_total
                a.ava_total = a.total -  msn_total 
                a.msn_total =  msn_total
                if a.total != 0:
                    results.append(a)
        
        elif self.m_head_id:
            status = self.m_head.status
            for a in self.pcharges:
                vat_total =  0
                msn_details = PCharge.find_details(a.invoice_no, a.type, a.line_no, None, None, a.uuid, a.uuid2)
                for b in msn_details:
                    if status == const.VAT_THEAD_STATUS_NEW:
                        if b.id != a.id: vat_total += pn(b.vat_total)
                    else:
                        vat_total += pn(b.vat_total)
                a.ava_total = a.total - vat_total 
                a.msn_total = vat_total
                results.append(a) 
                
        return sorted(results.__iter__(), key=lambda x:x.line_no)
    
    def update_details(self, ** args):
        remark = []
        for i in self.find_details():
            mg = merge([i.vat_total, i.remark,i.tax_rate, i.vat_qty,i.desc_zh if i.desc_zh else i.item_desc,str(i.unit_price),i.line_no],[args.get('vat_total_%s' % i.id, 0), args.get('remark_%s' % i.id,''), float(args.get('tax_%s' % i.id, 0))/100,int(args.get('qty_%s' % i.id, 0)),args.get('desc_%s' % i.id, ''),args.get('price_%s' % i.id,0) if args.get('price_%s' % i.id,0) else str(i.unit_price)],['Payment Amount', 'Remark' , 'Tax', 'VAT Qty','Description','Unit Price','Line NO'])
            if mg: remark.append(mg)
            i.vat_qty = int(args.get('qty_%s' % i.id, 0))
            i.desc_zh = args.get('desc_%s' % i.id, '')
            i.vat_total = args.get('vat_total_%s' % i.id, 0)
            i.remark  = args.get('remark_%s' % i.id, '')
            if args.get('tax_%s' % i.id): i.tax_rate = Decimal(args.get('tax_%s' % i.id, ''))/100
            price      = args.get('price_%s' % i.id)
            if price: i.unit_price = str(args.get('price_%s' % i.id, 0))
            ItemDesc.save(** {'code':self.supplier, 'item_no':i.item_no, 'description':i.desc_zh})
            DBSession.merge(i)
        return ",".join(remark) if len(remark)>0 else None   

    def update_charges(self, ** args):
        remark = []
        for i in self.find_charges():
            if args.get('total_%s' % i.id):
                mg = merge([i.vat_total,i.line_no],[Decimal(args.get('total_%s' % i.id))],['VAT Qty','Line NO'])
                if mg: remark.append(mg)
            i.vat_total = Decimal(args.get('total_%s' % i.id))
            DBSession.merge(i)
        return ",".join(remark) if len(remark)>0 else None
    
       
class PiDetail(Table_PiDetail):
    
    @classmethod
    def create(cls, piDetails, ** args):
        if args.has_key('s_head_id'):
            end_post = []
            for pid in piDetails:
                keys = ['head_type','s_head_id', 'pi_head_id', ('qty', 'vat_qty'),('vat_qty','d_ava_qty'),'base_unit_price','base_tax_rate',
                    'invoice_no', 'sc_no', 'company_code', 'line_no', 'item_total',
                    'item_no', 'item_desc', 'desc_zh', 'unit_price', 'unit', 'po_no', 'po_line_no', 'tax_rate', 'include_tax', 'uuid', 'remark']
                d_invoice_dict = args.get("d_invoice_dict")
                item = d_invoice_dict.get(pid.invoice_no, [])
                if len(item) > 0:
                    if_post = None
                    for i in item:
                        if i.get('po_line_no') == pid.po_line_no and i.get("item_no")== pid.item_no and i.get('id') not in end_post:
                            if_post = 1
                            end_post.append(i.get('id'))
                            piHead = PiHead.get_phead_info(pid.invoice_no, None, None, args.get('s_head_id'))
                            args.update({'pi_head_id':piHead.id, 'head_type':const.CHARGE_TYPE_S_PI})
                            pid.dn_detail_id = i.get("id")
                            pid.d_ava_qty = i.get("qty")
                            pid.unit_price = i.get("unit_price", 0)
                            keys.extend([
                                         'dn_detail_id',
                                         'kingdee_date',
                                         {'note_no':i.get("note_no")},
                                         {'category':i.get("category")},
                                         ('st_detail_id','')
                                         ])
                            break
                    if not if_post:continue
                else:
                    pid.d_ava_qty = 0
                params   = _get_params_from_args_and_obj(keys, pid, ** args)
                piDetail = cls( ** params)
                piDetail.uuid2 = str(uuid.uuid4())
                DBSession.add(piDetail)
                DBSession.flush()
                Period.update_pi_flag(pid.invoice_no, pid.item_no, pid.po_no)
                
        else:
            if_post = []
            dn = args.get('dn')
            for pid in piDetails:
                en_post = None
                keys = ['head_type', 'pi_head_id', 'qty', ('vat_qty', 'ava_qty'), ('base_unit_price', 'unit_price'),('base_tax_rate', 'tax_rate'),
                        'invoice_no', 'sc_no', 'company_code', 'line_no', 'item_total', 'uuid', 'uuid2', 'item_no', 'item_desc', ('desc_zh', 'item_desc'), 
                        'unit_price', 'unit', 'po_no', 'po_line_no', 'tax_rate', 'include_tax']
                if args.get("m_head_id"):
                    keys.append('m_head_id')
                else:
                    keys.append("p_head_id")
                invoice_dict = args.get('invoice_dict')
                piHead = PiHead.get(args.get('pi_head_id'))
                if invoice_dict:
                    item = invoice_dict.get(pid.purchase_invoice_no)
                    for it in item:
                        if it.get('item_no') == pid.item_no and it.get('id') not in if_post:
                            if_post.append(it.get('id'))
                            en_post   = True
                            st_detail = STDetail.get(it.get("id"))
                            pid.so_no = st_detail.so_no
                            pid.so_date = st_detail.so_date
                            pid.po_date = st_detail.po_date
                            pid.pi_date = st_detail.pi_date
                            pid.customer_code = st_detail.customer_code
                            pid.kingdee_date = None
                            if st_detail.kingdee_date:
                                pid.kingdee_date =  _get_lastday_of_month(st_detail.kingdee_date)
                            args.update({
                                         "st_detail_id":it.get("id"),
                                         "qty":it.get("qty"),
                                         "ava_qty":it.get("qty"),
                                         "item_total":it.get("item_total")
                                         })
                            keys.extend([
                                         'st_detail_id',
                                         'kingdee_date',
                                         'so_no',
                                         'so_date',
                                         'po_date',
                                         'pi_date',
                                         'customer_code',
                                         {'category':it.get("category")}
                                         ])
                            break
                if dn:
                    en_post   = True
                    pid.qty = 0
                    pid.ava_qty = 0
                    pid.item_total = 0
                if not en_post:
                    continue
                params = _get_params_from_args_and_obj(keys, pid, ** args)
                piDetail = cls( ** params)
                item_desc = ItemDesc.get(piHead.supplier, piDetail.item_no)
                if item_desc: piDetail.desc_zh = item_desc.description
                if args.get("m_head_id"):
                    vat_total2 = 0
                    type = args.get("head_type")
                    mf_details = cls.find_details(pid.invoice_no, type, None, pid.line_no, pid.uuid, pid.uuid2)
                    for c in mf_details: vat_total2 += pn(c.vat_total)
                    piDetail.item_total = pid.vat_qty * pid.unit_price
                    piDetail.vat_total  = piDetail.item_total*(1+pid.tax_rate) - vat_total2
                    if -0.005<float(piDetail.vat_total) and  float(piDetail.vat_total)<0.005:
                        pass
                    else:
                        DBSession.add(piDetail)
                        DBSession.flush()
                else:
                    piDetail.uuid = str(uuid.uuid4())
                    DBSession.add(piDetail)
                    DBSession.flush()
    
    @classmethod
    def get_phead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.p_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]

    @classmethod
    def get_shead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.s_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]
    
    @classmethod
    def get_mhead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.m_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]
    
    @classmethod
    def get_details(cls, po_no, item_no = None, line_no = None):
        data =  DBSession.query(cls).filter(cls.po_no == po_no).filter(cls.active == 0)
        if item_no:data = data.filter(cls.item_no == item_no)
        if line_no:data = data.filter(cls.line_no == line_no)
        return data.all()
    
    @classmethod
    def find_details(cls,invoice_no=None,type=None,item_no=None,line_no=None,uuid=None,uuid2=None, po_no = None, po_line_no = None, flag = None):
        data = DBSession.query(cls).filter(cls.active == 0)
        if invoice_no:data = data.filter(cls.invoice_no == invoice_no)
        if type:data = data.filter(cls.head_type == type)
        if item_no:data = data.filter(cls.item_no == item_no)
        if line_no:data = data.filter(cls.line_no == line_no)
        if uuid:data = data.filter(cls.uuid == uuid)
        if uuid2:data = data.filter(cls.uuid2 == uuid2)
        if po_no:data = data.filter(cls.po_no == po_no)
        if po_line_no:data = data.filter(cls.po_line_no == po_line_no)
        if flag:data = data.filter(cls.flag == flag)
        return data.all()
    
    @classmethod
    def parse_details(cls,invoice_no=None,type=None,item_no=None,line_no=None,uuid=None,uuid2=None, po_no = None, po_line_no = None, flag = None):
        ps, ss, rs, cn = [], [], [], []
        details = cls.find_details(invoice_no, type, item_no, line_no, uuid, uuid2, po_no, po_line_no)
        for i in details:
            if i.p_head_id:
                ps.append(i)
            elif i.s_head_id:
                ss.append(i)
        for p in ps:
            cn_qty = 0
            for s in ss:
                if s.s_head.p_head_id == p.p_head_id and s.id not in cn:
                    cn_qty += s.vat_qty
                    cn.append(s.id)
            p.curr_qty = p.qty - cn_qty
            rs.append(p)
        return rs
                
    
    @classmethod
    def find_s_head_id_by_category(cls, category, invoice_no = None, type = None):
        data =  DBSession.query(cls).filter(cls.active == 0).filter(cls.category == category)
        if invoice_no:
            data = data.filter(cls.invoice_no == invoice_no)
        if type == const.ERP_HEAD_TYPE_ST:
            data = data.filter(cls.p_head_id != None)
        else:
            data = data.filter(cls.s_head_id != None)
        return data.first()
        
    
    @classmethod
    def find_details_by_dzd(cls, id, type = None):
        data = DBSession.query(cls).filter(cls.active == 0)
        if type:
            data = data.filter(cls.st_detail_id == id).filter(cls.p_head_id != None)
        else:
            data = data.filter(cls.dn_detail_id == id).filter(cls.s_head_id != None)
        return data.first()
    
    @classmethod
    def update_pi_flag(cls, pi_no, item_no):
        pidetails = cls.find_details(pi_no, None, item_no)
        for pidetail in pidetails:
            if pidetail.flag == 1:
                pidetail.flag = 0
                DBSession.merge(pidetail)
    
            
class PoHead(Table_PoHead):
    pass
        
class PoDetail(Table_PoDetail):
    
    @classmethod
    def get_phead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.p_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]

    @classmethod
    def get_shead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.s_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]

class PCharge(Table_PCharge):
    
    @classmethod
    def insert(cls, ** kw):
        pHead = PHead.get(kw.get('p_head_id'))
        keys = ['company_code', 'p_head_id', 's_head_id', 'po_head_id', 'pi_head_id', 'type','line_no','charge_code','amount','total','vat_total','note_no', 'uuid', 'uuid2']
        params = _get_params_from_args_and_obj(keys, pHead, ** kw)
        pcharge = cls( ** params)
        pcharge.uuid = str(uuid.uuid4())
        DBSession.add(pcharge)
        DBSession.flush()
        
    @classmethod
    def create(cls, type, charges=[], ** args):
        args.update({'type':type})
        charge_dict = args.get('charge_dict')
        d_charge_dict = args.get('d_charge_dict')
        if args.has_key('charge_dict') or args.has_key('invoice_dict'):
            charges = []
        if charge_dict and len(charge_dict) >0:
            posted = {}
            for k, v in charge_dict.iteritems():
                if not v: continue
                for l in v:
                    cline_no = l.get('line_no')
                    if cline_no in posted.get(k,[]):
                        continue
                    if not l.get('charge'):
                        picharges = PICharge.find(k)
                    else:
                        picharges = [l.get('charge')]
                    for i in picharges:
                        if type == const.CHARGE_TYPE_P_PI: 
                            if len(cls.find_details(i.purchase_invoice_no, None, i.line_no, None, args.get('p_head_id', None))) == 0:
                                cobj = copy.deepcopy(i)
                                cobj.total  = l.get('total')
                                cobj.vat_total  = l.get('total')
                                cobj.st_detail_id = l.get("id")
                                if posted.get(k):posted[k].append(cline_no)
                                else:posted.update({k:[cline_no]})
                                charges.append(cobj)    
        for charge in charges:
            keys = ['company_code', 'po_no', 'type',
                    'line_no', 'percentage', 'amount', 'po_head_id', 
                    'pi_head_id', 'charge_code', 'percentage', 'uuid','uuid2']
            if_post = None
            if d_charge_dict and len(d_charge_dict) > 0:
                if hasattr(charge, 'invoice_no'):
                    d_charge = d_charge_dict.get(charge.invoice_no, [])
                else:
                    d_charge = d_charge_dict.get(charge.note_no, [])
                for d in d_charge:
                    if hasattr(charge, 'invoice_no'):
                        charge_code = charge.charge_code
                    else:
                        charge_code = charge.chg_discount_code
                    if const.CHARGE_CODES.get(charge_code) and d.get("charge_code") in const.CHARGE_CODES.get(charge_code)\
                    and charge.line_no == d.get("line_no") and charge.note_no == d.get('note_no'):
                        dn_detail = DNDetail.get(d.get("id"))
                        if dn_detail.kingdee_date:
                            keys.append({"kingdee_date":_get_lastday_of_month(dn_detail.kingdee_date)})
                        keys.extend([
                                     {'total':d.get("amount", 0)},
                                     {'vat_total':d.get("amount", 0)},
                                     {'dn_detail_id':d.get("id")},
                                     {'note_no':d.get('note_no')},
                                     {'currency':d.get('currency', 'RMB')}
                                     ])
                        if_post = 1
                        break
                if not if_post:continue
            elif hasattr(charge, 'st_detail_id') and charge_dict and len(charge_dict) >0:
                st_detail = STDetail.get(charge.st_detail_id)
                charge.kingdee_date = None
                if st_detail.kingdee_date:
                    charge.kingdee_date =  _get_lastday_of_month(st_detail.kingdee_date)
                keys.extend(["st_detail_id", "kingdee_date"])
            if charge.__tablename__ == "vat_pcharge": 
                keys.append('invoice_no')
            if charge.__tablename__ == "t_purchase_invoice_charges":
                keys.append(('invoice_no','purchase_invoice_no'))
                
            if type in const.CHARGE_TYPE_B: 
                pihead = PiHead.get_phead_info(charge.invoice_no, charge.po_no, None, args.get('s_head_id'))
                if not pihead:continue
                keys.append('s_head_id')
                args.update({'pi_head_id':pihead.id})
                if not if_post:   keys.extend([('total','amount'),('vat_total','amount')])
                
            elif type in const.CHARGE_TYPE_A:
                pihead = PiHead.get_phead_info(charge.purchase_invoice_no, charge.po_no, args.get('p_head_id'))
                if not pihead:continue
                args.update({'pi_head_id':pihead.id})
                keys.extend(['p_head_id', 'total', 'vat_total']) 
                
            elif type in [const.CHARGE_TYPE_S_MF, const.CHARGE_TYPE_S_NMF] or type in const.CHARGE_TYPE_M_MAN: 
                keys.extend(['m_head_id', ('total','vat_total'), ('vat_total','ava_total2')])
                
            elif type == const.CHARGE_TYPE_S_ERP:
                keys.extend(['s_head_id',('charge_code','chg_discount_code')])
            params = _get_params_from_args_and_obj(keys, charge, ** args)
            obj    = cls( ** params)
            if type in [const.CHARGE_TYPE_P_PRI, const.CHARGE_TYPE_P_PI]:
                obj.uuid = str(uuid.uuid4())
            elif type in [const.CHARGE_TYPE_S_PI, const.CHARGE_TYPE_S_PRI]:
                obj.uuid2 = str(uuid.uuid4())
            DBSession.add(obj)
            DBSession.flush()
            
    @classmethod
    def find_other_charges_from_vat(cls, head_id, type, head_type, pi_head_id = None):
        ava_total, result = 0, []
        data = DBSession.query(cls).filter(cls.active == 0)
        if isinstance(type, list) and len(type)>0:data = data.filter(cls.type.in_(type))
        elif type:data = data.filter(cls.type == type)
        if head_id: data = data.filter(getattr(cls, head_type) == head_id)
        if pi_head_id:data = data.filter(cls.pi_head_id == pi_head_id)
        data = data.all()
        for a in data:
            vat_total, vat_total2 =  0, 0
            if a.p_head_id:status = a.p_head.status
            if a.s_head_id:status = a.s_head.status
            if a.m_head_id:status = a.m_head.status
            msn_details = PCharge.find_details(a.invoice_no, a.type, a.line_no, None, None, a.uuid, a.uuid2, a.charge_code, a.note_no)
            for b in msn_details:
                if status == const.VAT_THEAD_STATUS_NEW:
                    if b.id != a.id: vat_total += pn(b.vat_total)
                else:
                    vat_total += pn(b.vat_total)
            cate = None
            if type == const.CHARGE_TYPE_A: cate = const.CHARGE_TYPE_S_MF
            if type == const.CHARGE_TYPE_B: cate = const.CHARGE_TYPE_S_NMF
            if type == const.CHARGE_TYPE_P: cate = const.CHARGE_TYPE_PM
            if type == const.CHARGE_TYPE_S: cate = const.CHARGE_TYPE_SM  
            msn_details2 = PCharge.find_details(a.invoice_no, cate, a.line_no, None, None, a.uuid, a.uuid2, a.charge_code, a.note_no) if cate else []
            for c in msn_details2:
                if status == const.VAT_THEAD_STATUS_NEW:
                    if c.id != a.id: vat_total2 += pn(c.vat_total)
                else:
                    vat_total2 += pn(c.vat_total)
            a.ava_total2 = a.vat_total - vat_total2   
            a.ava_total = a.total - vat_total 
            a.msn_total = vat_total
            result.append(a)
        return result   
    
    @classmethod
    def find_details(cls,invoice_no = None, types = None, line_no = None, pi_head_id = None, p_head_id=None, uuid=None, uuid2=None, charge_code = None, note_no = None):
        data = DBSession.query(cls).filter(cls.active == 0)
        if invoice_no:data = data.filter(cls.invoice_no == invoice_no)
        if types:
            if type(types) == type([]):
                data = data.filter(cls.type.in_(types))
            else:data = data.filter(cls.type == types)
        if line_no:data = data.filter(cls.line_no == line_no)
        if pi_head_id:data = data.filter(cls.pi_head_id == pi_head_id)
        if p_head_id: data = data.filter(cls.p_head_id == p_head_id)
        if uuid: data = data.filter(cls.uuid == uuid)
        if uuid2: data = data.filter(cls.uuid2 == uuid2 )
        if charge_code: data = data.filter(cls.charge_code == charge_code)
        if note_no: data = data.filter(cls.note_no == note_no)
        return data.all()
    
    @classmethod
    def find_type_charges(cls, type, head_id, invoice_no):
        data = DBSession.query(cls).filter(cls.invoice_no == invoice_no)
        if type:
            data = data.filter(cls.type == type)
        if type == const.CHARGE_TYPE_P_PI or type == const.CHARGE_TYPE_P_PO:
            data = data.filter(cls.p_head_id == head_id)
        elif type == const.CHARGE_TYPE_S_PI or type == const.CHARGE_TYPE_S_PO:
            data =data.filter(cls.s_head_id == head_id)
        return data.all()

    @classmethod
    def find_details_by_po(cls, po_no):
        return DBSession.query(cls).filter(cls.po_no == po_no).all()
      
    @classmethod
    def find_details_by_dzd(cls, id, type = None):
        data = DBSession.query(cls).filter(cls.active == 0)
        if type:
            data = data.filter(cls.st_detail_id == id).filter(cls.p_head_id != None)
        else:
            data = data.filter(cls.dn_detail_id == id).filter(cls.s_head_id != None)
        return data.first()
      
class UI(Table_UI):
    
    @classmethod
    def find(cls, pi_no = None, supplier = None, note_type = None):
        data = DBSession2.query(cls) 
        if pi_no:
            data = data.filter(cls.ref_code.ilike('%%%s%%' % pi_no))
        if supplier:
            data = data.filter(cls.supplier == supplier)
        if note_type:
            data = data.filter(cls.note_type == note_type)
        return data.all() 
    
    @classmethod
    def find_cust(cls, supplier = None):
        data = DBSession2.query(cls).filter(cls.company_code.in_(getCompanyCode())).filter(cls.pi_no == None)
        if supplier:
            data = data.filter(cls.supplier == supplier)
        return data.all()     
    
    @classmethod
    def find_by_note(cls, note_no):
        return DBSession2.query(cls).filter(cls.note_no == note_no).first()
      
class UID(Table_UIDetail):
    
    @classmethod
    def find_details(cls, pi_no = None, po_no = None, item_no = None , qty = None, unit_price = None, line_no = None):
        data = DBSession2.query(cls)
        if pi_no: data = data.filter(cls.pi_no == pi_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if qty: data = data.filter(cls.note_qty == int(qty))
        if unit_price: data = data.filter(cls.unit_price == unit_price)
        if line_no: data = data.filter(cls.line_no == line_no)
        return data.all()
    
    @classmethod
    def find_details_by_note_no(cls, note_no):
        return DBSession2.query(cls).filter(cls.note_no == note_no).all()

     
class UICharge(Table_UICharge):
    
    @classmethod
    def find_details(cls, pi_no, line_no=None, charge_code = None):
        data_list = [] 
        if pi_no:
            uis = UI.find(pi_no)
            for a in uis:
                if len(a.ref_code.strip()) != len(pi_no):
                    continue
                data = DBSession2.query(cls).filter(cls.note_no == a.note_no)
                if line_no:
                    data = data.filter(cls.line_no == line_no)
                if charge_code:
                    data = data.filter(cls.chg_discount_code == charge_code)
                for b in data.all():
                    b.pi_no       = pi_no
                    b.charge_code = b.chg_discount_code
                    b.supplier    = a.supplier
                    b.note_no     = a.note_no
                    b.note_type = a.note_type
                    b.status    = a.status
                    b.note_date = a.create_date
                    b.remark    = a.remark
                    data_list.append(b)     
        return data_list
    
    @classmethod
    def find_details_by_note_no(cls, note_no, line_no = None):
        data = DBSession2.query(cls).filter(cls.note_no == note_no)
        if line_no:
            data = data.filter(cls.line_no == line_no)
        data = data.all()
        return data
    
    @classmethod
    def search_charge_erp(cls, ** args):
        data_list = []
        supplier, pi_no, note_no, line_no, time_start, time_end = [args.get(i, None) for i in ['supplier', 'pi_no', 'note_no', 'line_no', 'create_time_start', 'create_time_end']]
        for a in UI.find(None, supplier):
            if not a.pi_no:
                curr_charges = []
                charges = DBSession2.query(cls).filter(cls.note_no == a.note_no).filter(cls.company_code.in_(getCompanyCode())).all()
                details, charges, include_tax = _all_rewrite_price_and_filter_charges(charges, [])
                for charge in charges:
                    if note_no and note_no != charge.note_no:
                        continue
                    if line_no and line_no != charge.line_no:
                        continue
                    if time_start and dt.strptime(time_start + "00:00:00", "%Y-%m-%d%H:%M:%S") > charge.create_date:
                        continue
                    if time_end and dt.strptime(time_end   + "23:59:59", "%Y-%m-%d%H:%M:%S") < charge.create_date:
                        continue
                    curr_charges.append(charge)
                other_charges = cls.parse_other_charges(a.note_no, curr_charges, supplier)
                for b in other_charges:
                    data_list.append({
                                      "supplier":a.supplier,
                                      "company_code":a.company_code,
                                      "note_no":a.note_no,
                                      "note_type":a.note_type,
                                      "status":a.status,
                                      "create_date":a.create_date,
                                      "remark":a.remark,
                                      "line_no":b.line_no,
                                      "chg_discount_code":b.chg_discount_code,
                                      "total":pf(b.total),
                                      })
                del charges, other_charges
        return data_list
    
    @classmethod
    def parse_other_charges(cls, note_no, other_charges, supplier):
        charges, tax_charges, curr_charge = [], [], []
        ui = UI.find_by_note(note_no)
        uids = UID.find_details_by_note_no(note_no)
        tax_rate = 0.17
        if ui.supplier in const.TAX_PERCENTAGE_SUPPLIER:
            tax_rate = 0.03
        detail_total, charge_total = 0, 0
        for uid in uids:
            detail_total += float(uid.item_total)
        for other_charge in other_charges:
            if other_charge.chg_discount_code in const.CHARGE_CODES.get(u'\u589e\u503c\u7a0e', []):
                tax_charges.append(other_charge)
            else:
                charge_total += float(other_charge.total)
                charges.append(other_charge)
        post_type, tax_charge = [], []
        for charge in tax_charges:
            if "%.3f" % charge.total == "%.3f" % (charge_total * float(tax_rate)):
                post_type.append(1)
            elif "%.3f" % charge.total == "%.3f" % (detail_total * float(tax_rate)):
                post_type.append(2)
            else:
                tax_charge.append(charge)
        result_charge = []
        for charge in charges:
            if 1 not in post_type and len(tax_charge) == 0:
                curr_total = charge.total
                charge.supplier = supplier
                charge.total = float(curr_total)/(float(1) + float(tax_rate))
            result_charge.append(charge)  
        result_charge.extend(tax_charge)
        return result_charge
    
    @classmethod
    def search_cust_charge_erp(cls, ** args):
        data_list = []
        pi_no, note_no, time_start, time_end = args.get('pi_no'), args.get('note_no'), args.get('create_time_start'), args.get('create_time_end')
        for a in UI.find_cust(args.get('supplier')):
            data = DBSession2.query(cls).filter(cls.note_no == a.note_no).filter(cls.company_code.in_(getCompanyCode()))
            for b in data.all():
                data_list.append({
                                  "company_code":a.company_code,
                                  "note_no":a.note_no,
                                  "note_type":a.note_type,
                                  "status":a.status,
                                  "create_date":a.create_date,
                                  "remark":a.remark,
                                  "line_no":b.line_no,
                                  "chg_discount_code":b.chg_discount_code,
                                  "total":b.total,
                                  })     
        return data_list


class STatement(Table_STatement):
    
    @classmethod
    def find(cls):
        return DBSession.query(cls).filter(cls.active == 0).all()
   
   
class ARLog(Table_ARLog):
    
    @classmethod
    def find(cls, ** args):
        id = int(args['id'])
        history = DBSession.query(cls)
        if args.get('type') == 'T':
            history = history.filter(cls.t_head_id==id)
        if args.get('type') == 'C':
            history = history.filter(cls.c_head_id==id)
        if args.get('type') == 'P':
            history = history.filter(cls.p_head_id==id)
        if args.get('type') == 'S':
            history = history.filter(cls.s_head_id==id) 
        if args.get('type') == 'M':
            history = history.filter(cls.m_head_id==id)
        if args.get('type') == 'O':
            history = history.filter(cls.o_head_id==id)
        if args.get('type') == 'N':
            history = history.filter(cls.n_head_id==id)
        return history.order_by("id").all()
    
    
    @classmethod
    def insert(cls, ** args):
        if args.get("remark"):
            DBSession.add(cls( ** args))
            DBSession.flush()
            
            
        
class STHead(Table_STHead):
    
    @classmethod
    def find_by_status(cls, status):
        return DBSession.query(cls).filter(cls.status == status).all()
    
    @classmethod
    def find(cls, ** args):
        ids, page, limit, cate =[0], 500, 0, 'next'
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit")) 
            offset = int(args.get("offset"))
        ids.extend(STDetail.find_sthead(args))
        ids.extend(DNDetail.find_sthead(args))
        if len(ids)>1:
            args['ids'] = list(set(ids))
        queryExtend = QueryExtend(cls, ** args)
        return cls.paset_result(queryExtend, limit, offset, [], limit,cate)

    @classmethod
    def paset_result(cls, QueryExtend, limit, offset, results, flimit, cate):
        tax_total, next_page = 0, limit
        QueryExtend.query_all(True, DBSession, True, limit,offset, ** {
                      const.QUERY_TYPE_EQ: ['status'],
                      const.QUERY_TYPE_LIKE: ['ref'],
                      const.QUERY_TYPE_LIKE_AND_OR: [('supplier', 'supplier_name', 'supplier_short_name')],
                      const.QUERY_TYPE_IN: [('id', 'ids')],
                      const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
                      const.QUERY_TYPE_ORDER_BY: ['create_time'],
                      const.QUERY_TYPE_NOT_NULL: []
                      })
        queryExtend_result = QueryExtend.result
        if len(queryExtend_result)==0:
            return results, next_page, flimit
        for i in QueryExtend.result:
            next_page += 1
            i.pi_amount = i.find_pi_amount()
            i.dn_amount = i.find_dn_amount()
            results.append(i)
            if len(results) > 24:break
        if len(results) < 25 and cate == 'next':
            limit = offset
            offset = offset + 25
            return cls.paset_result(QueryExtend, limit, offset, results, flimit, cate)
        else:
            return results, next_page, flimit
    
    @classmethod
    def upload_file(cls, **kw):
        id = kw.get('id')
        if_submit = kw.get('sm')
        type = kw.get('type', const.IMPORT_STATEMENT_NO)
        if if_submit:
            file_path = kw['attachment']
            (pre, ext)=os.path.splitext(file_path.filename)
            fileDir = os.path.join(os.path.abspath(os.path.curdir), "report_download/sys")
            if not os.path.exists(fileDir): os.makedirs(fileDir)
            file_name="%s%.4d%s"%(dt.now().strftime("%Y%m%d%H%M%S"), random.randint(1, 1000), ext)
            filepath = os.path.join(fileDir, file_name)
            permanent_file = open(filepath, 'wb')
            permanent_file.write(file_path.file.read())
            permanent_file.close()
            if type == const.IMPORT_STATEMENT_YES:
                st_head = STHead.import_data(filepath, ** kw)
                if st_head:
                    if file_path.filename:
                        if st_head.upload_name:
                            st_head.upload_name = " | ".join([st_head.upload_name, file_path.filename.split("\\")[-1]])
                        else:
                            st_head.upload_name = file_path.filename.split("\\")[-1]
                    st_head.file_name = filepath
                    st_head.i_file_name =  file_name
                    DBSession.merge(st_head)
                    DBSession.flush()
                    STHead.parse_match(st_head.id)
                    STHead.parse_dndetails(st_head.id)
                    return "Import and save DB Successfully!"
            else:
                state = {
                         'st_head_id':id,
                         'upload_name':file_path.filename,
                         'file_name':filepath,
                         'i_file_name':file_name
                        }
                statement = STatement(** state)
                DBSession.add(statement)
                DBSession.flush()
                return "Import and not save DB, We will save it later!"
      
    @classmethod
    def scheduled_tasks(cls):
        statements = STatement.find()
        for i in statements:
            filepath = i.file_name
            upload_name = i.upload_name
            file_name = i.i_file_name
            st_head = STHead.import_data(filepath, ** {})
            if st_head:
                if upload_name:
                    st_head.upload_name = upload_name.split("\\")[-1]
                st_head.file_name = filepath
                st_head.i_file_name =  file_name
                DBSession.merge(st_head)
                DBSession.flush()
                STHead.parse_match(st_head.id)
                STHead.parse_dndetails(st_head.id)
                i.st_head_id = st_head.id
                i.active = 1
                DBSession.merge(i)
                DBSession.flush()
         
    @classmethod
    def get_product_information(cls, pi_no, sc_no = None):
        pi = PID.get_details_by_pi_no(pi_no)
        po = PO.find_detail(pi.po_no)
        so = None
        if sc_no:
            so = SO.get(sc_no)
        elif po.sc_no:
            so = SO.get(po.sc_no)
        return dict(
                    so_no = so.sales_contract_no if so else None, 
                    so_date = so.create_date if so else None, 
                    po_date = po.create_date, 
                    pi_date = pi.create_date,
                    customer_code = so.customer_code if so else None
                    )
            
    @classmethod
    def import_data(cls, permanent_file, ** kw):
        from vatsystem.util.excel_helper import APExcel
        APExcels = APExcel(templatePath = permanent_file)
        data = APExcels.outputData()
        refTime = dt.now().strftime('%Y%m')[2:]
        ref = 'DZD%s' % refTime
        max = DBSession.query(func.max(cls.ref)).filter(cls.ref.like('%s%%' % ref)).first()[0]
        if max and len(max) == 13: max = int(max[7:]) + 1
        else: max = 1 
        if kw.get('id'):
            st_head = STHead.get(kw.get('id'))
        else:
            st_head = cls( ** {'name':"", 
                               'supplier_short_name':"", 
                               'ref':'%s%06d' % (ref, max)}
                          )
            DBSession.add(st_head)
            DBSession.flush()
        
        st_details = data.get('pi_list')
        dn_details = data.get('dn_list')
        for b in st_details:
            pi_no =  b.get('invoice_no')
            info = cls.get_product_information(pi_no)
            if not b.get('reconciliation_lot'):
                continue
            if b.get('issue_date'):
                b.update({"issue_date":datetime.datetime.fromtimestamp (int(b.get('issue_date')))})
            if b.get('item_amount'):
                b.update({"rmb_amount":b.get('item_amount'), "rmb_amount_p":b.get('item_amount', 0)*(1+const.TAX_PERCENTAGE)})
            b.update(info)
            st_detail = STDetail( ** b)
            st_detail.st_head_id = st_head.id
            
            if b.get('qty'):
                if not b.get('unit_price'):
                    b.update({'unit_price':b.get('unit_price', 0)})
                st_detail.type = const.ERP_TYPE_DETAIL
            else:
                st_detail.type = const.ERP_TYPE_CHARGE
                st_detail.qty = 1
                st_detail.unit_price = b.get('item_amount')
            if b.get('billing_month') == 'cancel':
                st_detail.status = 'complete'
            DBSession.add(st_detail)
            DBSession.flush()
        
        for c in dn_details:
            if not c.get('reconciliation_lot'):
                continue
            if c.get('issue_date'):
                c.update({"issue_date":datetime.datetime.fromtimestamp (int(c.get('issue_date')))})
            dn_detail = DNDetail(** c)
            if c.get('internal_item_code'):
                dn_detail.type = const.ERP_TYPE_DETAIL
            elif c.get('other_ref') and not c.get('internal_item_code'):
                if "PO" in c.get('other_ref'):
                    dn_detail.order_qty = 1
                    dn_detail.unit_price = c.get('amount')
                    dn_detail.type = const.ERP_TYPE_OTHER_CHARGE
                else:
                    dn_detail.type = const.ERP_TYPE_CHARGE
                    dn_detail.order_qty = 1
                    dn_detail.unit_price = c.get('amount')
            elif not c.get('other_ref') and not c.get('internal_item_code'):
                dn_detail.order_qty = 1
                dn_detail.unit_price = c.get('amount')
                dn_detail.type = const.ERP_TYPE_OTHER_CHARGE
            if c.get('billing_month') == 'cancel':
                dn_detail.status = 'complete'
            dn_detail.st_head_id = st_head.id
            DBSession.add(dn_detail)
            DBSession.flush()
        return st_head
    
    @classmethod
    def parse_phead(cls, phead, charge):
        for c, h in charge.iteritems():
            st_detail = STDetail.get(c)
            pidetails = phead.pi_details
            for pidetail in pidetails:
                if st_detail.category == phead.category and st_detail.st_head.ref == phead.dzd and pidetail.invoice_no == st_detail.invoice_no and \
                        st_detail.pi_line_no == pidetail.line_no:
                    st_detail.mpi_id = phead.id
                    st_detail.mpi_ref = phead.ref
                    DBSession.merge(st_detail)
                                 
    @classmethod
    def parse_match(cls, ids):
        st_head = cls.get(ids)
        s_details, s_charges = [], []
        invoice_dict, charge_list, is_post_dict = {}, {}, {}
        contrast_charge = {
                           const.ERP_HEAD_TYPE_PI : {}, 
                           const.CHARGE_TYPE_P_PI : {}, 
                           const.TAX_RAX : {}, 
                           const.CHARGE_OTHER_CHARGE:{}
                           }
        st_details = STDetail.find_details_by_status(st_head.id)
        
        pids = []
        for a in st_details:
            if a.reconciliation_lot:
                pids.extend(PID.find_details_by_pi_no(a.invoice_no, a.item_code, None, None, a.pi_line_no))
                
        for a in st_details:
            if not a.reconciliation_lot:continue
            category = "_".join([a.supplier_code, a.reconciliation_lot.split("(")[0]])
            a.category = category
            if a.type == const.ERP_TYPE_DETAIL:
                s_details.append(a)
            else:
                if not a.status == "complete":
                    s_charges.append(a)
          
        pid_qty = {}
        pid_total = {}
        for d in pids:
            key = "%s_%s_%s" % (d.purchase_invoice_no, d.item_no, d.line_no)
            if pid_qty.get(key):
                pid_qty[key] += d.qty
            else:
                pid_qty.update({key:d.qty})

            if pid_total.get(d.purchase_invoice_no):
                if pid_total[d.purchase_invoice_no].get(d.item_no):
                    pid_total[d.purchase_invoice_no][d.item_no] += d.item_total
                else:
                    pid_total[d.purchase_invoice_no].update({d.item_no:d.item_total})
            else:
                pid_total.update({d.purchase_invoice_no:{d.item_no:d.item_total}})
                 
        for a in s_details:
            
            pk = "%s|%s" % (a.invoice_no, a.category)
            key = "%s_%s_%s" % (a.invoice_no, a.item_code, a.pi_line_no)
            contrast_charge[const.TAX_RAX].update({pk: a.tax_rate})
            if contrast_charge[const.ERP_HEAD_TYPE_PI].get(pk):
                contrast_charge[const.ERP_HEAD_TYPE_PI][pk] += a.item_amount
            else:
                contrast_charge[const.ERP_HEAD_TYPE_PI].update({pk:a.item_amount})
            
            if a.status == "complete":
                continue    
            
            item_qty = 0  
            other_details = STDetail.find_details_by_inovice(a.invoice_no , a.item_code, None, a.pi_line_no)
            for b in other_details:
                item_qty += b.qty
                
            erro =  {}
            if not a.unit_price: 
                a.unit_price = 0
            if len(pids)>0:
                for d in pids:
                    if d.purchase_invoice_no != a.invoice_no or d.line_no != int(a.pi_line_no):
                        continue
                    curcount = 0
                    curerro = []
                    if a.item_code == d.item_no:
                        curcount += 1
                        curerro.append('item_code') 
                    if "%.3f" % a.unit_price == "%.3f" % d.unit_price:
                        curcount += 1
                        curerro.append('unit_price') 
                    if a.qty == d.qty:
                        curcount += 1
                        curerro.append('qty')
                    if pid_qty.get(a.invoice_no) and int(item_qty) < int(pid_qty.get(key, 0)):
                        curcount += 1
                        curerro.append('lessThan')
                    erro.update({curcount:curerro})
                    
                    if pid_qty.get(key) and a.item_code == d.item_no and int(a.pi_line_no) == d.line_no\
                    and "%.3f" % a.unit_price == "%.3f" % d.unit_price and int(item_qty) <= int(pid_qty.get(key, 0)):
                        if invoice_dict.get(a.invoice_no):
                            invoice_dict[a.invoice_no].append({
                                                                'line_no':d.line_no,
                                                                'item_no':d.item_no,
                                                                'po_line_no':d.po_line_no,
                                                                'qty':int(a.qty),
                                                                'item_total':a.qty*a.unit_price,
                                                                'category':a.category,
                                                                'id':a.id
                                                                })
                        else:
                            invoice_dict.update({a.invoice_no:[{
                                                                'line_no':d.line_no,
                                                                'item_no':d.item_no,
                                                                'po_line_no':d.po_line_no,
                                                                'qty':int(a.qty),
                                                                'item_total':a.qty*a.unit_price,
                                                                'category':a.category,
                                                                'id':a.id
                                                                 }]})
                        st_head.supplier = d.supplier
                        st_head.supplier_name = d.supplier_name
                        st_head.supplier_short_name = d.supplier_short_name 
                        a.status = "complete"
                        a.invoice_no = d.purchase_invoice_no
                        ItemDesc.save(** {'code':d.supplier, 'item_no':a.item_code, 'description':a.item_description})
                        DBSession.merge(a)
                        DBSession.flush()
                        break
                if a.status == "uncomplete":
                    if len(erro) > 0:
                        merror = max(erro.iteritems(),key=lambda x:x)
                        values = ",".join(merror[1])
                        a.error = values
                        DBSession.merge(a)
        
        for s_charge in s_charges:
            contrast_tax_charge = contrast_charge[const.CHARGE_OTHER_CHARGE]    
            contrast_charge_charge = contrast_charge[const.CHARGE_TYPE_P_PI]
            pk = "%s|%s" % (s_charge.invoice_no, s_charge.category)
            item_amount = 0  
            other_charge = STDetail.find_details_by_inovice(s_charge.invoice_no, s_charge.item_code, None, s_charge.pi_line_no)
            for b in other_charge:
                item_amount += b.item_amount
                
            if s_charge.item_code not in const.CHARGE_CODES.get(const.CHARGE_CODE_TAX):
                curr_charge = contrast_tax_charge
            else:
                curr_charge = contrast_charge_charge
            if curr_charge.get(pk):
                curr_charge[pk]["total"] += s_charge.item_amount
                if s_charge.id not in curr_charge[pk]["id"].keys():
                    curr_charge[pk]["id"].update({s_charge.id:s_charge.item_amount})
                    curr_charge[pk]["charge_code_list"].update({s_charge.id:s_charge.item_code})
                    curr_charge[pk]["line_no"].update({s_charge.id:s_charge.pi_line_no})
            else:
                curr_charge.update({pk:{
                                       "line_no":{s_charge.id:s_charge.pi_line_no},
                                       "total":s_charge.item_amount,
                                       "item_total":item_amount,
                                       "tax_rate":s_charge.tax_rate, 
                                       "id":{s_charge.id:s_charge.item_amount},
                                       "charge_code":s_charge.item_code,
                                       "charge_code_list":{s_charge.id:s_charge.item_code}
                                       }})
                
        picharges = []
        s_charges_invoices = list(set([sc.invoice_no for sc in s_charges]))
        for s_charge_invoice in s_charges_invoices:
            picharges.extend(PICharge.find_details_by_pi(s_charge_invoice))  
            
        charge_dict = {}
        for picharge in picharges:
            if charge_dict.get(picharge.purchase_invoice_no):
                if charge_dict[picharge.purchase_invoice_no].get(picharge.charge_code):
                    charge_dict[picharge.purchase_invoice_no][picharge.charge_code] += picharge.total
                else:
                    charge_dict[picharge.purchase_invoice_no].update({picharge.charge_code:picharge.total})
            else:
                charge_dict.update({picharge.purchase_invoice_no:{picharge.charge_code:picharge.total}})    
           
        for a in s_charges:
            erro =  {}
            item_amount = 0  
            other_charge = STDetail.find_details_by_inovice(a.invoice_no, a.item_code, None, a.pi_line_no)
            for b in other_charge:
                item_amount += b.item_amount
            for b in picharges:
                curcount = 0
                curerro = []
                if a.item_code == b.charge_code:
                    curcount += 1
                    curerro.append('item_code') 
                if charge_dict.get(a.invoice_no) and "%.3f" % item_amount < "%.3f" %  charge_dict[a.invoice_no].get(b.charge_code, 0):
                    curcount += 1
                    curerro.append('lessTan')
                if charge_dict.get(a.invoice_no) and "%.3f" %  item_amount == "%.3f" %  charge_dict[a.invoice_no].get(b.charge_code, 0):
                    curcount += 1
                    curerro.append('equal')
                erro.update({curcount:curerro})
                
        erp_pi, erp_charge, erp_other_charge = {}, {}, {}
        for k, v in pid_total.iteritems():
            a_i = 0
            for a1, b1 in v.iteritems(): 
                a_i += b1
            erp_pi.update({k:a_i})
            
        for k, v in charge_dict.iteritems():
            a_i = 0
            a_o = 0
            for a1, b1 in v.iteritems():
                if a1 in const.CHARGE_CODES.get(const.CHARGE_CODE_TAX):
                    a_i += b1
                else:
                    a_o += b1
            erp_charge.update({k:a_i})
            erp_other_charge.update({k:a_o})
                
        is_contrast_charge = {}
        c_pi = contrast_charge[const.ERP_HEAD_TYPE_PI]
        c_charge = contrast_charge[const.CHARGE_TYPE_P_PI]
        c_tax_charge = contrast_charge[const.CHARGE_OTHER_CHARGE]
        c_rate = contrast_charge[const.TAX_RAX]
        
        tax_charge_out = {}
        if len(c_charge) > 0:
            for k, v in c_charge.iteritems():
                ids, comp = {}, {}
                invoice = k.split("|")
                c_pi_i = c_pi.get(k, 0)
                c_charge_i = v
                c_charge_ids = c_charge_i["id"]
                c_charge_line_no_list = c_charge_i["line_no"]
                c_rate_i = c_rate.get(k, const.TAX_PERCENTAGE)
                c_tax_charge_i = c_tax_charge.get(k, {"id":[],"charge_code_list":{}, "line_no":{}})
                c_tax_charge_ids = c_tax_charge_i["id"]
                c_tax_charge_list = c_tax_charge_i["charge_code_list"]
                c_tax_charge_line_no_list = c_tax_charge_i["line_no"]
                if (c_pi_i + c_tax_charge_i.get("total", 0)) != 0 and -0.005 <= float(c_charge_i["total"]/(c_pi_i+ c_tax_charge_i.get("total", 0))) - float(c_rate_i) <= 0.005\
                and float(c_charge_i['item_total']) <= float(charge_dict.get(invoice[0],{}).get(c_charge_i['charge_code'], 0)):
                    if not (erp_pi.get(invoice[0], 0) != 0 and -0.005 <= float(erp_charge.get(invoice[0], 0)/(erp_pi.get(invoice[0], 0) + erp_other_charge.get(invoice[0], 0))) - float(c_charge_i.get("total", 0)/(c_pi_i+ c_tax_charge_i.get("total", 0))) <= 0.005):
                        ids.update(c_charge_ids)
                        ids.update(c_tax_charge_ids)
                    else:
                        ids.update(c_tax_charge_ids)
                        tax_charge_out.update(c_charge_ids)
                else:
                    ids.update(c_charge_ids)
                    ids.update(c_tax_charge_ids)
                    
                comp.update(c_charge_ids)
                comp.update(c_tax_charge_ids)
                for c, o in comp.iteritems():
                    st_detail = STDetail.get(c)
                    st_detail.status = "complete"
                    DBSession.merge(st_detail)
                    
                pi_charge_list = []
                no = 0 
                for k1, v1 in ids.iteritems():
                    if k1 in c_charge_ids:
                        pi_cg = PICharge.get_details_by_pi(invoice[0], c_charge_line_no_list.get(k1))
                    else:
                        pi_cg = PICharge.find_charge_by_item_code(invoice[0], c_tax_charge_list.get(k1), const.ERP_HEAD_TYPE_PI, c_tax_charge_line_no_list.get(k1))
                    if not pi_cg:continue
                    if charge_list.get(invoice[0]):
                        charge_list[invoice[0]].append({
                                                        'line_no':"%s_%s_%s" % (pi_cg.line_no, pi_cg.po_chrg_line_no, a.tax_rate),
                                                        'category':invoice[1],
                                                        'id':k1,
                                                        'total':v1,
                                                        'charge':pi_cg,
                                                        'charge_code':pi_cg.charge_code
                                                        })
                    else:
                        charge_list.update({invoice[0]:[{
                                                        'line_no':"%s_%s_%s" % (pi_cg.line_no, pi_cg.po_chrg_line_no, a.tax_rate),
                                                        'category':invoice[1],
                                                        'id':k1,
                                                        'total':v1,
                                                        'charge':pi_cg,
                                                        'charge_code':pi_cg.charge_code
                                                        }]})
                    DBSession.merge(st_head)
                    
        if len(invoice_dict) > 0 or len(charge_list)>0:
            invoice_categroy_dict = {}
            for k, v in invoice_dict.iteritems():
                for a in v:
                    category = a.get('category')
                    if invoice_categroy_dict.get(category):
                        invoice_dict = invoice_categroy_dict[category]['invoice_dict']
                        if invoice_dict.get(k):
                            if not isinstance(a, list):
                                a = [a]
                            invoice_dict[k].extend(a)
                        else:
                            invoice_dict.update({k:[a]})
                    else:
                        invoice_categroy_dict.update({
                                              category:{
                                                        "invoice_dict":{k:[a]}
                                                        }})
            charge_categroy_dict = {}
            for k, v in charge_list.iteritems():
                for a in v:
                    category = a.get('category')
                    if charge_categroy_dict.get(category):
                        charge_dict = charge_categroy_dict[category]['charge_dict']
                        if charge_dict.get(k):
                            if not isinstance(a, list):
                                a = [a]
                            charge_dict[k].extend(a)
                        else:
                            charge_dict.update({k:[a]})
                    else:
                        charge_categroy_dict.update({
                                              category:{
                                                        "charge_dict":{k:[a]}
                                                        }})
                        
            for k, v in invoice_categroy_dict.iteritems():
                invoice_dict = v.get('invoice_dict')
                if invoice_dict:
                    invoice_str = ",".join(["%s$custom" % i for i in invoice_dict.keys()])
                else:continue
                query_dict = {'supplier': '', 
                              "head_type":"P_PI", 
                              "ids":invoice_str, 
                              "invoice_dict":invoice_dict, 
                              "charge_dict":{}
                              }
                if st_head.ref:
                    p_head_id = PHead.get_id_by_ref_category(st_head.ref, k)
                    query_dict.update({'p_head_id':p_head_id}) 
                phead = PHead.create(user=request.identity["user"], ** query_dict)
            
                if phead:
                    for x, x1 in invoice_dict.iteritems():
                        for u in x1:
                            is_post_dict.update({u.get('id'):[phead.id, phead.ref]})
                    st_head_status = 'complete'
                    st_details = st_head.st_details
                    for g in st_details:
                        if g.status == 'uncomplete':
                            st_head_status = 'uncomplete'
                            break
                    st_head.status = st_head_status      
                    st_head.name = phead.supplier_short_name
                    st_head.supplier = phead.supplier
                    st_head.supplier_name = phead.supplier_name
                    st_head.supplier_short_name = phead.supplier_short_name
                    DBSession.merge(st_head)
                    phead.dzd = st_head.ref
                    phead.category = k
                    DBSession.merge(phead)
                    DBSession.flush()
                    
                    status_dict = {
                                   "ids":str(phead.id),
                                   "status":const.VAT_CHEAD_STATUS_POST
                                   }
                    PHead.update_all_status(user=request.identity["user"], ** status_dict)
                    cls.parse_phead(phead, tax_charge_out)
                    
            for key, value in charge_categroy_dict.iteritems():
                phead = PHead.get_phead_by_ref_category(st_head.ref, key)
                if not phead: continue
                charge_dict = value.get('charge_dict', {})
                for x in charge_dict.values():
                    for u in x:
                        is_post_dict.update({u.get('id'):[phead.id, phead.ref]})
                for key1, value1 in charge_dict.iteritems():
                    shArgs = {'head_type':const.CHARGE_TYPE_P_PI, 'p_head_id':phead.id}
                    piHead = PiHead.get_pihead_id(key1, phead.id)
                    if piHead:
                        shArgs.update({
                                       'pi_head_id':piHead.id,
                                       'charge_dict':charge_dict
                                       })
                        i_charge = [i.get('charge') for i in value1]
                        PCharge.create(const.CHARGE_TYPE_P_PI, i_charge, ** shArgs)
                            
        st_details = st_head.st_details        
        for g in st_details:
            ref_id = is_post_dict.get(g.id)
            if ref_id and len(ref_id)>1:
                g.mpi_id  = ref_id[0]
                g.mpi_ref = ref_id[1]
                DBSession.merge(g)
                DBSession.flush()
                              
    
    
    @classmethod
    def parse_dndetails(cls, ids):
        st_head = cls.get(ids)
        detail_dict, charge_dict, other_charge_dict = {}, {}, {}
        pi_dict, po_dict = {},{}
        category_dict = {}
        d_details = {}
        d_ids, charge_list, other_charge_list =[], [], []
        dn_details = DNDetail.find_details_by_status(st_head.id)
        detail_total, charge_total, tax_total = {}, {}, {}
        for a in dn_details:
            if not a.reconciliation_lot:continue
            category = "_".join([a.supplier_code, a.reconciliation_lot.split("(")[0]])
            a.category = category
            if a.type == const.ERP_TYPE_DETAIL:
                if detail_total.get(a.other_ref):
                    detail_total[a.other_ref] += a.amount
                else:
                    detail_total.update({a.other_ref:a.amount})
                if a.status == 'complete':
                    continue
                if not a.unit_price:
                    a.unit_price  = 0
                uids = UID.find_details(a.other_ref, None, None , None, None, a.sn_line_no)
                erro =  {}
                for b in uids:
                    curcount = 0
                    curerro = []
                    if a.item_code == b.item_no:
                        curcount += 1
                        curerro.append('item_code') 
                    if "%.3f" % a.unit_price == "%.3f" % b.unit_price:
                        curcount += 1
                        curerro.append('unit_price') 
                    if a.order_qty == b.note_qty:
                        curcount += 1
                        curerro.append('qty')
                    erro.update({curcount:curerro})
                    if not (a.item_code == b.item_no and "%.3f" % a.unit_price == "%.3f" % b.unit_price and int(a.order_qty) == int(b.note_qty)):
                        continue
                    pidetails = PiDetail.find_details(a.other_ref, None, a.item_code)
                    f = 0
                    if len(pidetails) == 0:
                        f = 1
                        phead_query = {
                              "dn": const.ERP_TYPE_CN,
                              "supplier": '', 
                              "head_type":const.CHARGE_TYPE_P_PI, 
                              "ids":"%s$%s" % (a.other_ref, a.other_ref)
                              }
                        phead = PHead.create(user=request.identity["user"], ** phead_query)
                        phead.dzd = st_head.ref
                        phead.category = category
                        phead.status = const.VAT_THEAD_STATUS_POST
                        DBSession.merge(phead)
                        pidetails = PiDetail.find_details(a.other_ref, None, a.item_code)
                    for c in pidetails:
                        print c.item_no, a.kingdee_date
                        p_head_id = c.p_head_id
                        if f == 1 or not c.kingdee_date:
                            c.kingdee_date =  _get_lastday_of_month(a.kingdee_date)
                        if not p_head_id:
                            continue 
                        d_ids.append(p_head_id)
                        key  =  {
                                'item_no':c.item_no,
                                'line_no':c.line_no,
                                'note_no':b.note_no,
                                'po_line_no':c.po_line_no,
                                'qty':a.order_qty,
                                'unit_price':a.unit_price,
                                'amount':a.amount,
                                'category':category,
                                'id':a.id,
                                'pidetails':c,
                                }
                        if d_details.get(p_head_id):
                            d_details[p_head_id].append(a.id)
                        else:
                            d_details.update({p_head_id:[a.id]})
                        if detail_dict.get(p_head_id):
                            if detail_dict[p_head_id].get(c.invoice_no):
                                detail_dict[p_head_id][c.invoice_no].append(key)
                            else:
                                detail_dict[p_head_id].update({c.invoice_no:[key]})
                        else:
                            detail_dict.update({p_head_id:{c.invoice_no:[key]}})
                        a.status = "complete"
                        DBSession.merge(a)
                        DBSession.merge(c)
                        DBSession.flush()
                        po_dict.update({c.po_no:{"pi_head_id":c.pi_head_id,"p_head_id":p_head_id}})   
                        pi_dict.update({c.invoice_no:{"pi_head_id":c.pi_head_id,"p_head_id":p_head_id}})
                        break
                if a.status == "uncomplete":
                    if len(erro) > 0:
                        merror = max(erro.iteritems(),key=lambda x:x)
                        values = ",".join(merror[1])
                        a.error = values
                        DBSession.merge(a)
            elif a.type == const.ERP_TYPE_CHARGE:
                if a.item_code and a.item_code in const.CHARGE_CODES.get(u'\u589e\u503c\u7a05-\u61c9\u4ed8'):
                    if tax_total.get("%s_%s" % (a.other_ref, a.id)):
                        tax_total["%s_%s" % (a.other_ref, a.id)] += a.amount
                    else:
                        tax_total.update({"%s_%s" % (a.other_ref, a.id):a.amount})
                else:
                    if charge_total.get(a.other_ref):
                        charge_total[a.other_ref] += a.amount
                    else:
                        charge_total.update({a.other_ref:a.amount})
                if a.status == 'uncomplete':
                    charge_list.append(a)
            elif a.type == const.ERP_TYPE_OTHER_CHARGE:
                if a.status == 'uncomplete':
                    other_charge_list.append(a)
                
        for k in list(set(d_ids)):
            d_dict = detail_dict.get(k, {})
            query_dict = { 
                          'id':k,
                          'd_invoice_dict':d_dict,
                          'd_charge_dict': {}
                          }
            if st_head.ref:
                s_head  = SHead.find_s_head_id(k)
                if s_head:
                    query_dict.update({'s_head_id':s_head.id})
            shead = SHead.create(user=request.identity["user"], ** query_dict)
            
            for k1, v1 in d_dict.iteritems():
                query_dict1 = {
                              's_head_id':shead.id,
                              'd_invoice_dict':{k1:d_dict.get(k1, {})}
                             } 
                PiDetail.create([pi.get('pidetails') for pi in v1], ** query_dict1)
                
            if shead:
                st_head_status = 'uncomplete'
                dn_details = st_head.dn_details
                for g in dn_details:
                    g_details = d_details.get(k, [])
                    if g.id in g_details:
                        g.msn_id = shead.id
                        g.msn_ref = shead.ref
                        DBSession.merge(g)
                        DBSession.flush()
                st_head.status = st_head_status      
                st_head.name = shead.supplier_short_name
                st_head.supplier = shead.supplier
                st_head.supplier_name = shead.supplier_name
                st_head.supplier_short_name = shead.supplier_short_name
                DBSession.merge(st_head)
                shead.dzd = st_head.ref
                DBSession.merge(shead)
                DBSession.flush()
                status_dict = {
                   "ids":str(shead.id),
                   "status":const.VAT_CHEAD_STATUS_POST
                   }
                SHead.update_all_status(user=request.identity["user"], ** status_dict)
                  
        charge_dict1 = {}
        d_charge_dict = {}
        for a in charge_list:
            pidetail = PiDetail.find_s_head_id_by_category(a.category, a.other_ref)
            erro =  {}
            curerro = []
            curcount = 0
            if not pidetail:
                curcount += 1
                curerro.append('mpi')
                continue
            s_head = pidetail.s_head
            s_head_id = s_head.id if s_head else None
            s_head_ref = s_head.ref if s_head else None
            if not s_head_id:continue
            a_tax_total = tax_total.get("%s_%s" % (a.other_ref, a.id))
            if a_tax_total and (-0.005 <= float(detail_total.get(a.other_ref, 0) * a.tax_rate - a_tax_total) <= 0.005 or \
                                -0.005 <= float(charge_total.get(a.other_ref, 0) * a.tax_rate - a_tax_total) <= 0.005):
                a.status = 'complete'
                a.msn_id = s_head_id
                a.msn_ref = s_head_ref
                DBSession.merge(a)
                continue
            is_uicharges = None
            uicharges = UICharge.find_details(a.other_ref, a.sn_line_no)
            for d in uicharges:
                if is_uicharges:
                    break
                if a.item_code == d.chg_discount_code:
                    curcount += 1
                    curerro.append('item_code') 
                if d.amount and "%.2f" %  a.amount == "%.2f" % d.amount:
                    curcount += 1
                erro.update({curcount:curerro})
                if (const.CHARGE_CODES.get(a.item_code) and d.chg_discount_code in const.CHARGE_CODES.get(a.item_code))\
                or (a.item_code == d.chg_discount_code or a.item_code in d.chg_discount_code or d.chg_discount_code in a.item_code):
                    is_uicharges = True
                    if pidetail:
                        d_charge = {
                                    'id':a.id,
                                    'charge_code': a.item_code,
                                    'line_no':d.line_no, 
                                    'amount': a.base_amount,
                                    'note_no':d.note_no,
                                    'currency':a.currency
                                    }
                        if d_charge_dict.get(a.other_ref):
                            d_charge_dict[a.other_ref].append(d_charge)
                        else:
                            d_charge_dict.update({a.other_ref:[d_charge]})
                        d.invoice_no = a.other_ref
                        d.po_no = a.po_no
                        if charge_dict1.get(s_head_id):
                            charge_dict1[s_head_id].append(d)
                        else:
                            charge_dict1.update({s_head_id:[d]})
                        a.status = 'complete'
                        a.msn_id = s_head_id
                        a.msn_ref = s_head_ref
                        DBSession.merge(a)
                        DBSession.flush()
                        break
                        
            erro.update({curcount:curerro})
            if a.status == "uncomplete":
                if len(erro) > 0:
                    merror = max(erro.iteritems(),key=lambda x:x)
                    values = ",".join(merror[1])
                    a.error = values
                    DBSession.merge(a)
                    
        for k, v in charge_dict1.iteritems():
            if v and len(v) > 0:
                shArgs = {
                          's_head_id': k,
                          'head_type':const.CHARGE_TYPE_S_PI,
                          'd_charge_dict':d_charge_dict
                          }
                PCharge.create(const.CHARGE_TYPE_S_PI, v, ** shArgs)
        
        d_charge_dict = {}

        for a in other_charge_list:
            if not category_dict.get(category):
                pidetail = PiDetail.find_s_head_id_by_category(category)
                if not pidetail:
                    phead_by_supplier = PHead.get_supplier(a.supplier_code)
                    if not phead_by_supplier:
                        continue
                    s_head = SHead.create(user=request.identity["user"], **{
                                                                              'type':const.CHARGE_TYPE_S_PRI,
                                                                              'phead':phead_by_supplier
                                                                            })
                    s_head.dzd = st_head.ref
                    DBSession.merge(s_head)
                    DBSession.flush()
                    status_dict = {
                       "ids":str(s_head.id),
                       "status":const.VAT_CHEAD_STATUS_POST
                       }
                    SHead.update_all_status(user=request.identity["user"], ** status_dict)
                else:
                    s_head = pidetail.s_head
                category_dict.update({category:{"s_head_id":s_head.id,"ref":s_head.ref}})
            uis = UI.find(None, a.supplier_code, a.note_type)
            for b in uis:
                uicharges = UICharge.find_details_by_note_no(b.note_no)
                for c in uicharges:
                    if (c.chg_discount_code == a.item_code or c.chg_discount_code in a.item_code or a.item_code in c.chg_discount_code)\
                    and "%.2f" %  a.amount == "%.2f" % c.total:
                        if a.note_type == 'C':
                            amount = a.amount
                        if a.note_type == 'D':
                            amount = -a.amount
                        d_charge = {
                                    'id':a.id,
                                    'charge_code': c.chg_discount_code,
                                    'line_no':c.line_no, 
                                    'amount': amount,
                                    'note_no':b.note_no,
                                    'currency':a.currency
                                    }
                        if d_charge_dict.get(b.note_no):
                            d_charge_dict[b.note_no].append(d_charge)
                        else:
                            d_charge_dict.update({b.note_no:[d_charge]})
                        s_head     = category_dict.get(category)
                        s_head_id  = s_head.get('s_head_id') if s_head else None
                        s_head_ref = s_head.get('ref') if s_head else None
                        if not s_head_id:continue
                        c.vat_total = a.base_amount
                        if other_charge_dict.get(s_head_id):
                            other_charge_dict[s_head_id].append(c)
                        else:
                            other_charge_dict.update({s_head_id:[c]})
                        a.status  = 'complete'
                        a.msn_id  = s_head_id
                        a.msn_ref = s_head_ref
                        DBSession.merge(a)
                        DBSession.flush()
                        break
                                           
        for k, v in other_charge_dict.iteritems():
            if v and len(v) > 0:
                shArgs = {
                          's_head_id': k,
                          'head_type':const.CHARGE_TYPE_P_ERP,
                          'd_charge_dict':d_charge_dict
                          }
                PCharge.create(const.CHARGE_TYPE_S_ERP, v, ** shArgs)
     
        st_head_status = 'complete'
        dn_details = st_head.dn_details
        st_details = st_head.st_details
        for g in chain(dn_details, st_details):
            if g.status == 'uncomplete':
                st_head_status = 'uncomplete'
                break
        st_head.status = st_head_status
        DBSession.merge(st_head)
        DBSession.flush()
           
    @classmethod      
    def update_invoice(self, item_obj):
        po_no = item_obj.po_no
        pids = PID.find_details_by_po_no(po_no)
        if len(pids)>0:
            qty_dict = {}
            for c in pids:
                if item_obj.item_code == c.item_no and "%.3f"  % Decimal(item_obj.rmb_unit) == "%.3f" % c.unit_price: 
                    if qty_dict.get(item_obj.item_code):
                        qty_dict[item_obj.item_code] += c.qty
                    else: qty_dict.update({item_obj.item_code : c.qty})                                    
            for d in pids:
                if item_obj.item_code == d.item_no and "%.3f" % Decimal(item_obj.rmb_unit) == "%.3f" % d.unit_price and pi(item_obj.qty) == pi(d.qty):
                    ItemDesc.save(** {'code':d.supplier, 'item_no':item_obj.item_code, 'description':item_obj.desc_zh})
                    item_obj.invoice_no = d.purchase_invoice_no
                    DBSession.merge(item_obj)
                    st_head_status = 'complete'
                    st_head = item_obj.st_head
                    for g in st_head.st_details:
                        if g.status == 'uncomplete':
                            st_head_status = 'uncomplete'
                            break
                    st_head.status = st_head_status 
                    DBSession.merge(st_head)
                    DBSession.flush()
                       
    @classmethod
    def search_query(cls, cid, ctype , ** args):
        filed = {
                 "supplier_code": args.get("supplier_code"),
                 "invoice_no": args.get("invoice_no"),
                 "billing_month": args.get("billing_month"),
                 "kingdee_date": args.get("kingdee_date"),
                 "reconciliation_lot": args.get("reconciliation_lot"),
                 "payment_date": args.get("payment_date"),
                 "number": args.get("number"),
                 "msn_ref": args.get("msn_ref"),
                 "mpi_ref": args.get("mpi_ref"),
                 'status': args.get('status')
                 }
        if ctype == const.ERP_HEAD_TYPE_ST:
            db   = STDetail
            data = STDetail.find_detail_order_by(cid)
        else:
            db   = DNDetail
            data = DNDetail.find_detail_order_by(cid)
        for k, v in filed.iteritems():
            if v and hasattr(db, k) and args.get("type") == ctype:
                v = v.strip()
                if v:
                    data = data.filter(getattr(db, k) == v)
        return data
                
    def find_pi_amount(self, piDetails = None):
        amount = 0
        if not piDetails:
           piDetails = self.st_details
        for i in piDetails:
            amount += i.item_amount
        return amount
    
    def find_dn_amount(self, dnDetails = None):
        d_amount = 0
        c_amount = 0
        if not dnDetails:
            dnDetails = self.dn_details
        for i in dnDetails:
            if i.note_type == "D":
               d_amount +=  i.amount
            else:
               c_amount +=  i.amount
        return d_amount - c_amount
 
class STDetail(Table_STDetail):
    
    @classmethod
    def find_detail(cls, args):
        query = DBSession.query(cls).filter(cls.active == 0)
        type = 0
        if args.get('po_no'): 
            type  = 1
            query = query.filter(cls.po_no == args.get('po_no'))
        if args.get('item_code'):
            type  = 1
            query = query.filter(cls.item_code == args.get('item_code'))
        if args.get('qty'):
            type  = 1
            query = query.filter(cls.qty == args.get('qty'))
        if args.get('unit'):
            type  = 1
            query = query.filter(cls.unit == args.get('unit'))
        if args.get('status'):
            type  = 1
            query = query.filter(cls.status == args.get('status'))
        if args.get('st_head_id'):
            type  = 1
            query = query.filter(cls.st_head_id == args.get('st_head_id'))
        if args.get('reconciliation_lot'):
            type  = 1
            query = query.filter(cls.reconciliation_lot == args.get('reconciliation_lot'))
        results =  query.all() if type == 1 else []
        return results
    
    @classmethod
    def find_detail_order_by(cls, id):
        return DBSession.query(cls).filter(cls.st_head_id == id).filter(cls.active == 0).order_by(asc(cls.id))
    
    @classmethod
    def find_sthead(cls,args):
        result = []
        st_details = cls.find_detail(args)
        for a in st_details:
            result.append(a.st_head.id)
        return list(set(result))

    @classmethod
    def find_details_by_status(cls, st_head_id, status = None, invoice_no = None, charge_code = None):
        data = DBSession.query(cls).filter(cls.st_head_id == st_head_id).filter(cls.active == 0)
        if status: data = data.filter(cls.status == status)
        if invoice_no: data = data.filter(cls.invoice_no == invoice_no)
        if charge_code: data = data.filter(cls.charge_code == charge_code)
        return data
    
    @classmethod
    def find_details_by_inovice(cls, invoice_no , charge_code = None, status = None, line_no = None):
        data = DBSession.query(cls).filter(cls.invoice_no == invoice_no).filter(cls.active == 0)
        if status: data = data.filter(cls.status == status)
        if charge_code: data = data.filter(cls.item_code == charge_code)
        if line_no: data = data.filter(cls.pi_line_no == line_no)
        return data
    
class DNDetail(Table_DNDetail):
    
    @classmethod
    def find_detail(cls, stock_adjustment_no= None, po_no = None, other_ref = None, supplier_code = None):
        data =  DBSession.query(cls).filter(cls.active == 0)
        if stock_adjustment_no:
            data = data.filter(cls.stock_adjustment_no == stock_adjustment_no)
        if po_no:
            data = data.filter(cls.po_no == po_no)
        if other_ref:
            data = data.filter(cls.other_ref == other_ref)
        if supplier_code:
            data = data.filter(cls.supplier_code == supplier_code)
        return data
    
    @classmethod
    def find_detail_order_by(cls, id):
        return DBSession.query(cls).filter(cls.st_head_id == id).filter(cls.active == 0).order_by(asc(cls.id))
        
    @classmethod
    def find_details_by_status(cls, st_head_id, status = None):
        data = DBSession.query(cls).filter(cls.st_head_id == st_head_id).filter(cls.active == 0)
        if status: data = data.filter(cls.status == status)
        return data
    
    @classmethod
    def find_detail_by_keys(cls, args):
        query = DBSession.query(cls).filter(cls.active == 0)
        type = 0
        if args.get('po_no'): 
            type  = 1
            query = query.filter(cls.po_no == args.get('po_no'))
        if args.get('item_code'):
            type  = 1
            query = query.filter(cls.item_code == args.get('item_code'))
        if args.get('order_qty'):
            type  = 1
            query = query.filter(cls.qty == args.get('order_qty'))
        if args.get('unit'):
            type  = 1
            query = query.filter(cls.unit == args.get('unit'))
        if args.get('status'):
            type  = 1
            query = query.filter(cls.status == args.get('status'))
        if args.get('st_head_id'):
            type  = 1
            query = query.filter(cls.st_head_id == args.get('st_head_id'))
        if args.get('reconciliation_lot'):
            type  = 1
            query = query.filter(cls.reconciliation_lot == args.get('reconciliation_lot'))
        results =  query.all() if type == 1 else []
        return results
    
    @classmethod
    def find_sthead(cls,args):
        result = []
        st_details = cls.find_detail_by_keys(args)
        for a in st_details:
            result.append(a.st_head.id)
        return list(set(result))
     
class OHead(Table_OHead):
    
    @classmethod
    def find(cls, category = None, ** args):
        ids = [0]
        page, limit, cate = 25, 0, 'next'
        item_code, invoice_no, sales_contract_no, vat_no, status, create_by_id= (args.get(i, '').strip() for i in ('item_code', 'invoice_no', 'sales_contract_no', 'vat_no', 'status', 'create_by'))
        if item_code:
            ids.extend(CoDetail.get_ohead_ids(item_code))
        if sales_contract_no or invoice_no:
            ids.extend(CoHead.get_ohead_ids(invoice_no, sales_contract_no))
        if args.get('create_by_id'):
            users =  cls.user_name_id(args['create_by_id'])
            if len(users)>0:
                args['create_by_id'] = users[0].user_id
            else:
                return []
        if len(ids) > 1: args['ids'] = list(set(ids))
        arr_not_null = []
        if vat_no: arr_not_null.append('vat_no')
        params = {
            const.QUERY_TYPE_LIKE: ['ref', 'customer_code'],
            const.QUERY_TYPE_LIKE_AND_OR: [('customer_name', 'customer_name', 'customer_short_name')],
            const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
            const.QUERY_TYPE_IN: [('id', 'ids')],
            const.QUERY_TYPE_EQ: ['status'],
            const.QUERY_TYPE_ORDER_BY: ['create_time'],
            const.QUERY_TYPE_CREATE_BY: ['create_by_id'],
            const.QUERY_TYPE_COMPANY_CODE: ['company_code'],
            const.QUERY_TYPE_NOT_NULL: arr_not_null
        }
        queryExtend = QueryExtend(cls, ** args)
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit")) 
            offset = int(args.get("offset"))
        if category:offset = None   
        queryExtend.query_all(True, DBSession, True, limit, offset, ** params)
        if vat_no:
            results = []
            for i in queryExtend.result:
                for j in i.vat_no.split(','):
                    if len(j.split('~')) == 1 and vat_no == j:
                        results.append(i)
                        break
                    elif len(j.split('~')) == 2:
                        kk = j.split('~')
                        if int(kk[0]) <= int(vat_no) and int(kk[1]) >= int(vat_no):
                            results.append(i)
                            break
            if category:
                return results
            else:
                return results, offset, limit
        else:
            if category:
                return queryExtend.result
            else:
                return queryExtend.result, offset, limit
        
    @classmethod
    def create(cls, ** args):
        mCRef = CRef()
        ids, customer_code, head_type  = (args.get(i, '') for i in ('ids', 'customer_code', 'head_type'))
        ref = 'CST'
        max = mCRef.get(ref) 
        customer = Customer.get(customer_code)
        params = {
            'head_type':head_type,
            'customer_code':customer.cust_code,
            'customer_name':customer.cust_name,
            'customer_short_name':customer.cust_short_name,
            'status':const.VAT_THEAD_STATUS_NEW,
            'company_code':getCompanyCode()[0],
            'ref':'%s%s' % (ref, max),
        }
        ohead = OHead( ** params)
        DBSession.add(ohead)
        DBSession.flush()
        if ids:
            for id in ids.split(','):
                shArgs = {'o_head_id': ohead.id}
                id = id.split('$')[0]
                thead = THead.get(id)
                thead.o_head_id = ohead.id
                c_heads = thead.c_heads
                for c_head in c_heads:
                    c_head.o_head_id = ohead.id
                    DBSession.merge(c_head)
                if thead.head_type == const.ERP_HEAD_TYPE_SO:
                    for so in thead.so_heads:
                        coHead = CoHead.create(so, ** shArgs)
                        shArgs.update({'co_head_id':coHead.id})
                        CoDetail.create(so.so_details, ** shArgs)
                        CpDetail.create(coHead.co_details, ** shArgs)
                elif thead.head_type == const.ERP_HEAD_TYPE_SI:
                    for si in thead.si_heads:
                        coHead = CoHead.create(si, ** shArgs)
                        shArgs.update({'co_head_id':coHead.id})
                        CoDetail.create(si.si_details, ** shArgs)
                        CpDetail.create(coHead.co_details, ** shArgs)
                ohead.vat_no = thead.vat_no
                ohead.vat_date = thead.vat_date
                ohead.head_type = thead.head_type
                ohead.thead_ref = thead.ref
                ohead.thead_id = thead.id
                DBSession.merge(ohead)
                DBSession.merge(thead)
                DBSession.flush()
        return ohead
    
    def update_details(self, ** args):
        remarks = []
        type = args.get('type')
        head_type = args.get('head_type')
        head = OHead.get(args.get('id'))
        codetails = head.co_details
        for codetail in codetails:
            cpdetails = codetail.cp_details
            for cpdetail in cpdetails:
                if type == 'Delete':
                    if args.get("checkbox_%s" % cpdetail.id):
                        DBSession.delete(cpdetail)
                        remarks.append("Item Line NO%s PO %s Line NO %s" % (codetail.line_no, cpdetail.po_no, cpdetail.line_no))
                else:
                    qty = args.get('qty_%s' % cpdetail.id)
                    remark = args.get('remark_%s' % cpdetail.id)
                    unit_price = args.get('price_%s' % cpdetail.id)
                    if qty  and unit_price:
                        mg = merge(
                               [cpdetail.remark, str(cpdetail.unit_price), str(cpdetail.pi_qty), cpdetail.line_no],
                               [remark,  unit_price, qty],
                               ['Remark', 'Unit Price', 'Qty', 'Line NO']
                               )
                        if mg: remarks.append(mg)
                        cpdetail.pi_qty = qty
                        cpdetail.unit_price = unit_price
                        cpdetail.pi_total = pf(float(qty) * float(unit_price))
                        DBSession.merge(cpdetail)
        if type == 'Delete':
            remark_head = "Delete item "
        else:
            remark_head = "Update item "
        return remark_head + ",".join(remarks) if len(remarks)>0 else None  
    
    @classmethod
    def update_all_status(cls, ** args):
        (status, ids) = (args.get(i, '') for i in ('status', 'ids'))
        oheads = cls.find_by_ids(ids)
        for i in oheads:
            i.remark = args.get("remark-%s" % i.id)
            i.status = status
            if status == const.VAT_THEAD_STATUS_CANCELLED:
                i.active = 1
                for j in i.cp_charges:
                    j.active = 1
                    DBSession.merge(j)
                for q in i.co_heads:
                    q.active = 1
                    DBSession.merge(q)
                for j in i.co_details:
                    j.active = 1
                    for k in j.cp_details:
                        Period.update_pi_flag(k.pi_no, k.item_no, k.po_no)
                        k.active = 1
                        DBSession.merge(k)
                    DBSession.merge(j)
                for j in i.charges:
                    j.active = 1
                    DBSession.merge(j)
                tHeads = i.t_heads
                for a in tHeads:
                    a.o_head_id = None
                    DBSession.merge(a)
                for z in i.charges:
                    z.status = status
                    DBSession.merge(z)
            DBSession.merge(i)
            DBSession.flush()

    @classmethod
    def update_all_vat_info(cls, ** args):
        vat_no, vat_date, ids = (args.get(i, '').strip() for i in ('vat_no', 'vat_date', 'ids'))
        oheads = cls.find_by_ids(ids)
        for i in oheads:
            i.vat_no = vat_no
            i.vat_date = dt.strptime('%s00:00:00' % vat_date, "%Y-%m-%d%H:%M:%S")
            DBSession.merge(i)
            DBSession.flush()
    
    @classmethod
    def find_po_no_by_so(cls, so, item_code, line_no):
        sql = '''
            SELECT DISTINCT GRN.PURCHASE_ORDER_NO, GRN.GRN_NO,GRN.LINE_NO GRN_Line_No, GRN.ITEM_NO, GRN.PO_LINE_NO, tsr.ITEM_NO, tscp.ITEM_LINE_NO, tsr.LOT_NO, tsr.RESERVE_QTY
             FROM t_stock_reserve tsr, t_grn_dtl grn,T_SALES_CONTRACT_PACKSET tscp  
          WHERE tscp.SALES_CONTRACT_NO='%s' AND tscp.SET_ITEM_NO='%s'
          AND tscp.ITEM_LINE_NO=%s
          AND tscp.SALES_CONTRACT_NO=tsr.DOCUMENT_NO
          AND tscp.LINE_NO=tsr.DOCUMENT_LINE_NO
          AND tscp.ITEM_CODE=tsr.ITEM_NO
          AND tsr.RESERVE_QTY<>0
          AND tsr.LOT_NO = grn.LOT_NO(+)
          AND tsr.ITEM_NO=grn.ITEM_NO(+)
          ORDER BY GRN_Line_No DESC
        ''' % (so, item_code, line_no)
        return DBSession2.execute(sql).fetchall()
    
    @classmethod
    def find_po_by_so(cls, po_no):
        return POD.find_details(po_no[0])
    
    @classmethod
    def find_po_charge_by_so(cls, po_no):
        return POCharge.find_details_by_all(po_no[0])

    @classmethod
    def find_pi_by_so(cls, po_no):
        result = {}
        pidetails =  PID.find_details_by_po_no(po_no[0])
        for pidetail in pidetails:
            if result.get(pidetail.purchase_invoice_no):
                result[pidetail.purchase_invoice_no].append(pidetail)
            else:
                result.update({pidetail.purchase_invoice_no:[pidetail]})
        return result
    
    @classmethod
    def find_pi_charge_by_so(cls, po_no):
        result = {}
        picharges = PICharge.find_details_by_po_no(po_no[0])
        for picharge in picharges:
            if result.get(picharge.purchase_invoice_no):
                result[picharge.purchase_invoice_no].append(picharge)
            else:
                result.update({picharge.purchase_invoice_no:[picharge]})
        return result

    @classmethod
    def auto_complete(cls, DB, db_dict, type, q):
        result = []
        for k, v in db_dict.iteritems():
            if type in v:
                if type == 'note_no' and k == 't_supl_note_charges':
                    DB = DBSession2
                if type == 'item_code' and  k in ['vat_si_detail', 'vat_so_detail']: 
                    type = 'item_no'
                if DB == DBSession2:
                    if type == 'item_code' and  k == 't_purchase_invoice_dtl': 
                        type = 'item_no'
                    sql = "SELECT distinct %s FROM %s where COMPANY_CODE in %s AND %s LIKE '%s' AND ROWNUM<=10 " % (type, k, getCompanyCode(1),type,q.upper()+'%')
                else:
                    if type in ['qty', 'unit']:
                        sql = "SELECT distinct %s FROM %s where  CAST(%s AS TEXT) LIKE '%s' limit 10 offset 0 " % (type, k, type, q.upper()+'%')
                    else:
                        sql = "SELECT distinct %s FROM %s where %s LIKE '%s' limit 10 offset 0 " % (type, k, type, q.upper()+'%')     
                rrs = DB.execute(sql).fetchall()
                for rr in rrs:
                    if not rr in result:
                        result.append(rr)
        return result 
    
     
    def find_charges(self): 
        result = []
        charges = self.charges
        for charge in charges:
            type = const.ERP_HEAD_TYPE_CST
            if charge.n_head_id:
                type = const.ERP_HEAD_TYPE_CCN
            all_charges = OCharge.find_details_by_type(charge, type)
            cst_total = 0
            for a in all_charges:
                if charge.o_head.status == const.VAT_THEAD_STATUS_NEW:
                    if charge.id != a.id:
                        cst_total += a.vat_total
                else:
                    cst_total += a.vat_total
            charge.cst_total = cst_total
            charge.ava_total = charge.total - cst_total
            result.append(charge)
        return result
    
    def update_charges(self, ** args):
        type = args.get('type')
        ohead = OHead.get(args.get('id'))
        cpcharges = ohead.cp_charges
        remarks = []
        if type == 'Save':
            for cpcharge in cpcharges:
                po_total = args.get('po_total_%s' % cpcharge.id)
                total = args.get('total_%s' % cpcharge.id)
                mg = merge(
                       [str(cpcharge.po_total), str(cpcharge.total), cpcharge.line_no],
                       [po_total, total],
                       ['PO total', 'PI total', 'Line NO']
                       )
                if total:
                    cpcharge.total = total
                if po_total:
                    cpcharge.po_total = po_total
                DBSession.merge(cpcharge)
                if mg: remarks.append(mg)
            return "Update Charge " + ",".join(remarks) if len(remarks)>0 else None  
        else:
            for cpcharge in cpcharges:
                check = args.get('check_%s' % cpcharge.id)
                if check:
                    DBSession.delete(cpcharge)
                    remarks.append("PO %s Line NO %s" % (cpcharge.po_no, cpcharge.line_no))
            return "Delete Charge " + ",".join(remarks) if len(remarks)>0 else None 
                                 
    @classmethod
    def get_ohead_by_thead(cls, thead):
        return DBSession.query(cls).filter(cls.thead_id == thead).filter(cls.active == 0).all()
    
    @classmethod
    def check_po_by_so(cls, ** args):
        ids = args.get('ids').split(',')
        if len(ids) > 0:
            for id in ids:
                id = id.split('$')[0]
                thead = THead.get(id)
                if thead.head_type == const.ERP_HEAD_TYPE_SO:
                    for so in thead.so_heads:
                        if not cls.chekck_po(so.so_details):
                            return None
                elif thead.head_type == const.ERP_HEAD_TYPE_SI:
                    for si in thead.si_heads:
                        if not cls.chekck_po(si.si_details):
                            return None
        return True
    
    @classmethod                    
    def chekck_po(cls, details):       
        for detail in details:
            if hasattr(detail, 'sc_no'):
                detail.sales_contract_no = detail.sc_no
                po_nos = OHead.find_po_no_by_so(detail.sales_contract_no, detail.item_no, detail.sc_item_line_no)
            else:
                po_nos = OHead.find_po_no_by_so(detail.sales_contract_no, detail.item_no, detail.line_no)
            if len(po_nos) == 0:
                return None
            else:
                return po_nos
    
    
    @classmethod
    def find_detail_charge_by_date(cls, date_from = None, date_to = None, item_code = None):
        static_count = 10
        result = []
        if date_from:
            year_date_from = dt.strptime("%s-01-0100:00:00" % date_from.year, "%Y-%m-%d%H:%M:%S")
        data_query = DBSession.query(cls).filter(cls.active == 0).filter(cls.company_code.in_(getCompanyCode()))
        if date_from:
            data_query = data_query.filter(cls.vat_date >= year_date_from).filter(cls.vat_date <= date_to)
        data_query = data_query.order_by(asc(cls.id))
        oheads = data_query.all()
        is_post = []
        for ohead in oheads:
            if not date_to or (ohead.vat_date.year <= date_to.year and ohead.vat_date.month <= date_to.month):
                for co_detail in ohead.co_details:
                    so_qty = co_detail.qty
                    cpdetails = co_detail.cp_details
                    for cp_detail in cpdetails:
                        cn = []
                        if item_code and cp_detail.item_no != item_code:continue
                        msn_cp_details = CpDetail.find_related_mcn(cp_detail)
                        msn_qty = 0
                        for m in msn_cp_details:
                            if m.active == 0 and m.n_head.active == 0:
                                ref = m.n_head.chead_ref
                                chead = CHead.find_chead_by_ref(ref)
                                if chead.thead_ref == ohead.thead_ref:
                                    msn_qty += m.po_qty
                                    cn.append({
                                               'date_time':chead.vat_date if chead.vat_date else None, 
                                               'qty':-m.po_qty
                                               })        
                        if cp_detail.po_qty - msn_qty >= 0:
                            cp_detail.head_type = const.SEARCH_TYPE_CST
                            cp_detail.vat_date = ohead.vat_date
                            cp_detail.cn = cn
                            cp_detail.cn_qty = msn_qty
                            cp_detail.date_time = ohead.vat_date
                            cp_detail.customer  = ohead.customer_code
                            cp_detail.curr_qty  =  - cp_detail.po_qty
                            cp_detail.base_curr_qty = -(cp_detail.po_qty - msn_qty)
                            cp_detail.amount = cp_detail.curr_qty * cp_detail.unit_price
                            cp_detail.so_no = cp_detail.sales_contract_no
                            if ohead.id not in is_post:
                                is_post.append(ohead.id)
                            result.append(cp_detail)
            
            for cp_charge in ohead.cp_charges:
                if ohead.id not in is_post:
                    continue
                cp_charge.head_type = const.SEARCH_TYPE_CHARGE
                cp_charge.date_time  = ohead.vat_date
                cp_charge.vat_date = ohead.vat_date
                cp_charge.customer   = ohead.customer_code
                cp_charge.unit_price = ''
                cp_charge.date_time = ohead.vat_date
                cp_charge.qty = None
                cp_charge.cn = []
                cp_charge.curr_qty = None
                cp_charge.so_no = cp_charge.so_no
                cp_charge.item_no = cp_charge.charge_code
                cp_charge.amount =  -cp_charge.po_total
                result.append(cp_charge)
        return result
    
    @classmethod
    def invoice_with_cost(cls, date_from = None, date_to = None, item_code = None):
        rs, lost = [], {}
        flag = 0
        details = cls.find_detail_charge_by_date(None, None, None)
        for detail in details:
            detail.billing_month = None
            if detail.__tablename__ == 'vat_cp_detail':
                cpdetail_qtys = []
                key = "%s_%s_%s" % (detail.pi_no, detail.item_no, detail.line_no)
                detail.curr_qty += detail.cn_qty
                if detail.pi_no:
                    pidetails = PiDetail.parse_details(detail.pi_no, None, detail.item_no, detail.line_no, None, None, \
                                                                detail.po_no, detail.po_line_no, flag)
                    cpdetails = CpDetail.parse_details(detail.po_no, detail.pi_no, detail.item_no, detail.line_no, flag)
                    
                    picosts  = PICost.find(detail.pi_no, detail.item_no)
                    dncosts  = DNCost.find(detail.pi_no, detail.item_no)
                    
                    piproceeds = PIProceeds.find(detail.pi_no, detail.item_no)
                    dnproceeds = DNProceeds.find(None, detail.pi_no, detail.item_no)
                    piproceed_qty = 0
                    for piproceed in piproceeds:
                        piproceed_qty += piproceed.qty
                    for dnproceed in dnproceeds:
                        piproceed_qty -= dnproceed.order_qty
                    
                    cost_qty, picost_qty, dncost_qty = 0, 0, 0
                    for picost in picosts:
                        picost_qty += picost.qty
                    for dncost in dncosts:
                        dncost_qty += dncost.order_qty
                    cost_qty = picost_qty - dncost_qty
        
                    cp_qty = 0
                    for cpdetail in cpdetails:
                        cpdetail_qtys.append({'id':cpdetail.id, 'qty':cpdetail.curr_qty})
                        cp_qty += cpdetail.curr_qty
                    g = lambda x:x['id']
                    cpdetail_qtys = sorted(cpdetail_qtys, key = g)
                    pi_qty = 0
                    for pidetail in pidetails:
                        pi_qty += pidetail.curr_qty
                        st_detail = pidetail.st_detail
                        
                    cp_qty = cp_qty + cost_qty
                    pi_qty = pi_qty +  piproceed_qty
                    print key, cp_qty, pi_qty
                    if cp_qty == pi_qty:
                        for pidetail in pidetails:
                            pidetail.flag = 1
                            DBSession.merge(pidetail)
                        for cpdetail in cpdetails:
                            cpdetail.flag = 1
                            DBSession.merge(cpdetail)
                            
                    elif cp_qty > pi_qty:
                        for i in cpdetail_qtys:
                            pi_qty -= i['qty']
                            if pi_qty < 0:
                                if i['id'] == detail.id:
                                    lost.update({key:pi_qty})
                                    detail.curr_qty = -pi_qty
                                    detail.base_curr_qty = -pi_qty
                                    detail.amount = pf(detail.base_curr_qty * detail.unit_price)
                                    rs.append(detail)
                                    break
                                pi_qty = 0
                else:
                    detail.base_curr_qty = -detail.curr_qty
                    detail.amount = pf(detail.curr_qty * detail.unit_price)
                    rs.append(detail)
            else:
                pcharges = PCharge.find_details(None, const.CHARGE_TYPE_P_PI, detail.line_no, None, None, None, None, \
                                                        detail.charge_code, detail.note_no)
                charge_total = 0
                for pcharge in pcharges:
                    msn_total = 0
                    msn_details = PCharge.find_details(pcharge.invoice_no,const.CHARGE_TYPE_S_PI, pcharge.line_no, None, None, pcharge.uuid, pcharge.uuid2)
                    for msn_detail in msn_details:
                        msn_total += pn(msn_detail.vat_total)
                    charge_total += pcharge.total
                    charge_total -= msn_total
                    st_detail = pcharge.st_detail
                    detail.billing_month = st_detail.billing_month
                if detail.total > charge_total:
                    detail.base_curr_qty = 0
                    detail.total = detail.total - charge_total
                    rs.append(detail)
        return rs
    
    
    @classmethod
    def find_invoice_without_cost(cls, date_from = None, date_to = None, item_code = None):
        rs, lost = [], {}
        flag = 0
        pidetail_cn, cpdetail_cn = [], []
        details = PHead.find_detail_charge_by_date(None, None, None)
        for detail in details:
            if detail.__tablename__ == 'vat_pi_detail':
                key = "%s_%s_%s_%s" % (detail.invoice_no, detail.head_type, detail.item_no, detail.line_no)
                qty, pi_qty, pidetail_qtys = 0, 0, []
                detail.curr_vat_date = None
                pidetails = PiDetail.parse_details(detail.invoice_no, None, detail.item_no, detail.line_no, None, None, None, flag)
                cpdetails = CpDetail.parse_details(detail.po_no, detail.invoice_no, detail.item_no, detail.line_no, flag)
                
                piproceeds = PIProceeds.find(detail.invoice_no, detail.item_no)
                dnproceeds = DNProceeds.find(detail.po_no, detail.invoice_no, detail.item_no)
                proceed_qty, piproceed_qty, dnproceed_qty = 0, 0, 0
                for piproceed in piproceeds:
                    piproceed_qty += piproceed.qty
                for dnproceed in dnproceeds:
                    dnproceed_qty += dnproceed.order_qty
                proceed_qty = piproceed_qty - dnproceed_qty
                
                picosts  = PICost.find(detail.invoice_no, detail.item_no)
                dncosts  = DNCost.find(detail.invoice_no, detail.item_no)
                    
                cost_qty, picost_qty, dncost_qty = 0, 0, 0
                for picost in picosts:
                    picost_qty += picost.qty
                for dncost in dncosts:
                    dncost_qty += dncost.order_qty
                cost_qty = picost_qty - dncost_qty
                
                for pidetail in pidetails:
                    pidetail_qtys.append({'id':pidetail.id, 'qty':pidetail.curr_qty})
                    pi_qty += pidetail.curr_qty
                g = lambda x:x['id']
                pidetail_qtys = sorted(pidetail_qtys, key = g)
                for cpdetail in cpdetails:
                    if not detail.so_no:
                        detail.so_no = cpdetail.co_detail.sales_contract_no
                    if cpdetail.o_head:
                        detail.curr_vat_date = cpdetail.o_head.vat_date
                    if cpdetail.co_detail.o_head_id:
                        qty += cpdetail.curr_qty
                        
                qty +=  cost_qty
                pi_qty += proceed_qty
                print key, pi_qty, qty
                if pi_qty == qty:
                    for pidetail in pidetails:
                        pidetail.flag = 1
                        DBSession.merge(pidetail)
                    for cpdetail in cpdetails:
                        cpdetail.flag = 1
                        DBSession.merge(cpdetail)
                        
                elif pi_qty > qty:
                    for i in pidetail_qtys:
                        qty -= i['qty']
                        if qty < 0:
                            if i['id'] == detail.id:
                                detail.base_curr_qty = -qty
                                detail.amount = pf(detail.base_curr_qty * detail.unit_price)
                                rs.append(detail)
                                break
                            qty = 0
        return rs
    
            
class NHead(Table_NHead):
    
    @classmethod
    def find(cls, category=None, ** args):
        ids = [0]
        page, limit, cate = 25, 0, 'next'
        item_code, invoice_no, sales_contract_no, vat_no, status, create_by_id = \
                    (args.get(i, '').strip() for i in ('item_code', 'invoice_no', 'sales_contract_no', 'vat_no', 'status', 'create_by_id'))
        if item_code:
            ids.extend(CoDetail.get_nhead_ids(item_code))
        if sales_contract_no or invoice_no:
            ids.extend(CoHead.get_nhead_ids(invoice_no, sales_contract_no))
        if args.get('create_by_id'):
            users =  cls.user_name_id(args['create_by_id'])
            if len(users)>0:
                args['create_by_id'] = users[0].user_id
            else:
                return []
        if len(ids) > 1: args['ids'] = list(set(ids))
        arr_not_null = []
        if vat_no: arr_not_null.append('vat_no')
        
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit")) 
            offset = int(args.get("offset"))
        
        if category:offset = None
        params = {
            const.QUERY_TYPE_LIKE: ['thead_ref', 'ref', 'customer_code'],
            const.QUERY_TYPE_LIKE_AND_OR: [('customer_name', 'customer_name', 'customer_short_name')],
            const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
            const.QUERY_TYPE_IN: [('id', 'ids')],
            const.QUERY_TYPE_EQ: ['status'],
            const.QUERY_TYPE_ORDER_BY: ['create_time'],
            const.QUERY_TYPE_CREATE_BY: ['create_by_id'],
            const.QUERY_TYPE_COMPANY_CODE: ['company_code'],
            const.QUERY_TYPE_NOT_NULL: arr_not_null
        }
        queryExtend = QueryExtend(cls, ** args)
        queryExtend.query_all(True, DBSession, True, limit, offset, ** params)
        if vat_no:
            results = []
            for i in queryExtend.result:
                for j in i.vat_no.split(','):
                    if len(j.split('~')) == 1 and vat_no == j:
                        results.append(i)
                        break
                    elif len(j.split('~')) == 2:
                        kk = j.split('~')
                        if int(kk[0]) <= int(vat_no) and int(kk[1]) >= int(vat_no):
                            results.append(i)
                            break
            if category:            
                return results
            else:
                return results, offset, limit
        else:
            if category: 
                return queryExtend.result
            else:
                return queryExtend.result, offset, limit
            
    @classmethod
    def create(cls, ** args):
        mCRef = CRef()
        ids, customer_code, head_type  = (args.get(i, '') for i in ('ids', 'customer_code', 'head_type'))
        ref = 'CCN'
        max = mCRef.get(ref) 
        customer = Customer.get(customer_code)
        params = {
            'head_type':head_type,
            'customer_code':customer.cust_code,
            'customer_name':customer.cust_name,
            'customer_short_name':customer.cust_short_name,
            'status':const.VAT_THEAD_STATUS_NEW,
            'company_code':getCompanyCode()[0],
            'ref':'%s%s' % (ref, max),
        }
        nhead = NHead( ** params)
        DBSession.add(nhead)
        DBSession.flush()
        if ids:
            for id in ids.split(','):
                shArgs = {'n_head_id': nhead.id}
                if nhead.head_type == const.ERP_HEAD_TYPE_CCN:
                    id = id.split('$')[0]
                    chead = CHead.get(id)
                    chead.n_head_id = nhead.id
                    if chead.head_type == const.ERP_HEAD_TYPE_SO:
                        for so in chead.so_heads:
                            coHead = CoHead.create(so, ** shArgs)
                            shArgs.update({'co_head_id':coHead.id, 'o_head_id': chead.o_head_id})
                            codetails = CoDetail.create(so.so_details, ** shArgs)
                            CpDetail.create(codetails, ** shArgs)
                    elif chead.head_type == const.ERP_HEAD_TYPE_SI:
                        for si in chead.si_heads:
                            coHead = CoHead.create(si, ** shArgs)
                            shArgs.update({'co_head_id':coHead.id, 'o_head_id': chead.o_head_id})
                            codetails = CoDetail.create(si.si_details, ** shArgs)
                            CpDetail.create(codetails, ** shArgs)
                    nhead.head_type = chead.head_type
                    nhead.chead_ref = chead.ref
                    nhead.chead_id = chead.id
                    DBSession.merge(nhead)
                    DBSession.merge(chead)
                    DBSession.flush()
        return nhead
    
    @classmethod
    def update_all_status(cls, ** args):
        (status, ids) = (args.get(i, '') for i in ('status', 'ids'))
        nheads = cls.find_by_ids(ids)
        for i in nheads:
            i.remark = args.get("remark-%s" % i.id)
            i.status = status
            if status == const.VAT_THEAD_STATUS_CANCELLED:
                i.active = 1
                for q in i.co_heads:
                    q.active = 1
                    DBSession.merge(q)
                for j in i.co_details:
                    j.active = 1
                    DBSession.merge(j)
                    for k in j.cp_details:
                        Period.update_pi_flag(k.pi_no, k.item_no, k.po_no)
                        k.active = 1
                        DBSession.merge(k)
                for j in i.charges:
                    j.active = 1
                    DBSession.merge(j)
                for j in i.cp_charges:
                    j.active = 1
                    DBSession.merge(j)
                cHeads = i.c_heads
                for a in cHeads:
                    a.n_head_id = None
                    DBSession.merge(a)
            DBSession.merge(i)
    
    @classmethod
    def update_all_vat_info(cls, ** args):
        vat_no, vat_date, ids = (args.get(i, '').strip() for i in ('vat_no', 'vat_date', 'ids'))
        oheads = cls.find_by_ids(ids)
        for i in oheads:
            i.vat_no = vat_no
            i.vat_date = dt.strptime('%s00:00:00' % vat_date, "%Y-%m-%d%H:%M:%S")
            DBSession.merge(i)
     
    def update_details(self, ** args):
        remarks = []
        head_type = args.get('head_type')
        head = NHead.get(args.get('id'))
        codetails = head.co_details
        for codetail in codetails:
            cpdetails = codetail.cp_details
            for cpdetail in cpdetails:
                qty = args.get('qty_%s' % cpdetail.id)
                remark = args.get('remark_%s' % cpdetail.id)
                if qty:
                    mg = merge(
                           [cpdetail.remark, str(cpdetail.pi_qty), cpdetail.line_no],
                           [remark, qty],
                           ['Remark', 'Qty', 'Line NO']
                           )
                    cpdetail.pi_qty = qty
                    cpdetail.pi_total = pf(float(qty) * float(cpdetail.unit_price))
                    DBSession.merge(cpdetail)
                    if mg: remarks.append(mg)
        return ",".join(remarks) if len(remarks)>0 else None  
    
    def find_charges(self): 
        result = []
        charges = self.charges
        for charge in charges:
            type = const.ERP_HEAD_TYPE_CST
            if charge.n_head_id:
                type = const.ERP_HEAD_TYPE_CCN
            all_charges = OCharge.find_details_by_type(charge, type)
            cst_total = 0
            for a in all_charges:
                if charge.n_head.status == const.VAT_THEAD_STATUS_NEW:
                    if charge.id != a.id:
                        cst_total += a.vat_total
                else:
                    cst_total += a.vat_total
            charge.cst_total = cst_total
            charge.ava_total = charge.total - cst_total
            result.append(charge)
        return result 
         
    def update_charges(self, ** args):
        remarks = []
        type = args.get('type')
        nhead = NHead.get(args.get('id'))
        cpcharges = nhead.cp_charges
        if type == 'Save':
            for cpcharge in cpcharges:
                total = args.get('total_%s' % cpcharge.id)
                if total:
                    mg = merge(
                       [str(cpcharge.total), cpcharge.line_no],
                       [total],
                       ['PI total', 'Line NO']
                       )
                    cpcharge.total = total
                    DBSession.merge(cpcharge)
                    if mg: remarks.append(mg)
            return "Update Charge " + ",".join(remarks) if len(remarks)>0 else None  
        else:
            for cpcharge in cpcharges:
                check = args.get('check_%s' % cpcharge.id)
                if check:
                    DBSession.delete(cpcharge)
                    remarks.append("PO %s Line NO %s" % (cpcharge.po_no, cpcharge.line_no))
            return "Delete Charge " + ",".join(remarks) if len(remarks)>0 else None 
               
class CoHead(Table_CoHead):
    
    @classmethod
    def create(cls, so=None, ** args):
        if so.t_head_id:
            keys = ['o_head_id', 'company_code', 'order_dept', 'status',
                'currency', 'create_date','cust_po_no', 'order_amt', 'item_amt']
        elif so.c_head_id:
            keys = ['n_head_id', 'company_code', 'order_dept', 'status',
                'currency', 'create_date','cust_po_no', 'order_amt', 'item_amt']
        if hasattr(so, 'so_details'):
            keys.extend(['sales_contract_no', 
                         'ae',
                         'customer_code',
                         'customer_name'
                         ])
        else:
            keys.extend(['invoice_no',
                         ('sales_contract_no', 'sc_no'),
                         ('ae','department'), 
                         ('customer_code', 'customer'),
                         ('customer_name', 'customer_short_name')])
        params = _get_params_from_args_and_obj(keys, so, ** args)
        coHead = cls(** params)
        DBSession.add(coHead)
        DBSession.flush()
        return coHead
    
    def find_details(self, si_type = None):
        results = []
        if self.o_head_id:
            for i in self.co_details:
                i.mso_qty = 0
                i.mcn_qty = 0
                i.cn_qty = 0
                i.msn_qty = 0
                i.tax_rate =0
                i.include_tax = 0
                i.available_qty = 0
                results.append(i)
                
        elif self.n_head_id:
            for i in self.co_details:
                i.tax_rate =0
                i.include_tax = 0
                i.available_qty = 0
                results.append(i)
                
        results = sorted(results.__iter__(), key=lambda x:x.line_no)
        return results

    @classmethod
    def get_ohead_ids(cls, invoice_no = None, sales_contract_no = None):
        data = DBSession.query(distinct(cls.o_head_id))
        if invoice_no:
            data = data.filter(cls.invoice_no == invoice_no)
        if sales_contract_no:
            data = data.filter(cls.sales_contract_no == sales_contract_no)
        results = [i[0] for i in data]
        return results if results else [0]
    
    @classmethod
    def get_nhead_ids(cls, invoice_no = None, sales_contract_no = None):
        data = DBSession.query(distinct(cls.n_head_id))
        if invoice_no:
            data = data.filter(cls.invoice_no == invoice_no)
        if sales_contract_no:
            data = data.filter(cls.sales_contract_no == sales_contract_no)
        results = [i[0] for i in data]
        return results if results else [0]
    
    
class CoDetail(Table_CoDetail):
    
    @classmethod
    def find(cls, limit=0, offset=25):
        return DBSession.query(cls).filter(cls.active == 0)[limit:offset]
    
    @classmethod
    def create(cls, details, ** args):
        co_head_id = args.get('co_head_id')
        cohead = CoHead.get(co_head_id)
        result, pidetails, codetails = [], [], []
        for detail in details:
            if detail.vat_qty == 0:
                continue
            if hasattr(detail, 'so_head_id'):
                qtys = SoDetail.get_qty_mso_mcn(detail.sales_contract_no, detail.line_no, detail.item_no, detail.uuid)
            else:
                qtys = SiDetail.get_qty_mso_mcn(detail.invoice_no, detail.line_no, detail.item_no, detail.uuid)
            detail.v_qty = detail.vat_qty - qtys[2]
            result.append(detail)
            
        for rs in result:
            if rs.t_head_id:
                keys = ['o_head_id', 'po_no', 'co_head_id', 'qty',
                    'company_code', 'item_no', 'description', 'invoice_no',
                    'desc_zh', 'unit_price', 'unit', ('vat_qty', 'v_qty'),'uuid','pi_no']
            else:
                keys = ['n_head_id', 'po_no', 'co_head_id', 'qty',
                    'company_code', 'item_no', 'description', 'invoice_no',
                    'desc_zh', 'unit_price', 'unit', 'vat_qty','uuid','remark', 'pi_no']
            if hasattr(rs, 'so_head_id'):
                keys.extend(['line_no', 'sales_contract_no'])
            else:
                keys.extend([('line_no', 'sc_item_line_no'), ('sales_contract_no', 'sc_no')])
            params = _get_params_from_args_and_obj(keys, rs, ** args)
            coDetail = cls( ** params)
            DBSession.add(coDetail)
            codetails.append(coDetail)
        return codetails

    @classmethod
    def get_details(cls, sales_contract_no, line_no = None, item_no= None, uuid=None):
        data =  DBSession.query(cls).filter(cls.sales_contract_no == sales_contract_no).filter(cls.active == 0)
        if line_no: data = data.filter(cls.line_no == line_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if uuid: data = data.filter(cls.uuid == uuid)
        return data.all()
    
    @classmethod
    def getLikePo(cls, detail, podetails, po_qtys, po_no):
        result = []
        podetails = copy.deepcopy(podetails)
        itemcodes = ItemCode.find_dict(detail.item_no, detail.vat_qty)
        for podetail in podetails:
            if podetail.purchase_order_no != po_no[0] or podetail.line_no != po_no[4]:
                continue
            items = itemcodes.get(podetail.stock_item_no)
            if hasattr(detail, 'create_type') and detail.create_type == const.CREATE_NEW_PI:
                podetail.create_type = const.CREATE_NEW_PI
            if items:
                type = items.get('type')
                itemQty  = items.get('qty', 0) 
                itemIQty = items.get('item_qty', 0)
                detail.all_qty = items.get('all_qty', 0)
                if itemQty <= 0:
                    continue
                po_qty = 0
                key = "%s_%s" % (podetail.purchase_order_no, podetail.line_no)
                po_qtys = po_qtys.get(key, {})
                for k, v in po_qtys.iteritems():
                    if k != detail.id:
                        po_qty += v
                pi_qty = 0
                if hasattr(detail, 'po_key'):
                    for k, v in detail.po_key.iteritems():
                        pi_qty += v
                if detail.all_qty == pi_qty:
                    continue
                podetail.d_qty = podetail.qty - CpDetail.find_sum_po_qty(podetail) - po_qty
                if detail.all_qty - pi_qty < podetail.d_qty:
                    podetail.d_qty = detail.all_qty - pi_qty
                if int(itemQty) >= int(podetail.d_qty):
                    podetail.curr_qty = podetail.d_qty
                    itemQty = itemQty - podetail.d_qty
                    podetail.locked = True
                else:
                    podetail.locked = False
                    podetail.curr_qty = itemQty
                    itemQty = 0
                podetail.all_qty = items.get('all_qty')
                itemcodes.update({podetail.stock_item_no:{'qty':itemQty, 'item_qty':itemIQty}})
                if podetail.curr_qty > 0:
                    if hasattr(detail, 'po_key'):
                        detail.po_key.update({key:podetail.curr_qty + detail.po_key.get(key, 0)})
                    else:
                        detail.po_key = {key:podetail.curr_qty}
                    podetail.co_detail_id = detail.id
                    podetail.unit = detail.unit
                    podetail.item_qty = itemIQty
                    podetail.curr_qty = int(podetail.curr_qty)
                    podetail.company_code = detail.company_code
                    if detail.__tablename__ == 'vat_si_detail':
                        podetail.invoice_no = detail.invoice_no
                        podetail.item_desc  = detail.item_desc
                    else:
                        podetail.sales_contract_no = detail.sales_contract_no
                        podetail.item_desc = detail.desc_zh
                    podetail.description   = detail.description
                    podetail.remark = detail.remark
                    result.append(podetail) 
        return result
    
    @classmethod
    def parsePoPi(cls, podetails, pidetails, detail, po_no, pi_qtys = None, items_dict = None):
        result = []
        podetails = copy.deepcopy(podetails)
        pidetails = copy.deepcopy(pidetails)
        header = detail.o_head
        for podetail in podetails:
            if podetail.purchase_order_no != po_no[0] or podetail.line_no != po_no[4]:
                continue
            pi_total = 0
            po_key = "%s_%s" % (podetail.purchase_order_no, podetail.line_no)
            if hasattr(detail, 'pi_key'):
                for k, v in detail.pi_key.iteritems():
                    pi_total += v
                if detail.all_qty == pi_total:
                    detail.locked = True
                    continue  
            curr_qty = podetail.curr_qty
            if len(pidetails) > 0:
                is_post, all_pi_qty = False, 0
                for pidetail in pidetails:
                    if podetail.purchase_order_no == pidetail.po_no and podetail.line_no == pidetail.po_line_no\
                    and podetail.purchase_order_no == po_no[0] and podetail.line_no == po_no[4] and pidetail.grn_line_no == po_no[2]\
                    and pidetail.grn_no == po_no[1] and pidetail.item_no == po_no[5]:
                        pi_qty = 0
                        key = "%s_%s" % (pidetail.grn_no, pidetail.grn_line_no)
                        pis = pi_qtys.get(key, {})                                                                                                                                
                        for k, v in pis.iteritems():
                            if k != detail.id:
                                pi_qty += v
                        pidetail.pi_no  = pidetail.purchase_invoice_no
                        pidetail.qty = pidetail.qty - CpDetail.find_sum_pi_qty(pidetail) - pi_qty
                        if detail.all_qty - pi_total < pidetail.qty:
                            pidetail.qty = detail.all_qty - pi_total
                        if curr_qty  == 0: 
                            continue
                        if curr_qty  >= int(pidetail.qty):
                            pidetail.pi_qty = int(pidetail.qty)
                            curr_qty = curr_qty - pidetail.qty
                        else:
                            pidetail.pi_qty = int(curr_qty)
                            curr_qty = 0
                        if hasattr(detail, 'pi_key'):
                            detail.pi_key.update({key:pidetail.pi_qty + detail.pi_key.get(key, 0)})
                        else:
                            detail.pi_key = {key:pidetail.pi_qty}
                        pidetail.unit = podetail.unit
                        pidetail.company_code = podetail.company_code
                        pidetail.sales_contract_no = podetail.sales_contract_no
                        pidetail.item_desc = podetail.item_desc
                        po = PO.find_detail(po_no[0])
                        if not pidetail.exchange_rate:
                            pidetail.exchange_rate = po.exchange_rate
                        if not pidetail.currency:
                            pidetail.currency  = po.currency
                        pidetail.key = key
                        pidetail.po_key = po_key
                        pidetail.ae            = po.ae
                        pidetail.ref           = header.ref
                        pidetail.customer_code = header.customer_code
                        pidetail.customer_name = header.customer_name
                        pidetail.stock_item_no = podetail.stock_item_no
                        pidetail.po_line_no    = podetail.line_no
                        pidetail.pi_unit_price = pidetail.unit_price
                        pidetail.unit_price    = podetail.unit_price
                        pidetail.description   = podetail.description
                        pidetail.remark        = podetail.remark
                        pidetail.supplier_code = pidetail.supplier
                        pidetail.co_detail_id  = podetail.co_detail_id
                        pidetail.po_qty        = pidetail.pi_qty
                        pidetail.item_qty      = podetail.item_qty
                        pidetail.locked        = podetail.locked
                        pidetail.pi_total      = pf(float(pidetail.pi_qty) * float(podetail.unit_price))
                        if int(pidetail.pi_qty) > 0:
                            is_post = True
                            all_pi_qty += pidetail.pi_qty 
                            result.append(pidetail)
                            
                if not is_post:
                    if hasattr(detail, 'no_pi_key') and detail.no_pi_key.get(po_key):
                        continue
                    po = PO.find_detail(po_no[0])
                    podetail.key = po_key
                    podetail.exchange_rate = po.exchange_rate
                    podetail.currency      = po.currency
                    supplier               = Supplier.get_detail_by_supplier(po.supplier)
                    podetail.ref           = header.ref
                    podetail.customer_code = header.customer_code
                    podetail.customer_name = header.customer_name
                    podetail.po_line_no    = podetail.line_no
                    podetail.po_no         = podetail.purchase_order_no
                    podetail.item_no       = podetail.stock_item_no
                    podetail.supplier_code = supplier.supl_code
                    podetail.supplier_name = supplier.supl_name
                    podetail.ae            = po.ae
                    podetail.pi_qty        = 0
                    podetail.po_qty        = podetail.curr_qty
                    podetail.no_pi_key      = True
                    if hasattr(detail, 'no_pi_key'):
                        detail.no_pi_key.update({po_key:podetail.curr_qty})
                    else:
                        detail.no_pi_key = {po_key:podetail.curr_qty}
                    result.append(podetail)
                else:
                    detail.po_key.update({po_key:detail.po_key.get(po_key, 0) - podetail.curr_qty + all_pi_qty})
            else:
                key = "%s_%s_%s" % (podetail.purchase_order_no, podetail.stock_item_no, podetail.line_no)
                po = PO.find_detail(po_no[0])
                podetail.exchange_rate = po.exchange_rate
                podetail.currency = po.currency
                supplier = Supplier.get_detail_by_supplier(po.supplier)
                podetail.ref           = header.ref
                podetail.customer_code = header.customer_code
                podetail.customer_name = header.customer_name
                podetail.po_line_no    = podetail.line_no
                podetail.po_no         = podetail.purchase_order_no
                podetail.item_no       = podetail.stock_item_no
                podetail.supplier_code = supplier.supl_code
                podetail.supplier_name = supplier.supl_name
                podetail.ae     = po.ae
                podetail.pi_qty = 0
                podetail.po_qty = podetail.curr_qty
                result.append(podetail)
        del podetails, pidetails
        return result
                                
    @classmethod
    def parsePoPiCharge(cls, pocharges, picharges, detail, post_po = None):
        result = []
        header = detail.o_head
        for pocharge in pocharges:
            pocharge.po_no = pocharge.purchase_order_no
            key = "%s_%s" % (pocharge.po_no, pocharge.line_no)
            if len(picharges) > 0:
                pi_total = 0
                pocharge.o_head_id = detail.o_head_id
                po_curr = CpCharge.find_all_po_charge(pocharge)
                pocharge.curr_total = pocharge.total - post_po.get(key, 0)
                po_total = float(pocharge.total) - po_curr - post_po.get(key, 0)
                for picharge in picharges:
                    if picharge.charge_code in const.CHARGE_CODES.get(pocharge.charge_code, []) and picharge.po_no == pocharge.po_no\
                    and picharge.po_chrg_line_no == pocharge.line_no:
                        pic_key = "%s_%s" % (picharge.purchase_invoice_no, picharge.line_no)
                        pi_total = float(picharge.total) - post_po.get(pic_key, 0)
                        if po_total == 0 or pi_total == 0:continue
                        if po_total >= pi_total:
                            picharge.total = picharge.total
                            po_total = po_total - float(picharge.total)
                        else:
                            picharge.total = po_total
                            po_total = 0
                        if po_total >= 0:
                            if hasattr(detail, 'o_head_id'):
                                picharge.o_head_id = detail.o_head_id
                            pi = PI.get(picharge.purchase_invoice_no)
                            picharge.pi_line_no    = picharge.line_no
                            picharge.line_no       = pocharge.line_no
                            picharge.ref           = header.ref
                            picharge.supplier      = pi.supplier
                            picharge.all_total     = pocharge.total
                            picharge.supplier_name = pi.supplier_name
                            picharge.supplier_short_name = pi.supplier_name
                            picharge.customer_code = header.customer_code
                            picharge.customer_name = header.customer_name
                            picharge.po_total = float(picharge.total)
                            picharge.so_no    = detail.sales_contract_no
                            picharge.type     = const.CHARGE_TYPE_P_MAN
                            picharge.pi_no    = picharge.purchase_invoice_no
                            picharge.total    = float(picharge.total)
                            if picharge.total >= 0.005:
                                result.append(picharge) 
            else:
                po  = PO.find_detail(pocharge.purchase_order_no)
                po_total          = CpCharge.find_all_po_charge(pocharge)
                pocharge.ref           = header.ref
                pocharge.supplier = po.supplier
                pocharge.supplier_name = po.supplier_name
                pocharge.supplier_short_name = po.supplier_short_name
                pocharge.customer_code = header.customer_code
                pocharge.customer_name = header.customer_name
                pocharge.po_no    = pocharge.purchase_order_no
                pocharge.all_total = pocharge.total
                pocharge.po_total = pocharge.total - po_total
                pocharge.so_no    = detail.sales_contract_no
                pocharge.type     = const.CHARGE_TYPE_P_MAN
                pocharge.total    = 0
                if pocharge.po_total >= 0.005:
                    result.append(pocharge) 
        return result

    @classmethod
    def get_details_by_like(cls, grn, item_code = None, type = None):
        data = DBSession.query(cls).filter(cls.relation_ap.ilike('%%%s%%' % grn)).filter(cls.active == 0)
        if item_code:
            data = data.filter(cls.item_no == item_code)
        if type:
            data = data.filter(cls.o_head_id != None)
        else:
            data = data.filter(cls.n_head_id != None)
        return data.all()
                
    @classmethod
    def get_ohead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.o_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]
    
    @classmethod
    def get_nhead_ids(cls, item_code):
        results = [i[0] for i in DBSession.query(distinct(cls.n_head_id)).filter(cls.item_no.ilike('%%%s%%' % item_code))]
        return results if results else [0]
    

    
class CpDetail(Table_CpDetail):
    
    @classmethod
    def find(cls, ** args):
        rs = []
        ref, po, pi, customer_code, customer_name \
                                        = [args.get(i) for i in ['ref', 'po_no', 'pi_no', 'customer_code', 'customer_name']]
        page, limit, cate = 25, 0, 'next'
        if args.get("page"):limit = int(args.get("page"))
        offset = limit + page
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit")) 
            offset = int(args.get("offset"))   
        queryExtend = QueryExtend(CoDetail, ** args)
        queryExtend.query_all(True, DBSession, None, limit, offset, ** {
                      const.QUERY_TYPE_LIKE: ['sales_contract_no', 'invoice_no', 'item_no'],
                      const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
                      const.QUERY_TYPE_ORDER_BY: ['create_time'],
                      const.QUERY_TYPE_COMPANY_CODE: ['company_code']
                      })
        
        codetails = queryExtend.result
        pidetails = cls.find_new_pi(codetails)
        for pidetail in pidetails:
            if po and pidetail.po_no != po:
                continue
            if pi and pidetail.pi_no != pi:
                continue
            if ref and pidetail.ref != ref:
                continue
            if customer_code and pidetail.customer_code != customer_code:
                continue
            if customer_name and pidetail.customer_name != customer_name:
                continue
            if hasattr(pidetail, 'pi_no'): 
                codetail = CoDetail.get(pidetail.co_detail_id)
                ohead = codetail.o_head
                pidetail.cst_id = ohead.id
                pidetail.cst_ref = ohead.ref
                rs.append(pidetail)
        return rs , offset, limit
                
   
    @classmethod
    def create(cls, details, ** args):
        pidetails, picharges, uicharges = [], [], []
        n_head_id = args.get('n_head_id')
        o_head_id = args.get('o_head_id')
        if o_head_id and n_head_id:
            ohead = OHead.get(o_head_id)
            codetails = ohead.co_details
            cpcharges = ohead.cp_charges
            for detail in details:
                detail.ohead_id = o_head_id
                vat_qty = detail.vat_qty
                for codetail in codetails:
                    if detail.uuid == codetail.uuid:
                        detail.po_qty = vat_qty 
                        cpdetails = codetail.cp_details
                        pidetails.extend(cls.parse_so_cp(detail, cpdetails))
            post_invoice = list(set([i.pi_no for i in pidetails]))
            
            for cpcharge in cpcharges:
                if cpcharge.pi_no in post_invoice or cpcharge.note_no:
                    cpcharge.curr_total = float(cpcharge.total) - CpCharge.find_sum_qty(cpcharge)
                    if cpcharge.curr_total > 0:
                        picharges.append(cpcharge)
                        
        elif o_head_id and not n_head_id:
            c_details =[]
            for detail in details:
                detail.ohead_id = o_head_id
                c_details.append(detail)
            pidetails, picharges = cls.format(c_details)
            post_invoice = list(set([i.pi_no for i in pidetails if hasattr(i, 'pi_no')]))
            for pi_no in post_invoice:
                res_details, res_charges, include_tax = _all_rewrite_price_and_filter_charges(UICharge.find_details(pi_no), [])
                for charge in res_charges:
                    if charge.note_type == 'D':
                        charge.total = - charge.total
                    charge.total = float(charge.total) - CpCharge.find_sum_qty(charge)
                    if charge.total > 0.005:
                        uicharges.append(charge)
        else:
            pidetails = details
        CpCharge.create(picharges, ** args)
        
        for rs in pidetails:
            if args.get('n_head_id'):
                keys = [('co_detail_id', 'bco_detail_id'), 'po_no',('po_qty', 'ccn_po_qty'), 'pi_no', ('pi_total', 'curr_total'),
                    ('pi_qty', 'vat_pi_qty'), 'supplier', 'supplier_name', 'desc_zh', 'pi_total',
                    'sales_contract_no', 'company_code', 'line_no', 'po_line_no',  'item_no','description','unit_price', 'pi_unit_price', 'unit', 'remark',
                    'ae', 'currency', 'exchange_rate', 'item_qty', 'grn_no', 'grn_line_no', 'n_head_id']
                Period.update_pi_flag(rs.pi_no, rs.item_no, rs.po_no)
            else:
                keys = ['co_detail_id', 'po_no', 'po_qty', 'pi_no', 'pi_total',
                    'pi_qty', ('supplier', 'supplier_code'), 'supplier_name', 'desc_zh', 
                    'sales_contract_no', 'company_code', 'line_no', 'po_line_no', 'item_no','description','unit_price', 'pi_unit_price', 'unit', 'remark',
                    'ae', 'currency', 'exchange_rate', 'item_qty', 'o_head_id','grn_no', 'grn_line_no']
                item_desc = ItemDesc.get(rs.supplier_code, rs.item_no)
                if item_desc:
                    rs.desc_zh = item_desc.description
            params   = _get_params_from_args_and_obj(keys, rs, ** args)
            cpDetail = cls( ** params)
            DBSession.add(cpDetail)
            

    @classmethod
    def find_new_pi(cls, codetails):
        result, post_pi_qtys = [], {}
        for codetail in codetails:
            ohead = codetail.o_head
            cpdetails = codetail.cp_details
            for cpdetail in cpdetails:
                if cpdetail.pi_qty < cpdetail.po_qty:
                    l, c = {}, []
                    pids = PID.find_details_by_po_no(cpdetail.po_no, cpdetail.item_no, cpdetail.po_line_no)
                    for pid in pids:
                        if l.get(pid.purchase_invoice_no):
                            l[pid.purchase_invoice_no].append(pid)
                        else:
                            l.update({pid.purchase_invoice_no:[pid]})
                    for key, value in l.iteritems():
                        picharges = PICharge.find_charge_by_item_code(key)
                        details, charges, tax = _all_rewrite_price_and_filter_charges(picharges, value)
                        uidetails = UID.find_details(key)
                        detail_qty, uidetail_qty = 0, 0
                        for detail in details:
                            detail_qty += int(detail.qty)
                        for uidetail in uidetails:
                            uidetail_qty += int(uidetail.note_qty)
                        if detail_qty != uidetail_qty:
                            c.extend(details)
                    for pid in c:
                        if cpdetail.item_no == pid.item_no and cpdetail.po_line_no == pid.po_line_no:
                            key = '%s_%s' % (pid.grn_no, pid.grn_line_no)
                            pid.co_detail_id = codetail.id
                            related_pis = cls.findRelatePOPIAll(pid)
                            pi_qty = 0
                            for related_pi in related_pis:
                                pi_qty += int(related_pi.pi_qty)
                            post_pi_qty = post_pi_qtys.get(key, 0)
                            if pid.qty - post_pi_qty > pi_qty and ohead:
                                pid.supplier_code = cpdetail.supplier
                                pid.item_qty = cpdetail.item_qty
                                pid.po_qty = cpdetail.po_qty
                                pid.pi_qty = cpdetail.pi_qty
                                pid.ava_pi_qty = int(pid.qty) - int(pi_qty) - int(post_pi_qty)
                                post_pi_qtys.update({key:pid.ava_pi_qty + int(post_pi_qty)})
                                pid.cst_id  = ohead.id
                                pid.cst_ref = ohead.ref
                                pid.pi_no = pid.purchase_invoice_no
                                pid.pi_total = pf(pid.unit_price * int(pid.qty))
                                if abs(Decimal(str(cpdetail.unit_price)) - Decimal(str(pid.unit_price))) > Decimal('0.00005'):
                                    pid.variance_type = True
                                if pid.ava_pi_qty > 0:
                                    result.append(pid)
        return result
    
    @classmethod
    def find_detail_by_po(cls, id, po_no, po_line_no):
        return DBSession.query(cls).filter(cls.co_detail_id == id).filter(cls.po_no == po_no).filter(cls.po_line_no == po_line_no).filter(cls.active == 0).first()
    
    @classmethod
    def find_detail_by_po_all(cls, id, po_no, po_line_no):
        return DBSession.query(cls).filter(cls.co_detail_id == id).filter(cls.po_no == po_no).filter(cls.po_line_no == po_line_no).filter(cls.active == 0).all()
    
    @classmethod
    def find_po(cls, detail):
        return DBSession.query(cls).filter(cls.active == 0).filter(cls.pi_no == detail.pi_no).filter(cls.po_no == detail.po_no)\
                .filter(cls.co_detail_id == detail.co_detail_id).filter(cls.po_line_no == detail.po_line_no)\
                    .filter(cls.grn_no == detail.grn_no).filter(cls.grn_line_no == detail.grn_line_no).first()
    
    @classmethod
    def findRelatePOPI(cls, detail):
        return DBSession.query(cls).filter(cls.active == 0).filter(cls.pi_no != None).filter(cls.po_no == detail.po_no)\
                        .filter(cls.co_detail_id == detail.co_detail_id).filter(cls.po_line_no == detail.po_line_no)\
                            .filter(cls.grn_no == detail.grn_no).filter(cls.grn_line_no == detail.grn_line_no).first()
    
    @classmethod
    def findRelatePOPIAll(cls, detail):
        return DBSession.query(cls).filter(cls.active == 0).filter(cls.pi_no == detail.purchase_invoice_no).filter(cls.po_no == detail.po_no)\
                .filter(cls.po_line_no == detail.po_line_no)\
                    .filter(cls.grn_no == detail.grn_no).filter(cls.grn_line_no == detail.grn_line_no).all()
                            
    @classmethod 
    def deletePOPI(cls, detail):
        cpdetails = DBSession.query(cls).filter(cls.active == 0).filter(or_(cls.pi_no == None, cls.pi_qty == 0)).filter(cls.po_no == detail.po_no)\
                        .filter(cls.co_detail_id == detail.co_detail_id).filter(cls.po_line_no == detail.po_line_no).all()
        for cpdetail in cpdetails:
            DBSession.delete(cpdetail)
    
    @classmethod
    def format(cls, so_details):
        presult, cresult, post_charge, curr_so_details = [], [], [], []
        p, podetailss, pochargess, pidetailss, pichargess =  {}, {}, {}, {}, {}
        for so_detail in so_details:
            related_nos = OHead.find_po_no_by_so(so_detail.sales_contract_no, so_detail.item_no, so_detail.line_no)
            for related_no in related_nos:
                if len(related_no) > 0:
                    po_no = related_no[0]
                    so_detail.base_itemcode  = ItemCode.find_dict(so_detail.item_no, so_detail.vat_qty)
                    so_detail.itemcode_qtys  = ItemCode.find_dict(so_detail.item_no, so_detail.vat_qty)
                    so_detail.related_po_no, so_detail.related_grn_no, so_detail.related_grn_line_no, so_detail.related_item_no, \
                            so_detail.related_po_line_no, so_detail.related_item_code, so_detail.related_item_line_no, so_detail.lot_no, so_detail.reserve_qty = related_no
                    if not so_detail.related_grn_no:
                        continue
                    curr_so_details.append(so_detail)
                    if podetailss.get(po_no):
                        podetails = podetailss.get(po_no)
                        pocharges = pochargess.get(po_no)
                    else:
                        podetails = POD.find_details(po_no)
                        pocharges = POCharge.find_details_by_all(po_no)
                        podetails, pocharges, include_tax = _all_rewrite_price_and_filter_charges(pocharges, podetails)
                        podetailss.update({po_no:podetails})
                        pochargess.update({po_no:pocharges})
                        
                    podetails = cls._format_po(so_detail, podetails)
                    podetails = cls._format_cn(podetails)
                    if pidetailss.get(po_no):
                        pidetails = pidetailss.get(po_no)
                    else:
                        pidetails = OHead.find_pi_by_so([po_no])
                        pidetailss.update({po_no:pidetails})
                    if len(pidetails) > 0:
                        for pi_no, pidetail in pidetails.iteritems():
                            if pichargess.get(pi_no):
                                picharges = pichargess.get(pi_no)
                            else:
                                picharges =  PICharge.find_details_by_pi(pi_no)
                                pichargess.update({pi_no:picharges})
                            pidetail, picharges, include_tax = _all_rewrite_price_and_filter_charges(picharges, pidetail)
                            pidetail = cls._format_cn(pidetail)
                            pidetail, picharges = CpDetail.par_pipi_charge(pidetail, picharges)
                            if len(pidetail) > 0:
                                pidetail = cls._format_pi_po(so_detail, podetails, pidetail)
                                picharges = cls._format_charges(so_detail, pocharges, picharges, p)
                                presult.extend(pidetail)
                                if len(picharges) > 0:
                                    for picharge in picharges:
                                        pocharge_key = "%s_%s" % (picharge.po_no, picharge.line_no)
                                        if p.get(pocharge_key):
                                            p[pocharge_key] += picharge.po_total
                                        else:
                                            p.update({pocharge_key:picharge.po_total})
                                        if hasattr(picharge, 'pi_no'):
                                            picharge_key = "%s_%s" % (picharge.pi_no, picharge.pi_line_no)
                                            if p.get(picharge_key):
                                                p[picharge_key] += picharge.total
                                            else:
                                                p.update({picharge_key:picharge.total})
                                cresult.extend(picharges) 
                    else:
                        pidetail = cls._format_pi_po(so_detail, podetails, [])
                        if so_detail.related_po_no not in post_charge:
                            picharges = cls._format_charges(so_detail, pocharges, [], {})
                            cresult.extend(picharges)
                            post_charge.append(so_detail.related_po_no)
                        presult.extend(pidetail)
                        
        result, pbridge = [], []
        for index1, p1 in enumerate(presult):
            if hasattr(p1, 'no_pi_key'):
                for index2, p2 in enumerate(presult):
                    if not hasattr(p2, 'no_pi_key') and hasattr(p2, 'po_key') and p1.key == p2.po_key and p1.update < p2.update:
                        p1.po_qty -= p2.po_qty
                if p1.po_qty > 0:
                    pbridge.insert(len(pbridge), p1)
            else:
                pbridge.insert(0, p1)

        for so_detail in curr_so_details:
            itemcodes = so_detail.base_itemcode
            for p1 in pbridge:
                qtys = itemcodes.get(p1.item_no, {})
                all_qty = qtys.get('all_qty')
                if p1.co_detail_id == so_detail.id and all_qty > 0:
                    if all_qty > p1.po_qty:
                        all_qty -= p1.po_qty
                    else:
                        p1.po_qty = all_qty
                        all_qty = 0
                    qtys.update({'all_qty': all_qty})
                    result.append(p1)
        return result, cresult
                                
    @classmethod
    def _format_cn(cls, details):
        pdetails = []
        for detail in details:
            if detail.__tablename__ == 't_purchase_invoice_dtl': 
                picost_total = 0
                picosts = PICost.find(detail.purchase_invoice_no, detail.item_no)
                dncosts = DNCost.find(detail.purchase_invoice_no, detail.item_no)
                for picost in picosts:
                    picost_qty = picost.qty - picost.payment_qty
                    dncost_qty = 0
                    for dncost in dncosts:
                        dncost_qty += (dncost.qty - dncost.payment_qty)
                    picost_total += (picost_qty - dncost_qty)
                if detail.qty > picost_total:
                    detail.qty -= picost_total
                else:
                    continue
                
                uids = UID.find_details(detail.purchase_invoice_no, detail.po_no, detail.item_no)
                uid_qty = 0
                for uid in uids:
                    if uid.pi_line_no == detail.line_no:
                        uid_qty += uid.note_qty
                detail.qty = detail.qty - uid_qty
                print detail.purchase_invoice_no, detail.item_no, detail.qty
                pdetails.append(detail)
            else:
                
                picost_total = 0
                picosts = PICost.find_by_po(detail.po_no, detail.stock_item_no)
                dncosts = DNCost.find_by_po(detail.po_no, detail.stock_item_no)
                for picost in picosts:
                    picost_qty = picost.qty - picost.payment_qty
                    dncost_qty = 0
                    for dncost in dncosts:
                        dncost_qty += (dncost.qty - dncost.payment_qty)
                    picost_total += (picost_qty - dncost_qty)
                if detail.qty > picost_total:
                    detail.qty -= picost_total
                else:
                    continue
                
                uids = UID.find_details(None, detail.po_no, detail.stock_item_no)
                uid_qty = 0
                for uid in uids:
                    if uid.po_item_line_no == detail.line_no:
                        uid_qty += uid.note_qty
                detail.qty = detail.qty - uid_qty
                pdetails.append(detail)
        return pdetails
                     
    @classmethod
    def _format_po(cls, so_detail, podetails):
        result = []
        podetails = deepcopy(podetails)
        for podetail in podetails:
            base_qty = podetail.qty
            podetail.po_no = podetail.purchase_order_no
            if podetail.po_no == so_detail.related_po_no and  podetail.line_no == so_detail.related_po_line_no:
                itemcode_qtys = so_detail.itemcode_qtys.get(podetail.stock_item_no)
                if itemcode_qtys:
                    post_item_qty, type, itemQty, itemIQty, all_qty  = (itemcode_qtys.get(i, 0) for i in ['post_item_qty', 'type', 'qty', 'item_qty', 'all_qty'])
                    print "~"*30, itemQty
                    po_key = "%s_%s" % (podetail.po_no, podetail.line_no)
                    if hasattr(so_detail, 'post_po_qtys'):
                        post_po_qty = so_detail.post_po_qtys.get(po_key, 0)
                    else:
                        post_po_qty = 0
                    if hasattr(so_detail, 'post_pi_qtys'):
                        for k, v in so_detail.post_pi_qtys.iteritems():
                            post_item_qty += v
                    if hasattr(so_detail, 'post_item_qtys'):
                        for k, v in so_detail.post_item_qtys.iteritems():
                            if k == podetail.stock_item_no:
                                itemQty -= v 
                    print "~"*30, itemQty
                    if itemQty > 0:
                        vat_po_qty  = CpDetail.find_sum_po_qty(podetail) 
                        podetail.post_qty = podetail.qty  - post_po_qty - vat_po_qty
                        if podetail.post_qty > 0:
                            if int(itemQty) >= int(podetail.post_qty):
                                podetail.curr_qty = podetail.post_qty
                                itemQty -= podetail.post_qty
                                podetail.locked = True
                            else:
                                podetail.locked = False
                                podetail.curr_qty = itemQty
                                itemQty = 0
                            so_detail.itemcode_qtys.update({podetail.stock_item_no:{'qty':itemQty, 'item_qty':itemIQty}})
                            if podetail.curr_qty > 0:
                                podetail.co_detail_id = so_detail.id                                                                                                                    
                                podetail.unit = so_detail.unit
                                podetail.item_qty = itemIQty
                                podetail.curr_qty = int(podetail.curr_qty)
                                podetail.company_code = so_detail.company_code
                                podetail.base_qty = int(podetail.curr_qty)
                                podetail.all_qty  = all_qty
                                if so_detail.__tablename__ == 'vat_si_detail':
                                    podetail.invoice_no = so_detail.invoice_no
                                    podetail.item_desc  = podetail.description
                                    podetail.sales_contract_no =  so_detail.sc_no                                                                                                           
                                else:
                                    podetail.sales_contract_no = so_detail.sales_contract_no
                                    podetail.item_desc = podetail.description
                                podetail.description   = podetail.description
                                podetail.remark = podetail.item_remark
                                result.append(podetail) 
        return result                                                                                                                                                    
    
    @classmethod
    def _format_pi_po(cls, so_detail, podetails, pidetails):
        result = []
        header = so_detail.o_head
        for podetail in podetails:
            all_pi_qty = 0
            base_qty = podetail.base_qty
            if podetail.curr_qty == 0:
                continue
            po_key = "%s_%s" % (podetail.po_no, podetail.line_no)
            if len(pidetails) > 0:
                is_post = False
                for pidetail in pidetails:
                    print pidetail.pi_no, pidetail.grn_no, so_detail.related_grn_no
                    if podetail.purchase_order_no == pidetail.po_no and podetail.line_no == pidetail.po_line_no\
                    and podetail.purchase_order_no == so_detail.related_po_no and podetail.line_no == so_detail.related_po_line_no \
                    and pidetail.grn_line_no == so_detail.related_grn_line_no and pidetail.grn_no == so_detail.related_grn_no and pidetail.item_no == so_detail.related_item_no:
                        pidetail.pi_no  = pidetail.purchase_invoice_no
                        pi_key = "%s_%s" % (pidetail.grn_no, pidetail.grn_line_no)
                        if hasattr(so_detail, 'post_pi_qtys'):
                            post_pi_qty = so_detail.post_pi_qtys.get(pi_key, 0)
                        else:
                            post_pi_qty = 0
                        pidetail.qty = pidetail.qty - CpDetail.find_sum_pi_qty(pidetail) - post_pi_qty
                        if podetail.curr_qty  == 0: continue
                        if podetail.curr_qty  >= int(pidetail.qty):
                            pidetail.pi_qty = int(pidetail.qty)
                            podetail.curr_qty -= pidetail.qty
                        else:
                            pidetail.pi_qty = int(podetail.curr_qty)
                            podetail.curr_qty = 0
                        if hasattr(so_detail, 'post_pi_qtys'):
                            so_detail.post_pi_qtys.update({pi_key:pidetail.pi_qty + so_detail.post_pi_qtys.get(pi_key, 0)})
                        else:
                            so_detail.post_pi_qtys = {pi_key:pidetail.pi_qty}
                        if hasattr(so_detail, 'post_item_qtys'):
                            so_detail.post_item_qtys.update({pidetail.item_no:pidetail.pi_qty + so_detail.post_item_qtys.get(pidetail.item_no, 0)})
                        else:
                            so_detail.post_item_qtys = {pidetail.item_no:pidetail.pi_qty}
                        pidetail.unit = podetail.unit
                        pidetail.company_code = podetail.company_code
                        pidetail.sales_contract_no = podetail.sales_contract_no
                        pidetail.item_desc = podetail.item_desc
                        po = PO.find_detail(pidetail.po_no)
                        if not pidetail.exchange_rate:
                            pidetail.exchange_rate = po.exchange_rate
                        if not pidetail.currency:
                            pidetail.currency  = po.currency
                        pidetail.all_qty       = podetail.all_qty
                        pidetail.uuid          = uuid.uuid4()
                        pidetail.key           = pi_key
                        pidetail.po_key        = po_key
                        pidetail.ae            = po.ae
                        pidetail.ref           = header.ref
                        pidetail.customer_code = header.customer_code
                        pidetail.customer_name = header.customer_name
                        pidetail.stock_item_no = podetail.stock_item_no
                        pidetail.po_line_no    = podetail.line_no
                        pidetail.pi_unit_price = pidetail.unit_price
                        pidetail.unit_price    = podetail.unit_price
                        pidetail.description   = podetail.description
                        pidetail.remark        = podetail.remark
                        pidetail.supplier_code = pidetail.supplier
                        pidetail.co_detail_id  = podetail.co_detail_id
                        #pidetail.po_qty        = podetail.curr_qty
                        pidetail.po_qty        = pidetail.pi_qty
                        pidetail.item_qty      = podetail.item_qty
                        pidetail.locked        = podetail.locked
                        pidetail.pi_total      = pf(float(pidetail.pi_qty) * float(podetail.unit_price))
                        pidetail.update        = datetime.datetime.now()
                        if int(pidetail.pi_qty) > 0:
                            is_post = True
                            all_pi_qty += pidetail.pi_qty 
                            result.append(pidetail)
                            
                if not is_post:
                    if hasattr(so_detail, 'no_pi_key') and so_detail.no_pi_key.get(po_key):
                        continue
                    po = PO.find_detail(podetail.po_no)
                    podetail.key = po_key
                    podetail.uuid          = uuid.uuid4()
                    podetail.exchange_rate = po.exchange_rate
                    podetail.currency      = po.currency
                    supplier               = Supplier.get_detail_by_supplier(po.supplier)
                    podetail.ref           = header.ref
                    podetail.customer_code = header.customer_code
                    podetail.customer_name = header.customer_name
                    podetail.po_line_no    = podetail.line_no
                    podetail.po_no         = podetail.purchase_order_no
                    podetail.item_no       = podetail.stock_item_no
                    podetail.supplier_code = supplier.supl_code
                    podetail.supplier_name = supplier.supl_name
                    podetail.ae            = po.ae
                    podetail.pi_qty        = 0
                    podetail.po_qty        = podetail.curr_qty
                    podetail.update        = datetime.datetime.now()
                    podetail.no_pi_key      = True
                    if hasattr(so_detail, 'no_pi_key'):
                        so_detail.no_pi_key.update({po_key:podetail.curr_qty})
                    else:
                        so_detail.no_pi_key = {po_key:podetail.curr_qty}
                    result.append(podetail)
                else:
                    pass
            else:
                if hasattr(so_detail, 'no_pi_key') and so_detail.no_pi_key.get(po_key):
                    continue
                po = PO.find_detail(podetail.po_no)
                podetail.uuid          = uuid.uuid4()
                podetail.exchange_rate = po.exchange_rate
                podetail.currency = po.currency
                supplier = Supplier.get_detail_by_supplier(po.supplier)
                podetail.ref           = header.ref
                podetail.customer_code = header.customer_code
                podetail.customer_name = header.customer_name
                podetail.po_line_no    = podetail.line_no
                podetail.po_no         = podetail.purchase_order_no
                podetail.item_no       = podetail.stock_item_no
                podetail.supplier_code = supplier.supl_code
                podetail.supplier_name = supplier.supl_name
                podetail.ae     = po.ae
                podetail.pi_qty = 0
                podetail.po_qty = podetail.curr_qty
                podetail.update = datetime.datetime.now()
                if hasattr(so_detail, 'no_pi_key'):
                    so_detail.no_pi_key.update({po_key:podetail.curr_qty})
                else:
                    so_detail.no_pi_key = {po_key:podetail.curr_qty}
                result.append(podetail)
            if  all_pi_qty > 0:
                if hasattr(so_detail, 'post_po_qtys'):
                    so_detail.post_po_qtys.update({po_key:so_detail.post_po_qtys.get(po_key, 0)  + all_pi_qty})
                else:
                    so_detail.post_po_qtys = {po_key:all_pi_qty}
                so_detail.itemcode_qtys[podetail.stock_item_no].update({'item_qty':so_detail.itemcode_qtys[podetail.stock_item_no].get('item_qty', 0) + podetail.curr_qty - all_pi_qty})
        return result
    
    @classmethod
    def _format_charges(cls, so_detail, pocharges, picharges, post_po):
        result = []
        pocharges = deepcopy(pocharges)
        picharges = deepcopy(picharges)
        header = so_detail.o_head
        for pocharge in pocharges:
            pocharge.po_no = pocharge.purchase_order_no
            key = "%s_%s" % (pocharge.po_no, pocharge.line_no)
            pocharge.o_head_id = so_detail.o_head_id
            po_curr = CpCharge.find_all_po_charge(pocharge)
            pocharge.curr_total = pocharge.total - post_po.get(key, 0)
            pocharge.total = float(pocharge.total) - po_curr - post_po.get(key, 0)

            if abs(pocharge.total) > 0.005 and len(picharges) > 0:
                pi_total = 0
                for picharge in picharges:
                    if picharge.charge_code in const.CHARGE_CODES.get(pocharge.charge_code, []) and picharge.po_no == pocharge.po_no\
                    and picharge.po_chrg_line_no == pocharge.line_no:
                        pic_key = "%s_%s" % (picharge.purchase_invoice_no, picharge.line_no)
                        cpcharges = CpCharge.find_charge(picharge.purchase_invoice_no, None, picharge.line_no)
                        curr_pi_qty = 0
                        for cpcharge in cpcharges:
                            curr_pi_qty += float(cpcharge.total)
                        picharge.total = float(picharge.total) - curr_pi_qty - post_po.get(pic_key, 0)
                        if abs(picharge.total) > 0.005:
                            if hasattr(so_detail, 'o_head_id'):
                                picharge.o_head_id = so_detail.o_head_id
                            pi = PI.get(picharge.purchase_invoice_no)
                            picharge.pi_line_no    = picharge.line_no
                            picharge.line_no       = pocharge.line_no
                            picharge.ref           = header.ref
                            picharge.supplier      = pi.supplier
                            picharge.all_total     = pocharge.total
                            picharge.supplier_name = pi.supplier_name
                            picharge.supplier_short_name = pi.supplier_name
                            picharge.customer_code = header.customer_code
                            picharge.customer_name = header.customer_name
                            picharge.po_total = float(picharge.total)
                            picharge.so_no    = so_detail.sales_contract_no
                            picharge.type     = const.CHARGE_TYPE_P_MAN
                            picharge.pi_no    = picharge.purchase_invoice_no
                            #picharge.total    = float(picharge.total) - CpCharge.find_sum_qty(picharge)
                            picharge.total    = float(picharge.total) 
                            if picharge.total >= 0.005:
                                result.append(picharge) 
            else:
                if abs(pocharge.total) > 0.005:
                    po  = PO.find_detail(pocharge.purchase_order_no)
                    po_total          = CpCharge.find_all_po_charge(pocharge)
                    pocharge.ref      = header.ref
                    pocharge.supplier = po.supplier
                    pocharge.supplier_name = po.supplier_name
                    pocharge.supplier_short_name = po.supplier_short_name
                    pocharge.customer_code = header.customer_code
                    pocharge.customer_name = header.customer_name
                    pocharge.po_no     = pocharge.purchase_order_no
                    pocharge.all_total = pocharge.total
                    pocharge.po_total  = pocharge.total - po_total
                    pocharge.so_no     = so_detail.sales_contract_no
                    pocharge.type      = const.CHARGE_TYPE_P_MAN
                    pocharge.total     = 0
                    if pocharge.po_total >= 0.005:
                        result.append(pocharge) 
        return result
    
    @classmethod
    def find_pi_charge(cls, details):
        po_qtys, pi_qtys, items_dict, post_po, p = {}, {}, {}, {}, {}
        pidetails, picharges, post_invoice, post_charge = [], [], [], []
        podetails_dict, pocharges_dict, pidetails_dict, picharges_dict = {}, {}, {}, {}
        for detail in details:
            detail.locked = None
            if detail.vat_qty == 0:
                continue
            po_nos = OHead.find_po_no_by_so(detail.sales_contract_no, detail.item_no, detail.line_no)
            for po_no in po_nos:
                if detail.locked: continue
                if len(po_no) == 0: 
                    continue
                if podetails_dict.get(po_no[0]):
                    podetail = podetails_dict.get(po_no[0])
                    pocharge = pocharges_dict.get(po_no[0])
                else:
                    podetail = OHead.find_po_by_so(po_no)
                    pocharge = OHead.find_po_charge_by_so(po_no)
                    podetails_dict.update({po_no[0]:podetail})
                    pocharges_dict.update({po_no[0]:pocharge})
                    
                ores = _all_rewrite_price_and_filter_charges(pocharge, podetail)
                pocharge = ores[1]
                podetail = CoDetail.getLikePo(detail, ores[0], po_qtys, po_no)
                if pidetails_dict.get(po_no[0]):
                    pidetail = pidetails_dict.get(po_no[0])
                else:    
                    pidetail = OHead.find_pi_by_so(po_no)
                    pidetails_dict.update({po_no[0]:pidetail})
                if len(pidetail) > 0:
                    for pi_no, pid in pidetail.iteritems():
                        if picharges_dict.get(pi_no):
                            pic = picharges_dict.get(pi_no)
                        else:
                            pic =  PICharge.find_details_by_pi(pi_no)
                            picharges_dict.update({pi_no:pic})
                        pid, pic, include_tax = _all_rewrite_price_and_filter_charges(pic, pid)
                        ires  = CpDetail.par_pipi_charge(pid, pic)
                        if len(ires[0]) == 0:
                            continue
                        pidetail = CoDetail.parsePoPi(podetail, ires[0], detail, po_no, pi_qtys, items_dict)
                        for pid in pidetail:
                            pidetails.append(pid)
                            if hasattr(pid, 'grn_no'):
                                key = "%s_%s" % (pid.grn_no, pid.grn_line_no)
                                if pi_qtys.get(key):
                                    if pi_qtys[key].get(pid.co_detail_id):
                                        pi_qtys[key][pid.co_detail_id] += pid.pi_qty
                                    else:
                                        pi_qtys[key].update({pid.co_detail_id: pid.pi_qty})
                                else:
                                    pi_qtys.update({key:{pid.co_detail_id: pid.pi_qty}})
                            pod_key = "%s_%s" % (pid.po_no, pid.po_line_no)  
                            if po_qtys.get(pod_key):
                                if po_qtys[pod_key].get(pid.co_detail_id):
                                    po_qtys[pod_key][pid.co_detail_id] += pid.po_qty
                                else:
                                    po_qtys[pod_key].update({pid.co_detail_id:pid.po_qty})
                            else:
                                po_qtys.update({pod_key:{pid.co_detail_id:pid.po_qty}})
                            po_key = "%s_%s_%s" % (pid.po_no, pid.stock_item_no, pid.po_line_no)
                            if items_dict.get(po_key):
                                items_dict[po_key] += pid.po_qty
                            else:
                                items_dict.update({po_key:pid.po_qty})
                            
                            picharge = CoDetail.parsePoPiCharge(pocharge, ires[1], detail, p)
                            if len(picharge) > 0:
                                for pic in picharge:
                                    poc_key = "%s_%s" % (pic.po_no, pic.line_no)
                                    pic_key = "%s_%s" % (pic.pi_no, pic.pi_line_no)
                                    if p.get(poc_key):
                                        p[poc_key] += pic.po_total
                                    else:
                                        p.update({poc_key:pic.po_total})
                                    if p.get(pic_key):
                                        p[pic_key] += pic.total
                                    else:
                                        p.update({pic_key:pic.total})
                                picharges.extend(picharge)
                                post_invoice.append(pi_no)
                                                                                                                                                                                                                                                                                                                   
                else:
                    pidetail = CoDetail.parsePoPi(podetail, [], detail, po_no)
                    if not po_no[0] in post_charge:
                        picharge = CoDetail.parsePoPiCharge(pocharge, [], detail)
                        picharges.extend(picharge)
                        post_charge.append(po_no[0])
                    pidetails.extend(pidetail)

        del podetails_dict, pocharges_dict, pidetails_dict, picharges_dict
        
        result = []
        for p1 in pidetails:
            if hasattr(p1, 'no_pi_key'):
                for p2 in pidetails:
                    if not hasattr(p2, 'no_pi_key') and p1.key == p2.po_key:
                        p1.po_qty -= p2.po_qty
                if p1.po_qty > 0:
                    result.append(p1)
            else:
                result.append(p1) 
            
        return result, picharges
    
    @classmethod
    def par_pipi_charge(cls, pidetails, picharges):
        post_pi, post_charge, pids, pics = {}, [], [], []
        for pidetail in pidetails:
            pidetail.pi_no = pidetail.purchase_invoice_no
            if post_pi.get(pidetail.pi_no):
                pis = post_pi[pidetail.pi_no][0]
                uis = post_pi[pidetail.pi_no][1]
            else:
                pis = PID.find_details_by_pi_no(pidetail.pi_no)
                uis = UID.find_details(pidetail.pi_no)
                post_pi.update({pidetail.pi_no:[pis, uis]})
            uids_qty, pids_qty = 0, 0
            for ui in uis:
                uids_qty += int(ui.note_qty)
            for pi in pis:
                pids_qty += int(pi.qty)
            if uids_qty != pids_qty:
                pids.append(pidetail)
                post_charge.append(pidetail.pi_no)
        if len(pidetails) > 0:
            pidetail = pidetails[0]
            po = PO.find_detail(pidetail.po_no)
        for picharge in picharges:
            if picharge.purchase_invoice_no in post_charge:
                picharge.supplier = pidetail.supplier
                picharge.ae = po.ae
                picharge.currency = pidetail.currency
                picharge.exchange_rate = pidetail.exchange_rate
                picharge.po_no = pidetail.po_no
                pics.append(picharge)
        return pids, pics
        
    @classmethod
    def parse_so_cp(cls, detail, cpdetails):
        result = []
        qty = detail.vat_qty
        itemcodes = ItemCode.find_dict(detail.item_no, qty)
        for cpdetail in cpdetails:
            items = itemcodes.get(cpdetail.item_no)
            if items:
                itemQty  = items.get('qty')
                itemIQty = items.get('item_qty')
                if itemQty == 0:
                    continue
                if itemQty >= cpdetail.pi_qty:
                    cpdetail.vat_pi_qty = cpdetail.pi_qty
                    itemQty = itemQty - cpdetail.pi_qty
                else:
                    cpdetail.vat_pi_qty = itemQty
                    itemQty = 0
                itemcodes.update({cpdetail.item_no:{'qty':itemQty, 'item_qty':itemIQty}})
                if itemQty >=  0:
                    cpdetail.ccn_po_qty = detail.vat_qty * itemIQty
                    cpdetail.bco_detail_id = detail.id
                    cpdetail.curr_total = pf(cpdetail.vat_pi_qty * cpdetail.unit_price)
                    result.append(cpdetail)
        return result
                    
    @classmethod
    def find_sum_pi_qty(cls, cpdetail):
        total = 0
        cpdetails = DBSession.query(cls).filter(cls.active == 0).filter(cls.grn_no == cpdetail.grn_no).filter(cls.grn_line_no == cpdetail.grn_line_no).all()
        for cpd in cpdetails:
            total += cpd.pi_qty
        return total
    
    @classmethod
    def find_sum_po_qty(cls, cpdetail):
        total = 0
        cpdetails = DBSession.query(cls).filter(cls.active == 0).filter(cls.po_no == cpdetail.purchase_order_no)\
                        .filter(cls.po_line_no == cpdetail.line_no).filter(cls.item_no == cpdetail.stock_item_no).all()
        co_details = []
        for cpd in cpdetails:
            if not cpd.co_detail_id in co_details:
                if hasattr(cpdetail, 'create_type') and cpdetail.create_type == const.CREATE_NEW_PI:
                    pass
                else:
                    total += cpd.po_qty
                    co_details.append(cpd.co_detail_id)
        return total
    
    @classmethod
    def find_pi(cls, pi_no, item_no= None, line_no = None):
        data = DBSession.query(cls).filter(cls.pi_no == pi_no).filter(cls.active == 0)
        if item_no: data = data.filter(cls.item_no == item_no)
        if line_no: data = data.filter(cls.line_no == line_no)
        return data.all()
    
    @classmethod
    def find_details(cls, po_no, pi_no = None, item_no = None, line_no = None, flag = None):
        data = DBSession.query(cls).filter(cls.active == 0).filter(cls.po_no == po_no)
        if pi_no: data = data.filter(cls.pi_no == pi_no)
        if item_no: data = data.filter(cls.item_no == item_no)
        if line_no: data = data.filter(cls.line_no == line_no)
        if flag: data = data.filter(cls.flag == flag)
        return data.all()
    
    @classmethod
    def parse_details(cls, po_no, pi_no = None, item_no = None, line_no = None, flag = None):
        oos, nns, rrs, cn = [], [], [], []
        details = cls.find_details(po_no, pi_no, item_no, line_no, flag)
        for i in details:
            co_detail = i.co_detail
            if co_detail.o_head_id and co_detail.active == 0:
                oos.append(i)
            elif co_detail.n_head_id and co_detail.active == 0:
                nns.append(i)
        for o in oos:
            cn_qty = 0
            for i in nns:
                chead = CHead.get(i.co_detail.n_head.chead_id)
                if chead.t_head_id == o.co_detail.o_head.thead_id and chead.id not in cn:
                    cn_qty += i.pi_qty
                    cn.append(chead.id)
            o.curr_qty = o.pi_qty - cn_qty 
            rrs.append(o)
        return rrs

    @classmethod
    def find_related_mcn(cls, detail):
        return DBSession.query(cls).filter(cls.active == 0).filter(cls.pi_no == detail.pi_no).filter(cls.po_no == detail.po_no)\
                .filter(cls.po_line_no == detail.po_line_no).filter(cls.n_head_id  != None)\
                    .filter(cls.grn_no == detail.grn_no).filter(cls.grn_line_no == detail.grn_line_no).all()
    
    @classmethod
    def find_variance(cls, **kw):
        result = []
        static_count = 10
        pi_no = kw.get('pi_no', '').strip()
        note_no = kw.get('note_no', '').strip()
        if note_no:
            ui = UI.find_by_note(note_no)
            supplier  = Supplier.get_detail_by_supplier(ui.supplier)
            uicharges = UICharge.find_details_by_note_no(note_no)
            ui_details, uicharges, include_tax = _all_rewrite_price_and_filter_charges(uicharges, [])
            for uicharge in uicharges:
                uicharge = copy.deepcopy(uicharge)
                variance = Variance.get_charge(uicharge.note_no, const.ERP_TYPE_OTHER_CHARGE, uicharge.line_no)
                if variance: continue
                uicharge.head_type = const.ERP_TYPE_OTHER_CHARGE
                uicharge.so_no = None
                uicharge.po_no = None
                uicharge.item_no = uicharge.chg_discount_code
                uicharge.purchase_invoice_no = ui.pi_no
                uicharge.charge_total = 0
                uicharge.currency = ui.ccy
                uicharge.designation = ui.department
                uicharge.po_qty = None
                uicharge.with_out_price = None
                uicharge.exchange_rate = ui.exchange_rate
                uicharge.with_out_amount = None
                uicharge.change_with_out_price  = None
                uicharge.supplier_short_name = supplier.supl_short_name
                if ui.note_type == 'C':
                    uicharge.change_with_out_amount = -uicharge.total
                    uicharge.variance_amount =  -uicharge.total
                else:
                    uicharge.change_with_out_amount = uicharge.total
                    uicharge.variance_amount = uicharge.total
                uicharge.variance_price = None
                uicharge.billing_month = None
                uicharge.change_project = None
                result.append(uicharge)
            return result, 0, 0
        else:
            piderp = None
            if pi_no:
                piderp = PID.get_details_by_pi_no(pi_no)
            counts = DBSession.query(distinct(cls.id)).filter(cls.active == 0)
            if piderp:
                counts = counts.filter(cls.po_no == piderp.po_no).count()
            else:
                counts = counts.count()
            if counts < static_count:
                range_count = [0]
            else:
                range_count = range(counts/static_count + 1)
            pos, pis, pisd, pos_charge, ppost_po, post_pi, post_po = {}, {}, {}, {}, [], [], {}
            for i in range_count:
                podetails = DBSession.query(cls).filter(cls.active == 0)
                if piderp:
                    podetails = podetails.filter(cls.po_no == piderp.po_no)
                podetails = podetails[i*static_count:(i+1)*static_count]
                for podetail in podetails:
                    if podetail.n_head_id:continue
                    if not pos.get(podetail.po_no):
                        supplier  = Supplier.get_detail_by_supplier(podetail.supplier)
                        pods = POD.find_details(podetail.po_no)
                        pochargs = POCharge.find_details_by_all(podetail.po_no)
                        pods, pochargs, include_tax = _all_rewrite_price_and_filter_charges(pochargs, pods)
                        pocharge_bridge = []
                        for pocharg in pochargs:
                            pocharg.ae  = podetail.ae
                            pocharg.so_no = podetail.sales_contract_no
                            pocharg.supplier_short_name = supplier.supl_short_name
                            pocharg.currency = podetail.currency
                            pocharg.purchase_invoice_no = podetail.pi_no
                            pocharg.po_no = podetail.po_no
                            pocharge_bridge.append(pocharg)
                        pos.update({podetail.po_no:{'pods':pods, 'pochargs':pocharge_bridge}})
                    else:
                        pods, pochargs = pos[podetail.po_no]['pods'], pos[podetail.po_no]['pochargs']
                    erp_pis = PID.find_details_by_po_no(podetail.po_no)
                    for erp_pi in erp_pis:
                        erp_pi.pi_no = erp_pi.purchase_invoice_no
                        if not pis.get(erp_pi.pi_no):
                            pids = PID.find_details_by_pi_no(erp_pi.pi_no)
                            picharges = PICharge.find_details_by_pi(erp_pi.pi_no)
                            pids, picharges, include_tax = _all_rewrite_price_and_filter_charges(picharges, pids)
                            pid_bridge = []
                            for pid in pids:
                                pid.ae  = podetail.ae
                                pid.so_no = podetail.sales_contract_no
                                pid_bridge.append(pid)
                            picharge_bridge = []
                            for picharge in picharges:
                                picharge.ae = podetail.ae
                                picharge.so_no = podetail.sales_contract_no
                                picharge.supplier_short_name = pid_bridge[0].supplier_short_name
                                picharge_bridge.append(picharge)
                            pis.update({erp_pi.pi_no:{'pids':pid_bridge, 'picharges':picharge_bridge}})
                    for pod in pods:
                        if pod.stock_item_no == podetail.item_no and pod.line_no == podetail.line_no:
                            if abs(float(pod.unit_price) - float(podetail.unit_price)) > Decimal('0.00005'):
                                if podetail.pi_no:
                                    #if pi_no and podetail.pi_no != pi_no:continue
                                    pids, picharges = pis[podetail.pi_no]['pids'], pis[podetail.pi_no]['picharges']
                                    for pid in pids:
                                        if pid.grn_no == podetail.grn_no and pid.grn_line_no == podetail.grn_line_no:
                                            pi_key = '%s_%s_%s' % (podetail.pi_no, podetail.grn_no, podetail.grn_line_no)
                                            if abs(Decimal(pid.unit_price) - Decimal(podetail.pi_unit_price)) > Decimal('0.00005'):
                                                if pisd.get(pi_key):
                                                    pisd[pi_key]['qty']    += int(podetail.pi_qty)
                                                    pisd[pi_key]['amount'] += Decimal(podetail.pi_total)
                                                else:
                                                    pisd.update({pi_key:{
                                                                        'qty':int(podetail.pi_qty), 
                                                                        'amount':Decimal(podetail.pi_qty*podetail.pi_unit_price), 
                                                                        'unit_price':Decimal(podetail.pi_unit_price), 
                                                                        'so_no':podetail.sales_contract_no,
                                                                        'ae':podetail.ae,
                                                                        'pidetail':pid
                                                                        }})
                                            else:
                                                post_pi.append(pi_key)
                                                po_key = "%s_%s_%s" % (podetail.po_no, pod.stock_item_no, pod.line_no)
                                                if post_po.get(po_key):
                                                    post_po[po_key].append(podetail)
                                                else:
                                                    post_po.update({po_key:[podetail]})
                                else:
                                    pass
                    if podetail.po_no in ppost_po:
                        continue
                    cpcharges = CpCharge.find_charges_by_po_no(podetail.po_no)
                    for cpcharge in cpcharges:
                        supplier = Supplier.get_detail_by_supplier(cpcharge.supplier)
                        charge_key = '%s_%s_%s' % (cpcharge.po_no, cpcharge.charge_code, cpcharge.line_no)
                        if pos_charge.get(charge_key):
                            pos_charge[charge_key]['amount'] += Decimal(cpcharge.po_total)
                        else:
                            pos_charge.update({charge_key:{
                                                           'amount':Decimal(cpcharge.po_total), 
                                                           'so_no':cpcharge.so_no, 
                                                           'ae':cpcharge.ae, 
                                                           'supplier_short_name':supplier.supl_short_name,
                                                           'pocharge':cpcharge
                                                           }})
                    ppost_po.append(podetail.po_no)
                                                                                                                                                                                    
            for po_no, pods in pos.iteritems():
                pocharges = pods['pochargs']
                cpcharges = CpCharge.find_charges_by_po_no(po_no)
                for pocharge in pocharges:
                    post_charge = None
                    for cpcharge in cpcharges:
                        if pocharge.charge_code == cpcharge.charge_code and pocharge.line_no == cpcharge.line_no:
                            post_charge = True
                    if not post_charge:
                        variances = Variance.get_charge(po_no, const.ERP_TYPE_PO_CHARGE, pocharge.line_no, pocharge.charge_code)
                        variance_amount = 0
                        for variance in variances:
                            variance_amount += variance.variance_amount
                        if abs(Decimal(pocharge.total) - variance_amount) > Decimal('0.05'):
                            pocharge.head_type = const.ERP_TYPE_CHARGE
                            pocharge.purchase_invoice_no = None
                            pocharge.item_no = pocharge.charge_code
                            pocharge.designation = None
                            pocharge.po_qty = None
                            pocharge.with_out_price = None
                            pocharge.exchange_rate = None
                            pocharge.with_out_amount = None
                            pocharge.change_with_out_price  = None
                            pocharge.change_with_out_amount = Decimal(pocharge.total)
                            pocharge.variance_amount =  Decimal(pocharge.total) - variance_amount
                            pocharge.variance_price = None
                            pocharge.billing_month  = None
                            pocharge.change_project = None
                            result.append(pocharge)
  
                
            for pi_no, pids in pis.iteritems():
                pidetails = pids['pids']
                picharges = pids['picharges']
                for pidetail in pidetails:
                    pidetail = copy.deepcopy(pidetail)
                    pi_key = '%s_%s_%s' % (pidetail.purchase_invoice_no, pidetail.grn_no, pidetail.grn_line_no) 
                    po_key = "%s_%s_%s" %(pidetail.po_no, pidetail.item_no, pidetail.po_line_no)
                    related_pi = post_po.get(po_key, [])
                    if pi_key not in post_pi:
                        post_related = None
                        for related in related_pi:
                            if related.grn_no == pidetail.grn_no and related.grn_line_no == pidetail.grn_line_no:
                                post_related = True
                        if not post_related:
                            continue
                        variances = Variance.get(pidetail.grn_no, pidetail.grn_line_no)
                        variance_amount, related_amount = 0, 0
                        for variance in variances:
                            if pidetail.purchase_invoice_no == variance.pi_no:
                                ids = variance.related.split(',')
                                for id in ids:
                                    cpdetail = cls.get(id)
                                    related_amount += cpdetail.pi_total
                                variance_amount += Decimal(variance.variance_amount)
                        if abs(pidetail.item_total - related_amount - variance_amount) > Decimal('0.005'):
                            pidetail.related_pi = related_pi
                            pidetail.head_type = const.ERP_TYPE_DETAIL
                            pidetail.po_qty = int(pidetail.qty)
                            pidetail.designation = pidetail.ae
                            pidetail.with_out_price = 0
                            pidetail.with_out_amount = 0
                            pidetail.change_with_out_price  = pidetail.unit_price
                            pidetail.change_with_out_amount = pidetail.item_total
                            pidetail.variance_price = pidetail.unit_price
                            pidetail.variance_amount =  pidetail.item_total - related_amount - variance_amount
                            pidetail.billing_month = None
                            pidetail.change_project = None
                            result.append(pidetail)
                            
            for key, detail in pisd.iteritems():
                pi_no, grn_no, grn_line_no = key.split('_')
                pi_qty, pi_amount, unit_price, so_no, ae, curr_pidetail = detail['qty'], detail['amount'], detail['unit_price'], detail['so_no'], detail['ae'], detail['pidetail']
                pidetails = pis[pi_no]['pids']
                picharges = pis[pi_no]['picharges']
                post_pidetail = None
                variances = Variance.get(grn_no, grn_line_no)
                variance_amount = 0
                for variance in variances:
                    variance_amount += Decimal(variance.variance_amount)
                for pidetail in pidetails:
                    if pidetail.grn_no == grn_no and pidetail.grn_line_no == int(grn_line_no):
                        post_pidetail = pidetail
                        if not Decimal(pidetail.unit_price) == unit_price:
                            if  abs(pi_amount + variance_amount - Decimal(pi_qty * pidetail.unit_price)) <= Decimal('0.05'):
                                continue
                            pidetail = copy.deepcopy(pidetail)
                            pidetail.head_type   = const.ERP_TYPE_DETAIL
                            pidetail.so_no       = so_no
                            pidetail.designation = ae
                            pidetail.po_qty      = int(pi_qty)
                            pidetail.with_out_price  = unit_price
                            pidetail.with_out_amount = pi_amount
                            pidetail.change_with_out_price  = Decimal(pidetail.unit_price)
                            pidetail.change_with_out_amount = pidetail.change_with_out_price * pidetail.po_qty
                            pidetail.variance_price  = Decimal(pidetail.unit_price)- unit_price
                            pidetail.variance_amount = pi_amount + variance_amount - Decimal(pi_qty * pidetail.unit_price)
                            pidetail.billing_month  = None
                            pidetail.change_project = None
                            result.append(pidetail)
                            
                if not post_pidetail and curr_pidetail:
                    if  abs(Decimal(pi_qty * pidetail.unit_price) - variance_amount) <= Decimal('0.05'):
                        continue
                    curr_pidetail.head_type       = const.ERP_TYPE_DETAIL
                    curr_pidetail.so_no           = curr_pidetail.sales_contract_no
                    curr_pidetail.designation     = curr_pidetail.ae
                    curr_pidetail.po_qty          = int(pi_qty)
                    curr_pidetail.with_out_price  = unit_price
                    curr_pidetail.with_out_amount = pi_amount
                    curr_pidetail.change_with_out_price  = 0
                    curr_pidetail.change_with_out_amount = 0
                    curr_pidetail.variance_price  = unit_price
                    curr_pidetail.variance_amount = Decimal(curr_pidetail.po_qty * unit_price) - variance_amount
                    curr_pidetail.billing_month   = None
                    curr_pidetail.change_project  = None
                    result.append(curr_pidetail)
                    

            for key, charge in pos_charge.iteritems():
                po_no, charge_code, line_no = key.split("_")
                amount, so_no, ae, supplier_short_name, curr_pocharge = charge['amount'], charge['so_no'], charge['ae'], charge['supplier_short_name'], charge['pocharge']
                pocharges = pos.get(po_no, {}).get('pochargs', [])
                post_pocharge = None
                variances = Variance.get_charge(po_no, const.ERP_TYPE_PO_CHARGE, line_no, charge_code)
                variance_amount = 0
                for variance in variances:
                    variance_amount += variance.variance_amount
                for pocharge in pocharges:
                    if charge_code == pocharge.charge_code and int(line_no) == int(pocharge.line_no):
                        pocharge = copy.deepcopy(pocharge)
                        post_pocharge = pocharge
                        if Decimal(pocharge.total) == amount:continue
                      
                        if abs(Decimal(pocharge.total) + variance_amount - amount)<= Decimal('0.05'):
                            continue
                        pocharge.head_type = const.ERP_TYPE_CHARGE
                        pocharge.so_no    = so_no
                        pocharge.item_no  = charge_code
                        pocharge.currency = None
                        pocharge.designation = ae
                        pocharge.po_qty      = None
                        pocharge.with_out_price  = None
                        pocharge.exchange_rate   = None
                        pocharge.with_out_amount = amount
                        pocharge.change_with_out_price  = None
                        pocharge.supplier_short_name    = supplier_short_name
                        pocharge.change_with_out_amount = Decimal(pocharge.total)
                        pocharge.variance_amount =  Decimal(pocharge.total) + variance_amount - amount
                        pocharge.variance_price  = None
                        pocharge.billing_month   = None
                        pocharge.change_project  = None
                        result.append(pocharge)
                
                if not post_pocharge and curr_pocharge:
                    if abs(variance_amount - Decimal(curr_pocharge.po_total))> Decimal('0.05'):
                        curr_pocharge.head_type = const.ERP_TYPE_PO_CHARGE
                        curr_pocharge.purchase_invoice_no = curr_pocharge.pi_no
                        curr_pocharge.so_no    = so_no
                        curr_pocharge.item_no  = charge_code
                        curr_pocharge.currency = None
                        curr_pocharge.designation = ae
                        curr_pocharge.po_qty      = None
                        curr_pocharge.with_out_price  = None
                        curr_pocharge.exchange_rate   = None
                        curr_pocharge.with_out_amount = amount
                        curr_pocharge.change_with_out_price  = None
                        curr_pocharge.supplier_short_name    = supplier_short_name
                        curr_pocharge.change_with_out_amount = None
                        curr_pocharge.variance_amount = variance_amount - Decimal(curr_pocharge.po_total)
                        curr_pocharge.variance_price  = None
                        curr_pocharge.billing_month   = None
                        curr_pocharge.change_project  = None
                        result.append(curr_pocharge)
                
        return result, 0, 0
                            

    @classmethod
    def update_pi_flag(cls, po_no, pi_no, item_no):
        cpdetails = cls.find_details(po_no, pi_no, item_no)
        for cpdetail in cpdetails:
            if cpdetail.flag == 1:
                cpdetail.flag = 0
                DBSession.merge(cpdetail)
                     
class CpCharge(Table_CpCharge):  
    
    @classmethod
    def find(cls, ** args):
        rs = []
        ref, po, pi, customer_code, customer_name \
                        = [args.get(i) for i in ['ref', 'po_no', 'pi_no', 'customer_code', 'customer_name']]
        limit = int(args.get("page", 0))
        offset = limit + 25
        if args.get("cate") == "pre":
            cate = 'pre'
            limit = int(args.get("limit", 0)) 
            offset = int(args.get("offset", 0))
        queryExtend = QueryExtend(CoDetail, ** args)
        queryExtend.query_all(True, DBSession, None, limit, offset, ** {
                      const.QUERY_TYPE_LIKE: ['sales_contract_no', 'invoice_no', 'item_no'],
                      const.QUERY_TYPE_DATE: [('create_time', 'date_from', 'date_to')],
                      const.QUERY_TYPE_ORDER_BY: ['create_time'],
                      const.QUERY_TYPE_COMPANY_CODE: ['company_code']
                      })
        codetails = queryExtend.result
        picharges =  cls.find_new_charge(codetails)
        for picharge in picharges:
            if po and picharge.po_no != po:
                continue
            if pi and picharge.pi_no != pi:
                continue
            if ref and picharge.ref != ref:
                continue
            if customer_code and picharge.customer_code != customer_code:
                continue
            if customer_name and picharge.customer_name != customer_name:
                continue
            if hasattr(picharge, 'pi_no'): 
                rs.append(picharge)
        return rs , offset, limit
    
    @classmethod
    def find_new_charge(cls, codetails):
        result, oheads, o_head_ids, p = [], [], [], {}
        for codetail in codetails:
            if codetail.o_head_id not in o_head_ids:
                o_head_ids.append(codetail.o_head_id)
                if codetail.o_head:
                    oheads.append(codetail.o_head)

        for ohead in oheads:
            for cpcharge in ohead.cp_charges:
                vat_total = cls.find_all_pi_charge(cpcharge)
                if Decimal(cpcharge.all_total) - Decimal(vat_total) > Decimal(0.05):
                    l, c = {}, []
                    if not cpcharge.po_no:continue
                    picharges = PICharge.find_details_by_po_no(cpcharge.po_no)
                    for picharge in picharges:
                        if l.get(picharge.purchase_invoice_no):
                            l[picharge.purchase_invoice_no].append(picharge)
                        else:
                            l.update({picharge.purchase_invoice_no:[picharge]})  
                             
                    for key, value in l.iteritems():
                        pids = PID.find_details_by_pi_no(key)
                        picharges = PICharge.find_details_by_all(key)
                        details, charges, tax = _all_rewrite_price_and_filter_charges(picharges, pids)
                        c.extend(charges)

                    for picharge in c:
                        pi_total = 0
                        if cpcharge.charge_code in const.CHARGE_CODES.get(picharge.charge_code, []):
                            if (cpcharge.pi_no and cpcharge.pi_line_no == picharge.line_no) or \
                                    (cpcharge.line_no == picharge.po_chrg_line_no and cpcharge.po_no == picharge.po_no):
                                picharge.pi_no = picharge.purchase_invoice_no
                                cpcharges = cls.find_charge(picharge.pi_no, picharge.po_chrg_line_no, picharge.line_no)
                                cpcharge_total = 0
                                for cpc in cpcharges:
                                    if cpc.o_head_id:
                                        cpcharge_total += cpc.total
                                pi_total += float(picharge.total)
                                pi_total -= float(cpcharge_total)
                                key = "%s_%s" % (picharge.purchase_invoice_no, picharge.line_no)
                                if pi_total > 0.005 and pi_total - p.get(key, 0) > 0.005:
                                    if abs(float(cpcharge.all_total) - float(picharge.total)) > 0.005:
                                        picharge.variance_type = True
                                    picharge.pi_line_no  = picharge.line_no
                                    picharge.line_no     = cpcharge.line_no
                                    picharge.cpcharge_id = cpcharge.id
                                    picharge.total       = pi_total
                                    picharge.o_head_id   = ohead.id
                                    picharge.pi_no       = picharge.purchase_invoice_no
                                    picharge.cst_id      = ohead.id
                                    picharge.cst_ref     = ohead.ref
                                    picharge.po_total    = float(cpcharge.all_total) - float(vat_total)
                                    picharge.all_total   = cpcharge.all_total
                                    picharge.ava_total   = pi_total
                                    if p.get(key):
                                        p[key] += picharge.ava_total
                                    else:
                                        p.update({key:picharge.ava_total})
                                    result.append(picharge)
        return result
                            
    @classmethod
    def create(cls, details, ** args):
        for detail in details:
            if args.get('n_head_id'):
                keys = ['n_head_id', 'type', 'status', 'supplier', 'supplier_name', 'supplier_short_name', 'company_code', 'line_no', 'pi_line_no',
                    'charge_code', 'total', 'all_total', 'po_total', 'pi_no', 'po_no', 'note_type', 'note_date', 'status',
                    'note_no', 'cust_code', 'cust_name', 'ae', 'so_no', 'currency', 'exchange_rate']
            else:
                cls.delete_charge(detail)
                keys = ['o_head_id', 'type', 'status', 'supplier', 'supplier_name', 'supplier_short_name', 'company_code', 'line_no', 'pi_line_no',
                    'charge_code', 'total', 'all_total', 'so_no', 'po_total', 'pi_no', 'po_no', 'note_type', 'note_date', 'status',
                    'note_no', ('cust_code', 'customer_code'), ('cust_name', 'customer_name'),'ae', 'currency', 'exchange_rate']
            params   = _get_params_from_args_and_obj(keys, detail, ** args)
            cpCharge = cls( ** params)
            DBSession.add(cpCharge)
            
    @classmethod
    def find_relate_charge(cls, detail):
        return DBSession.query(cls).filter(cls.active == 0).filter(cls.pi_no == detail.pi_no).filter(cls.po_no == detail.po_no)\
                        .filter(cls.o_head_id == detail.o_head_id).filter(cls.line_no == detail.line_no).first()
                        
    @classmethod
    def find_po_charge(cls, detail):
        if not hasattr(detail, 'o_head_id'): return
        return DBSession.query(cls).filter(cls.active == 0).filter(or_(cls.pi_no == None, cls.total == 0)).filter(cls.po_no == detail.po_no)\
                        .filter(cls.o_head_id == detail.o_head_id).filter(cls.line_no == detail.line_no).all()
    
    @classmethod
    def find_all_po_charge(cls, detail):
        cpcharges  =  DBSession.query(cls).filter(cls.active == 0).filter(cls.po_no == detail.po_no).filter(cls.line_no == detail.line_no).all()
        pis = []
        po_total = 0
        for cpcharge in cpcharges:
            if hasattr(detail, 'o_head_id') and not cpcharge.o_head_id:continue
            if hasattr(detail, 'n_head_id') and not cpcharge.n_head_id:continue
            if hasattr(cpcharge, 'pi_no') and cpcharge.pi_no not in pis:
                po_total += float(cpcharge.po_total)
                pis.append(cpcharge.pi_no)
            elif not cpcharge.pi_no:
                po_total += float(cpcharge.po_total)
        return po_total
    
    @classmethod
    def find_all_pi_charge(cls, detail):
        cpcharges  =  DBSession.query(cls).filter(cls.active == 0).filter(cls.po_no == detail.po_no).filter(cls.line_no == detail.line_no).all()
        pi_total = 0
        for cpcharge in cpcharges:
            if hasattr(detail, 'o_head_id') and not cpcharge.o_head_id:continue
            if hasattr(detail, 'n_head_id') and not cpcharge.n_head_id:continue
            pi_total += float(cpcharge.total)
        return pi_total
                         
    @classmethod
    def delete_charge(cls, detail):
        cpcharges =  cls.find_po_charge(detail)
        if cpcharges:
            for cpcharge in cpcharges:
                DBSession.delete(cpcharge)
            
    @classmethod
    def get_charge_by_like(cls, note_no, line_no):
        return DBSession.query(cls).filter(cls.note_no == note_no).filter(cls.line_no == line_no).filter(cls.active == 0).all()
    
    @classmethod
    def find_charge(cls, pi_no, line_no = None, pi_line_no = None):
        data = DBSession.query(cls).filter(cls.pi_no == pi_no).filter(cls.active == 0)
        if line_no: data = data.filter(cls.line_no == line_no)
        if pi_line_no: data = data.filter(cls.pi_line_no == pi_line_no)
        return data.all()
    
    @classmethod
    def find_charges_by_po_no(cls, po_no):
        return DBSession.query(cls).filter(cls.po_no == po_no).filter(cls.active == 0).all()
    
    @classmethod
    def find_sum_qty(cls, charge):
        total = 0
        data = DBSession.query(cls).filter(cls.active == 0)
        if hasattr(charge, 'n_head_id'):
            data = data.filter(cls.n_head_id != None)
        if hasattr(charge, 'note_no') and charge.note_no:
            data = data.filter(cls.note_no == charge.note_no)
        if hasattr(charge, 'pi_no') and charge.pi_no:
            data = data.filter(cls.pi_no == charge.pi_no)
        cpcharges = data.all()
        for cpc in cpcharges:
            total += float(cpc.total)
        return total
                 
class OCharge(Table_OCharge):
    
    @classmethod
    def create(cls, charges=[], ** args):
        keys = []
        if args.get('o_head_id'):
            chargeType = const.ERP_HEAD_TYPE_CST
        else:
            chargeType = const.ERP_HEAD_TYPE_CCN
        for charge in charges:
            if u'\u7a0e' in charge.charge_code or u'\u7a05' in charge.charge_code:continue
            if charge.__tablename__ == "vat_pcharge":
                type = const.SEARCH_TYPE_PSIPSO
                keys = ['uuid', 'type', 'company_code', 'line_no', 'charge_code', 'total', 'vat_total', 
                        'invoice_no', 'po_no', 'p_charge_id',  'o_head_id',  'n_head_id' ]
            elif charge.__tablename__ == "t_purchase_invoice_charges":
                type = const.SEARCH_TYPE_PI
                keys = ['type', 'company_code', 'line_no', 
                        'charge_code', 'total',  ('vat_total','total'),
                        ('invoice_no', 'purchase_invoice_no'), 'po_no', 'o_head_id', 'n_head_id' ]
            elif charge.__tablename__ == "t_purchase_order_charges":
                type = const.SEARCH_TYPE_PO
                keys = [
                        'type', 'company_code',  'line_no', 'charge_code', 
                        'total', ('vat_total', 'total'), ('po_no', 'purchase_order_no'), 'o_head_id', 'n_head_id' ]
            args.update({'type':type})    
            params = _get_params_from_args_and_obj(keys, charge, ** args)
            detail = cls( ** params)
            all_charges = cls.find_details_by_type(detail, chargeType)
            cst_total = 0
            for a in all_charges:
                cst_total += a.vat_total
            detail.vat_total = detail.total - cst_total
            DBSession.add(detail)

    @classmethod
    def find_details_by_type(cls, charge, type = None):
        data = DBSession.query(cls).filter(cls.type == charge.type).filter(cls.charge_code == charge.charge_code).filter(cls.active == 0)
        if type == const.ERP_HEAD_TYPE_CST:
            data = data.filter(cls.o_head_id != None)
        if type == const.ERP_HEAD_TYPE_CCN:
            data = data.filter(cls.n_head_id != None)
        if type == const.SEARCH_TYPE_PI:
            data = data.filter(cls.invoice_no == charge.invoice_no)
        if type == const.SEARCH_TYPE_PO:
            data = data.filter(cls.po_no == charge.po_no)
        if type == const.SEARCH_TYPE_PSIPSO:
            data = data.filter(cls.invoice_no == charge.invoice_no)
        return data.all()

class Variance(Table_Variance):
    
    @classmethod
    def get(cls, grn_no, grn_line_no):
        return DBSession.query(cls).filter(cls.grn_no == grn_no).filter(cls.grn_line_no == grn_line_no).filter(cls.active == 0).all()
    
    @classmethod
    def get_charge(cls, no, type = None, line_no = None, item_no = None):
        if type == const.ERP_TYPE_CHARGE:
            return DBSession.query(cls).filter(cls.pi_no == no).filter(cls.type == type).filter(cls.line_no == line_no).filter(cls.active == 0).all()
        elif type == const.ERP_TYPE_OTHER_CHARGE:
            return DBSession.query(cls).filter(cls.note_no == no).filter(cls.type == type).filter(cls.line_no == line_no).filter(cls.active == 0).all()
        elif type == const.ERP_TYPE_PO_CHARGE:
            return DBSession.query(cls).filter(cls.po_no == no).filter(cls.item_no == item_no).filter(cls.line_no == line_no).filter(cls.active == 0).all()
        else:
            return DBSession.query(cls).filter(cls.pi_no == no).filter(cls.type.in_([const.ERP_TYPE_CHARGE, const.ERP_TYPE_OTHER_CHARGE])).filter(cls.active == 0).all()
        
    @classmethod
    def find(cls):
        return DBSession.query(cls).filter(cls.active == 0).all()

class Supplier(Table_Supplier):
    
    @classmethod
    def get_detail_by_supplier(cls, supplier):
        return DBSession2.query(cls).filter(cls.supl_code == supplier).first()
    
    
class DN(Table_DN):
    
    @classmethod
    def find(cls, sc_no):
        return  DBSession2.query(cls).filter(cls.sc_no == sc_no).all()
    
    @classmethod
    def find_dn(cls, sc_no):
        result = []
        data = cls.find(sc_no)
        for d in data:
            if d.dn_no not in result:
                result.append(d.dn_no)
        return result
 
    
class PIProceeds(Table_PIProceeds):
    
    @classmethod
    def find(cls, pi_no, item_code):
        return DBSession.query(cls).filter(cls.pi_no == pi_no).filter(cls.item_code == item_code).filter(cls.flag == 0).all()
    
    @classmethod
    def update_pi_flag(cls, pi_no, item_code):
        piproceeds = cls.find(pi_no, item_code)
        for piproceed in piproceeds:
            if piproceed.flag == 1:
                piproceed.flag = 0
                BDSession.merge(piproceed)
    

class DNProceeds(Table_DNProceeds):
    
    @classmethod
    def find(cls, po_no, pi_no, item_code):
        return DBSession.query(cls).filter(cls.other_ref == pi_no).filter(cls.item_code == item_code).filter(cls.flag == 0).all()
    
    @classmethod
    def update_pi_flag(cls, po_no, pi_no, item_code):
        dnproceeds = cls.find(po_no, pi_no, item_code)
        for dnproceed in dnproceeds:
            if dnproceed.flag == 1:
                dnproceed.flag = 0
                BDSession.merge(dnproceed)

class PICost(Table_PICost):
    
    @classmethod
    def find(cls, pi_no, item_code):
        return DBSession.query(cls).filter(cls.invoice_number == pi_no).filter(cls.item_code == item_code).filter(cls.flag == 0).all()
    
    @classmethod
    def find_by_po(cls, po_no, item_code):
        return DBSession.query(cls).filter(cls.po_no == po_no).filter(cls.item_code == item_code).filter(cls.flag == 0).all()
    
    @classmethod
    def update_pi_flag(cls, pi_no, item_code):
        picosts = cls.find(pi_no, item_code)
        for picost in picosts:
            if picost.flag == 1:
                picost.flag = 0
                BDSession.merge(picost)
            
    
class DNCost(Table_DNCost):
    
    @classmethod
    def find(cls, pi_no, item_code):
        return DBSession.query(cls).filter(cls.other_ref == pi_no).filter(cls.item_code == item_code).filter(cls.flag == 0).all()
    
    @classmethod
    def find_by_po(cls, po_no, item_code):
        return DBSession.query(cls).filter(cls.po_no == po_no).filter(cls.item_code == item_code).filter(cls.flag == 0).all()
            
    @classmethod
    def update_pi_flag(cls, pi_no, item_code):
        dncosts = cls.find(pi_no, item_code)
        for dncost in dncosts:
            if dncost.flag == 1:
                dncost.flag = 0
                BDSession.merge(dncost)



class Period(Table_Period):
    
    @classmethod
    def get(cls, date, company_code = None):
        return DBSession.query(cls).filter(cls.date == date).filter(cls.company_code == company_code).first()
    
    
    @classmethod
    def find(cls, date = None):
        query =  DBSession.query(cls).filter(cls.company_code.in_(getCompanyCode()))
        if date:
            query = query.filter(cls.date <= date)
        return query.all()
            
    
    @classmethod
    def find_by_column(cls, item_code= None, date = None):
        d = {}
        if item_code:
            rows = PeriodDetail.find(item_code, date)
        else:
            rows = cls.find(date)
        for row in rows:
            for columnName in row.__table__.columns.keys():
                if 'qty' in columnName or 'amount' in columnName:
                    if not d.get(columnName):d.update({columnName:0})
                    d[columnName] += getattr(row, columnName)
        return d
    
    @classmethod
    def find_all_by_item(cls, item_code = None, date=None):
        qty, amount = 0, 0
        keys = ['piproceeds_qty','piproceeds_amount','dnproceeds_qty','dnproceeds_amount','picost_qty','picost_amount','dncost_qty','dncost_amount']
        datas = cls.find_by_column(item_code, date)
        piproceeds_qty, piproceeds_amount, dnproceeds_qty, dnproceeds_amount, picost_qty, picost_amount, dncost_qty, dncost_amount =  [datas.get(key, 0) for key in keys]
        qty += (piproceeds_qty - dnproceeds_qty) - (picost_qty - dncost_qty)
        amount += (piproceeds_amount - dnproceeds_amount) - (picost_amount - dncost_amount)
        return qty, amount
        
    @classmethod
    def update_pi_flag(cls, pi_no, item_code, po_no = None):
        PIProceeds.update_pi_flag(pi_no, item_code)
        DNProceeds.update_pi_flag(po_no, pi_no, item_code)
        PICost.update_pi_flag(pi_no, item_code)
        DNCost.update_pi_flag(pi_no, item_code)
        PiDetail.update_pi_flag(pi_no, item_code)
        CpDetail.update_pi_flag(po_no, pi_no, item_code)


class PeriodDetail(Table_PeriodDetaul):
    
    @classmethod
    def get(cls, item_code, date = None, company_code = None):
        query = DBSession.query(cls).filter(cls.item_code == item_code).filter(cls.company_code == company_code)
        if date:
           query = query.filter(cls.date == date) 
        return query.first()
    
    
    @classmethod
    def find(cls, item_code = None, date = None):
        query =  DBSession.query(cls)
        if item_code:
            query = query.filter(cls.item_code == item_code).filter(cls.company_code.in_(getCompanyCode()))
        if date:
            query = query.filter(cls.date <= date)
        return query.all()
            
    
        
    