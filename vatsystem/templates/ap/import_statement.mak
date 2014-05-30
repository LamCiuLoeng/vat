<%inherit file="vatsystem.templates.master"/>
<%
from vatsystem.util import const
%>
<%def name="extTitle()">r-pac - AP</%def>

<%def name="extJavaScript()">
 
</%def>

<div class='submenu' id="function-menu">
    <ul>
        <li class='li-start'></li>
        <li class='li-center'> <a href="/ap/index"><img src="/images/images/VAT-ERP_g.jpg"></a></li>
        <li class='li-center'> <a href="/ap/import_statement?import=0"><img src="/images/images/Import-Excel_g.jpg"></a></li>
        <li class='li-end'></li>
    </ul> 
</div>
<div class="nav-tree">AP&nbsp;&nbsp;&gt;&nbsp;&nbsp;Import statement</div>

<div style="margin: 20px 10px; overflow: hidden;">
  <div style="float: left;">
    <div>
     <form name="form1" enctype="multipart/form-data" method="post" action="/ap/import_statement">
     	%if kw.get("id"):
     	<input name="id" value="${kw.get("id")}" type="hidden">
     	%endif
     <label>
       <input type="file" name="attachment"> <input type="submit" value="Submit" name="sm">
    </label>
    <p>
    <input type="radio" name="type" id='type1' value="${const.IMPORT_STATEMENT_YES}" checked> <label for='type1'>Import and save into DB immediately</label> 
    <br />
	<input type="radio" name="type" id='type2' value="${const.IMPORT_STATEMENT_NO}"> <label for='type2'>Import and upload the excel file to server, we will save it later with night job</label> 
	</p>
  </form>
   </div>  
    </div>
</div>



