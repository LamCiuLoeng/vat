<%
    from decimal import Decimal
    from vatsystem.util import const
    from vatsystem.util.mako_filter import b,pd,pt,pi,pf,get_sum_vat_total
%>
%if flag==1:
<script>
    showError("Error");
</script>
%else:
<script type="text/javascript">
	initPayment();
	initStatement();
	$(document).ready(function(){
		initDetail('${cHead.ref}');
		initToogle();
		initSumQty();
		initChangeVal();
 		initGetAll('#${cHead.ref}');
})
</script>
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>MCN Information</div>
    <div>
    	<div class="toolbar">
    	    <form action="/report/export" method="post" id="form5_chead_so_${cHead.id}" style="display:none">
	            <input type="hidden" name="id" value="${cHead.id}"/>
	            <input type="hidden" name="head_type" value="cHead"/>
            </form>
            <input type="button" class="btn" Value="Export" onclick="exportData('chead_so_${cHead.id}')" />
        	<input type="button" class="btn" value="History" onclick="OpenDialog('/ar/view_history?type=C&id=${cHead.id}','#searchDialog','${cHead.ref} History')" href="javascript:void(0)" > 
        </div>
        <ul>
            <li class="li1">Customer Code:</li>
            <li class="li2">${cHead.customer_code}</li>
            <li class="li1">Customer Name:</li>
            <li class="li2 fcn" style="float:left;width:400px;">${cHead.customer_short_name}</li>
        </ul><ul>
            <li class="li1">Status:</li>
            <li class="li2">${cHead.status}</li>
            <li class="li1">Ref No:</li>
            <li class="li2">${cHead.ref}</li>
        </ul>
        %if cHead.vat_no or cHead.vat_date:
        <ul>
            <li class="li1">VAT No:</li>
            <li class="li2">${cHead.vat_no}</li>
            <li class="li1">VAT Date:</li>
            <li class="li2">${pt(cHead.vat_date)}</li>
        </ul>
        %endif
        <ul>
            <li class="li1">Create Date:</li>
            <li class="li2">${pt(cHead.create_time)}</li>
            <li class="li1">Export Date:</li>
            <li class="li2">${pt(cHead.export_time)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>SO</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl4">
                <tr>
                    <th class="head">So No</th>
                    <th>Department</th>
                    <th>Currency</th>
                    <th>AE</th>
                    <th>Cust Po No</th>
                    <th class="cl5">Order Amount</th>
                    <th class="cl5">Item Amount</th>
                    <th>Order Amount</th>
                    <th>Item Amount</th>
                    <th>Create Time</th>
                </tr>
            </thead>
            <tbody>
                % for so in cHead.so_heads:
                <tr class="so_head_${cHead.ref}" pre_detail=".so_detail_${so.id}">
                    <td class="head"><a href="javascript:void(0)" onclick="toggleOne('tr2_'+${so.id})">${so.sales_contract_no}</a></td>
                    <td>${so.order_dept}</td>
                    <td>${so.currency}</td>
                    <td>${so.ae}</td>
                    <td>${b(so.cust_po_no)|n}</td>
                    <td>${round(so.order_amt, 2)}</td>
                    <td>${round(so.item_amt, 2)}</td>
                    <td class='payment' cate='order_amount' id="order_amount_${so.sales_contract_no}" invoice='${so.sales_contract_no}' Head_id='${so.id}'> &nbsp;</td>
                    <td class='payment' cate='item_amount' id="item_amount_${so.sales_contract_no}" invoice='${so.sales_contract_no}' Head_id='${so.id}'> &nbsp;</td>
                    <td>${pd(so.create_date)}</td>
                </tr>
                <tr class="toggle none" id="tr2_${so.id}">
                    <td colspan="100" class="gridInTd">
                        <div class="gridInDiv">
                            <form action="/ar/update_chead_details" method="post" id="_form_so${so.id}">
                                %if cHead.status == const.VAT_CHEAD_STATUS_NEW:
                                	<input type="submit" class="btn" onclick="ajaxForm('#_form_so${so.id}','Save Success!','${cHead.id}','${cHead.ref}',toSaveCheadDetails('so','${so.id}'),'mcn')" value="Save" />
                                %endif
                                <input type="hidden" name="id" value="${so.id}"/>
                                <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SO}"/>
                                <div class="title">Detail</div>
                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl4">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Item NO</th>
                                            <th>Available Qty</th>
                                            <th class='cl3'>MSO Qty</th>
                                            <th>VAT Qty</th>
                                            <th>Description</th>
                                            <th>Item Amount(Without Tax)</th>
                                            <th>Item Amount</th>
                                            <th>Unit Price</th>
                                            <th>Unit</th>
                                            <th>Remark</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in so.find_details():
                                        % if j.qty != 0:
                                        <%
                                        if j.desc_zh:
                                        	zh = j.desc_zh
                                        else:
                                        	zh = j.description
                                        	
                                        relations_dic = {}
                                        relation_li = [li for li in j.invoice_qty.split(",") if len(li) > 0] if j.invoice_qty else []
                                        for di in relation_li: 
					                        dic = di.split(":") 
					                        if len(dic) > 0:relations_dic.update({dic[0]:dic[1]})
                                        %>
                                        % if j.available_qty != 0:
                                        <tr name="detail_${j.id}" class="so_detail_${so.id}">
                                        	<td>${j.line_no}</td>
                                        	<td>${j.item_no}</td>
                                        	%if cHead.status == const.VAT_CHEAD_STATUS_NEW:
                                            	<td class="head available_qty">${j.available_qty}</td>
                                            %else:
                                            	<td class="head available_qty">${j.ava_qty}</td>
                                            %endif
                                            <td>${j.qty}</td>
                                            %if cHead.status == const.VAT_CHEAD_STATUS_NEW:
                                            	<td><input statement class="qty numeric" type="text" name="qty_${j.id}" value="${j.vat_qty}" cate='detail' ids='${j.id}' /></td>
                                            	<td><input statement class="desc" type="text" name="desc_${j.id}" value="${zh}" cate='detail' ids='${j.id}' /></td>
                                            %else:
                                            <td class="head">${j.vat_qty}</td>
                                            <td>${zh}</td>
                                            %endif
                                            <td id="rmb_amount_p_${j.id}" >${round(j.vat_qty*j.unit_price,2)}</td>
                                            <td id="rmb_amount_${j.id}">${round(j.vat_qty*j.unit_price*Decimal("1.17"),2)}</td>
                                            <td>${j.unit_price}</td>
                                            <td>${j.unit}</td>
                                            <td>${j.remark}&nbsp;</td>
                                        	    <input  class="tax" type="hidden" name="tax_${j.id}" value="17" cate='detail' ids='${j.id}' />
                                        	    <input tax_rate='0.17' class="price" type="hidden" name="price_${j.id}" value="${j.unit_price}" cate='detail' ids='${j.id}' />
                                        	    <input  type="hidden" name="item_amount_${j.id}" value="${round(j.vat_qty*j.unit_price,2)}" cate='item_amount' ids='${j.id}'   unit_price='${j.unit_price}'   invoice="${so.sales_contract_no}" Head_id='${so.id}'/>
                                            	<input  type="hidden" name="order_amount_${j.id}" value="${round(j.vat_qty*j.unit_price*Decimal("1.17"),2)}" cate='order_amount' ids='${j.id}'   unit_price='${j.unit_price}'   invoice="${so.sales_contract_no}" Head_id='${so.id}'/>
                                        </tr>
                                        <!--si list -->
										% if len(collections)>0:
						                  <tr  style="display: table-row;">
						                    <td class="gridInTd" colspan="100">
						                        <div class="gridInDiv">
						                        <form action="/ar/update_other_charges_vat_total" method="POST" id="update_other_charges_vat_total_c" >
						  								<div class="title other_charge_tab" >Related SI</div>
						  								<div class="other_charge_content" style="display:none" >
							                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
												            <thead>
												                <tr>
												                    <th>Line NO</th>
												                    <th>Invoice NO</th>
												                    <th>Item NO</th>
												                    <th>Qty</th>
												                    <th >CN Qty</th>
												                    <th class="cl3">Available Qty</th>
												                    <th class="cl3" style="display:none">MSI Qty</th>
												                    <th class="cl4">MCN Qty</th>
												                    <th>Unit</th>
												                    <th>Unit Price</th>
												                    <th>Description</th>
												                </tr>
												            </thead>
												            <tbody>
												                % for i in collections:
												                <input type="hidden" name="invoice_no_${j.id}" value="${i.invoice_no}">
												                % if i.item_no == j.item_no:
												                <tr>
												                    <td class="head">${i.line_no}</td>
												                    <td>${i.invoice_no}</td>
												                    <td>${i.item_no}</td>
												                    <td>${pi(i.qty)}</td>
												                    <td>${pi(i.ri_qty)}</td>
												                    <td><!--${pi(i.available_qty)}--> ${pi(i.qty-i.ri_qty)}</td>
												                    <td style="display:none">${pi(i.msi_qty)}</td>
												                    <td><input  class="numeric" type="text" name="${i.invoice_no}_${i.line_no}_${j.id}" value="${relations_dic.get("%s_%s_%s" % (i.invoice_no,i.line_no,j.id),0)}" cate='detail' ids='${j.id}' redirct='qty_${j.id}' /></td>
												                    <td>${i.unit}</td>
												                    <td>${i.unit_price}</td>
												                    <td>${i.item_desc}</td>
												                </tr>
												                % endif
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
                                        % endif
                                        % endfor
                                    </tbody>
                                </table>
                                <% charges = so.find_charges() %>
                                % if len(charges) > 0:
                                <div class="title">Charge</div>
                                <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl4">
                                        <tr>
                                            <th>Line NO</th>
                                            <th class='cl3'>Total</th>
                                            <th>Available Total</th>
                                            <th>VAT Total</th>
                                            <th>Charge Code</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in charges:
                                        <tr name="charge_${j.id}">
                                            <td class="head">${j.line_no}</td>
                                            <td>${pf(j.total)}</td>
                                            <td class="available_qty">${pf(j.available_total)}</td>
                                            %if cHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <td><input class="qty numeric" type="text" name="total_${j.id}" value="${pf(j.vat_total)}" cate='charge' ids='${j.id}' /></td>
                                            %else:
                                            <td>${pf(j.vat_total)}</td>
                                            %endif
                                            <td>${j.charge_code}</td>
                                        </tr>
                                        % endfor
                                    </tbody>
                                </table>
                                % endif
                            </form>
                        </div>
                    </td>
                </tr>
                % endfor
               <!-- other charges list start-->
  			    % if len(other_charges_from_vat) > 0:
                  <tr   style="display: table-row;">
                    <td class="gridInTd" colspan="100">
                        <div class="gridInDiv">
                        <form action="/ar/update_other_charges_vat_total" method="POST" id="update_other_charges_vat_total_c1" >
                        		<input type="hidden" name="id" value="${cHead.id}" />
                        		<input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_CHEAD}" />
  								<div class="title other_charge_tab" >Other Charge</div>
  								<div class="other_charge_content" style="display:none" >
  								% if cHead.status == const.VAT_THEAD_STATUS_NEW:
  								 <input type="submit" class="btn"  id="save_other_charge" value="Save" style="float:left;margin-right:15px;clear:none;margin-left:15px;" name="save" onclick="ajaxForm('#update_other_charges_vat_total_c1','Save Success!','${cHead.id}','${cHead.ref}',toSaveSISOCharge('#update_other_charges_vat_total_c1'),'mcn')" > 
  								% endif
  								 <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl4">
                                       <tr>
                                            <th>Line NO</th>
                                            <th class="cl3">MSI Total</th>
                                            <th>Available Total</th>
                                            <th>VAT Total</th>
                                            <th>Chg Discount Code</th>
                                            <th>Type</th>
                                            <th>Note No</th>
                                            <th>Create Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                      % for k, other_charge in enumerate(other_charges_from_vat):
                                     <%
                                     available_total = other_charge.total
                                     available_total = available_total-get_sum_vat_total(other_charge.t_head_id, other_charge.line_no, other_charge.id)
                                     %>
                                       <tr name="other_charge_${other_charge.id}">
	                                        <td class="head">${k+1}</td>
	                                        %if not other_charge.vat_total:
	                                        <td>
	                                        %else:
	                                        <td id="no_check">
	                                        % endif
	                                        ${round(other_charge.total,2)}</td>
	                                        <td class="available_qty" >
	                                        ${pf(available_total)}
	                                        </td>
	                                        <td>&nbsp;
	                                        %if cHead.status == const.VAT_THEAD_STATUS_NEW:
	                                        <input type="text" value="${pf(other_charge.vat_total)}" name="vat_total_${other_charge.id}" class="qty numeric" cate='other_charge' ids='${other_charge.id}' > 
											%else:
									        ${pf(other_charge.vat_total)}
											% endif
											</td>
	                                        <td>${other_charge.charge_code}</td>
	                                        <td> 
	                                        <% 
	                                        if other_charge.type == "C_ERP":
	                                        	charge_type = "Customer" 
	                                        else:
	                                        	charge_type = "Manual"
	                                        %>
	                                        ${charge_type}
	                                        </td>
	                                        <td>${other_charge.note_no}&nbsp;</td>
	                                        <td>${pd(other_charge.create_time)}</td>
                                        </tr>
                                        % endfor  
                                    </tbody>
                                </table>
								</div>
								</div>
								</form>
				</td>
				</tr>
				% endif 
  				<!-- other charges list end  -->
            </tbody>
        </table>
    </div>
