# -*- coding: utf-8 -*-

import datetime
from datetime import date, datetime as dt
from email import Encoders
from email.header import Header
import os
import pickle
import random
import smtplib
import traceback
import calendar
from decimal import Decimal

from email.MIMEBase import MIMEBase
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE
from email.Utils import formatdate
from tg import flash
from tg import redirect
from tg import response
from tg import session
from tg import config
from vatsystem.model import *
from vatsystem.util import const


from sqlalchemy import *
from sqlalchemy.sql import and_

DISPLAY_DATE_FORMAT="%Y-%m-%d"


__all__=['getCompanyCode', "tabFocus", "Date2Text", "getOr404",
         "sendEmail", "number2alphabet", "serveFile", 'alphabet2number',
         'gerRandomStr', 'allAlpha', 'comp', '_get_params_from_args_and_obj', '_orderly_dict', '_get_lastday_of_month', 'CRef']

def comp(obj,compObj):
    if type(obj) == type(1):compObj = int(compObj)
    if type(obj) == type(Decimal("1.00")):
        obj     = float(str(obj))
        if compObj:
            compObj = float(str(compObj))
    if type(obj) == type(u'') or type(compObj) == type(u''):
        obj     = obj.encode("utf-8").replace("\r\n",'') if obj else None
        if compObj:
            compObj = compObj.encode("utf-8")
    return [True,str(obj),str(compObj)] if not obj==compObj else [False]
        
           
    
def getCompanyCode(type = None):
    company_code = [session['company_code']]
    if type == 1: company_code = "('%s')"  % session['company_code']
    return company_code
        

def tabFocus(tab_type=""):
    def decorator(fun):
        def returnFun(*args, ** keywordArgs):
            returnVal=fun(*args, ** keywordArgs)
            if type(returnVal)==dict and "tab_focus" not in returnVal:
                returnVal["tab_focus"]=tab_type
            return returnVal
        return returnFun
    return decorator


def Date2Text(value=None, dateTimeFormat=DISPLAY_DATE_FORMAT, defaultNow=False):
    if not value and defaultNow: value=datetime.now()

    format=dateTimeFormat
    result=value

    if isinstance(value, date):
        try:
            result=value.strftime(format)
        except:
            traceback.print_exc()
    elif hasattr(value, "strftime"):
        try:
            result=value.strftime(format)
        except:
            traceback.print_exc()

    if not result:
        result=""

    return result

def getOr404(obj, id, redirect_url="/index", message="The record deosn't exist!"):
    try:
        v=DBSession.query(obj).get(id)
        if v: return v
        else: raise "No such obj"
    except:
        traceback.print_exc()
        flash(message)
        redirect(redirect_url)

def number2alphabet(n):
    result=[]
    while n>=0:
        if n>26:
            result.insert(0, n%26)
            n/=26
        else:
            result.insert(0, n)
            break
    return "".join([chr(r+64) for r in result]) if result else None

def alphabet2number(str):
    if not str or not isinstance(str, basestring): raise TypeError
    if not str.isalpha(): raise ValueError
    return  reduce(lambda a, b:  (a*26)+ord(b)-ord("a")+1, str.lower(), 0)

def sendEmail(send_from, send_to, subject, text, cc_to=[], files=[], server="192.168.42.13"):
    assert type(send_to)==list
    assert type(files)==list

    msg=MIMEMultipart()
    msg.set_charset("utf-8")
    msg['From']=send_from
    msg['To']=COMMASPACE.join(send_to)

    if cc_to:
        assert type(cc_to)==list
        msg['cc']=COMMASPACE.join(cc_to)
        send_to.extend(cc_to)

    msg['Date']=formatdate(localtime=True)
    msg['Subject']=subject

    msg.attach(MIMEText(text))

    for f in files:
        part=MIMEBase('application', "octet-stream")
        part.set_payload(open(f, "rb").read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"'%Header(os.path.basename(f), 'utf-8'))
        msg.attach(part)

    smtp=smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

def serveFile(fileName, contentType="application/x-download", contentDisposition="attachment", charset="utf-8"):
    response.headers['Content-type']='application/x-download' if not contentType else contentType
    #response.headers['Content-Disposition']="%s;filename=%s"%(contentDisposition, Header(os.path.basename(fileName), charset))
    response.headers['Content-Disposition']="%s;filename=%s"%(contentDisposition, os.path.basename(fileName).encode('utf-8'))
    f=open(fileName, 'rb')
    content="".join(f.readlines())
    f.close()
    return content

def defaultIfNone(blackList=[None, ], default=""):
    def returnFun(value):
        defaultValue=default() if callable(default) else default
        if value in blackList:
            return defaultValue
        else:
            try:
                return str(value)
            except:
                try:
                    return repr(value)
                except:
                    pass
        return defaultValue
    return returnFun



def _get_params_from_args_and_obj(keys, obj, ** args):
    params = {}
    for i in keys:
        if type(i) == dict:
            params.update(i)
        else:
            i, j = i if ((type(i) == list or type(i) == tuple) and len(i) == 2) else (i, i)
            if args.get(j) != None:
                params[i] = args.get(j)
            elif obj.__dict__.get(j) != None:
                params[i] = obj.__dict__[j]
    return params

def _orderly_dict(list, coor):
    new_list = {}
    for i in list:
        if new_list.get(i.get(coor)):
            new_list[i.get(coor)].append(i)
        else:
            new_list.update({i.get(coor):[i]})
    new_dict = []
    for key, value in new_list.iteritems():
        new_dict.extend(value)
    return new_dict

def _get_lastday_of_month(date_str):
    date_str = date_str.split(".")
    last_day = calendar.monthrange(int(date_str[0]), int(date_str[1]))[1]
    return datetime.datetime.strptime("%s.%s.%s" % (date_str[0], date_str[1], last_day if len(date_str) < 3 else date_str[2]), "%Y.%m.%d")

class CRef(object):
    
    def __init__(self):
        self.file = os.path.join(os.path.abspath(os.path.curdir), 'data', "ref.pickle")
    
    def save(self, **kwargs):
        pickle.dump(kwargs, open(self.file, "w"))
        
    def get(self, head_type):
        refTime = dt.now().strftime('%Y%m')[2:]
        if os.path.isfile(self.file):
            obj = pickle.load(open(self.file, 'r'))
            r = obj.get(head_type, 0) 
            if r and r != 0 and str(r)[:4] != refTime:
                r = 0
            else:
                r = int(r[4:]) if isinstance(r, str) else 0
            r = "%s%06d" % (refTime, r + 1)
            obj.update({head_type:r})
            self.save(**obj)
            return r
        else:
            r = "%s%06d" % (refTime, 1)
            self.save(**{head_type:r})
            return r
            
            
null2blank=defaultIfNone(blackList=[None, "NULL", "null", "None"])
numberAlpha=[str(a) for a in range(10)]
lowerAlpha=[chr(a) for a in range(ord("a"), ord("z")+1)]
upperAlpha=[chr(a) for a in range(ord("A"), ord("Z")+1)]
allAlpha=numberAlpha+lowerAlpha+upperAlpha
gerRandomStr=lambda str_length, randomRange=numberAlpha : "".join(random.sample(randomRange, str_length))



