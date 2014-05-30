# -*- coding: utf-8 -*-


from tw.api import WidgetsList
from tw.forms import TableForm
from tw.forms.fields import HiddenField

from vatsystem.model import DBSession
from vatsystem.model import *

from vatsystem.widgets.components import *

class SearchForm(RPACForm):

    group_options=DBSession.query(Group.group_id, Group.group_name).order_by(Group.group_name)

    permission_options=DBSession.query(Permission.permission_id, Permission.permission_name).order_by(Permission.permission_name)

    fields=[
        RPACText("user_name", label_text="User Name"),
        RPACSelect("group_id", label_text="Group Name", options=group_options),
        RPACSelect("permission_id", label_text="Permission Name", options=permission_options)
        ]

access_search_form=SearchForm("search")


class UserForm(RPACForm):
    fields=[
              HiddenField("id"),
              RPACText("user_name", label_text="User Name"),
              RPACText("password", label_text="Password"),
              RPACText("email_address", label_text="E-mail Address"),
              RPACText("display_name", label_text="Display Name"),
              RPACText("phone", label_text="Phone"),
              RPACText("fax", label_text="Fax"),
              ]

user_update_form=UserForm()


class GroupForm(RPACForm):
    fields=[
        HiddenField("id"),
        RPACText("group_name", label_text="Group Name"),
        ]

group_update_form=GroupForm()


class PermissionForm(RPACForm):
    fields=[
        HiddenField("id"),
        RPACText("permission_name", label_text="Permission Name"),
        ]

permission_update_form=PermissionForm()

