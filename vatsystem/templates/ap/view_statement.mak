<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf,pt
%>
%if flag==1:
<script>
    showError("Error");
</script>
%else:
<script type="text/javascript">
	$("#vatDialog27_${st_head.id}").find("select[cid='dzd_search']").change(function(){
		if($(this).val().length>0){
			changeParseDate($(this), '${st_head.id}');
		}
	})
	initTr2();
	initStatement();
	parseDzdInput('${st_head.id}');
</script>
<style type="text/css">
<!-- 
	.ui-dialog{width:800px;}
-->
</style>
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>Statement Information</div>
    <div>
    <div class="toolbar">
    <input type="button" onclick="javascript:dzdImport('${st_head.id}')" class="btn" value="Import Excel">
    </div>
        <ul>
            <li class="li1">Name:</li>
            <li class="li2">${st_head.upload_name}</li>
           <li class="li1">Ref:</li>
            <li class="li2">${st_head.ref}</li>
        </ul>
        <ul>
            <li class="li1">PI Amount:</li>
            <li class="li2">${pi_amount}</li>
           <li class="li1">DN Amount:</li>
            <li class="li2">${dn_amount}</li>
        </ul>
        <ul>
            <li class="li1">Create Date:</li>
            <li class="li2">${pt(st_head.create_time)}</li>
            <li class="li1">Update Date:</li>
            <li class="li2">${pt(st_head.update_time)}</li>
        </ul>
        <div class="clear"></div>
        
    </div>
    <div class="clear"></div>
</div>
 
<div class="none" id="vatDialog27_${st_head.id}">
    <input type="hidden" name="id" value="${st_head.id}"/>
    <input type="hidden" name="type" value="st_head_id"/>
    <div >
        ${dzd_set_date_form()|n}
        <div class="clear"></div>
    </div>
    <div class="box7">
    	<div style="display:none"><input type="text"  id="vat_no26_${st_head.id}" /></div>
        <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form26_'+${st_head.id},'Save Success!','0','0',saveNewDateForm('${st_head.id}','${st_head.ref}','${pi_pager}','${dn_pager}',billing_month_data, kingdee_date_data, payment_date_data),'saveMSN')"/>
        <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
    </div>
</div>
<input type='hidden' id='st_head_type' value="${const.IMP_TYPE}" />

