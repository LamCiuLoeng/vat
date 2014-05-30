<%
    from decimal import Decimal
    from vatsystem.model import RID,RICharge
    from vatsystem.util import const
    from vatsystem.util.mako_filter import b,pd,pi,pf,pt,pq,get_last_line_no,get_the_cn_detail,get_si_detail_total,get_cn_total
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
	initGetAll('#${tHead.ref}');
	$("#charge_code").autocomplete(data);
	$(document).ready(function() {
		$("#${tHead.ref}_erp").fancybox({ 
			'width'				: '80%',
			'height'			: '80%',
			'autoScale'			: false,
			'transitionIn'		: 'none',
			'transitionOut'		: 'none',
			'type'				: 'iframe',
			onClosed	        :  function() {viewThead('${tHead.id}','${tHead.ref}')}
			
		})
		% if len(other_charges_from_vat) > 0:
			%for other_charge in other_charges_from_vat:
				openIframe('#pending_${other_charge.id}', '${tHead.id}', '${tHead.ref}')
			%endfor
		% endif 
		$("#${tHead.ref}_si").fancybox({ 
			'width'				: '80%',
			'height'			: '80%',
			'autoScale'			: false,
			'transitionIn'		: 'none',
			'transitionOut'		: 'none',
			'type'				: 'iframe',
			onClosed	        :  function() {viewThead('${tHead.id}','${tHead.ref}')}
		})

	});
