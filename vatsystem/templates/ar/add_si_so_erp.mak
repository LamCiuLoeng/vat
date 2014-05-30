<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf
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
  	initTr();
  	replayLink('/ar/add_si_so_erp?type=${kws.get("type")}&tHead_id=${kws.get("tHead_id")}&customer_code=${kws.get("customer_code")}','.pager_link')
    $(".datepicker").datepicker({dateFormat: 'yy-mm-dd',changeYear: true,changeMonth: true,showOn: 'both',buttonImage: '../images/calendar.gif', buttonImageOnly: true});
  });   
  </script>      
</head>
<body>
<input type="hidden" name="cust" id="cust" value="1"/>
<div class="box1">
<div class="title1">
<div class="toggle_down">
	% if kws.get("type") == '1':
		</div>Search SI From ERP</div>
	% else:
		</div>Search SO From ERP</div>
	% endif
	<div class="search none ui-accordion ui-widget ui-helper-reset" id="accordion" role="tablist" style="display: block;">
		<form action="/ar/add_si_so_erp?viewPager=1" method="post" id="search_Charge_Erp" style="margin-left:30px;">
		  <ul>
		  		% if kws.get("type") == '1':
				   <li class="li1">SI Number</li>
				   <li class="li2" ><input type="text" name="invoice_no">
				   <input type="hidden" name="type" value="1">
				   </li>
			   % else:
			   	   <li class="li1">SO Number</li>
			   	   <li class="li2" ><input type="text" name="sales_contract_no">
			   	   <input type="hidden" name="type" value="2">
			   	   </li>
			   % endif 
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
		  
		   <input type="hidden" name="customer_code" value="${kws.get("customer_code")}">
		   <input type="hidden" name="tHead_id" value="${kws.get("tHead_id")}">
		   <input type="submit" value="Search" class="btn"> 
		</form>
	<br />
	</div>
