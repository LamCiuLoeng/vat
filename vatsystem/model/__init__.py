# -*- coding: utf-8 -*-
"""The application's model objects"""

from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
#from sqlalchemy import MetaData
from sqlalchemy.ext.declarative import declarative_base

# Global session manager: DBSession() returns the Thread-local
# session object appropriate for the current web request.
maker = sessionmaker(autoflush=True, autocommit=False, extension=ZopeTransactionExtension())
maker2 = sessionmaker(autoflush=False, autocommit=False)
DBSession = scoped_session(maker)
DBSession2 = scoped_session(maker2)
# Base class for all of our model classes: By default, the data model is
# defined with SQLAlchemy's declarative extension, but if you need more
# control, you can switch to the traditional method.
DeclarativeBase = declarative_base()
DeclarativeBase2 = declarative_base()
# There are two convenient ways for you to spare some typing.
# You can have a query property on all your model classes by doing this:
# DeclarativeBase.query = DBSession.query_property()
# Or you can use a session-aware mapper as it was used in TurboGears 1:
# DeclarativeBase = declarative_base(mapper=DBSession.mapper)

# Global metadata.
# The default metadata is the one from the declarative base.
metadata = DeclarativeBase.metadata
metadata2 = DeclarativeBase2.metadata
# If you have multiple databases with overlapping table names, you'll need a
# metadata for each database. Feel free to rename 'metadata2'.
#metadata2 = MetaData()

#####
# Generally you will not want to define your table's mappers, and data objects
# here in __init__ but will want to create modules them in the model directory
# and import them at the bottom of this file.
#
######

def init_model(engine1, engine2):
    """Call me before using any of the tables or classes in the model."""

#    DBSession.configure(bind=engine)
    DBSession.configure(bind=engine1)
    DBSession2.configure(bind=engine2)

    metadata.bind = engine1
    metadata2.bind = engine2

# Import your model modules here.
from vatsystem.model.auth import User, Group, Permission
from vatsystem.model.base_erp import *
from vatsystem.model.base_vat import *
from vatsystem.model.erp import * 
from vatsystem.model.systemutil import *