<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>
    % if const.IMP_TYPE == 2:
    	PI List
    % else:
    	Statement Detail
    % endif 
    </div>
    <div class="box4">
	    <div id="piSearch" class="piSearch_${st_head.id}">
		    <input type="hidden" name="id" value="${st_head.id}" cid='piSearch'/>
		    <input type="hidden" name="pi_pager" value="0" cid='piSearch'/>
		    <input type="hidden" name="dn_pager" value="0" cid='piSearch'/>
		    <input type="hidden" name="type" value="${const.ERP_HEAD_TYPE_ST}" cid='piSearch'/>
		    ${dzd_pi_search_form()|n}
		    <input type="button" id="piResetSearchButton"  value="Reset" class="btn" onclick="javascript:resetDzdSearch('.piSearch_${st_head.id}', 'piSearch')">
		    <input type="button" id="piSearchButton"  value="Search" class="btn" onclick="javascript:dzdSearch('.piSearch_${st_head.id}', '${st_head.ref}', 'piSearch')">
	    </div>
    	<div class="clear"></div>
    <form action="/report/export_dzd" method="post" id="form5_st_head_pi_${st_head.id}" style="display:none">
        <input type="hidden" name="id" value="${st_head.id}"/>
        <input type="hidden" name="head_type" value="pi"/>
    </form>
    <form action="/report/export_mpi" method="post" id="form5_st_head_mpi_${st_head.id}" style="display:none">
        <input type="hidden" name="id" value="${st_head.id}"/>
        <input type="hidden" name="head_type" value="pi"/>
    </form>
    <form action="/ap/update_statement" method="POST" id="${st_head.ref}_update_statement">
    	<input name='st_head' type='hidden' value='${st_head.id}'/>
    	<input name='category' type='hidden' value="${const.ERP_HEAD_TYPE_ST}"/>
    	<input name='p_ids' type="hidden" value="">
    	<p><input type="submit" class="btn"  id="update_statement" value="Add to MPI" style="float:left;margin-right:15px;clear:none;margin-left:15px;" name="type" onclick="ajaxForm('#${st_head.ref}_update_statement','Save Success!','${st_head.id}','${st_head.ref}',null,'statement')"> 
		<input type="submit" class="btn" value="Save" style="clear:none;margin-left:15px;" name="type" onclick="ajaxForm('#${st_head.ref}_update_statement','Save Success!','${st_head.id}','${st_head.ref}',checkSelect('#${st_head.ref}_update_statement'),'statement')" >
        <input type="submit" class="btn" value="Delete" style="clear:none;margin-left:15px;" name="type" onclick="ajaxForm('#${st_head.ref}_update_statement','Delete Success!','${st_head.id}','${st_head.ref}',checkSelectNoComplete('#${st_head.ref}_update_statement', 'pi'),'statement')" >
        <input type="button" class="btn" value="Set Date" style="clear:none;margin-left:15px;" name="type" onclick="javascript:openNewSetDateForm('${st_head.id}', 'pi')" >
        &nbsp;<input type="button" onclick="javascript:exportData('st_head_pi_${st_head.id}')" value="Export" class="btn">
        &nbsp;<input type="button" onclick="javascript:exportData('st_head_mpi_${st_head.id}')" value="Export MPI" class="btn">
        </p>
        <br />
        % if const.IMP_TYPE == 2:
        	<p style="font-weight:bold">PI Amount: ${c_pi_amount}</p>
        	<table class="gridTable" cellpadding="0" cellspacing="0" border="0">
	            <thead>
	                <tr>
	                	<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'${st_head.id}_pi_list')" value="0"></th>
	                	<th>No.</th>
	                    <th>Invoice Number</th>
	                    <th>Item Code</th>
	                    <th>Qty</th>
	                    <th>Unit Price</th>
	                    <th>Item Amount</th>
	                    <th>Item Base Amount</th>
	                    <th>${u'\u7a0e\u7387'}</th>
	                    <th>${u'\u5f00\u7968\u6708\u4efd'}</th>
	                    <th>${u'\u5165\u91d1\u8776\u6708\u4efd'}</th>
	                    <th>${u'\u5bf9\u5e10\u6279\u53f7'}</th>
	                    <th>${u'\u4ed8\u6b3e\u65e5\u671f'}</th>
	                    <th>MPI Ref</th>
	                    <th>Department</th>
	                    <th>Issue Date</th>
	                    <th>Supplier Code</th>
	                    <th>Supplier Name</th>
	                    <th>Supplier Short Name</th>
	                    <th>Remark</th>
	                    <th>Currency</th>
	                    <th>Posted Status</th>
	                    <th>Invoice Amount</th>
	                    <th>Invoice Base Amount</th>
	                    <th>PO No.</th>
	                    <th>GRN No.</th>
	                    <th>Corporate Customer</th>
	                    <th>Private Brand</th>
	                    <th>Private Brand Sub-Line</th>
	                    <th>Packaging Category</th>
	                    <th>Packaging Type</th>
	                    <th>Material</th>
	                    <th>Merchandise</th>
	                    <th>Internal Item Code</th>
	                    
	                    <th style="width:120px;overflow:hidden">Item Description</th>
	                    
	                    <th>Unit</th>
	                   
	                    <th>Status</th>
	                </tr>
	            </thead>
	            <tbody class="${st_head.id}_pi_list">
	                % for i in stdetails:
	                <% errors = i.error.split(",") if i.status == "uncomplete" and i.error else [] %>
	                <tr>
	                	<td class="head"><input type="checkbox"  value="${i.id}" class="cboxClass" name='select_id'></td>
	                	<td>${i.id}</td>
	                    <td class="head">${i.invoice_no}&nbsp;</td>
	                    %if i.status == 'uncomplete':
	                   	%if "item_code" in errors:
	                    	<td>
	                    %else:
	                    	<td style="background-color:#f00">
	                    %endif 
	                    	<input class="item_code" name='item_code_${i.id}' type='text' value='${i.item_code}' statement='item_code' ids='${i.id}'/>
	                    </td>
	                    %else:
	                    <td>${i.item_code}</td>
	                    %endif 
	                    %if i.status == 'uncomplete':
		                  	%if "qty" in errors:
		                    	<td>
		                    %else:
		                    	<td style="background-color:#f00">
		                    %endif 
		                    	<input class="qty" name='qty_${i.id}' type='text' value='${i.qty}' statement='qty' ids='${i.id}'/></td>
		                %else:
		                	<td>${i.qty}&nbsp;</td>
		                %endif
	                    %if i.status == 'uncomplete':
		                    %if "unit_price" in errors:
		                    	<td>
		                    %else:
		                    	<td style="background-color:#f00">
		                    %endif 
		                    	<input class="unit" name='unit_${i.id}' type='text' value='${i.unit_price}' statement='unit' ids='${i.id}'/></td>
		                %else:
		                	<td>${i.unit_price}&nbsp;</td>
		                %endif 
	                    <td id='item_amount_${i.id}'>${i.item_amount}&nbsp;</td>
	                    <td id='item_base_amount_${i.id}'>${i.item_base_amount}&nbsp;</td>
	                    <td>${i.tax_rate}</td>
	                    % if i.billing_month or i.status == 'complete':
	                    <td>
	                    % else:
	                    	<td style="background-color:#f00">
	                    % endif 
	                    <input name='billing_month_${i.id}' type='text' value='${i.billing_month}' ids='${i.id}'/>&nbsp;</td>
	                   	% if i.kingdee_date or i.status == 'complete':
	                    <td>
	                    % else:
	                    	<td style="background-color:#f00">
	                    % endif 
	                    <input name='kingdee_date_${i.id}' type='text' value='${i.kingdee_date}' ids='${i.id}'/>&nbsp;</td>
	                    % if i.reconciliation_lot or i.status == 'complete':
	                    <td>
	                    % else:
	                    	<td style="background-color:#f00">
	                    % endif 
	                    <input name='reconciliation_lot_${i.id}' type='text' value='${i.reconciliation_lot}' ids='${i.id}'/>&nbsp;</td>
	                   	% if i.payment_date or i.status == 'complete':
	                    <td>
	                    % else:
	                    	<td style="background-color:#f00">
	                    % endif 
						<input name='payment_date_${i.id}' type='text' value='${i.payment_date}' ids='${i.id}'/>&nbsp;</td>
	                    <td>
	                    %if i.mpi_id:
	                    <a href="javascript:viewPhead('${i.mpi_id}', '${i.mpi_ref}')">${i.mpi_ref}</a>&nbsp;
	                    %endif
	                    </td>
	                    <td>${i.department}</td>
	                    <td>${i.issue_date}&nbsp;</td>
	                    <td>${i.supplier_code}&nbsp;</td>
	                    <td>${i.supplier_name}&nbsp;</td>
	                    <td>${i.supplier_short_name}&nbsp;</td>
	                    <td>${i.remark}&nbsp;</td>
	                    <td>${i.currency}&nbsp;</td>
	                    <td>${i.posted_status}&nbsp;</td>
	                    <td>${i.invoice_amount}&nbsp;</td>
	                    <td>${i.invoice_base_amount}&nbsp;</td>
	                    <td>${i.po_no}&nbsp;</td>
	                    <td>${i.grn_no}&nbsp;</td>
	                    <td>${i.corporate_customer}&nbsp;</td>
	                    <td>${i.private_brand}&nbsp;</td>
	                    <td>${i.private_brand_sub_line}&nbsp;</td>
	                    <td>${i.packaging_category}&nbsp;</td>
	                    <td>${i.packaging_type}&nbsp;</td>
	                    <td>${i.material}&nbsp;</td>
	                    <td>${i.merchandise}&nbsp;</td>
	                    <td>${i.internal_item_code}&nbsp;</td>
	                    <td><div style="width:120px;overflow:hidden">${i.item_description}&nbsp;</div></td>
	                    <td>${i.unit}&nbsp;</td>
	                    <td>${i.status}&nbsp;
	                    <input name='tax_rate_${i.id}' type='hidden' value='0.17' ids='${i.id}'/>
	                    <input name='status_b_${i.id}' type='hidden' value='${i.status}'/>
	                    <input name='mpi_b_${i.id}' type='hidden' value='${i.mpi_id}'/>
	                    </td>
	                </tr>
	             % endfor
	            </tbody>
	            <tfoot>
	            <tr>
	            <td style="border-right:0px;border-bottom:0px" colspan="100">
	            <div id="topSpace" style="font-weight:bold">
		             %if pi_pager>0:
		             	<a onclick="viewStatement1('${st_head.id}','${st_head.ref}', '${pi_pager-1}', '${dn_pager}')" class="pager_link" href="javascript:void(0)" style="float:left">pre&nbsp;page</a>
		             %endif
		             % if len(stdetails) == 15:
		             	<a onclick="viewStatement1('${st_head.id}','${st_head.ref}', '${pi_pager+1}', '${dn_pager}')" class="pager_link" href="javascript:void(0)" style="float:left">next&nbsp;page</a>
		            % endif
	            </div>
	            </td>
	            </tr>
	            </tfoot>
	        </table>
        % else:
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                	<th  class="head"><input type="checkbox" onclick="selectAllDetail(this,'${st_head.id}_item_list')" value="0"></th>
                    <th>D/N No</th>
                    <th>PO NO</th>
                    <th>Product Name</th>
                    <th >Item Code</th>
                    <th >Qty</th>
                    <th>Unit</th>
                    <th>Tax Rate</th>
                    <th>RMB Unit</th>
                    <th>RMB Amount</th>
                    <th>RMB Tax</th>
                    <th>RMB Amount</th>
                    <th>Status</th>
                    <th>Remark</th>
                </tr>
            </thead>
            <tbody class="${st_head.id}_item_list">
                % for i in stdetails:
                <% errors = i.error.split(",") if i.status == "uncomplete" and i.error else [] %>
                <tr>
                	<td class="head"><input type="checkbox"  value="${i.id}" class="dboxClass" name='select_id'></td>
                    <td class="head">${i.dn_no}&nbsp;</td>
                    <td>${i.po_no}</td>
                    <td>${i.desc_zh}&nbsp;</td>
                    %if i.status == 'uncomplete':
                    %if "item_code" in errors:
                    	<td>
                    %else:
                    	<td style="background-color:#f00">
                    %endif 
                    	<input class="item_code" name='item_code_${i.id}' type='text' value='${i.item_code}' statement='item_code' ids='${i.id}'/></td>
                    %if "qty" in errors:
                    	<td>
                    %else:
                    	<td style="background-color:#f00">
                    %endif 
                    	<input class="qty" name='qty_${i.id}' type='text' value='${i.qty}' statement='qty' ids='${i.id}'/></td>
                    %if "unit_price" in errors:
                    	<td>
                    %else:
                    	<td style="background-color:#f00">
                    %endif 
                    	<input class="unit" name='unit_${i.id}' type='text' value='${i.unit_price}' statement='unit' ids='${i.id}'/></td>
                    <td><input class="tax_rate" name='tax_rate_${i.id}' type='text' value='${i.tax_rate}' statement='tax_rate' ids='${i.id}'/></td>
                    %else:
                    	<td>${i.item_code}</td>
                    	<td>${i.qty}</td>
                    	<td>${i.unit_price}&nbsp;</td>
                    	<td>${i.tax_rate}&nbsp;</td>
                    %endif 
                    <td id='rmb_unit_${i.id}'>${i.rmb_unit}&nbsp;</td>
                    <td id='rmb_amount_${i.id}'>${i.rmb_amount}&nbsp;</td>
                    <td id='rmb_tax_${i.id}'>${i.rmb_tax}&nbsp;</td>
                    <td id='rmb_amount_p_${i.id}'>${i.rmb_amount_p}&nbsp;</td>
                    <td>${i.status}
                    <td><input class="unit" name='remark_${i.id}' type='text' value='${i.remark}'/></td>
                    <input name='rmb_unit_${i.id}' type='hidden' value='${i.rmb_unit}' ids='${i.id}'/>
                    <input name='rmb_amount_${i.id}' type='hidden' value='${i.rmb_amount}' ids='${i.id}'/>
                    <input name='rmb_tax_${i.id}' type='hidden' value='${i.rmb_tax}' ids='${i.id}'/>
                    <input name='rmb_amount_p_${i.id}' type='hidden' value='${i.rmb_amount_p}' ids='${i.id}'/>
                    </td>
                </tr>
             % endfor
            </tbody>
        </table>
        % endif
        </form>
    </div>
