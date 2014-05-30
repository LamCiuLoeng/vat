<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf
%>
<script type="text/javascript">
		initTr();
		initScroll();
		initDate();
		disableBtn('#btn_save_as_msi', true);
	    var resetBtn = function(){
	        var vals = getCboxArr();
	        var btnValidate = vals.length ? true : false;
	        if(btnValidate){
	            disableBtn('#btn_save_as_msi', false)
	        }else{
	            disableBtn('#btn_save_as_msi', true)
	        }
	    }
</script>
<input type="hidden" name="cust" id="cust" value="${cust}"/>
<ul class="ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all" >
    <li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">Variance</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search Variance Result</div>
        <div class="box4">
        	<form action="/cost/update_variance" id="_form" method="post">
            <table class="gridTable gridTables" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
								        <input type="hidden" name="ids" id="ids"/>
								    	<input type="submit" class="btn" value="Save" id="btn_save_as_msi" onclick="ajaxForm('#_form','Save Success!','0','0',saveAllToThead(),'save')" />
								    	<input type="submit" style="display:none">
                                </div>
                                <div class="r" style="font-weight:bold" id="topSpace">
                                	 <a href="/cost?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr id="theadObj">
			        	<th class="head cl3"><input type="checkbox" onclick="selectAllDetail(this, 'gridTables')" value="0"></th>
			        	<th class="cl3">SO#</th>
			            <th class="cl3">PO#</th>
			            <th class="cl3">PI#</th>
			            <th class="cl3">Note No</th>
			            <th class="cl3">GRN No</th>
			            <th class="cl3">GRN Line No</th>
			            <th class="cl3">Supplier Short Name</th>
			            <th class="cl3">designation</th>
			            <th class="cl3">Set Item</th>
			            <th class="cl3">PO Qty</th> 
			            <th class="cl3">币别</th> 
			            <th class="cl3">汇率</th>
			            <th class="cl3">未税单价</th>
			            <th class="cl3">未税金额</th>
			            <th class="cl3">货款所属期（开票月份）</th>
			            <th class="cl3">更改项目</th>
			            <th>未税单价</th>
			            <th>未税金额</th>
			            <th>应调整成本差异</th>
			            <th>Adjusted Date</th>
			            <th>Related PI</th>
                    </tr>
                </thead>
                <tbody>
                     % for i in collections:
                     % if i.head_type == const.ERP_TYPE_DETAIL:
                     <% variance_key = '%s$%s' % (i.grn_no, i.grn_line_no)%>
                     % elif i.head_type == const.ERP_TYPE_CHARGE:
                     <% variance_key = '%s$%s$%s' % (i.purchase_invoice_no, i.head_type, i.line_no)%>
                     % else:
                     <% variance_key = '%s$%s$%s' % (i.note_no, i.head_type, i.line_no)%>
                     % endif
                    <tr id="tr1_">
			            <td class="head">
							<input type="checkbox" class="cboxClass"  value="${variance_key}"  name="checkd" onclick="selectOne()">
			        	</td>
			        	% if i.so_no:
			        		<td class="SO#">${i.so_no}<input value="${i.so_no}" type="hidden" name="so_no_${variance_key}" />&nbsp;</td>
			        	% else:
			        		<td class="SO#"><input type="text" name="so_no_${variance_key}" />&nbsp;</td>
			        	% endif 
			        	% if i.po_no:
			            	<td class="PO#">${i.po_no}<input value="${i.po_no}" type="hidden" name="po_no_${variance_key}" />&nbsp;</td>
			            % else:
			            	<td class="PO#"><input type="text" name="po_no_${variance_key}" />&nbsp;</td>
			            % endif 
			            % if i.purchase_invoice_no and i.head_type in [const.ERP_TYPE_DETAIL, const.ERP_TYPE_CHARGE]:
			            	<td class="PI#">${i.purchase_invoice_no}<input type="hidden" name="pi_no_${variance_key}" value="${i.purchase_invoice_no}"/>&nbsp;</td>
			            % else:
			            	<td class="PI#"><input type="text" name="pi_no_${variance_key}" value="${i.purchase_invoice_no}"/></td>
			            % endif 
			            <td class="Note No">${i.note_no if i.head_type == const.ERP_TYPE_OTHER_CHARGE else None}&nbsp;</td>
			            <td class="Grn No">${i.grn_no if i.head_type == const.ERP_TYPE_DETAIL else ' '}&nbsp;</td>
			            <td class="Grn Line No">${i.grn_line_no if i.head_type == const.ERP_TYPE_DETAIL else ' '}&nbsp;</td>
			            <td title="Supplier Short Name">${i.supplier_short_name}<input type="hidden" value="${i.supplier_short_name}" name="supplier_short_name_${variance_key}" />&nbsp;</td>
			            <td title="designation">${i.designation}<input type="hidden" value="${i.designation}" name="designation_${variance_key}" />&nbsp;</td>
			            <td title="Set Item">${i.item_no}<input type="hidden" value="${i.item_no}" name="item_no_${variance_key}" />&nbsp;</td>
			            <td title="PO Qty">${i.po_qty}<input type="hidden" value="${i.po_qty}" name="po_qty_${variance_key}" />&nbsp;</td> 
			            <td title="币别">${i.currency}<input type="hidden" value="${i.currency}" name="currency_${variance_key}" />&nbsp;</td> 
			            <td title="汇率">${i.exchange_rate}<input type="hidden" value="${i.exchange_rate}" name="exchange_rate_${variance_key}" />&nbsp;</td>
			            <td title="未税单价" id="with_out_price_${variance_key}">&nbsp;${i.with_out_price}</td> 
			            <td title="未税金额" id="with_out_amount_${variance_key}">&nbsp;${i.with_out_amount}</td> 
			            <td title="货款所属期（开票月份）"><input type="text" value="${i.billing_month}" name="billing_month_${variance_key}"/>&nbsp;</td> 
			            <td title="更改项目"><input type="text" value="${i.change_project}" name="change_project_${variance_key}"/>&nbsp;</td> 
			            <td title="未税单价">${i.change_with_out_price} <input type="hidden" value="${i.change_with_out_price}" name="change_with_out_price_${variance_key}"/>&nbsp;</td> 
			            <td title="未税金额">${i.change_with_out_amount} <input type="hidden" value="${i.change_with_out_amount}" name="change_with_out_amount_${variance_key}"/>&nbsp;</td> 
			            <td title="应调整成本差异" id="variance_amount_${variance_key}">${i.variance_amount}&nbsp;
			             </td> 
			             <td><input type="text" class="datePickerNoImg" name="variance_date_${variance_key}"/></td>
			             <td>
			             % if hasattr(i, 'related_pi'):
			             <input type="button" value="Add" class="btn" onclick="autoDialog('${variance_key.replace('$', '_')}', 'related SI')"/>
			             <input type="hidden" value="" name="related_${variance_key}" />
			             % endif
			             &nbsp;
			             </td>
		             	<input type="hidden" value="${i.variance_amount}" name="variance_amount_${variance_key}"/>
						% if i.head_type == const.ERP_TYPE_CHARGE:
							<input type="hidden" value="${i.charge_code}" name="charge_code_${variance_key}"/>
						% else:
							<input type="hidden" value="${i.variance_price}" name="variance_price_${variance_key}"/>	
						% endif
			             <input type="hidden" value="${i.with_out_price}" name="with_out_price_${variance_key}"/>
			             <input type="hidden" value="${i.with_out_amount}" name="with_out_amount_${variance_key}" />
                    </tr>
                    %endfor
                    </tbody>
                    <tfoot>
             			<tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace"> <a href="/cost?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a></td></tr>
                    </tfoot>
            </table>
            </form>
        </div>
    </div>
