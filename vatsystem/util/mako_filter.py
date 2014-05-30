# -*- coding: utf-8 -*-
from datetime import date
from datetime import timedelta
from vatsystem.model import *



b = lambda v:"&nbsp;" if not v else v
na = lambda v: 'N/A' if not v else v
pd = lambda v:"&nbsp;" if not v else str(v)[0:10]
pt = lambda v:" " if not v else str(v)[0:19]
pi = lambda v:0 if not v else int(v)
pq = lambda v:0 if not v else -float(v)
pn = lambda v:0 if not v else v

def tp(v):
    if not v : return "&nbsp;"
    return "<span class='tooltip' title='%s'>%s</span>" % (v,v)

def pf(v):
    if not v: return 0
    else:
        v = float('%.6f' % float(v))
        return 0 if v == 0 else v
    
def pf2(v):
    if not v: return 0
    else:
        v = float('%.2f' % float(v))
        return 0 if v == 0 else v

def pipo(i):
    if hasattr(i, 'invoice_no'):
        a = i.invoice_no
    elif hasattr(i, 'purchase_invoice_no'):
        a = i.purchase_invoice_no
    elif hasattr(i, 'purchase_order_no'):
        a = i.purchase_order_no
    return a

def last_month():
    format = '%Y-%m-%d'
    today = date.today()
    month = timedelta(days=30)
    return [(today - month).strftime(format), today.strftime(format)]

def get_last_line_no(tHead_id):
    sql ='''select MAX(line_no)+1 from vat_charge where (type='T_ERP' or type='T_Manual') and t_head_id='%s' ''' % (tHead_id)
    max_len_no =  DBSession.execute(sql).fetchone()
    if max_len_no[0]==None:
        return 1
    else:
        return max_len_no[0]

def get_sum_vat_total(tHead_id,line_no,id):
    sql ='''select sum(vat_total) from vat_charge where (type='C_ERP' or type='C_Manual') and t_head_id='%s' and line_no='%s' and id !='%s' and active=0 ''' % (tHead_id,line_no,id)
    sum_vat_total =  DBSession.execute(sql).fetchone()
    if sum_vat_total[0]==None:
        return 0
    else:
        return sum_vat_total[0]
    
def get_the_cn_detail(invoice_no,item_no,line_no):
    sql = ''' SELECT note_qty FROM "RPAC"."T_CUST_NOTE_DTL" where INVOICE_NO='%s' and ITEM_NO='%s' and invoice_item_line_no='%s' ''' % (invoice_no,item_no,line_no)
    cn_detail = DBSession2.execute(sql).fetchone()
    if cn_detail==None:
        return 0
    else:
        return int(cn_detail[0])
    
def get_cn_total(invoice_no,chg_discount_code):
    sql = '''
            SELECT TNC.TOTAL FROM "RPAC"."T_CUST_NOTE_CHARGES" TNC,"RPAC"."T_CUST_NOTE_DTL" TCN  
                WHERE TNC.NOTE_NO=TCN.NOTE_NO AND TCN.INVOICE_NO='%s' AND TNC.CHG_DISCOUNT_CODE='%s'
            '''  % (invoice_no,chg_discount_code)
    the_cn_total =  DBSession2.execute(sql).fetchone()
    if the_cn_total==None:
        return 0
    else:
        return the_cn_total[0]

def get_si_detail_total(invoice_no,item_no,id,line_no):
    sql = '''SELECT sum(vat_qty) FROM "public"."vat_si_detail" where invoice_no='%s' and item_no='%s' and id != '%s' and line_no='%s' and active=0''' % (invoice_no,item_no,id,line_no)
    si_detail_total =  DBSession.execute(sql).fetchone()
    if si_detail_total[0] == None:
        return 0
    else:
        return int(si_detail_total[0])