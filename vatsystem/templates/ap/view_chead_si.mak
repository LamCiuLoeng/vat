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
	$(document).ready(function() {
		initGetAll('#${sHead.ref}');
		//initDetail('${sHead.ref}');
		initToogle();
		initChangeVal();
		initStatement();
	});
</script>
<div class="box1">
    <div class="title1">
        <div class="toggle_down"></div>MSN Information
    </div>
    <div>
    	<div class="toolbar">
    		<input type="button" onclick="javascript:exportData('shead_pi_${sHead.id}')" value="Export" class="btn">
			<form action="/report/export" method="post" id="form5_shead_pi_${sHead.id}" style="display:none">
	            <input type="hidden" name="id" value="${sHead.id}"/>
	            <input type="hidden" name="head_type" value="sHead"/>
            </form>
            
        	<input type="button" class="btn" value="History" onclick="OpenDialog('/ar/view_history?type=S&id=${sHead.id}','#searchDialog','${sHead.ref} History')" href="javascript:void(0)" > 
        	%if sHead.status == const.VAT_THEAD_STATUS_POST:
        	<!-- end show frame-->
            <input type="hidden" onclick="javascript:openNewMfForm('${sHead.id}','${const.CHARGE_TYPE_S_PI}')" value="Create MF" class="btn">
	            <!--start show frame-->
	            <div class="none" id="vatDialog26_${sHead.id}">
	            <form action="/ap/save_to_mf" method="post" id="form26_d_${sHead.id}">
	                <div class="box6">
	                    <ul>
	                        <li class="li1">VAT No Range </li>
	                        <li class="li2"><input type="text" name="vat_no" id="vat_no26_d_${sHead.id}" /></li>
	                        <li class="li4">(e.g. 00000001~00000010,00000099)</li>
	                    </ul>
	                    <div class="clear"></div>
	                </div>
	                <div class="box7">
	                	<input type="hidden" id="vat_no26" value="${sHead.vat_no}">
	                    <input type="hidden" value=${sHead.id}  name="id">
	                    <div style="display:none"><input type="text"/></div>
	                    <input type="hidden" value="s_head_id"  name="type">
	                    <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form26_d_${sHead.id}','Save Success!','${sHead.id}','${sHead.ref}',saveNewMfForm2('d_${sHead.id}', '${sHead.vat_no}'),'saveMSN')" />
	                    <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
	                </div>
	            </form>
	            </div>
				<!-- end show frame-->
				%endif
        </div>
        <ul>
            <li class="li1">Supplier Code:</li>
            <li class="li2">${sHead.supplier}</li>
            <li class="li1">Supplier Name:</li>
            <li class="li2 fcn" style="float:left;width:400px;" >${sHead.supplier_short_name}</li>
        </ul><ul>
            <li class="li1">Status:</li>
            <li class="li2">${sHead.status}</li>
            <li class="li1">Ref No:</li>
            <li class="li2">${sHead.ref}</li>
        </ul>
        %if sHead.vat_no or sHead.vat_date:
        <ul>
            <li class="li1">VAT No:</li>
            <li class="li2"  id='vat_no_${sHead.id}'>${sHead.vat_no}</li>
            <li class="li1">VAT Date:</li>
            <li class="li2">${pt(sHead.vat_date)}</li>
        </ul>
        %endif
        <ul>
            <li class="li1">Create Date:</li>
            <li class="li2">${pt(sHead.create_time)}</li>
            <li class="li1">Update Date:</li>
            <li class="li2">${pt(sHead.update_time)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>
%if len(sHead.m_heads) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MF</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class='cl3'>
                <tr>
                    <th class="head">Ref</th>
                    <th>VAT No</th>
                    <th>Status</th>
                    <th>VAT Date</th>
                    <th>Export Date</th>
                    <th>Create Date</th>
                </tr>
            </thead>
            <tbody>
                % for i in sHead.m_heads:
                <tr>
                    <td class="head"><a href="javascript:viewMhead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
                    <td>${b(i.vat_no)|n}</td>
                    <td>${b(i.status)|n}</td>
                    <td>${pd(i.vat_date)|n}</td>
                    <td>${pd(i.export_time)|n}</td>
                    <td>${pd(i.create_time)|n}</td>
                </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>
%endif
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>PI</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl4">
                <tr>
                    <th class="head">Invoice NO</th>
                    <th>Note NO</th>
                    <th>PO NO</th>
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
                % for si in sHead.pi_heads:
                <tr class="so_head_${sHead.ref}" pre_detail=".so_detail_${si.id}" >
                    <td class="head"><a href="javascript:void(0)" onclick="toggleOne('tr2_'+${si.id})">${si.invoice_no}</a></td>
                    <td>${si.note_no}</td>
                    <td>${si.po_no}</td>
                    <td>${si.department}</td>
                    <td>${si.currency}</td>
                    <td>${round(si.order_amt,2)}</td>
                    <td>${round(si.item_amt,2)}</td>
                    <td class='payment' cate='order_amount' id="order_amount_${si.invoice_no}" invoice='${si.invoice_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td class='payment' cate='item_amount' id="item_amount_${si.invoice_no}" invoice='${si.invoice_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td>${pd(si.create_time)|n}</td>
                </tr>
                <tr class="toggle none" id="tr2_${si.id}">
                    <td colspan="100" class="gridInTd">
                        <div class="gridInDiv">
                            <form action="/ap/update_shead_details" method="post" id="_form_si${si.id}">
                                %if sHead.status == const.VAT_CHEAD_STATUS_NEW:
                                <input type="submit" onclick="ajaxForm('#_form_si${si.id}','Save Success!','${sHead.id}','${sHead.ref}',toSaveCheadDetails('si','${si.id}'),'msn')"  class="btn"  value="Save" />
                                %endif
                                <input type="hidden" name="id" value="${si.id}"/>
                                <input type="hidden" name="head_type" value="${const.CHARGE_TYPE_S_PI}"/>
                                <div class="title">Detail</div>
                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl4">
                                        <tr>
                                           	<th>Line NO</th>
                                            <th>Item NO</th>
                                            <th>Available Qty</th>
                                            <th class='cl3'>MPI Qty</th>
                                            <th>VAT Qty</th>
                                            <th>Description</th>
                                            <th>Item Amount</th>
                                            <th style='display:none'>Item Amount</th>
                                            <th>Unit Price</th>
                                            <th>Tax(%)</th>
                                            <th>Unit</th>
                                            <th>Remark</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in si.find_details():
                                        <%
                                        if j.desc_zh:
                                        	zh = j.desc_zh
                                        else:
                                        	zh = j.item_desc
                                        %>
                                        <tr name="detail_${j.id}" class="so_detail_${si.id}">
                                            <td>${j.line_no}</td>
                                            <td>${j.item_no}</td>
                                            <td class="head available_qty"> ${j.ava_qty}</td>
                                            <td>${j.qty}</td>
                                            %if sHead.status == const.VAT_CHEAD_STATUS_NEW:
                                            <td><input statement class="qty numeric" type="text" name="qty_${j.id}" value="${j.vat_qty}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}'  unit_price='${j.unit_price}' met='shead'  include_tax='${j.include_tax}'/></td>
                                            <td><input class="desc" type="text" name="desc_${j.id}" value="${zh}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' met='shead'   include_tax='${j.include_tax}' /></td>
                                            %else:
                                            <td class="head">${j.vat_qty}</td>
                                            <td>${zh}</td>
                                            %endif
                                            <td id="rmb_amount_p_${j.id}" >${round(j.vat_qty*j.unit_price,2)}</td>
                                            <td  style='display:none' id="rmb_amount_${j.id}">${round(j.vat_qty*j.unit_price*(1+j.tax_rate),2)}</td>
                                            <td>${j.unit_price}</td>
                                            <td>${int(j.tax_rate*100)}</td>
                                            <td>${j.unit}</td>
                                            <td>${j.remark}&nbsp;
                                            <input  type="hidden" name="remark_${j.id}" value="${j.remark}" />
                                           	<td><input class="price" type="hidden" name="price_${j.id}" value="${j.unit_price}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}'/></td>
	                                        <td><input class="tax" type="hidden" name="tax_${j.id}" value="${float(j.tax_rate*100)}" tax_rate='${j.tax_rate}'  unit_price='${j.unit_price}' include_tax='${j.include_tax}' cate='detail' ids='${j.id}' /></td>
	                                        <input  type="hidden" name="item_amount_${j.id}" value="${round(j.vat_qty*j.unit_price,2)}" cate='item_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.invoice_no}" Head_id='${si.id}'/>
                                            <input  type="hidden" name="order_amount_${j.id}" value="${round(j.vat_qty*j.unit_price*(1+j.tax_rate),2)}" cate='order_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.invoice_no}" Head_id='${si.id}'/>
                                            </td>
                                        </tr>
                                        % endfor
                                    </tbody>
                                </table>
                                <% charges = si.find_charges() %>
                                % if len(charges) > 0:
                                <div class="title">Charge</div>
                                <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl4">
                                        <tr>
                                            <th>Line NO</th>
                                            <th class='cl3'>MPI Total</th>
                                            <th>Available Total</th>
                                            <th>VAT Total</th>
                                            <th>Charge Code</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in charges:
                                        % if j.ava_total != 0:
                                        <tr name="charge_${j.id}">
                                            <td class="head">${j.line_no}</td>
                                            <td>${pf(j.total)}</td>
                                            <td class="available_qty">${pf(j.ava_total)}</td>
                                            %if sHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <td><input class="qty numeric" type="text" name="total_${j.id}" value="${pf(j.vat_total)}" cate='charge' ids='${j.id}'  forid="total_${j.id}_charge_1"/></td>
                                            %else:
                                            <td>${pf(j.vat_total)}</td>
                                            %endif
                                            <td>${j.charge_code}
                                               <input type="hidden"  value="${pf(j.vat_total)}" cate='order_amount' invoice="${si.invoice_no}" Head_id='${si.id}'/>
                                            </td>
                                        </tr>
                                        % endif
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
  			    % if len(Other_Charges_From_vats) > 0:
                  <tr style="display: table-row;">
                    <td class="gridInTd" colspan="100">
                        <div class="gridInDiv">
                        <form action="/ap/update_other_charges_vat_total" method="POST" id="update_other_charges_vat_total_c" >
  								<div class="title other_charge_tab">Other Charge</div>
  								<div class="other_charge_content" style="display:none" >
  								% if sHead.status == const.VAT_THEAD_STATUS_NEW:
  								 <input type="submit" class="btn"  id="save_other_charge" value="Save" style="float:left;margin-right:15px;clear:none;margin-left:15px;" name="save" onclick="ajaxForm('#update_other_charges_vat_total_c','Save Success!','${sHead.id}','${sHead.ref}',toSaveSISOCharge('#update_other_charges_vat_total_c'),'msn')" > 
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
                                      % for v,k in enumerate(Other_Charges_From_vats):
                                         <tr name="other_charge_${k.p_head_id}">
                                            <td class="head">${v+1}</td>
                                            <td>${k.total}</td>
                                            <td class="available_qty" >${k.ava_total}</td>
                                            <td>&nbsp;
                                            %if sHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <input type="text" value="${pf(k.vat_total)}" name="${k.id}" class="qty numeric" cate='other_charge' ids='${k.id}' forid='${k.id}_other_charge_1' > 
											%else:
									        ${pf(k.vat_total)}
											% endif
											</td>
                                            <td>${k.charge_code}</td>
                                            <td> 
                                            <% 
                                            if k.type=="${const.CHARGE_TYPE_S_ERP}":
                                            	other_charge_type = "Supplier" 
                                            else:
                                            	other_charge_type = "Manual"
                                            %>
                                            ${other_charge_type}
                                            </td>
                                            <td>${k.note_no} &nbsp;</td>
                                            <td>${pd(k.create_time)}</td>
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
%if sHead.status!=const.VAT_CHEAD_STATUS_CANCELLED:
<div class="clear"></div>
<div class="box3">
    <div class="title1"><div class="toggle2 toggle_right"></div>Sheet</div>
    <div class="box4" id="${sHead.ref}">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class='cl4'>
                <tr>
                	<th>MSI/MSO No.</th>
                    <th>Note No.</th>
                    <th>Invoice No.</th>
                    <th>Supplier PO No.</th>
                    <th>PO NO</th>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Item Desc(Chinese)</th>
                    <th>Unit</th>
                    <th>Currency</th>
                    <th style='display:none'>Unit Price</th>
                    <th>Freight</th>
                    <th>Unit Price(without tax)</th>
                    <th>Total Amount(without tax)</th>
                    <th style='display:none'>Total Amount(without tax)</th>
                    <th style='display:none'>Tax</th>
                    <th>Total Amount</th>
                </tr>
            </thead>
            <tbody>
                % for si_infos in sHead.pi_heads:
                % for detail in si_infos.pi_details:
                % if detail.vat_qty != 0:
                <tr  id="detail_${detail.id}">
                % else:
                <tr style="display:none" id="detail_${detail.id}">
                % endif
                	<td class="head">${detail.pi_head.s_head.ref}</td>
                    <td class="head">${detail.pi_head.note_no}</td>
                    <td>${detail.invoice_no}</td>
                    <td>${b(detail.pi_head.po_no)|n}</td>
                    <td>${detail.pi_head.po_no}</td>
                    <td>${detail.item_no}</td>
                    <td class="quantity" id="qty_${detail.id}_detail">${detail.vat_qty}</td>
                    <td id="desc_${detail.id}_detail">
                    <%
                    tax_rate          = 1 + detail.tax_rate
                    tax_rate_out_self = detail.tax_rate 
                    if detail.include_tax == 0:
                    	unit_price        = round(detail.unit_price,6)
                    	total_amount      = round(detail.vat_qty * unit_price, 2)
                    	unit_price_tax    = round(detail.unit_price/tax_rate,6)
                    	total_amount_without_tax  = round(detail.vat_qty * unit_price_tax, 2)
                    else:
                    	unit_price        = round(detail.unit_price*tax_rate,6)
                    	total_amount      = round(detail.vat_qty * detail.unit_price*tax_rate, 2)
                    	unit_price_tax    = round(detail.unit_price,6)
                    	total_amount_without_tax = round(detail.vat_qty * detail.unit_price, 2)
                    if detail.desc_zh:
                    	zh = detail.desc_zh
                    else:
                    	zh = detail.item_desc
                    %>
                    ${zh}&nbsp;
                    </td>
                    <td>${detail.unit}</td>
                    <td>${detail.pi_head.currency}</td>
                    <td  style='display:none' id='unit_price_${detail.id}_detail'>${unit_price}</td>
                    <td>&nbsp;</td>
                    <td id='unit_price_tax_${detail.id}_detail'>${unit_price_tax}</td>
                    <td class="total_amount" id="total_amount_${detail.id}_detail">${total_amount}</td>
                    <td  style='display:none' class="total_amount_without_tax" id="total_amount_without_tax_${detail.id}_detail">${total_amount_without_tax}</td>
                    <td  style='display:none' class="tax" id="tax_${detail.id}_detail">${round(total_amount - total_amount_without_tax , 2)}</td>
                    <td class="total_amount_total_amount" id="total_amount_total_amount_${detail.id}_detail">${total_amount_without_tax}</td>
                </tr>
                % endfor
                % endfor
                 <!-- charge list -->
 				% for u,si_infos in enumerate(sHead.pi_heads):
                % for k,detail in enumerate(si_infos.pi_details):
                % if k == 0:
                % for si in sHead.pi_heads:
       			<% charges = si.find_charges() %>
       			% for j in charges:
       			% if detail.pi_head_id == j.pi_head_id:
       			% if j.vat_total != 0: 
                <tr id="charge_${j.id}">
                % else:
                <tr style="display:none" id="charge_${j.id}">
                % endif
                	<td class="head">${detail.pi_head.s_head.ref}</td>
                    <td class="head">${detail.pi_head.note_no} </td>
                    <td>${detail.invoice_no}</td>
                    <td>${b(detail.pi_head.po_no)|n}</td>
                    <td>${detail.pi_head.po_no}</td>
                    <td>&nbsp;</td>
                    <td  class="quantity" >&nbsp;</td>
                    <td>${j.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${detail.pi_head.currency}</td>
                    <td  style='display:none'>&nbsp;</td>
                    <td class="freights" id="total_${j.id}_charge_1">${pf(j.vat_total)}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount">&nbsp;</td>
                    <td style='display:none' class="total_amount_without_tax">&nbsp;</td>
                    <td style='display:none' class="tax" >&nbsp;</td>
                    <td class="total_amount_total_amount" id="total_${j.id}_charge">${pf(j.vat_total)}</td>
                </tr>
                % endif
                % endfor
                % endfor
                % endif
                % endfor
                % endfor
                <!-- charge list end -->
                <!-- other charge list start -->
                % for c,v in enumerate(Other_Charges_From_vats):
                % if v.vat_total != 0:
                <tr id='other_charge_${v.id}'>
                % else:
                <tr style="display:none" id='other_charge_${v.id}'>
                % endif
                	<td class="head">${sHead.ref}</td>
                    <td>${v.note_no}</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="quantity" >&nbsp;</td>
                    <td>${v.charge_code}</td>
                     <td>&nbsp;</td>
                    <td>${v.currency}</td>
                    <td  style='display:none'>&nbsp;</td>
                    <td  class="freights" id='${v.id}_other_charge_1'>${v.vat_total}</td>
                    <td>&nbsp;</td>
					<td  class="total_amount">&nbsp;</td>
                    <td  style='display:none' class="total_amount_without_tax" >&nbsp;</td>
                    <td  style='display:none' class="tax" >&nbsp;</td>
                    <td class="total_amount_total_amount" id='${v.id}_other_charge'>${v.vat_total}</td>
                </tr>
                % endfor 

                <!-- other charge list end   -->
                <!-- statistics start -->
	            <tr>
	                <td class="head">&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>Total</td>
	                <td class="quantity_all">&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td style='display:none'>&nbsp;</td>
	                <td class="freights_all">&nbsp;</td>
	                <td>&nbsp;</td>
					<td class="total_amount_all">&nbsp;</td>
                    <td  style='display:none' class="total_amount_without_tax_all">&nbsp;</td>
                    <td  style='display:none' class="tax_all" >&nbsp;</td>
                    <td class="total_amount_total_amount_all" >&nbsp;</td>
	            </tr>
                <!-- statistics end   -->
            </tbody>
        </table>
    </div>
</div>
%endif
%endif
 