</div>
%if cHead.status!=const.VAT_CHEAD_STATUS_CANCELLED:
<div class="clear"></div>
<div class="box3">
    <div class="title1"><div class="toggle2 toggle_right"></div>Sheet</div>
    <div class="box4" id="${cHead.ref}" >
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class='cl4'>
                <tr>
                    <th>MSI/MSO No.</th>
                    <th>Invoice No.</th>
                    <th>Customer PO No.</th>
                    <th>SO Sales Contact</th>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Item Desc(Chinese)</th>
                    <th>Unit</th>
                    <th>Currency</th>
                    <th>Unit Price</th>
                    <th>Freight</th>
                    <th>Total Amount</th>
                    <th>Unit Price(without tax)</th>
                    <th>Total Amount(without tax)</th>
                    <th>Tax</th>
                    <th>Total Amount(total amount + feight + tax)</th>
                </tr>
            </thead>
            <tbody>
                % for so_infos in cHead.so_heads:
                % for detail in so_infos.so_details:
                % if detail.vat_qty != 0:
                <tr  id="detail_${detail.id}">
                % else:
                <tr style="display:none" id="detail_${detail.id}">
                % endif
                    <td class="head">${detail.so_head.c_head.ref}</td>
                    <td>&nbsp;</td>
                    <td>${b(detail.so_head.cust_po_no)|n}</td>
                    <td>${detail.so_head.sales_contract_no}</td>
                    <td>${detail.item_no}</td>
                    <td class="quantity" id="qty_${detail.id}_detail">${detail.vat_qty}</td>
                    <td id="desc_${detail.id}_detail">
                    <%
                    if detail.desc_zh:
                    	zh = detail.desc_zh
                    else:
                    	zh = detail.description
                    %>
                    ${zh}&nbsp;</td>
                    <td>${detail.unit}</td>
                    <td>${detail.so_head.currency}</td>
                    <td id='unit_price_${detail.id}_detail'>${detail.unit_price* Decimal("1.17")}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount" id="total_amount_${detail.id}_detail">${round(detail.vat_qty * detail.unit_price* Decimal("1.17"), 2)}</td>
                    <td id='unit_price_tax_${detail.id}_detail'>${detail.unit_price}</td>
                    <td class="total_amount_without_tax" id="total_amount_without_tax_${detail.id}_detail">${round(detail.vat_qty * detail.unit_price, 2)}</td>
                    <td class="tax" id="tax_${detail.id}_detail">${round(detail.vat_qty * detail.unit_price  * Decimal("0.17"), 2)}</td>
                    <td class="total_amount_total_amount" id="total_amount_total_amount_${detail.id}_detail">${round(detail.vat_qty * detail.unit_price   + detail.vat_qty * detail.unit_price  * Decimal("0.17"), 2)}</td>
                </tr>
                % endfor
                % endfor
                <!-- charge list -->
 				% for u,si_infos in enumerate(cHead.so_heads):
                % for k,detail in enumerate(so_infos.so_details):
                % if k == 0:
                % for so in cHead.so_heads:
       			<% charges = so.find_charges() %>
       			% for j in charges:
       			% if detail.t_head_id == j.t_head_id:
       			% if j.vat_total !=0: 
                <tr id="charge_${j.id}">
                % else:
                <tr style="display:none" id="charge_${j.id}">
                % endif
                    <td class="head">${detail.so_head.c_head.ref}</td>
                    <td>${j.invoice_no}&nbsp;</td>
                    <td>${b(detail.so_head.cust_po_no)|n}</td>
                    <td>${detail.so_head.sales_contract_no}</td>
                    <td>&nbsp;</td>
                    <td  class="quantity" >&nbsp;</td>
                    <td>${j.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${detail.so_head.currency}</td>
                    <td>&nbsp;</td>
                    <td  class="freights" >&nbsp;</td>
                    <td class="total_amount"  id="total_amount_${j.id}_charge">${pf(j.vat_total*Decimal('1.17'))}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax"  id="total_amount_without_tax_${j.id}_charge">${pf(j.vat_total)}</td>
                    <td class="tax"  id="tax_${j.id}_charge">${pf(j.vat_total*Decimal('0.17'))}</td>
                    <td class="total_amount_total_amount"  id="total_amount_total_amount_${j.id}_charge">${pf(j.vat_total*Decimal('1.17'))}</td>
                </tr>
                % endif
                % endfor
                % endfor
               
                % endif
                % endfor
                % endfor
                <!-- charge list end -->
                <!-- other charge list start -->
                % for u,si_infos in enumerate(cHead.so_heads):
 				% if u == 0:
                % for k,detail in enumerate(so_infos.so_details):
                % if k == 0:
                % for k, other_charge in enumerate(other_charges_from_vat):
                % if other_charge.vat_total != 0:
                    <tr id='other_charge_${other_charge.id}'>
                    % else:
                    <tr style="display:none" id='other_charge_${other_charge.id}'>
                % endif
                	<% 
                    if other_charge.vat_total == None:
                    	vat_total = other_charge.total
                    else:
                    	vat_total = other_charge.vat_total
                    %>
                    <td class="head">${detail.so_head.c_head.ref}</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="quantity"  >&nbsp;</td>
                    <td>${other_charge.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${detail.so_head.currency}</td>
                    <td>&nbsp;</td>
                    <td  class="freights" >&nbsp;</td>
					<td  class="total_amount" id="total_amount_${other_charge.id}_other_charge">${pf(vat_total*Decimal('1.17'))}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax" id="total_amount_without_tax_${other_charge.id}_other_charge">${pf(vat_total)}</td>
                    <td class="tax" id="tax_${other_charge.id}_other_charge">${pf(vat_total*Decimal('0.17'))}</td>
                    <td class="total_amount_total_amount" id="total_amount_total_amount_${other_charge.id}_other_charge">${pf(vat_total*Decimal('1.17'))}</td>
                </tr>
                % endfor 
                % endif
                % endfor
                % endif
                % endfor
                <!-- other charge list end   -->
                <!-- statistics start -->
	            <tr>
	                <td class="head">&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>Total</td>
	                <td class="quantity_all">&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td class="freights_all">&nbsp;</td>
					<td class="total_amount_all">&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax_all">&nbsp;</td>
                    <td class="tax_all" >&nbsp;</td>
                    <td class="total_amount_total_amount_all" >&nbsp;</td>
	            </tr>
                <!-- statistics end   -->
            </tbody>
        </table>
    </div>
</div>
%endif
%endif