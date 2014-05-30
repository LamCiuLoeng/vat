# -*- coding: utf-8 -*-
import ldap, traceback
ldap.set_option(ldap.OPT_REFERRALS, 0)
from tg import config
from vatsystem.util.common import *
from repoze.who.plugins.sa import SQLAlchemyAuthenticatorPlugin, SQLAlchemyUserMDPlugin
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class MyAuthMixin(object):
    def get_user(self, value):
        try:
            return self.user_class.identify(value)
        except (NoResultFound, MultipleResultsFound):
            return None

class MySQLAlchemyAuthenticatorPlugin(MyAuthMixin, SQLAlchemyAuthenticatorPlugin):

    def authenticate(self, environ, identity):
        def _auth_db():
            validator=getattr(user, self.translations['validate_password'])
            if validator(identity['password']):
                return identity['login']

        def _auth_ad():
            password=identity['password']
            del identity['password']
            try:
                rc=ldapcon.simple_bind(dn, password)
                ldapcon.result(rc)
                return identity['login']
            except ldap.INVALID_CREDENTIALS:
                return None
            finally:
                try:
                    ldapcon.unbind()
                except ldap.LDAPError, e:
                    pass

        if not ('login' in identity and 'password' in identity): return None
        if not identity["login"] or not identity["password"]: return None
        user=self.get_user(identity['login'])
        if user and user.user_name!='admin':
            ignore_user_list=config.get('ignore_user_list', '').split(',')
            for i in ignore_user_list:
                if i.strip().upper()==identity['login'].upper(): return _auth_db()
            ldapConfig=config.ldap
            ldapcon=ldap.initialize("ldap://%s:%d"%(ldapConfig.host, ldapConfig.port))
            ldapcon.simple_bind_s(ldapConfig.initdn, ldapConfig.initpw)
            filter="(sAMAccountName=%s)"%identity['login']
            dn=None

            for bdn in ldapConfig.basedn:
                rc=ldapcon.search(bdn, ldap.SCOPE_SUBTREE, filter)
                objects=ldapcon.result(rc)[1]
                if len(objects)==1:
                    dn=objects[0][0]
                    break
            else:  
                return _auth_db()
            return _auth_ad()
        elif user:
            return identity['login']


from repoze.who.plugins.friendlyform import FriendlyFormPlugin
 

class FriendlyTimeoutPlugin(FriendlyFormPlugin):
    def identify(self, environ):
        identity=super(FriendlyTimeoutPlugin, self).identify(environ)
        if identity:
            identity['max_age']=6000
            config['company_code'] = environ['webob._parsed_post_vars'][0]['company']
        return identity
