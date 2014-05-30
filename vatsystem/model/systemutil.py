# -*- coding: utf-8 -*-
from datetime import datetime as dt

from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref

from vatsystem.model import DeclarativeBase, metadata, DBSession
from vatsystem.model.auth import *


class SystemLog(DeclarativeBase):
    __tablename__ = 'system_log'
    id = Column(Integer,Sequence('system_log_hdr_id_seq'), primary_key=True)
    
    log_type = Column(Unicode(20), nullable = True)
    log_content = Column(Unicode(1000), nullable = True)
    create_time = Column(DateTime, default=dt.now)
    create_by_id = Column(Integer, ForeignKey('tg_user.user_id'))
    create_by = relation(User,backref="logs")
    active = Column(Integer,default=0)
    
    
class DataDictionary(DeclarativeBase):
    __tablename__ = 'data_dictionary'
    
    id = Column(Integer,Sequence('data_dictionary_id_seq'), primary_key=True)
    
    flag = Column(Unicode(10), nullable = True)
    category = Column(Unicode(50), nullable = True)
    sub_category = Column(Unicode(50), nullable = True)
    description = Column(Unicode(1000), nullable = True)
    create_time = Column(DateTime, default=dt.now)
    active = Column(Integer,default=0)