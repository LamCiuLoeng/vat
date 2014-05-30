<%
    from vatsystem.util import const
    from vatsystem.util.mako_filter import pf
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
   <li class="li2" style="width:300px;"><input type="text" name="create_time_start" class="datepicker" id="datepicker1"> (YYYY-MM-DD)</li>
  </ul>  
  <ul>
   <li class="li1">TO</li>
   <li class="li2" style="width:300px;"><input type="text" name="create_time_end" class="datepicker"  id="cheadEndDate"> (YYYY-MM-DD)</li>
  </ul>
  <div style="clear:both"></div>
  <input type="submit" value="Search" class="btn"> 
</form>
<br />
</div>
</div>
<!--other charges-->
% if len(charges) > 0:
<div class="title1">Other Charges</div>
<form action="/ap/add_other_charges_from_manual" method="post" id="update_other_charges_vat_total">
<input type="hidden" name="select_id" value="" id="select_id"/>
<input type="hidden" name="p_head" value="${kws['pHead_id']}" />
<P><input type="submit"  onclick="ajaxForm('#update_other_charges_vat_total','Save Success!','${pHead.id}','${pHead.ref}',checkSelect('#update_other_charges_vat_total'),'si_search')"  value="OK" class="btn" style="font-size:12px;"></P>
<table class="gridTable" style="width:800px;border:1px solid #777777" cellpadding="0" cellspacing="0" border="0">
  <thead class="cl3">
    <tr>
      <th width="20px" class="head"><input type="checkbox" onclick="selectAll(this)" id="selectAlls"></th>
      <th>Note No</th>
      <th>Line NO</th>
      <th>Note Type</th>
      <th>Status</th>
      <th>Chg Discount Code</th>
      <th>TOTAL</th>
      <th>Note Date</th>
      <th>Remark</th>
    </tr>
  </thead>
  <tbody>
  % for v,k in enumerate(charges):
  <tr>
  <!--other charges list-->
    <td width="20px" class="head"><input type="checkbox" onclick="selectOne()" value="${v}" class="cboxClass"></td>
    <td class="head">${k.get('note_no')}</td>
    <td >${k.get('line_no')}</td>
    <td>${k.get('note_type')}</td>
    <td>${k.get('status')}</td>
    <td>${k.get('chg_discount_code')}</td>
    <td>${pf(k.get('total',0))}
    <div style="display:none" id="search_charge_${v}">
      line_no:
      <input type="text" name="line_no_${v}" value="${k.get('line_no')}" />
       charge_code:
      <input type="text" name="charge_code_${v}" value="${k.get('chg_discount_code')}"  />
       total:
      <input type="text" name="total_${v}" value="${k.get('total')}"  />
      <input type="text" name="vat_total_${v}" value="${k.get('total')}"  />
      <input type="hidden" name="active_${v}" value="0"/>
      <input type="hidden" name="company_code_${v}" value="${k.get('company_code')}"/>
      <input type="hidden" name="type_${v}" value="${const.CHARGE_TYPE_P_ERP}"/>
	  <input type="hidden" name="note_no_${v}" value="${k.get('note_no')}" />
    </div>
    </td>
    <td>${k.get('create_date')}</td>
    <td>${k.get('remark')}&nbsp;</td>
  </tr>
  % endfor
  </tbody>
</table>
 </form>
% endif
</body>
</html>