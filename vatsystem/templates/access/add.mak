<%inherit file="vatsystem.templates.master"/>

<%def name="extTitle()">r-pac - Access</%def>

<%def name="extJavaScript()">
	<script language="JavaScript" type="text/javascript">
    //<![CDATA[

    //]]>
   </script>
</%def>


<div id="function-menu">
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
  <tbody><tr>
    <td width="36" valign="top" align="left"><img src="/images/images/menu_start.jpg"/></td>
    <td width="176" valign="top" align="left"><a href="/access/index"><img src="/images/images/VAT-ERP_g.jpg"/></a></td>
    <td width="23" valign="top" align="left"><img height="21" width="23" src="/images/images/menu_last.jpg"/></td>
    <td valign="top" style="background:url(/images/images/menu_end.jpg) repeat-x;width:100%"></td>
  </tr>
</tbody></table>
</div>

<div class="nav-tree">Access&nbsp;&nbsp;&gt;&nbsp;&nbsp;New</div>

<div style="margin: 10px 0px; overflow: hidden;">
  <div style="float: left;">
    <div>
      <form name="userForm" class="tableform" method="post" action="/access/save_new">
      	<input type="hidden" name="type" value="user"/>
        <div class="case-list-one">
          <div class="case-list">
            <ul>
              <li class="label">
                <label for="userForm_user_name" class="fieldlabel">User name</label>
              </li>
              <li>
                <input type="text" id="userForm_user_name" name="user_name" class="textfield" style="width: 250px;"/>
              </li>
            </ul>
            <ul>
              <li class="label">
                <label for="userForm_display_name" class="fieldlabel">Display name</label>
              </li>
              <li>
                <input type="text" id="userForm_display_name" name="display_name" class="textfield" style="width: 250px;"/>
              </li>
            </ul>
            <ul>
              <li class="label">
                <label for="userForm_password" class="fieldlabel">Password</label>
              </li>
              <li>
                <input type="text" id="userForm_password" name="password" class="textfield" style="width: 250px;"/>
              </li>
            </ul>
            <ul>
              <li class="label">
                <label for="userForm_email_address" class="fieldlabel">E-mail</label>
              </li>
              <li>
                <input type="text" id="userForm_email_address" name="email_address" class="textfield" style="width: 250px;"/>
              </li>
            </ul>
            <ul>
              <li class="label">
                <label for="userForm_phone" class="fieldlabel">Phone</label>
              </li>
              <li>
                <input type="text" id="userForm_phone" name="phone" class="textfield" style="width: 250px;"/>
              </li>
            </ul>
            <ul>
              <li class="label">
                <label for="userForm_fax" class="fieldlabel">Fax</label>
              </li>
              <li>
                <input type="text" id="userForm_fax" name="fax" class="textfield" style="width: 250px;"/>
              </li>
            </ul>
          </div>
        </div>
        <div class="case-list-one">
          <div class="case-list">
            <input type="submit" name="submit" value="Save User" class="submitbutton" id="userForm_submit"/>
            <input type="reset" name="reset" value="Reset" class="resetbutton" id="userForm_reset"/>
          </div>
        </div>
        <div style="clear: both;"><br/>
        </div>
      </form>
    </div>
    <div>
      <form name="groupForm" class="tableform" method="post" action="/access/save_new">
      	<input type="hidden" name="type" value="group"/>
        <div class="case-list-one">
          <div class="case-list">
            <ul>
              <li class="label">
                <label for="groupForm_group_name" class="fieldlabel">Group name</label>
              </li>
              <li>
                <input type="text" id="groupForm_group_name" name="group_name" class="textfield" style="width: 250px;"/>
              </li>
            </ul>
          </div>
        </div>
        <div class="case-list-one">
          <div class="case-list">
            <input type="submit" name="submit" value="Save Group" class="submitbutton" id="groupForm_submit"/>
            <input type="reset" name="reset" value="Reset" class="resetbutton" id="groupForm_reset"/>
          </div>
        </div>
        <div style="clear: both;"><br/>
        </div>
      </form>
    </div>
    <div>
      <form name="permissionForm" class="tableform" method="post" action="/access/save_new">
      	<input type="hidden" name="type" value="permission"/>
        <div class="case-list-one">
          <div class="case-list">
            <ul>
              <li class="label">
                <label for="permissionForm_permission_name" class="fieldlabel">Permission Name</label>
              </li>
              <li>
                <input type="text" id="permissionForm_permission_name" name="permission_name" class="textfield" style="width: 250px;"/>
              </li>
            </ul>
            <ul>
              <li class="label">
                <label for="permissionForm_description" class="fieldlabel">Permission description</label>
              </li>
              <li>
                <textarea class="textarea" name="description" cols="30" rows="2" id="permissionForm_description"></textarea>
              </li>
            </ul>
          </div>
        </div>
        <div class="case-list-one">
          <div class="case-list">
            <input type="submit" name="submit" value="Save Permission" class="submitbutton" id="permissionForm_submit"/>
            <input type="reset" name="reset" value="Reset" class="resetbutton" id="permissionForm_reset"/>
          </div>
        </div>
        <div style="clear: both;"><br/>
        </div>
      </form>
    </div>
  </div>
</div>



