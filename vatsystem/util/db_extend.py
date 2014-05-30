from datetime import datetime as dt
from sqlalchemy import asc
from sqlalchemy import desc
from sqlalchemy import or_
from vatsystem.model import *
from vatsystem.util import const
from vatsystem.util.common import *

# DBSession = DBSession

class QueryExtend():

    def __init__( self, cls, ** kw ):
        self.cls = cls
        self.result = []
        self.kw = kw


    #===========================================================================
    # query the db and return the all result or [limit:offset] records
    #
    # @flag : return all the result ,or just the [limit:offset] records
    # @DBSession : the data source session
    # @ignoreActive : whether to add the active = 0 conditions to the filter
    # @limit : for the paginate usage
    # @offset : for the paginate usage
    # @kw : the query conditions
    # @return: list of the records
    #
    # ----------- by CL
    #===========================================================================
    def query_all( self, flag = True, DBSession = DBSession, ignoreActive = False, limit = 0, offset = 25, ** kw ):
        self.result = DBSession.query( self.cls )
        if not ignoreActive: self.result = self.result.filter( self.cls.active == 0 )
        for k, v in kw.iteritems():
            self.query( k, v )
        if flag:
            self.result = self.result[limit:offset]
        else:
            self.result = self.result.all()

    #===========================================================================
    # build up the DBSession filter condition
    #
    # @queryType : db operation type
    # @queryList : a list of value
    # @return : DBSession query result set
    #
    # ----------- by CL
    #===========================================================================
    def query( self, queryType, queryList ):
        ( cls, result, kw ) = ( self.cls, self.result, self.kw )
        #=======================================================================
        # prepare the params for DBSession query , and foramt the value
        # ----------- by CL
        #=======================================================================
        def getQueryKw():
            queryDict = {}
            for i in queryList:
                if isinstance( i, list ) or isinstance( i, tuple ):
                    if len( i ) == 3:
                        if queryType == const.QUERY_TYPE_LIKE_AND_OR:
                            value = ( self.pd( kw.get( i[0], '' ) ), self.pd( i[1] ), self.pd( i[2] ) )
                        elif queryType == const.QUERY_TYPE_DATE:
                            value = ( self.pd( kw.get( i[1], '' ) ), self.pd( kw.get( i[2], '' ) ) )
                    else:
                        value = self.pd( kw.get( i[1], '' ) )
                    if value:
                        queryDict.update( {i[0]:value} )
                elif isinstance( i, str ) or isinstance( v, unicode ):
                    value = self.pd( kw.get( i, '' ) )
                    if value:
                        queryDict.update( {i:value} )
            return queryDict

        if queryType == const.QUERY_TYPE_LIKE:    # like
            for k, v in getQueryKw().iteritems():
                result = result.filter( getattr( cls, k ).ilike( '%%%s%%' % v ) )
        elif queryType == const.QUERY_TYPE_EQ:    # ==
            for k, v in getQueryKw().iteritems():
                result = result.filter( getattr( cls, k ) == v )
        elif queryType == const.QUERY_TYPE_CREATE_BY:    # ==
            for k, v in getQueryKw().iteritems():
                result = result.filter( getattr( cls, k ) == v )
        elif queryType == const.QUERY_TYPE_NOT_EQ:    # !=
            for k, v in getQueryKw().iteritems():
                if isinstance( v, list ):
                    result = result.filter( ~getattr( cls, k ).in_( v ) )    # not in the list
                else:
                    result = result.filter( getattr( cls, k ) != v )
        elif queryType == const.QUERY_TYPE_MATCH:    # ilike
            for k, v in getQueryKw().iteritems():
                result = result.filter( getattr( cls, k ).match( v ) )
        elif queryType == const.QUERY_TYPE_IN:    # in
            for k, v in getQueryKw().iteritems():
                if isinstance( v, str ) or isinstance( v, unicode ):
                    result = result.filter( getattr( cls, k ).in_( [int( i ) for i in v.split( ',' )] ) )
                else:
                    result = result.filter( getattr( cls, k ).in_( v ) )
        elif queryType == const.QUERY_TYPE_NOT_IN:    # not in
            for k, v in getQueryKw().iteritems():
                if isinstance( v, str ) or isinstance( v, unicode ):
                    result = result.filter( ~getattr( cls, k ).in_( [int( i ) for i in v.split( ',' )] ) )
                else:
                    result = result.filter( ~getattr( cls, k ).in_( v ) )
        elif queryType == const.QUERY_TYPE_DATE:    # date1 < v < date2
            for k, v in getQueryKw().iteritems():
                if len( v ) == 2 and v[0]:
                    result = result.filter( getattr( cls, k ) >= dt.strptime( v[0] + "00:00:00", "%Y-%m-%d%H:%M:%S" ) )
                if len( v ) == 2 and v[1]:
                    result = result.filter( getattr( cls, k ) <= dt.strptime( v[1] + "23:59:59", "%Y-%m-%d%H:%M:%S" ) )
        elif queryType == const.QUERY_TYPE_LIKE_AND_OR:    # like or like
            for k, v in getQueryKw().iteritems():
                if v[0]:
                    result = result.filter( or_( getattr( cls, v[1] ).ilike( '%%%s%%' % v[0] ), getattr( cls, v[2] ).ilike( '%%%s%%' % v[0] ) ) )
        elif queryType == const.QUERY_TYPE_NOT_NULL:    # != null
            for i in queryList:
                result = result.filter( getattr( cls, i ) != None )
        elif queryType == const.QUERY_TYPE_COMPANY_CODE:    # company code in
            result = result.filter( getattr( cls, 'company_code' ).in_( getCompanyCode() ) )
        elif queryType == const.QUERY_TYPE_ORDER_BY:    # order by
            # asc_orders = [v for k, v in getQueryKw().iteritems()]
            orders = []
            for i in queryList:
                _asc, _order = ( 'desc', i )
                if len( i.split( '-' ) ) > 1:
                    _asc, _order = i.split( '-' )
                if _asc == 'asc':
                    orders.append( asc( getattr( cls, _order ) ) )
                else:
                    orders.append( desc( getattr( cls, _order ) ) )
            result = result.order_by( * orders )
        self.result = result

    def pd( self, data ):
        if isinstance( data, list ) or isinstance( data, tuple ):
            result = []
            for a in data:
                if isinstance( a, str ) or isinstance( a, unicode ):
                    a = a.strip()
                result.append( a )
            data = result
        elif isinstance( data, str ) or isinstance( data, unicode ):
            data = data.strip()
        return data
