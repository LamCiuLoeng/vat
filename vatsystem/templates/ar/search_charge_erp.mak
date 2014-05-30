<%
    from decimal import Decimal
    from vatsystem.util import const
    from vatsystem.util.mako_filter import b,pd,pt,pi,pf,get_last_line_no
%>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>r-pac - VAT System</title>
<link type="images/x-icon" rel="shortcut icon" href="/images/favicon.ico" />
<link type="text/css" rel="stylesheet" href="/css/theme/jquery-ui-1.8.5.custom.css" />
<link type="text/css" rel="stylesheet" href="/css/jquery.autocomplete.css" />
<link type="text/css" rel="stylesheet" href="/css/impromt.css" />
<link type="text/css" rel="stylesheet" href="/css/tipsy.css" />
<link type="text/css" rel="stylesheet" href="/css/screen.css" />
<link rel="stylesheet" href="/css/ar.css" />
<script type="text/javascript" src="/js/jquery-1.4.2.min.js"></script>
<script type="text/javascript" src="/js/jquery-ui-1.8.5.custom.min.js"></script>
<script type="text/javascript" src="/js/numeric.js"></script>
<script type="text/javascript" src="/js/jquery.autocomplete.pack.js"></script>
<script type="text/javascript" src="/js/jquery-impromptu.3.1.min.js"></script>
<script type="text/javascript" src="/js/jquery.blockUI.js"></script>
<script type="text/javascript" src="/js/jquery.cookie.js"></script>
<script type="text/javascript" src="/js/jquery.tipsy.js"></script>
<script type="text/javascript" src="/js/jquery.form.js"></script>
<script type="text/javascript" src="/js/common.js"></script>
<script type="text/javascript" src="/js/vat_ar.js"></script>
  <script> 
  $(document).ready(function() {
    $(".datepicker").datepicker({dateFormat: 'yy-mm-dd',changeYear: true,changeMonth: true,showOn: 'both',buttonImage: '../images/calendar.gif', buttonImageOnly: true});
  });   
  </script>   
</head>
<body>
<div class="box1">
<div class="title1"><div class="toggle_down"></div>Search Other Charges</div>
<div class="search none ui-accordion ui-widget ui-helper-reset" id="accordion" role="tablist" style="display: block;">
<form action="" method="post" id="search_Charge_Erp" style="margin-left:30px;">
  <ul>
   <li class="li1">Note No</li>
   <li class="li2" ><input type="text" name="note_no"></li>
  </ul>  
  <ul> 
   <li class="li1">Create Date</li>
   <li class="li2" style="width:300px;"><input type="text" name="date_from" class="datepicker" id="datepicker1"> (YYYY-MM-DD)</li>
  </ul>  
  <ul>
   <li class="li1">TO</li>
   <li class="li2" style="width:300px;"><input type="text" name="date_to" class="datepicker"  id="cheadEndDate"> (YYYY-MM-DD)</li>
  </ul>
  <div style="clear:both"></div>
  <input type="submit" value="Search" class="btn"> 
</form>
<br />
</div>
</div>
<!--other charges-->
% if len(other_charges_from_erp) > 0:
<div class="title1">Other Charges</div>
<form action="/ar/add_other_charges_from_manual" method="post" id="update_other_charges_vat_total">
<input type="hidden" name="select_id" value="" id="select_id"/>
<P><input type="submit"  onclick="ajaxForm('#update_other_charges_vat_total','Save Success!','${tHead.id}','${tHead.ref}',checkSelect('#update_other_charges_vat_total'),'si_search')"  value="OK" class="btn"></P>
<table class="gridTable" style="width:800px;border:1px solid #777777" cellpadding="0" cellspacing="0" border="0">
  <thead class="cl3">
    <tr>
      <th width="20px" class="head"><input type="checkbox" onclick="selectAll(this)" id="selectAlls"></th>
      <th>Note No</th>
      <th>Line NO</th>
      <th>Note Type</th>
      <th>Status</th>
      <th>Chg Discount Code</th>
      <th>Total</th>
      <th>VAT Total</th>
      <th>Note Date</th>
      <th>Remark</th>
    </tr>
  </thead>
  <tbody>
  % for v,k in enumerate(other_charges_from_erp):
  <tr>
  <!--other charges list-->
    <td width="20px" class="head"><input type="checkbox" onclick="selectOne()" value="${v}" class="cboxClass"></td>
    <td class="head">${k.note_no}</td>
    <td >${k.line_no}</td>
    <td>${k.note_type}</td>
    <td>${k.status}</td>
    <td>
    %if k.status:
    	${k.chg_discount_code}
    %else:
    	&nbsp;
    %endif
     </td>
    <td>${k.total}</td>
    <td>${k.vat_total}</td>
    <td>${k.note_date}</td>
    <td>
	% if k.remark:
		${k.remark}
	% else:
		&nbsp;
	% endif
    </td>
  </tr>
      <div style="display:none" id="search_charge_${v}">
      <input type="text" name="t_head_${v}" value="${kws['tHead_id']}" />
      line_no:
      <input type="text" name="line_no_${v}" value="${k.line_no}" />
       charge_code:
      <input type="text" name="charge_code_${v}" value="${k.chg_discount_code}"  />
       total:
      <input type="text" name="total_${v}" value="${k.total}"  />
      <input type="text" name="vat_total_${v}" value="${k.vat_total}"  />
      <input type="hidden" name="active_${v}" value="0"/>
      <input type="hidden" name="type_${v}" value="T_ERP"/>
      <input type="hidden" name="note_type_${v}" value="${k.note_type}" />
      <input type="hidden" name="note_no_${v}" value="${k.note_no}" />
	  %if kws.get('id'):
	  	<input type="hidden" name="id_${v}" value="${kws['id']}" />
	  %endif
    </div>
  % endfor
  </tbody>
</table>
 </form>
% endif
</body>
</html>