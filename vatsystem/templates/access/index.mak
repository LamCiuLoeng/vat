<%inherit file="vatsystem.templates.master"/>

<%def name="extTitle()">r-pac - Access</%def>

<%def name="extJavaScript()">
	<script language="JavaScript" type="text/javascript">
    //<![CDATA[
          function toSearch(){
          	$("form").submit()
          }

          function toUG(){
          	location.href="/access/group_manage?id="+$("select[name='group_id']").val();
          }

          function toUP(){
          	location.href="/access/permission_manage?id="+$("select[name='permission_id']").val();
          }
    //]]>
   </script>
</%def>


<div id="function-menu">
    <table width="100%" cellspacing="0" cellpadding="0" border="0">
  <tbody><tr>
    <td width="36" valign="top" align="left"><img src="/images/images/menu_start.jpg"/></td>
    <td width="176" valign="top" align="left"><a href="/access/index"><img src="/images/images/VAT-ERP_g.jpg"/></a></td>
    <td width="64" valign="top" align="left"><a href="#" onclick="toSearch()"><img src="/images/images/menu_search_g.jpg"/></a></td>
    <td width="64" valign="top" align="left"><a href="/access/add"><img src="/images/images/menu_new_g.jpg"/></a></td>
    <td width="64" valign="top" align="left"><a href="#" onclick="toUG()"><img src="/images/images/menu_ug_g.jpg"/></a></td>
    <td width="64" valign="top" align="left"><a href="#" onclick="toUP()"><img src="/images/images/menu_up_g.jpg"/></a></td>
    <td width="23" valign="top" align="left"><img height="21" width="23" src="/images/images/menu_last.jpg"/></td>
    <td valign="top" style="background:url(/images/images/menu_end.jpg) repeat-x;width:100%"></td>
  </tr>
</tbody></table>
</div>

<div class="nav-tree">Access&nbsp;&nbsp;&gt;&nbsp;&nbsp;Main</div>

<div>
	${widget(action="/access/index")|n}
</div>

<div style="clear:both"><br /></div>

%if result:

	<table class="gridTable" cellpadding="0" cellspacing="0" border="0" style="width:800px">
		<thead>
			<tr><td style="text-align:right;border-right:0px;border-bottom:0px"  colspan="10"><span>${tmpl_context.paginators.result.pager()}</span></td></tr>
			<tr>
				<th width="300">User Name</th><th width="500">Belong to Group</th>
			</tr>
		</thead>
		<tbody>
			%for u in result:
			<tr>
				<td><a href="/access/user_manage?id=${u.user_id}">${u.user_name}</a>&nbsp;</td>
				<td>${",".join([g.group_name for g in u.groups])}&nbsp;</td>
			</tr>
			%endfor
			<tr><td style="text-align:right;border-right:0px;border-bottom:0px"  colspan="10"><span>${tmpl_context.paginators.result.pager()}</span></td></tr>
		</tbody>
	</table>

%endif

