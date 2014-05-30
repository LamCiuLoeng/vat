<%
    from decimal import Decimal
    from vatsystem.model import RID,RICharge,UID,UICharge,PI
    from vatsystem.util import const
    from vatsystem.util.mako_filter import b,pd,pi,pf,pt,pq,pipo
%>
%if flag==1:
<script>
    showError("Error");
</script>
%else:
<script type="text/javascript">
	initTotal();
	initToogle();
	initChangeVal();
	intiParsePrice();
	initPayment();
	initStatement();
	initPOTotal('${oHead.id}');
	initGetAll('#${oHead.ref}');
	$("#charge_add_${oHead.id}").fancybox({ 
		'width'				: '80%',
		'height'			: '80%',
		'autoScale'			: false,
		'transitionIn'		: 'none',
		'transitionOut'		: 'none',
		'type'				: 'iframe',
		onClosed	        :  function() {viewOhead('${oHead.id}','${oHead.ref}')}		
	})
</script>
<style type="text/css">
<!--
.iframe{border: 1px solid #336633; padding: 4px; background-color:#ffeedd;color:#336633;font-weight:bold;margin:0}
-->
</style>
<!--header start-->
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>CST Information</div>
    <div>
        <div class="toolbar">
             <input type="button" onclick="javascript:exportData('cost_${oHead.id}_1')" value="Export" class="btn">
	        	<form action="/report/export_cst" method="post" id="form5_cost_${oHead.id}_1" style="display:none">
		            <input type="hidden" name="id" value="${oHead.id}"/>
		            <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_CST}"/>
	            </form>
        	<input type="button" class="btn" value="History" onclick="OpenDialog('/ar/view_history?type=O&id=${oHead.id}','#searchDialog','${oHead.ref} History')" href="javascript:void(0)" > 
        </div>
        <ul>
            <li class="li1">Customer:</li>
            <li class="li2">${oHead.customer_code}</li>
            <li class="li1">Customer Name:</li>
            <li class="li2 fcn" style="float:left;width:400px;" >${oHead.customer_short_name}</li>
        </ul>
         % if len(oHead.t_heads)>0:
        <ul>
            <li class="li1">MSI/MSO Ref:</li>
            <% t_head = oHead.t_heads[0] %>
            <li class="li2">${t_head.ref }</li>
            <li class="li1">MSI/MSO VAT No:</li>
            <li class="li2">${t_head.vat_no}</li>
        </ul>
        %endif 
        <ul>
            <li class="li1">Status:</li>
            <li class="li2">${oHead.status}</li>
            <li class="li1">Ref No:</li>
            <li class="li2">${oHead.ref}</li>
        </ul>
        %if oHead.vat_no or oHead.vat_date:
        <ul>
            <li class="li1">VAT No:</li>
            <li class="li2"  id='vat_no_${oHead.id}'>${oHead.vat_no}</li>
            <li class="li1">VAT Date:</li>
            <li class="li2">${pt(oHead.vat_date)}</li>
        </ul>
        %endif
        <ul>
            <li class="li1">Create Date:</li>
            <li class="li2">${pt(oHead.create_time)}</li>
            <li class="li1">Update Date:</li>
            <li class="li2">${pt(oHead.update_time)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>
<div class="clear"></div>
<!--cst start-->
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>CST</div>
    <div class="box4" id="check_ava_$${oHead.id}">	
	     %if oHead.status == const.VAT_THEAD_STATUS_NEW:
	    	<p style='display:none'>
	    		<input type="button" class="btn"  value="Delete" onclick="deleteItem('/cost/ajax_delete_item','${oHead.ref}_item_list','CST','${oHead.id}','${oHead.ref}')" />
	    		<br />
	    	</p>
	    %endif
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                	%if oHead.status == const.VAT_THEAD_STATUS_NEW:
                	<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'${oHead.ref}_item_list')" value="0"></th>
                    %endif
                    <th class="head">SO NO</th>
                    <th>SI No</th>
                    <th>Designation</th>
                    <th>Customer</th>
                    <th>Currency</th>
                    <th class="cl5">Order Amount</th>
                    <th class="cl5">Item Amount</th>
                    <th>Order Amount</th>
                    <th>Item Amount</th>
                    <th>Create Time</th>
                </tr>
            </thead>
            <tbody class="${oHead.ref}_item_list">
            	<% 
            	curr_charge1 = []
            	curr_charge2 = []
            	charges = []
            	%>
            	<% 
                for cha in oHead.cp_charges:
                	if cha.type == const.CHARGE_TYPE_P_MAN:
                	    if not cha in curr_charge1:
                	        curr_charge1.append(cha)
                	else:
                	    if cha not in curr_charge2:
                	        curr_charge2.append(cha)
                	if cha not in charges:
                	    charges.append(cha) 
                %>
                % for so in oHead.co_heads:
                <tr>
                	%if oHead.status == const.VAT_THEAD_STATUS_NEW:
                		<td class="head"><input type="checkbox"   value="${so.id}" class="dboxClass"></td>
                    % endif
                    <td>
                    <a href="javascript:void(0)" onclick="toggleOne('tr2_'+${so.id})">${so.sales_contract_no}</a></td>
                    <td>${so.invoice_no}&nbsp;</td>
                    <td>${so.ae}&nbsp;</td>
                    <td>${so.customer_name}</td>
                    <td>${so.currency}</td>
                    <td>${round(so.order_amt,2)}</td>
                    <td>${round(so.item_amt,2)}</td>
                    <td class='payment' cate='order_amount' id="order_amount_${so.sales_contract_no}" invoice='${so.sales_contract_no}' Head_id='${so.id}'> &nbsp;</td>
                    <td class='payment' cate='item_amount' id="item_amount_${so.sales_contract_no}" invoice='${so.sales_contract_no}' Head_id='${so.id}'> &nbsp;</td>
                    <td>${pd(so.create_time)}</td>
                </tr>
                <tr class="toggle none" id="tr2_${so.id}">
                    <td colspan="100" class="gridInTd">
                        <div class="gridInDiv">
                            <form action="/cost/update_ohead_details" method="post" id="_form_si${so.id}">
                                %if oHead.status == const.VAT_THEAD_STATUS_NEW:
                                	<input name='type' type="submit" style="display:none" class="btn"  value="Save" onclick="ajaxForm('#_form_si${so.id}','Save Success!','${oHead.id}','${oHead.ref}',toSaveSISODetails('so','${so.id}'),'cst_save')" style="clear:none;margin-right:10px;"/>
                                	<input name='type' type="submit" class="btn"  value="Delete" onclick="ajaxForm('#_form_si${so.id}','Delete Success!','${oHead.id}','${oHead.ref}',toSaveSISODetails('so','${so.id}'),'cst_save')" style="clear:none;margin-right:10px;"/>
                                %endif
                                <input type="hidden" name="id" value="${oHead.id}"/>
                                <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_CST}"/>
                                <div class="title">Detail</div>
                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Item NO</th>
                                            <th>VAT Qty</th>
                                            <th>Unit Price</th>
                                            <th>Description</th>
                                            <th>Item Amount(Without Tax)</th>
                                            <th>Item Amount</th>
                                            <th>Unit</th>
                                            <th>Remark</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in so.find_details():
                                        <tr name="detail_${j.id}" >
                                            <td class="head"> ${j.line_no} </td>
                                            <td>${j.item_no}</td>
                                            <td>${j.vat_qty}</td>
                                            <td>${j.unit_price}</td>
                                            <td>${j.desc_zh if j.desc_zh else j.description}&nbsp;</td>
                                            <td id="rmb_amount_p_${j.id}" >${round(j.vat_qty*j.unit_price,2)}</td>
	                                        <td id="rmb_amount_${j.id}" >${round(j.vat_qty*j.unit_price*(1+j.tax_rate),2)}</td>
                                            <td>${j.unit}</td>
                                            <td><input type="text" name="remark_${j.id}" value="${j.remark}">
                                        	<input statement class="qty numeric" type="hidden" name="qty_${j.id}" value="${j.vat_qty}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' />
	                                        <input class="desc" type="hidden" name="desc_${j.id}" value="${j.desc_zh if j.desc_zh else j.description}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}'/>
                                        	<input type="hidden" name="item_amount_${j.id}" value="${round(j.vat_qty*j.unit_price,2)}" cate='item_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${so.sales_contract_no}" Head_id='${so.id}'/>
											<input type="hidden" name="order_amount_${j.id}" value="${round(j.vat_qty*j.unit_price*(1+j.tax_rate),2)}" cate='order_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${so.sales_contract_no}" Head_id='${so.id}'/>
                                       		</td>
                                        </tr>
                                       <!--si list -->
										  %if len(j.cp_details) > 0:
						                  <tr  style="display: table-row;">
						                    <td class="gridInTd" colspan="100">
						                        <div class="gridInDiv">
						  								<div class="title other_charge_tab" >Related PO/PI</div>
						  								<div class="other_charge_content" style="display:none" >
							                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
												            <thead class='cl3'>
												                <tr>
												                	%if oHead.status == const.VAT_THEAD_STATUS_NEW:
												                		<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'relation_pi_${j.id}')" value="0"></th>
												                    %endif
												                    <th>Line NO</th>
												                    <th>PO NO</th>
												                    <th>PI NO</th>
												                    <th>GRN NO</th>
												                    <th>GRN Line NO</th>
												                    <th>Supplier Code</th>
												                    <th>Supplier Name</th>
												                    <th>Item NO</th>
												                    <th>Item Qty</th>
												                    <th>Unit</th>
												                    <th>PO Qty</th>
												                    <th>PI Qty</th>
												                    <th>Unit Price</th>
												                    <th>PI Unit Price</th>
												                    <th>PO Amount</th>
												                    <th>PI Amount</th>
												                    <th>Description</th>
												                </tr>
												            </thead>
												            <tbody>
												                % for i in j.cp_details:
												                <tr class="relation_pi_${j.id}">
												                	%if oHead.status == const.VAT_THEAD_STATUS_NEW:
													                	<td class="head">
																			<input type="checkbox" value="${so.id}" class="dboxClass" name="checkbox_${i.id}">
													                	</td>
												                	%endif
												                    <td class="head">${i.line_no}</td>
												                    <td>${i.po_no}</td>
												                   	<td>${i.pi_no}&nbsp;</td>
												                   	<td>${i.grn_no}&nbsp;</td>
												                   	<td>${i.grn_line_no}&nbsp;</td>
												                   	<td>${i.supplier}</td>
												                   	<td>${i.supplier_name}</td>
												                    <td>${i.item_no}</td>
												                    <td>${i.item_qty}</td>
												                    <td>${i.unit}</td>
												                    <td>${i.po_qty}</td>
												                    %if oHead.status == 'const.VAT_THEAD_STATUS_NEW':
												                    	<td><input tax_rate='0.17' class="qty numeric" type="text" name="qty_${i.id}" value="${pi(float(i.pi_qty))}"/></td>
												                    	<td><input class="price" type="text" name="price_${i.id}" value="${i.unit_price}" /></td>
												                    %else:
												                    	 <td>${pi(float(i.pi_qty))}</td>
												                    	 <td>${i.unit_price}</td>
												                    %endif
												                    <td>${i.pi_unit_price} &nbsp;</td>
												                    <td>${pf(i.po_qty * i.unit_price)} &nbsp;</td>
												                    <td>${pf(i.pi_qty * i.unit_price)} &nbsp;</td>
												                    <td>${i.description}&nbsp;</td>
												                </tr>
												             % endfor
												            </tbody>
												        </table>
							                        </div>
													<!-- details end -->
												   </div>
												</div>
											  </td>
											</tr>
										 %endif
										<!--si list end-->
                                        % endfor
                                    </tbody>
                                </table>
                            </form>
                        </div>
                    </td>
                </tr>
                % endfor
                <tr id="${oHead.ref}_tr">
                <td class="gridInTd" colspan="100" >
                <div class="gridInDiv">
                       <form action="/cost/update_to_othead" method="post" id="form1_charge${oHead.id}">
                        %if oHead.status == const.VAT_THEAD_STATUS_NEW:
	                        <input type="hidden" name="type" class="btn" value="Save" onclick="ajaxForm('#form1_charge${oHead.id}','Save Success!','${oHead.id}','${oHead.ref}',toSaveSISODetails('so','${so.id}'),'cst_save')" style="clear:none;margin-right:10px;">
							<input type="hidden" style="clear:none;margin-right:10px;" onclick="OpenDialog('/cost/ajax_view_new_charge?id=${oHead.id}', '#view_pi_${oHead.id}', 'Add Charge')" class="btn" value="Add Charge" name="add_new_charge">
							<input type="button" name="type" class="btn" value="Add Other Charge" id="charge_add_${oHead.id}" style="clear:none;margin-right:10px;" href="/cost/ajax_view_charge?head_type=${const.ERP_HEAD_TYPE_CST}&id=${oHead.id}" >
							<input type="submit" name="type" class="btn" value="Delete" onclick="ajaxForm('#form1_charge${oHead.id}','Delete Success!','${oHead.id}','${oHead.ref}',toSaveSISODetails('so','${so.id}'),'cst_save')" style="clear:none;margin-right:10px;">
							<input type="hidden" value="${const.ERP_HEAD_TYPE_CST}" name="head_type">
	                        <input type="hidden" value="${oHead.id}" name="id">
						%endif
							
								<div class="gridInDiv" style="margin-left:0">
                          		<div class="title other_charge_tab">Charge</div>
                          		% if len(curr_charge1) > 0:
  								<div class="other_charge_content" style="display:none" id="${oHead.ref}_charge" >
  								  <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                       <tr>
               								%if oHead.status == const.VAT_THEAD_STATUS_NEW:
						                	 	<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'relation_charge_${oHead.id}')" value="0"></th>
						                    %endif
                                            <th>Line NO</th>
                                            <th>PO NO</th>
                                            <th>PO Total</th>
                                            <th>PI NO</th>
                                            <th class="cl3">PI Total</th> 
                                            <th>Charge Code</th>
                                            <th>Type</th> 
                                        </tr>
                                    </thead>
                                    <tbody class="relation_charge_${oHead.id}">
                                    % for v,k in enumerate(curr_charge1):
                                        <tr>
                							%if oHead.status == const.VAT_THEAD_STATUS_NEW:
							                	<td class="head">
													<input type="checkbox" value="c" class="dboxClass" name="check_${k.id}">
							                	</td>
						                	%endif
                                            <td class="head">${v+1}</td>
                                            <td>${k.po_no}&nbsp;</td>
                                            %if oHead.status == 'const.VAT_THEAD_STATUS_NEW':
                                            	<td><input type="text" value="${pf(k.po_total)}" name="po_total_${k.id}" attr_id='${k.id}' class='charge_po_total_${oHead.id}'/>&nbsp;</td>
                                            %else:
                                            	<td>${k.po_total}&nbsp;</td>
                                            %endif
                                            <td>${k.pi_no}&nbsp;</td>
                                            %if oHead.status == 'const.VAT_THEAD_STATUS_NEW':
                                            	<td><input type="text" name="total_${k.id}" value="${pf(k.total)}"  class='charge_po_total_${oHead.id}' attr_id='${k.id}'></td> 
                                            %else:
                                            	<td>${k.total}</td> 
                                            %endif
                                            	<td>${k.charge_code}</td>
                                            %if k.pi_no:
                                            	<td> PI </td> 
                                            %else:
                                            	<td> PO </td>
                                            %endif
                                        </tr>
                                    % endfor  
                                    </tbody>
                                </table>
               			 	</div>
               			 	% endif
               			 	</div>
               			 	% if len(curr_charge2) > 0:
               			 	<div class="gridInDiv"  style="margin-left:0">
               			 	   <div class="title other_charge_tab">Other Charge</div>
  								<div class="other_charge_content" style="display:none" id="${oHead.ref}_charge" >
  								  <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                       <tr>
               								%if oHead.status == const.VAT_THEAD_STATUS_NEW:
						                		<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'relation_other_charge_${oHead.id}')" value="0"></th>
						                    %endif
						                    <th>Supplier</th>
						                    <th>Note NO</th>
                                            <th>Line NO</th>
                                            <th>Note Type</th>
                                            <th>Status</th>
                                            <th>Chg Discount Code</th> 
                                            <th>Total</th>
                                            <th>Note Date</th> 
                                            <th>Remark</th>
                                        </tr>
                                    </thead>
                                    <tbody class="relation_other_charge_${oHead.id}">
                                    % for v,k in enumerate(curr_charge2):
                                        <tr>
                							%if oHead.status == const.VAT_THEAD_STATUS_NEW:
							                	<td class="head">
													<input type="checkbox" value="c" class="dboxClass" name="check_${k.id}">
							                	</td>
						                	%endif
						                	<td>${k.supplier}</td>
						                	<td>${k.note_no}</td>
                                            <td class="head">${k.line_no}</td>
                                            <td>${k.note_type}&nbsp;</td>
                                            <td>${k.status}&nbsp;</td>
                                            <td>${k.charge_code}</td>
                                            %if oHead.status == 'const.VAT_THEAD_STATUS_NEW':
                                            <td><input type="text" name="total_${k.id}" value="${k.total}"></td> 
                                            %else:
                                            	<td>${k.total}</td> 
                                            %endif
                                            <td>${k.note_date}</td>
                                            <td>${k.remark}&nbsp;</td> 
                                        </tr>
                                    % endfor  
                                    </tbody>
                                </table>
               			 	</div>
						</div>
						% endif
						</form>
					  </div>
					</td>
				</tr>
            </tbody>
        </table>
    </div>
