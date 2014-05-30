
def login():
    import pycurl
    curlobj=pycurl.Curl()
    curlobj.setopt(pycurl.URL, 'http://192.168.20.55:100/login_handler?__logins=0&came_from=192.168.20.55:100/post_login')
    curlobj.setopt(pycurl.POSTFIELDS, 'login=admin&password=ecrmadmin');
    curlobj.setopt(pycurl.COOKIEFILE, "cookies.txt")
    curlobj.setopt(pycurl.COOKIEJAR, "cookies.txt")
    curlobj.perform()
    curlobj.close()


def request_scheduled_tasks():
    import sys, os, re, pycurl, StringIO
    strio=StringIO.StringIO()
    curlobj=pycurl.Curl()
    curlobj.setopt(pycurl.URL, 'http://192.168.20.55:100/ap/import_statement_dzd')
    curlobj.setopt(pycurl.COOKIEFILE, "cookies.txt")
    curlobj.setopt(pycurl.WRITEFUNCTION, strio.write)
    curlobj.perform()
    curlobj.close()
    print strio.getvalue()
    
def scheduled_tasks():
    login()
    request_scheduled_tasks()
   

scheduled_tasks()