</div>

<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>DN List</div>
    <div class="box4">
    <form action="" method="get" id="dnSearch" class="dnSearch_${st_head.id}">
	    <input type="hidden" name="id" value="${st_head.id}" cid='dnSearch'/>
	    <input type="hidden" name="pi_pager" value="0" cid='dnSearch'/>
	    <input type="hidden" name="dn_pager" value="0" cid='dnSearch'/>
	    <input type="hidden" name="type" value="${const.ERP_HEAD_TYPE_DN}" cid='dnSearch'/>
	    ${dzd_dn_search_form()|n}
	    <input type="button" id="dnResetSearchButton"  value="Reset" class="btn" onclick="javascript:resetDzdSearch('.dnSearch_${st_head.id}', 'dnSearch')">
	    <input type="button" id="dnSearchButton" value="Search" class="btn" onclick="javascript:dzdSearch('.dnSearch_${st_head.id}', '${st_head.ref}', 'dnSearch')">
    </form>
    <div class="clear"></div>
    <form action="/report/export_dzd" method="post" id="form5_st_head_dn_${st_head.id}" style="display:none">
        <input type="hidden" name="id" value="${st_head.id}"/>
        <input type="hidden" name="head_type" value="dn"/>
    </form>
    <form action="/report/export_msn" method="post" id="form5_st_head_msn_${st_head.id}" style="display:none">
        <input type="hidden" name="id" value="${st_head.id}"/>
        <input type="hidden" name="head_type" value="dn"/>
    </form>
    <form action="/ap/update_statement" method="POST" id="${st_head.ref}_d_update_statement">
	    <input name='st_head' type='hidden' value='${st_head.id}'/>
	    <input name='category' type='hidden' value="${const.ERP_HEAD_TYPE_DN}"/>
	    <input name='p_ids' type="hidden" value="" >
    	<p><input type="submit" class="btn"  id="update_statement" value="Add to MSN" style="float:left;margin-right:15px;clear:none;margin-left:15px;" name="type" onclick="ajaxForm('#${st_head.ref}_d_update_statement','Save Success!','${st_head.id}','${st_head.ref}',null,'statement')"> 
		<input type="submit" class="btn" value="Save" style="clear:none;margin-left:15px;" name="type" onclick="ajaxForm('#${st_head.ref}_d_update_statement','Save Success!','${st_head.id}','${st_head.ref}',checkSelect('#${st_head.ref}_d_update_statement'),'statement')" >
        <input type="submit" class="btn" value="Delete" style="clear:none;margin-left:15px;" name="type" onclick="ajaxForm('#${st_head.ref}_d_update_statement','Delete Success!','${st_head.id}','${st_head.ref}',checkSelectNoComplete('#${st_head.ref}_d_update_statement', 'dn'),'statement')" >
        <input type="button" class="btn" value="Set Date" style="clear:none;margin-left:15px;" name="type" onclick="javascript:openNewSetDateForm('${st_head.id}','dn')" >
        &nbsp;<input type="button" onclick="javascript:exportData('st_head_dn_${st_head.id}')" value="Export" class="btn">
        &nbsp;<input type="button" onclick="javascript:exportData('st_head_msn_${st_head.id}')" value="Export MSN" class="btn">
        </p>
        <br />
        <p style="font-weight:bold">DN Amount: ${c_dn_amount}</p>
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                	<th  class="head"><input type="checkbox" onclick="selectAllDetail(this,'${st_head.id}_dn_list')" value="0"></th>
                    <th>No.</th>
                    <th>Item Code</th>
                    <th>Order Qty</th>
                    <th>Unit</th>
                    <th>Unit Price</th>
                    <th>Amount</th>
                    <th>Base Amount</th>
                    <th>${u'\u5f00\u7968\u6708\u4efd'}</th>
                    <th>${u'\u5165\u91d1\u8776\u6708\u4efd'}</th>
                    <th>${u'\u5bf9\u5e10\u6279\u53f7'}</th>
                    <th>${u'\u4ed8\u6b3e\u65e5\u671f'}</th>
                    <th>MSN Ref</th>
                    <th>Stock Adjustment No.</th>
                    <th>SO NO</th>
                    <th>PO NO</th>
                    <th>Note Type</th>
                    <th>Other Ref</th>
                    <th>Note Remark</th>
                    <th>Issue Date</th>
                    <th>Department</th>
                    <th>Supplier Code</th>
                    <th>Supplier Name</th>
                    <th>Sales Contact</th>
                    <th>Currency</th>
                    <th>Note Amount</th>
                    <th>Note Base Amount</th>
                    <th>Corporate Customer</th>
                    <th>Private Brand</th>
                    <th>Private Brand Sub-Line</th>
                    <th>Packaging Category</th>
                    <th>Packaging Type</th>
                    <th>Material</th>
                    <th>Merchandise</th>
                    <th>Internal Item Code</th>
                    <th>Item Description</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody class="${st_head.id}_dn_list">
                % for i in dndetails:
                <% errors = i.error.split(",") if i.status == "uncomplete" and i.error else [] %>
                <tr>
                	<td class="head"><input type="checkbox"  value="${i.id}" class="cboxClass" name='select_id'></td>
                    <td class="head">${i.number}&nbsp;</td>
                    %if i.status == 'uncomplete':
                   	%if "item_code" in errors:
                    	<td>
                    %else:
                    	<td style="background-color:#f00">
                    %endif 
                    	<input class="item_code" name='item_code_${i.id}_' type='text' value='${i.item_code}' statement='item_code' ids='${i.id}_'/>&nbsp;
                    	</td>
	                %else:
	                	<td>${i.item_code}&nbsp;</td>
	                %endif
                   	%if i.status == 'uncomplete':
                   	%if "qty" in errors:
                    	<td>
                    %else:
                    	<td style="background-color:#f00">
                    %endif 
                    	<input class="qty" name='qty_${i.id}_' type='text' value='${i.order_qty}' statement='qty' ids='${i.id}_'/>&nbsp;
                    </td>
	                    <td>${i.unit}&nbsp;</td>
	                %if "unit_price" in errors:
                    	<td>
                    %else:
                    	<td style="background-color:#f00">
                    %endif 
                    	<input class="unit" name='unit_${i.id}_' type='text' value='${i.unit_price}' statement='unit' ids='${i.id}_'/>&nbsp;</td>
                    %else:
	                    <td>${i.order_qty}&nbsp;</td>
	                    <td>${i.unit}&nbsp;</td>
	                    <td>${i.unit_price}&nbsp;</td>
                   	%endif
                    <td id='rmb_amount_${i.id}_'>${i.amount}&nbsp;</td>
                    <td id='rmb_amount_p_${i.id}_'>${i.base_amount}&nbsp;</td>
                    
                	% if i.billing_month or i.status == 'complete':
                    <td>
                    % else:
                    	<td style="background-color:#f00">
                    % endif 
	                <input name='billing_month_${i.id}_' type='text' value='${i.billing_month}' ids='${i.id}_'/>&nbsp;</td>
                    % if i.kingdee_date or i.status == 'complete':
                    <td>
                    % else:
                    	<td style="background-color:#f00">
                    % endif 
                    <input name='kingdee_date_${i.id}_' type='text' value='${i.kingdee_date}' ids='${i.id}_'/>&nbsp;</td>
                    % if i.reconciliation_lot or i.status == 'complete':
                    <td>
                    % else:
                    	<td style="background-color:#f00">
                    % endif 
                    <input name='reconciliation_lot_${i.id}_' type='text' value='${i.reconciliation_lot}' ids='${i.id}_'/>&nbsp;</td>
                    % if i.payment_date or i.status == 'complete':
                    <td>
                    % else:
                    	<td style="background-color:#f00">
                    % endif 
                    <input name='payment_date_${i.id}_' type='text' value='${i.payment_date}' ids='${i.id}_'/>&nbsp;</td>
                    <td>
                    %if i.msn_id:
                    <a href="javascript:viewShead('${i.msn_id}', '${i.msn_ref}')">${i.msn_ref}</a>&nbsp;
                    %endif
                    </td>
                    <td>${i.stock_adjustment_no}&nbsp;</td>
                    %if i.status == 'uncomplete':
                    <td>
                    	<input  name='so_no_${i.id}' type='text' value='${i.so_no}' />&nbsp;
					</td>
                    %else:
                    <td>${i.so_no}&nbsp;</td>
                    %endif
                    <td>${i.po_no}&nbsp;</td>
                    <td>${i.note_type}&nbsp;</td>
                    %if 'mpi' in errors:
                    <td style="background-color:#f00">
                    % else:
                    <td>
                    % endif 
                    ${i.other_ref}&nbsp;</td>
                    <td>${i.note_remark}&nbsp;</td>
                    <td>${i.issue_date}&nbsp;</td>
                    <td>${i.department}&nbsp;</td>
                    <td>${i.supplier_code}&nbsp;</td>
                    <td>${i.supplier_name}&nbsp;</td>
                    <td>${i.sales_contact}&nbsp;</td>
                    <td>${i.currency}&nbsp;</td>
                    <td>${i.note_amount}&nbsp;</td>
                    <td>${i.note_base_amount}&nbsp;</td>
                    <td>${i.corporate_customer}&nbsp;</td>
                    <td>${i.private_brand}&nbsp;</td>
                    <td>${i.private_brand_sub_line}&nbsp;</td>
                    <td>${i.packaging_category}&nbsp;</td>
                    <td>${i.packaging_type}&nbsp;</td>
                    <td>${i.material}&nbsp;</td>
                    <td>${i.merchandise}&nbsp;</td>
                    <td>${i.internal_item_code}&nbsp;</td>
	                <td><div style="width:120px;overflow:hidden">${i.item_description}&nbsp;</div></td>
                    <td>${i.status}
                    <input name='tax_rate_${i.id}_' type='hidden' value='0' ids='${i.id}_'/>
                    <input name='status_b_${i.id}_' type='hidden' value='${i.status}'/>
                    <input name='msn_b_${i.id}_' type='hidden' value='${i.msn_id}'/>
                    </td>
                </tr>
             % endfor
            </tbody>
            <tfoot>
	            <tr>
	            <td style="border-right:0px;border-bottom:0px;" colspan="100">
	            <div id="topSpace" style="font-weight:bold;text-align:left">
	             %if dn_pager>0:
	             <a onclick="viewStatement1('${st_head.id}','${st_head.ref}', '${pi_pager}', '${dn_pager-1}')" class="pager_link" href="javascript:void(0)" style="float:left">pre&nbsp;page</a>
	             %endif
	             % if len(dndetails) == 15:
	             <a onclick="viewStatement1('${st_head.id}','${st_head.ref}', '${pi_pager}', '${dn_pager+1}')" class="pager_link" href="javascript:void(0)" style="float:left">next&nbsp;page</a>
	             % endif
	            </div>
	            </td>
	            </tr>
	            </tfoot>
        </table>
        </form>
    </div>
</div>
%endif

 
