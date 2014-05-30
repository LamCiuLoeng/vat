<%
    from decimal import Decimal
    from vatsystem.util import const
    from vatsystem.util.mako_filter import b,pd,pt,pi,pf,pipo,get_sum_vat_total
%>
%if flag==1:
<script>
    showError("Error");
</script>
%else:
<script type="text/javascript">
	initPayment();
	$(document).ready(function() {
		initGetAll('#${nHead.ref}');
		//initDetail('${nHead.ref}');
		initToogle();
		initChangeVal();
		initStatement();
	});
</script>
<div class="box1">
    <div class="title1">
        <div class="toggle_down"></div>CCN Information </div>
    <div>
	<div class="toolbar">
         <input type="button" onclick="javascript:exportData('cost_${nHead.id}')" value="Export" class="btn">
    	<form action="/report/export_cst" method="post" id="form5_cost_${nHead.id}" style="display:none">
            <input type="hidden" name="id" value="${nHead.id}"/>
            <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_CCN}"/>
        </form>
    	<input type="button" class="btn" value="History" onclick="OpenDialog('/ar/view_history?type=N&id=${nHead.id}','#searchDialog','${nHead.ref} History')" href="javascript:void(0)" > 
    </div>
        <ul>
            <li class="li1">Customer Code:</li>
            <li class="li2">${b(nHead.customer_code)|n}</li>
            <li class="li1">Customer Name:</li>
            <li class="li2 fcn" style="float:left;width:400px;" >${nHead.customer_short_name}</li>
        </ul>
        %if len(nHead.c_heads)>0:
        <ul>
            <li class="li1">MCN Ref:</li>
            <% c_head = nHead.c_heads[0] %>
            <li class="li2">${c_head.ref }</li>
            <li class="li1">MCN VAT No:</li>
            <li class="li2">${c_head.vat_no}</li>
        </ul>
        %endif
        <ul>
            <li class="li1">Status:</li>
            <li class="li2">${nHead.status}</li>
            <li class="li1">Ref No:</li>
            <li class="li2">${nHead.ref}</li>
        </ul>
        %if nHead.vat_no or nHead.vat_date:
        <ul>
            <li class="li1">VAT No:</li>
            <li class="li2"  id='vat_no_${nHead.id}'>${nHead.vat_no}</li>
            <li class="li1">VAT Date:</li>
            <li class="li2">${pt(nHead.vat_date)}</li>
        </ul>
        %endif
        <ul>
            <li class="li1">Create Date:</li>
            <li class="li2">${pt(nHead.create_time)}</li>
            <li class="li1">Update Date:</li>
            <li class="li2">${pt(nHead.update_time)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>CCN</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl4">
                <tr>
                    <th class="head">SO NO</th>
                    <th>SI NO</th>
                    <th>Department</th>
                    <th>Currency</th>
                    <th class="cl5">Order Amount</th>
                    <th class="cl5">Item Amount</th>
                    <th>Order Amount</th>
                    <th>Item Amount</th>
                    <th>Create Time</th>
                </tr>
            </thead>
            <tbody>
            	<% charges = nHead.cp_charges %>
                % for si in nHead.co_heads:
                <tr class="so_head_${nHead.ref}" pre_detail=".so_detail_${si.id}" >
                    <td class="head"><a href="javascript:void(0)" onclick="toggleOne('tr2_'+${si.id})">${si.sales_contract_no}</a></td>
                    <td>${si.invoice_no}&nbsp;</td>
                    <td>${si.ae}&nbsp;</td>
                    <td>${si.currency}</td>
                    <td>${round(si.order_amt, 2)}</td>
                    <td>${round(si.item_amt, 2)}</td>
                    <td class='payment' cate='order_amount' id="order_amount_${si.sales_contract_no}" invoice='${si.sales_contract_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td class='payment' cate='item_amount' id="item_amount_${si.sales_contract_no}" invoice='${si.sales_contract_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td>${pd(si.create_time)|n}</td>
                </tr>
                <tr class="toggle none" id="tr2_${si.id}">
                    <td colspan="100" class="gridInTd">
                        <div class="gridInDiv">
                            <form action="/cost/update_nhead_details" method="post" id="_form_si${si.id}">
                                %if nHead.status == const.VAT_CHEAD_STATUS_NEW:
                                	<input type="hidden" onclick="ajaxForm('#_form_si${si.id}','Save Success!','${nHead.id}','${nHead.ref}',toSaveCheadDetails('si','${si.id}'),'ccn_save')"  class="btn"  value="Save" />
                                %endif
                                <input type="hidden" name="id" value="${nHead.id}"/>
                                <input type="hidden" name="head_type" value="${const.CHARGE_TYPE_S_PI}"/>
                                <div class="title">Detail</div>
                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl4">
                                        <tr>
                                       	<th>Line NO</th>
                                        <th>Item NO</th>
                                        <th>VAT Qty</th>
                                        <th>Description</th>
                                        <th>Item Amount(Without Tax)</th>
                                        <th>Item Amount</th>
                                        <th>Unit Price</th>
                                        <th>Tax(%)</th>
                                        <th>Unit</th>
                                        <th>Remark</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in si.find_details():
                                        % if j.ava_qty != 0:
	                                        <tr name="detail_${j.id}" class="so_detail_${si.id}">
	                                            <td>${j.line_no}</td>
	                                            <td>${j.item_no}</td>
	                                            <td class="head">${j.vat_qty}</td>
	                                            <td>${j.desc_zh if j.desc_zh else j.description}&nbsp;</td>
	                                            <td id="rmb_amount_p_${j.id}" >${round(j.vat_qty*j.unit_price,2)}</td>
	                                            <td id="rmb_amount_${j.id}">${round(j.vat_qty*j.unit_price*(1+j.tax_rate),2)}</td>
	                                      		<td>${j.unit_price}</td>
	                                            <td>${int(j.tax_rate*100)}</td>
	                                            <td>${j.unit}</td>
	                                            <td>
	                                            <input type="text" name="remark_${j.id}" value="${j.remark}" />
		                                        <input class="tax" type="hidden" name="tax_${j.id}" value="${float(j.tax_rate*100)}" tax_rate='${j.tax_rate}'  unit_price='${j.unit_price}' include_tax='${j.include_tax}' cate='detail' ids='${j.id}' />
		                                        <input type="hidden" name="item_amount_${j.id}" value="${round(j.vat_qty*j.unit_price,2)}" cate='item_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.sales_contract_no}" Head_id='${si.id}'/>
	                                            <input type="hidden" name="order_amount_${j.id}" value="${round(j.vat_qty*j.unit_price*(1+j.tax_rate),2)}" cate='order_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.sales_contract_no}" Head_id='${si.id}'/>
	                                            <input statement class="qty numeric" type="hidden" name="qty_${j.id}" value="${j.vat_qty}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}'  unit_price='${j.unit_price}' met='nHead'  include_tax='${j.include_tax}'/>
	                                            <input class="desc" type="hidden" name="desc_${j.id}" value="${j.desc_zh if j.desc_zh else j.description}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' met='nHead'   include_tax='${j.include_tax}' />
	                                            </td>
	                                        </tr>
		                                   <!--si list -->
	                                    <% 
	                                    relation_pi = j.cp_details
	                                    %>
										% if len(relation_pi)>0:
						                  <tr  style="display: table-row;">
						                    <td class="gridInTd" colspan="100">
						                        <div class="gridInDiv">
						                        <form action="/ar/update_other_charges_vat_total" method="POST" id="update_other_charges_vat_total_c" >
						                        		<input type="hidden" style="clear:none;margin-right:10px;" onclick="relatedPIPO('.relation_pi_${j.id}','1')" value="Save" class="btn">
						  								<input type="hidden" style="clear:none;margin-right:10px;" onclick="relatedPIPO('.relation_pi_${j.id}','2')" value="Add" class="btn">
						  								<input type="hidden" style="clear:none;margin-right:10px;" onclick="relatedPIPO('.relation_pi_${j.id}','3')" value="Delete" class="btn">
						  								<div class="title other_charge_tab" >Related PO/PI</div>
						  								<div class="other_charge_content" style="display:none" >
							                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
												            <thead class="cl4">
												                <tr>
												                	%if nHead.status == const.VAT_THEAD_STATUS_NEW:
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
												                    <th>Amount</th>
												                    <th>Description</th>
												                </tr>
												            </thead>
												            <tbody>
												                % for k, i in enumerate(relation_pi):
												     				<tr class="relation_pi_${j.id}">
													                	%if nHead.status == const.VAT_THEAD_STATUS_NEW:
														                	<td class="head">
																				<input type="checkbox" value="${i.id}" class="dboxClass" name="checkbox_${i.id}">
														                	</td>
													                	%endif
													                    <td class="head">${i.line_no}</td>
													                    <td>${i.po_no}</td>
													                   	<td>${i.pi_no}</td>
													                   	<td>${i.grn_no}&nbsp;</td>
													                   	<td>${i.grn_line_no}&nbsp;</td>
													                   	<td>${i.supplier}</td>
													                   	<td>${i.supplier_name}</td>
													                    <td>${i.item_no}</td>
													                    <td>${i.item_qty}</td>
													                    <td>${i.unit}</td>
													                    <td>${i.po_qty}</td>
													                    %if nHead.status == 'const.VAT_THEAD_STATUS_NEW':
													                    <td><input tax_rate='0.17' class="qty numeric" type="text" name="qty_${i.id}" value="${pi(float(i.pi_qty))}"/></td>
													                    %else:
													                    	 <td>${pi(float(i.pi_qty))}</td>
													                    %endif
													                    <td>${i.unit_price}</td>
													                    <td>${i.pi_total} &nbsp;</td>
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
                                        % endif
                                        % endfor
                                    </tbody>
                                </table>
                            </form>
                        </div>
                    </td>
                </tr>
                % endfor
                 <!-- other charges list start-->
                % if len(charges) > 0:
                	<tr id="${nHead.ref}_tr">
                % else:
                	<tr id="${nHead.ref}_tr" style="display:none">
                % endif
                    <td class="gridInTd" colspan="100" >
                        <div class="gridInDiv" >
                        <form action="/cost/update_to_othead" method="post" id="_form_charge${si.id}">
                        %if nHead.status == const.VAT_THEAD_STATUS_NEW:
	                        <input type="hidden" name="type" class="btn" value="Save" onclick="ajaxForm('#_form_charge${si.id}','Save Success!','${nHead.id}','${nHead.ref}',null,'ccn_save')" style="clear:none;margin-right:10px;">
							<input type="submit" name="type" class="btn" value="Delete" onclick="ajaxForm('#_form_charge${si.id}','Delete Success!','${nHead.id}','${nHead.ref}',null,'ccn_save')" style="clear:none;margin-right:10px;">
							<input type="hidden" value='${nHead.id}' name="id">
	                        <input type="hidden" value="${const.ERP_HEAD_TYPE_CCN}" name="head_type">
						%endif
                          	<div class="title other_charge_tab">Charge</div>
  							<div class="other_charge_content" style="display:none" id="${nHead.ref}_charge" >
  								% if len(charges) > 0: 
  								   <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl4">
                                       <tr>
                                       		%if nHead.status == const.VAT_THEAD_STATUS_NEW:
						                		<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'relation_charge_${nHead.id}')" value="0"></th>
						                    %endif
                                            <th>Line NO</th>
                                            <th>PO NO</th>
                                            <th>PO Total</th>
                                            <th>PI NO</th>
                                            <th>Total</th> 
                                            <th>Charge Code</th>
                                            <th>Type</th> 
                                        </tr>
                                    </thead>
                                    <tbody class="relation_charge_${nHead.id}">
                                    % for v, k in enumerate(charges):
                                          <tr>
                							%if nHead.status == const.VAT_THEAD_STATUS_NEW:
							                	<td class="head">
													<input type="checkbox" value="c" class="dboxClass" name="check_${k.id}">
							                	</td>
						                	%endif
                                            <td class="head">${v+1}</td>
                                            <td>${k.po_no}&nbsp;</td>
                                            <td>${k.po_total}&nbsp;</td>
                                            <td>${k.pi_no}&nbsp;</td>
                                            %if nHead.status == 'const.VAT_THEAD_STATUS_NEW':
                                            <td><input type="text" name="total_${k.id}" value="${k.total}"></td> 
                                            %else:
                                            	<td>${k.total}</td> 
                                            %endif
                                            <td>${k.charge_code}</td>
                                            <td> PI </td> 
                                        </tr>
                                    % endfor  
                                    </tbody>
                                </table>
               			 		% endif
           			 		</div>
						</div>
						</div>
						</form>
					</td>
				</tr>
            </tbody>
        </table>
    </div>
</div>
%if nHead.status!=const.VAT_CHEAD_STATUS_CANCELLED:
<div class="clear"></div>
<div class="box3">
    <div class="title1"><div class="toggle2 toggle_right"></div>Sheet</div>
    <div class="box4" id="${nHead.ref}">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class='cl4'>
                <tr>
                    <th>CCN No.</th>
                    <th>SO No.</th>
                    <th>SI NO.</th>
                    <th>PO NO.</th>
                    <th>PI NO.</th>
                    <th>Supplier</th>
                    <th>Item</th>
                    <th>AR VAT Qty</th>
                    <th>PI Qty</th>
                    <th>Item Desc(Chinese)</th>
                    <th>Unit</th>
                    <th>Currency</th>
                    <th>Unit Price</th> 
                    <th>Total Amount</th>
                </tr>
            </thead>
            <tbody>
                % for si_infos in nHead.co_heads:
                % for detail in si_infos.co_details:
                 	% for j in detail.cp_details: 
                	<tr id="detail_${j.id}">
	                    <td class="head">${detail.co_head.n_head.ref}</td>
	                    <td>${detail.sales_contract_no}&nbsp;</td>
	                    <td>${si_infos.invoice_no}&nbsp;</td>
	                    <td>${j.po_no}&nbsp;</td>
	                    <td>${j.pi_no}&nbsp;</td>
	                    <td>${j.supplier_name}</td>
	                    <td>${j.item_no}</td>
	                    <td>${detail.qty}</td>
	                    <td class="quantity" id="qty_${j.id}">${j.pi_qty}</td>
	                    <td id="desc_${detail.id}_detail"> ${j.id}, ${j.description}&nbsp;</td>
	                    <td>${detail.unit}</td>
	                    <td>${detail.co_head.currency}</td>
	                    <td id='unit_price_${j.id}' class="unit_price_detail" >${j.unit_price}</td>
	                    <td class="total_amount">${j.pi_total}</td>
	                </tr>
	            % endfor
                % endfor
                % endfor
                 <!--charge start-->
                % for k, j in enumerate(charges):
                <tr>
                    <td class="head">${nHead.ref}</td>
                    <td>${j.so_no}&nbsp;</td>
                    <td>${j.si_no}&nbsp;</td>
                    <td>${b(j.po_no)|n}&nbsp;</td>
                    <td>${b(j.pi_no)|n}&nbsp;</td>
                    <td>${j.supplier_name} &nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="quantity">&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>${j.charge_code}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>${nHead.co_heads[0].currency}&nbsp;</td>
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
	                <td>Total</td>
	                <td>&nbsp;</td>
	                <td class="quantity_all">&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td> 
					<td class="total_amount_all">&nbsp;</td>
	            </tr>
                <!-- statistics end   -->
            </tbody>
        </table>
    </div>
</div>
%endif
%endif
 