</div>

<table class="gridTableb" cellpadding="0" cellspacing="0" border="0" id="scroll" style="position:absolute;left:7px;top:0px;display:none">
    <thead>
        <tr id="scrollObj">
        	<th class="head cl3"><input type="checkbox" onclick="selectAllDetail(this, 'gridTables')" value="0"></th>
        	<th class="cl3">SO#</th>
            <th class="cl3">PO#</th>
            <th class="cl3">PI#</th>
            <th class="cl3">Charge</th>
            <th class="cl3">Supplier Short Name</th>
            <th class="cl3">designation</th>
            <th class="cl3">Set Item</th>
            <th class="cl3">PO Qty</th> 
            <th class="cl3">币别</th> 
            <th class="cl3">汇率</th>
            <th class="cl3">未税单价</th>
            <th class="cl3">未税金额</th>
            <th class="cl3">Charge Total</th>
            <th class="cl3">货款所属期（开票月份）</th>
            <th class="cl3">更改项目</th>
            <th>未税单价</th>
            <th>未税金额</th>
            <th>应调整成本差异</th>
            <th>Variance Date</th>
        </tr>
    </thead>
</table>

% for i in collections:
 % if i.head_type == const.ERP_TYPE_DETAIL:
 <% variance_key = '%s$%s' % (i.grn_no, i.grn_line_no)%>
 % elif i.head_type == const.ERP_TYPE_CHARGE:
 <% variance_key = '%s$%s$%s' % (i.purchase_invoice_no, i.head_type, i.line_no)%>
 % else:
 <% variance_key = '%s$%s$%s' % (i.note_no, i.head_type, i.line_no)%>
 % endif
 <div style="display:none" id="dialog_${variance_key.replace('$', '_')}" class="dialog_${variance_key.replace('$', '_')}">
 		<form action="/cost/related" method="post" id="form1_${variance_key.replace('$', '_')}">
 		<p><input type="button" value="Save" po_qty ="${i.po_qty}" onclick="checkRelated('dialog_${variance_key.replace('$', '_')}')" class="btn"></p>
 		<table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr id="theadObj">
			        	<th class="head cl3"><input type="checkbox" onclick="selectAllDetail(this, 'dialog_${variance_key.replace('$', '_')}')" value="0"></th>
			        	<th class="cl3">PO#</th>
			            <th class="cl3">PI#</th>
			            <th class="cl3">Item No</th>
			            <th class="cl3">Unit Price</th>
			           	<th class="cl3">Qty</th>
			           	<th class="cl3">Total</th>
                    </tr>
                </thead>
                <tbody>
                	 % if hasattr(i, 'related_pi'):
 					 %for related in i.related_pi:
 					 	<tr>
                		<td class="head">
							<input type="checkbox" class="cboxClass"  value="${related.id}"  name="ids" onclick="selectOne()">
			        	</td>
			        	<td>${related.po_no}</td>
			        	<td>${related.pi_no}</td>
			        	<td>${related.item_no}</td>
			        	<td>${related.pi_unit_price}</td>
			        	<td>${related.pi_qty} <input type="hidden" name="pi_qty" value='${related.pi_qty}' ids="${related.id}" unit_price="${related.pi_unit_price}"/></td>
			        	<td>${related.pi_total}</td>
			        	</tr>
			        %endfor
 					% endif
                </tbody>
        </table>
        </form>
 </div>
% endfor