</script>
<style type="text/css">
<!--
.iframe{border: 1px solid #336633; padding: 4px; background-color:#ffeedd;color:#336633;font-weight:bold;margin:0}
-->
</style>
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>MSI Information</div>
    <div>
        <div class="toolbar">
            %if tHead.status == const.VAT_THEAD_STATUS_POST:
            <input type="button" class="btn" Value="Create MCN" onclick="javascript:openNewMcnForm2('${tHead.id}','${tHead.vat_no}')" />
                                <!--start show frame-->
                                <div class="none" id="vatDialog5_${tHead.id}">
                                <form action="/ar/save_to_chead" method="post" id="form25_${tHead.id}">
                                    <div class="box6">
                                        <ul>
                                            <li class="li1">VAT No Range </li>
                                            <li class="li2"><input type="text" name="vat_no" id="vat_no25_${tHead.id}" /></li>
                                            <li class="li4">(e.g. 00000001~00000010,00000099)</li>
                                        </ul>
                                        <div class="clear"></div>
                                    </div>
                                    <div class="box7">
                                    	<input type="hidden" id="vat_no25" value="${tHead.vat_no}">
                                        <input type="hidden" value=${tHead.id}  name="id">
                                        <div style="display:none"><input type="text"/></div>
                                        <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form25_'+${tHead.id},'Save Success!','${tHead.id}','${tHead.ref}',saveNewMcnForm2('${tHead.id}', '${tHead.vat_no}', '${tHead.ref}'),'si_so_save')" />
                                        <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
                                    </div>
                                </form>
                                </div>
            					<!-- end show frame-->
            %endif
            <form action="/report/export" method="post" id="form5_thead_si_${tHead.id}" style="display:none">
            <input type="hidden" name="id" value="${tHead.id}"/>
            <input type="hidden" name="head_type" value="tHead"/>
            </form>
            <input type="button" class="btn" Value="Export" onclick="javascript:exportData('thead_si_${tHead.id}')" />
             %if tHead.status == const.VAT_THEAD_STATUS_NEW:
             <input type="button" class="btn iframe" value="Add Other Charges From ERP" href="/ar/search_charge_erp?tHead_id=${tHead.id}&customer_code=${tHead.customer_code}" id="${tHead.ref}_erp" />
             <input type="button" class="btn" Value="Add Other Manual Charges" onclick="javascript:Add_Other_Charges_From_Manual('${tHead.id}')" />
        	 <input type="button" value="Add Other SI From ERP" class="btn" href="/ar/add_si_so_erp?type=1&tHead_id=${tHead.id}&customer_code=${tHead.customer_code}&viewPager=1" id="${tHead.ref}_si" >
        	% endif
        	 <input type="button" class="btn" value="History" onclick="OpenDialog('/ar/view_history?type=T&id=${tHead.id}','#searchDialog','${tHead.ref} History')" href="javascript:void(0)" > 
        	<!--save a new charge-->
             <div class="none" id="Add_Other_Charges_From_Manual_${tHead.id}">
             <form action="/ar/add_other_charges_from_manual" method="POST" id="form15_${tHead.id}"  >
             <div class="box6">
           	<ul style="display:none">
   				<li class="li1">Line No</li>
   				<li class="li2"><input type="hidden"  name="line_no" value="${get_last_line_no(tHead.id)}" /></li>
			</ul>
			<ul>
   				<li class="li1">Charge Code</li>
   				<li class="li2"><input type="text" name="charge_code" id="charge_code" /></li>
			</ul>
			<ul>
   				<li class="li1">Total</li>
   				<li class="li2"><input type="text" name="total" id="total"  /></li>
   				<li class="li4" style="text-align:left">(e.g. 2000)</li>
			</ul>
			<ul>
   				<li class="li1">SI No</li>
   				<li class="li2">
   								<select name="invoice_no" id="invoice_np" style="width:149px;">
   									<option  value=""></option>
   									 % for si in tHead.si_heads:
   										<option value="${si.invoice_no}">${si.invoice_no}</option>
   									 % endfor
   								</select>
   				</li>
			</ul>
			<ul>
   				<li class="li1">Pending</li>
   				<li class="li2" style="float:left"><input type="checkbox" name='pending'></li>
			</ul>
			    <input type="hidden" name="t_head_id" value=${tHead.id} /> 
             <div class="clear"></div>
             </div>
            <div class="box7">
                     <input type="hidden" name="active" value="0"/>
                     <input type="hidden" name="company_code" value="RPACSZ"/>
                     <input type="hidden" name="type" value="T_Manual"/>
                     <input type="hidden" name="vat_total" value="" />
                     <input type="submit" class="btn" value="Submit" id="form15_btn_${tHead.id}"  onclick="ajaxForm('#form15_${tHead.id}','Success!','${tHead.id}','${tHead.ref}',checkNull('#form15_${tHead.id}'),'si_so_save')"/>
                     <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
           </div>
           </form>
            </div>
            <!-- end show frame-->
        </div>
        <ul>
            <li class="li1">Customer Code:</li>
            <li class="li2">${tHead.customer_code}</li>
            <li class="li1">Customer Name:</li>
            <li class="li2 fcn" style="float:left;width:400px;" >${tHead.customer_short_name}</li>
        </ul><ul>
            <li class="li1">Status:</li>
            <li class="li2">${tHead.status}</li>
            <li class="li1">Ref No:</li>
            <li class="li2">${tHead.ref}</li>
        </ul>
        %if tHead.vat_no or tHead.vat_date:
        <ul>
            <li class="li1">VAT No:</li>
            <li class="li2">${tHead.vat_no}</li>
            <li class="li1">VAT Date:</li>
            <li class="li2">${pt(tHead.vat_date)}</li>
        </ul>
        %endif
        <ul>
            <li class="li1">Express No:</li>
            <li class="li2">${tHead.express_no}</li>
            <li class="li1">Express Date:</li>
            <li class="li2">${tHead.express_date}</li>
        </ul>
        <ul>
            <li class="li1">Create Date:</li>
            <li class="li2">${pt(tHead.create_time)}</li>
            <li class="li1">Export Date:</li>
            <li class="li2">${pt(tHead.export_time)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>
%if len(tHead.c_heads) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MCN</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class='cl4'>
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
                % for i in tHead.c_heads:
                <tr>
                    <td class="head"><a href="javascript:viewChead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
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
    <div class="title1"><div class="toggle_down"></div>SI</div>
    <div class="box4" id="check_ava_$${tHead.id}">	
     %if tHead.status == const.VAT_THEAD_STATUS_NEW:
    	<p><input type="button" class="btn"  value="Delete" onclick="deleteItem('/ar/ajax_delete_item','${tHead.ref}_item_list','SI','${tHead.id}','${tHead.ref}')" />
    </p><br />
    %endif
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                	%if tHead.status == const.VAT_THEAD_STATUS_NEW:
                	<th  class="head"><input type="checkbox" onclick="selectAllDetail(this,'${tHead.ref}_item_list')" value="0"></th>
                    %endif
                    <th class="head">Invoice NO</th>
                    <th>Sales Contract No</th>
                    <th>Department</th>
                    <th>SO Sales Contact</th>
                    <th>Currency</th>
                    <th  class="cl5">Order Amount</th>
                    <th  class="cl5">Item Amount</th>
                    <th>Order Amount</th>
                    <th>Item Amount</th>
                    <th>Charge Amount</th>
                    <th>Create Time</th>
                </tr>
            </thead>
            <tbody class="${tHead.ref}_item_list">
                % for si in tHead.si_heads:
                <tr>
                	%if tHead.status == const.VAT_THEAD_STATUS_NEW:
                	<td class="head"><input type="checkbox"   value="${si.id}" class="dboxClass"></td>
                    % endif
                    <td>
                    <a href="javascript:void(0)" onclick="toggleOne('tr2_'+${si.id})">${si.invoice_no}</a></td>
                    <td>${si.sc_no}</td>
                    <td>${si.department}</td>
                    <td>${si.so_sales_contact}</td>
                    <td>${si.currency}</td>
                    <td>${round(si.order_amt,2)}</td>
                    <td>${round(si.item_amt,2)}</td>
                    <td class='payment' cate='order_amount' id="order_amount_${si.invoice_no}" invoice='${si.invoice_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td class='payment' cate='item_amount' id="item_amount_${si.invoice_no}" invoice='${si.invoice_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td class='payment' cate='charge' id="charge_${si.invoice_no}" invoice='${si.invoice_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td>${pd(si.create_date)}</td>
                </tr>
                <tr class="toggle none" id="tr2_${si.id}">
                    <td colspan="100" class="gridInTd">
                        <div class="gridInDiv">
                            <form action="/ar/update_thead_details" method="post" id="_form_si${si.id}">
                                %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                <input type="submit" class="btn"  value="Save" onclick="ajaxForm('#_form_si${si.id}','Save Success!','${tHead.id}','${tHead.ref}',toSaveSISODetails('si','${si.id}'),'si_so_save')" />
                                %endif
                                <input type="hidden" name="id" value="${si.id}"/>
                                <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SI}"/>
                                <div class="title">Detail</div>
                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Item NO</th>
                                            <th>Qty</th>
                                            <th>CN Qty</th>
                                            <th>Available Qty</th>
                                            <th class="cl4">MCN(MSO) Qty</th>
                                            <th class="cl4">MCN Qty</th>
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
                                        % for j in si.find_details():
                                        <%
                                        if j.desc_zh:
                                        	zh = j.desc_zh
                                        else:
                                        	zh = j.item_desc
                                        %>
                                        <tr name="detail_${j.id}" >
                                            <td class="head">${j.line_no}</td>
                                            <td>${j.item_no}</td>
                                            <td>${j.qty}</td>
                                            <td>${pi(j.cn_qty)} </td>
                                            <td class="available_qty">${pi(j.available_qty)}</td>
                                            <td>${j.msc_qty}</td>
                                            <td>${j.mcn_qty}</td>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            	<td><input statement  tax_rate='0.17' class="qty numeric" type="text" name="qty_${j.id}" value="${j.vat_qty}" cate='detail' ids='${j.id}' /></td>
                                            	<td><input statement  tax_rate='0.17' class="price" type="text" name="price_${j.id}" value="${j.unit_price}" cate='detail' ids='${j.id}' /></td>
                                            	<td><input class="desc" tax_rate='0.17' type="text" name="desc_${j.id}" value="${zh}" cate='detail' ids='${j.id}' /></td>
                                            %else:
                                            	<td>${j.vat_qty}</td>
                                            	<td>${j.unit_price}</td>
                                            	<td>${zh}</td>
                                            %endif
                                            <td id="rmb_amount_p_${j.id}">${round(j.vat_qty*j.unit_price,2)}</td>
	                                       	<td id="rmb_amount_${j.id}">${round(j.vat_qty*j.unit_price*Decimal("1.17"),2)}</td>
                                            <td>${j.unit}</td>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <td><input type="text"  name="remark_${j.id}" value="${j.remark}"></td>
                                            %else:
                                            <td>${j.remark}&nbsp;</td>
                                            %endif
                                        </tr>
                                        	  <input class="tax" type="hidden" name="tax_${j.id}" value="17" cate='detail' ids='${j.id}' />
                                       		 <input  tax_rate='0.17' type="hidden" name="item_amount_${j.id}" value="${round(j.vat_qty*j.unit_price,2)}" cate='item_amount' ids='${j.id}'  unit_price='${j.unit_price}'  invoice="${si.invoice_no}" Head_id='${si.id}'/>
											 <input  tax_rate='0.17' type="hidden" name="order_amount_${j.id}" value="${round(j.vat_qty*j.unit_price*Decimal("1.17"),2)}" cate='order_amount' ids='${j.id}'  unit_price='${j.unit_price}' invoice="${si.invoice_no}" Head_id='${si.id}'/>
                                        % endfor
                                    </tbody>
                                </table>
                                <!--this is the other charges list -->
                                <% charges = si.find_charges() %>
                                % if len(charges) > 0:
                                <div class="title">Charge</div>
                                <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Total</th>
                                            <th>CN Total</th>
                                            <th>Available Total</th>
                                            <th class="cl4">MCN Total</th>
                                            <th>VAT Total</th>
                                            <th>Charge Code</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in charges:
                                        <tr name="charge_${j.id}">
                                            <td class="head">${j.line_no}</td>
                                            <td>${pf(j.total)}</td>
                                            <td>${get_cn_total(j.invoice_no,j.charge_code)}</td>
                                            <td class="available_qty">${pf(j.available_total)}</td>
                                            <td>${pf(j.mcn_total)}</td>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            	<td><input class="qty numeric" type="text" name="total_${j.id}" value="${pf(j.vat_total)}"  cate='charge' ids='${j.id}' /></td>
                                            %else:
                                            	<td>${pf(j.vat_total)}</td>
                                            %endif
                                            <td>${j.charge_code}</td>
                                            <input type="hidden" name="charge_${j.id}" value="${pf(j.vat_total)}" cate='charge' ids='${j.id}' invoice="${si.invoice_no}" Head_id='${si.id}'/>
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
                	<tr id="${tHead.ref}_tr">
                % else:
                	<tr id="${tHead.ref}_tr" style="display:none">
                % endif
                    <td class="gridInTd" colspan="100" >
                        <div class="gridInDiv">
                        <form action="/ar/update_other_charges_vat_total" method="POST" id="${tHead.ref}_update_other_charges_vat_total_si">
                        		<input type="hidden" value="${tHead.id}" name="id" />
                        		<input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_THEAD}" />
                          		<div class="title other_charge_tab">Other Charge</div>
  								<div class="other_charge_content" style="display:none" id="${tHead.ref}_charge" >
  								% if len(other_charges_from_vat) > 0:
  								% if tHead.status == const.VAT_THEAD_STATUS_NEW:
  								    <input type="submit" class="btn"  id="save_other_charge" value="Save" style="float:left;margin-right:15px;clear:none;margin-left:15px;" name="save" onclick="ajaxForm('#${tHead.ref}_update_other_charges_vat_total_si','Save Success!','${tHead.id}','${tHead.ref}',toSaveSISOCharge('#${tHead.ref}_update_other_charges_vat_total_si'),'si_so_save')"> 
                        			<input type="submit" class="btn" value="Delete" style="clear:none;margin-left:15px;" name="delete" onclick="ajaxForm('#${tHead.ref}_update_other_charges_vat_total_si','Delete Success!','${tHead.id}','${tHead.ref}',checkSelect('#${tHead.ref}_update_other_charges_vat_total_si'),'si_so_save')" >
  								% endif
  								  <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                       <tr>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <th width="20px" class="head"><input type="checkbox" onclick="selectAll(this)" id="selectAlls"></th>
                                            %endif
                                            <th>Line NO</th>
                                            <th>Pending</th>
                                            <th class="cl3">Total</th>
                                            <th>Vat Total</th>
                                            <th>Chg Discount Code</th>
                                            <th>Type</th>
                                            <th>Note No</th>
                                            <th>Create Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                    % for k, other_charge in enumerate(other_charges_from_vat):
                                        <tr name="other_charge_${other_charge.id}">
                                        	%if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <td width="20px" class="head"><input type="checkbox"  value="${other_charge.id}" class="cboxClass"  name="checkbox_${other_charge.id}"></td>
                                            %endif
                                            <td class="head">${k+1}</td>
                                            %if other_charge.pending:
                                            	<td><input type="checkbox" name="pending_${other_charge.id}" checked='checked' disabled="disabled" ></td>
                                            %else:
                                            	<td><input type="checkbox" name="pending_${other_charge.id}" disabled="disabled" ></td>
                                            %endif
                                            %if not other_charge.vat_total:
                                            <td class='available_qty' >
                                            %else:
                                             <td id="no_check">
                                            % endif
                                            	${round(other_charge.total,2)}
                                            </td>
                                            <td>&nbsp;
											<% 
                                            if other_charge.vat_total == None:
                                            	vat_total = round(other_charge.total,2)
                                            else:
                                            	vat_total = round(other_charge.vat_total,2)
                                            %>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            	<input type="text" value="${vat_total}" name="vat_total_${other_charge.id}" class="qty numeric check_numbers" cate='other_charge' ids='${other_charge.id}' > 
											% else:
												${vat_total}
											% endif
											</td>
                                            <td>
                                            ${other_charge.charge_code}</td>
                                            <td> 
                                            <% 
                                            if other_charge.type == "T_ERP":
                                            	charge_type = "Customer" 
                                            else:
                                            	charge_type = "Manual"
                                            %>
                                            ${charge_type}
                                            </td>
                                            %if other_charge.note_no:
                                            	<td>${other_charge.note_no} &nbsp;</td>
                                            %else:
                                            	%if other_charge.pending:
                                            		<td><input type="button" value="Add"  class="btn iframe" id="pending_${other_charge.id}"  href="/ar/search_charge_erp?tHead_id=${tHead.id}&customer_code=${tHead.customer_code}&id=${other_charge.id}"/> &nbsp;</td>
                                            	%else:
                                            		<td>&nbsp;</td>
                                            	%endif
                                            %endif
                                            <td>${pd(other_charge.create_time)}</td>
                                        </tr>
                                    % endfor  
                                    </tbody>
                                </table>
               			 		% endif
               			 		</div>
								</div>
				</td>
				</tr>
			
            </tbody>
        </table>
        </form>
    </div>
</div>
<!-- other charges list end  -->
%if tHead.status!=const.VAT_THEAD_STATUS_CANCELLED:
<div class="clear"></div>
<div class="box3">
    <div class="title1"><div class="toggle2 toggle_right"></div>Sheet</div>
    <div class="box4" id="${tHead.ref}">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
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
                % for si_infos in tHead.si_heads:
                % for detail in si_infos.si_details:
                % if detail.vat_qty != 0:
                <tr  id="detail_${detail.id}">
                % else:
                <tr style="display:none" id="detail_${detail.id}">
                % endif
                    <td class="head">${detail.si_head.t_head.ref}</td>
                    <td>${detail.invoice_no}</td>
                    <td>${b(detail.si_head.cust_po_no)|n}</td>
                    <td>${detail.si_head.sc_no}</td>
                    <td>${detail.item_no}</td>
                    <td class="quantity" id="qty_${detail.id}_detail">${detail.vat_qty}</td>
                    <td id="desc_${detail.id}_detail">
                    <%
                    if detail.desc_zh:
                    	zh = detail.desc_zh
                    else:
                    	zh = detail.item_desc
                    %>
                    ${zh}&nbsp;</td>
                    <td>${detail.unit}</td>
                    <td>${detail.si_head.currency}</td>
                    <td id='unit_price_${detail.id}_detail' class="unit_price_detail" >${detail.unit_price* Decimal("1.17")}</td>
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
                % for u, si_infos in enumerate(tHead.si_heads):
       			<% charges = si_infos.find_charges() %>
       			% for j in charges:
       			% if j.type=='T_SI':
       			% if j.vat_total !=0: 
                <tr id="charge_${j.id}">
                % else:
                <tr style="display:none" id="charge_${j.id}">
                % endif
                    <td class="head">${j.t_head.ref}</td>
                    <td>${j.invoice_no}</td>
                    <td>${b(j.cust_po_no)|n}</td>
                    <td>${j.sales_contract_no}</td>
                    <td>&nbsp;</td>
                    <td class="quantity">&nbsp;</td>
                    <td>${j.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${j.currency}</td>
                    <td>&nbsp;</td>
                    <td  class="freights">&nbsp;</td>
                    <td class="total_amount" id="total_amount_${j.id}_charge">${pf(j.vat_total*Decimal('1.17'))}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax" id="total_amount_without_tax_${j.id}_charge">${pf(j.vat_total)}</td>
                    <td class="tax"   id="tax_${j.id}_charge">${pf(j.vat_total*Decimal('0.17'))}</td>
                    <td class="total_amount_total_amount"  id="total_amount_total_amount_${j.id}_charge">${pf(j.vat_total*Decimal('1.17'))}</td>
                </tr>
                % endif
                % endfor
                % endfor
                <!-- charge list end -->
                <!-- other charge list start -->
                % for u,si_infos in enumerate(tHead.si_heads):
 				% if u == 0:
                % for k,detail in enumerate(si_infos.si_details):
                % if k == 0:
                % for c, other_charge in enumerate(other_charges_from_vat):
                % if other_charge.vat_total != 0:
                <tr id='other_charge_${other_charge.id}'>
                % else:
                <tr style="display:none" id='other_charge_${other_charge.id}'>
                % endif
                	<% 
                    if other_charge.vat_total==None:
                    	vat_total = other_charge.total
                    else:
                    	vat_total = other_charge.vat_total
                    %>
                    <td class="head">${detail.si_head.t_head.ref}</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="quantity" >&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>${detail.si_head.currency}</td>
                    <td>&nbsp;</td>
                    <td class="freights">&nbsp;</td>
					<td  class="total_amount" id="total_amount_${other_charge.id}_other_charge">${round(vat_total*Decimal('1.17'), 2)}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax" id="total_amount_without_tax_${other_charge.id}_other_charge">${round(vat_total, 2)}</td>
                    <td class="tax"  id="tax_${other_charge.id}_other_charge">${round(vat_total*Decimal('0.17'), 2)}</td>
                    <td class="total_amount_total_amount"  id="total_amount_total_amount_${other_charge.id}_other_charge">${round(vat_total*Decimal('1.17'), 2)}</td>
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
 
 
 
 
 