</div>
<!-- other charges list end  -->
%if oHead.status!=const.VAT_THEAD_STATUS_CANCELLED:
<div class="clear"></div>
<div class="box3">
    <div class="title1"><div class="toggle2 toggle_right"></div>Sheet</div>
    <div class="box4" id="${oHead.ref}">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                    <th>CST No.</th>
                    <th>SO No.</th>
                    <th>SI No.</th>
                    <th>PO No.</th>
                    <th>PI No.</th>
                    <th>Supplier</th>
                    <th>Item</th>
                    <th>AR VAT Qty</th>
                    <th>Qty</th>
                    <th>Item Desc(Chinese)</th>
                    <th>Unit</th>
                    <th>Currency</th>
                    <th>Unit Price</th> 
                    <th>Total Amount</th>
                </tr>
            </thead>
            <tbody>
                % for si_infos in oHead.co_heads:
                % for detail in si_infos.co_details:
                <% 
                	relation_pi = detail.cp_details
                %>
            	% for j in relation_pi: 
                	<tr id="detail_${j.id}">
	                    <td class="head">${detail.co_head.o_head.ref}</td>
	                    <td>${detail.sales_contract_no}&nbsp;</td>
	                    <td>${si_infos.invoice_no}&nbsp;</td>
	                    <td>${j.po_no}&nbsp;</td>
	                    <td>${j.pi_no}&nbsp;</td>
	                    <td>${j.supplier_name}</td>
	                    <td>${detail.item_no}</td>
	                    <td>${detail.vat_qty}</td>
	                    %if j.pi_no:
	                    	<td class="quantity" id="qty_${j.id}">${j.pi_qty}</td>
	                    %else:
	                    	<td class="quantity" id="qty_${j.id}">${j.po_qty}</td>
	                    %endif
	                    <td id="desc_${detail.id}_detail"> ${j.description}&nbsp;</td>
	                    <td>${detail.unit}</td>
	                    <td>${detail.co_head.currency}</td>
	                    <td id='unit_price_${j.id}' class="unit_price_detail" >${j.unit_price}</td>
	                    %if j.pi_no:
	                    	<td class="total_amount">${j.pi_total}</td>
	                    %else:
	                    	<td class="total_amount">${pf(j.po_qty * j.unit_price)}</td>
	                    %endif
	                </tr>
	            %endfor
                % endfor
                % endfor
                <!--charge start-->
                % for j in curr_charge1:
                <tr id="charge">
                    <td class="head">${oHead.ref}</td>
                    <td>${j.so_no}&nbsp;</td>
                    <td>${j.si_no}&nbsp;</td>
                    <td>${b(j.po_no)|n}&nbsp;</td>
                    <td>${b(j.pi_no)|n}&nbsp;</td>
                    <td>${j.supplier_name}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="quantity">&nbsp;</td>
                    <td>${j.charge_code}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>${oHead.co_heads[0].currency}</td>
                    <td>&nbsp;</td>
                    % if j.pi_no:
                    	<td class="total_amount">${j.total}</td>
                    % else:
                    	<td class="total_amount">${j.po_total}</td>
                    % endif
                </tr>
                %endfor
                % for j in curr_charge2:
                <tr id="charge">
                    <td class="head">${oHead.ref}</td>
                    <td>${j.so_no}&nbsp;</td>
                    <td>${j.si_no}&nbsp;</td>
                    <td>${b(j.po_no)|n}&nbsp;</td>
                    <td>${b(j.pi_no)|n}&nbsp;</td>
                    <td>${j.supplier_name}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="quantity">&nbsp;</td>
                    <td>${j.charge_code}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>${oHead.co_heads[0].currency}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount">${j.total}</td>
                </tr>
                %endfor
                <!--charge end-->
                <!-- statistics start -->
	            <tr>
	                <td class="head">&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>Total</td>
	                <td class="quantity_all">&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
					<td class="total_amount_all">&nbsp;</td>
	            </tr>
                <!-- statistics end -->
            </tbody>
        </table>
    </div>
</div>
%endif
%endif
 
 