</div>
<!--other charges-->
    <div class="box4">
    % if kws.get("type") == '1':
      <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
        <thead>
          <tr>
            <td colspan="100" style="border-right:0px;border-bottom:0px"><div class="toolbar">
                <div class="l">
                  <form action="/ar/save_all_to_thead" id="_form" method="post">
                    <input type="hidden" name="ids" id="ids"/>
                    <input type="hidden" name="customer_code" id="hid_customer_code"  value="${kws.get("customer_code")}" />
                    <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SI}"/>
                    <input type="hidden" name="t_head_id" value="${kws.get("tHead_id")}"/>
                    <input type="submit" class="btn" value="Save to MSI" id="btn_save_as_msi" onClick="ajaxForm('#_form','Save Success!','0','0',saveAllToThead(),'save')" />
                    <input type="submit" style="display:none">
                  </form>
                </div>
            <div class="r" style="font-weight:bold" id="topSpace">
            	 <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
            </div>
              </div></td>
          </tr>
          <tr>
            <th class="head" style="width:20px"><input type="checkbox" value="0" onClick="selectAll(this)" /></th>
            <th>Invoice NO</th>
            <th>SO No</th>
            <th>Qty</th>
            <th>CN Qty</th>
            <th class="cl3">Available Qty</th>
            <th class="cl3">MSI Qty</th>
            <th class="cl4">MCN Qty</th>
            <th>Charge</th>
            <th>CN Charge</th>
            <th class="cl3">Available Charge</th>
            <th class="cl3">MSI Charge </th>
            <th class="cl4">MCN Charge</th>
            <th>Status</th>
            <th>Cust Code</th>
            <th>Cust Name</th>
            <th>Order Amt</th>
            <th>Item Amt</th>
            <th>Curr.</th>
            <th>SO Sales Contact</th>
            <th>Dept.</th>
            <th>Create Time</th>
          </tr>
        </thead>
        <tbody>
        % for i in collections:
	        <tr>
	          <td class="head">
	          <input type="checkbox" class="cboxClass" value="${i.invoice_no}$${i.customer}" onClick="selectOne()" /></td>
	          <td><a href="javascript:void(0)" onClick="OpenDialog('/ar/ajax_view_si?invoice_no=${i.invoice_no}','#searchDialog','${i.invoice_no} Detail')">${i.invoice_no}</a></td>
	          <td><a href="javascript:void(0)" onClick="OpenDialog('/ar/ajax_view_so?sales_contract_no=${i.sc_no}','#searchDialog','${i.sc_no} Detail')">${i.sc_no}</a></td>
	          <td>${i.qty}</td>
	          <td>${i.ri_qty}</td>
	          <td>${i.available_qty}</td>
	          <td>${i.msi_qty}</td>
	          <td>${i.mcn_qty}</td>
	          <td>${pf(i.charge_total)}</td>
	          <td>${pf(i.ri_total)}</td>
	          <td>${pf(i.available_total)}</td>
	          <td>${pf(i.msi_total)}</td>
	          <td>${pf(i.mcn_total)}</td>
	          <td>${i.status}</td>
	          <td>${i.customer}</td>
	          <td class="fcn">${i.customer_short_name}</td>
	          <td>${pf(i.order_amt)}</td>
	          <td>${pf(i.item_amt)}</td>
	          <td>${i.currency}</td>
	          <td>${i.so_sales_contact}</td>
	          <td>${i.department}</td>
	          <td>${pd(i.create_date)}</td>
	        </tr>
        % endfor
         </tbody>
          <tfoot class="tfoot">
	         <tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace"> <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a></td></tr>
	     </tfoot>
         </table>
      % else:
      	     <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div id="toolbar">
                                <div class="l">
							    <form action="/ar/save_all_to_thead" id="_form" method="post">
							        <input type="hidden" name="ids" id="ids"/>
							        <input type="hidden" name="customer_code" id="hid_customer_code"  value="${kws.get("customer_code")}" />
							        <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SO}"/>
							        <input type="hidden" name="t_head_id" value="${kws.get("tHead_id")}"/>
							        <input type="submit" style="display:none">
							    	<input type="submit" class="btn" value="Save to MSO" id="btn_save_as_msi" onclick="ajaxForm('#_form','Save Success!','0','0',saveAllToThead(),'save')" />
							    </form>
                                </div>
                                <div class="r" style="font-weight:bold" id="topSpace">
                                	 <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr>
                        <th class="head" style="width:20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
                        <th>SO No</th>
                        <th>Qty</th>
                        <th>Invoiced Qty</th>
                        <th class="cl3">Available Qty</th>
                        <th class="cl3">MSO Qty</th>
                        <th class="cl4">MCN Qty</th>
                        <th>Charge</th>
                        <th class="cl3">Available Charge</th>
                        <th class="cl3">MSO Charge</th>
                        <th class="cl4">MCN Charge</th>
                        <th>Status</th>
                        <th>Cust Code</th>
                        <th>Cust Name</th>
                        <th>Cust Po No</th>
                        <th>Order Amt</th>
                        <th>Item Amt</th>
                        <th>Curr.</th>
                        <th>AE</th>
                        <th>Dept.</th>
                        <th>Create Time</th>
                    </tr>
                </thead>
                <tbody>
                    % for i in collections:
                    <tr>
                        <td class="head"><input type="checkbox" class="cboxClass" value="${i.sales_contract_no}$${i.customer_code}" onclick="selectOne()" /></td>
                        <td><a href="javascript:void(0)" onClick="OpenDialog('/ar/ajax_view_so?sales_contract_no=${i.sales_contract_no}','#searchDialog','${i.sales_contract_no} Detail')" >${i.sales_contract_no}</a></td>
                        <td>${i.qty}</td>
                        <td>${i.invoiced_qty}</td>
                        <td>${i.available_qty}</td>
                        <td>${i.mso_qty}</td>
                        <td>${i.mcn_qty}</td>
                        <td>${pf(i.charge_total)}</td>
                        <td>${pf(i.available_total)}</td>
                        <td>${pf(i.mso_total)}</td>
                        <td>${pf(i.mcn_total)}</td>
                        <td>${i.status}</td>
                        <td>${i.customer_code}</td>
                        <td class="fcn">${i.customer_short_name}</td>
                        <td>${b(i.cust_po_no)|n}</td>
                        <td>${pf(i.order_amt)}</td>
                        <td>${pf(i.item_amt)}</td>
                        <td>${i.currency}</td>
                        <td>${i.ae}</td>
                        <td>${i.order_dept}</td>
                        <td>${pd(i.create_date)}</td>
                    </tr>
                    % endfor
                     </tbody>
	                 <tfoot class="tfoot">
	         			 <tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace"> <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a></td></tr>
	                 </tfoot>
            </table>
      % endif
    </div>
</body>
</html>
	