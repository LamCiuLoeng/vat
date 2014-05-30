<%
    from decimal import Decimal
    from vatsystem.util import const
    from vatsystem.util.mako_filter import b,pd,pt,pi,pf,get_last_line_no
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
	initPayment();
	initStatement();
	intiParsePrice();
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
		$("#${tHead.ref}_so").fancybox({ 
			'width'				: '80%',
			'height'			: '80%',
			'autoScale'			: false,
			'transitionIn'		: 'none',
			'transitionOut'		: 'none',
			'type'				: 'iframe',
			onClosed	        :  function() {viewThead('${tHead.id}','${tHead.ref}')}
		})
			$("#${tHead.ref}_si").fancybox({ 
				'width'				: '80%',
				'height'			: '80%',
				'autoScale'			: false,
				'transitionIn'		: 'none',
				'transitionOut'		: 'none',
				'type'				: 'iframe',
				 onStart            : function(){
										var sum_qty = 0;
										var sum_si_qty = 0;
										$(".qty").each(function(){
											%if tHead.status == const.VAT_THEAD_STATUS_NEW:
												sum_qty += Number($(this).val());
											%else:
												sum_qty += Number($(this).html());
											%endif
										
										})
										$(".si_qty").each(function(){
											sum_si_qty += Number($(this).html());
										})
										if(sum_qty == sum_si_qty){
											 showError("Over the MSO VAT Qty!");
											 return false;
										}
										if(sum_qty < sum_si_qty){
											showError("The related SI sum Qty more than the MSO VAT Qty,please check and modifly it!");
											return false;
										}
				},
				onClosed	        :  function() {viewThead('${tHead.id}','${tHead.ref}')}
			})
		
	});
</script>
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>MSO Information</div>
    <div>
       <!--head bottom start-->
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
                                    <div style="display:none"><input type="text" /></div>
                                    	<input type="hidden" id="vat_no25" value="${tHead.vat_no}">
                                        <input type="hidden" value=${tHead.id}  name="id">
                                        <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form25_'+${tHead.id},'Save Success!','${tHead.id}','${tHead.ref}',saveNewMcnForm2('${tHead.id}', '${tHead.vat_no}', '${tHead.ref}'),'si_so_save')"/>
                                        <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
                                    </div>
                                </form>
                                </div>
            <!-- end show frame-->
            %endif
            <form action="/report/export" method="post" id="form5_thead_so_${tHead.id}" style="display:none" >
            <input type="hidden" name="id" value="${tHead.id}"/>
            <input type="hidden" name="head_type" value="tHead"/>
            </form>
            <input type="button" class="btn" Value="Export" onclick="exportData('thead_so_${tHead.id}')" />
            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
             	<input type="button" class="btn iframe" value="Add Other Charges From ERP" href="/ar/search_charge_erp?tHead_id=${tHead.id}&customer_code=${tHead.customer_code}" id="${tHead.ref}_erp" />
             	<input type="button" class="btn" Value="Add Other Manual Charges" onclick="javascript:Add_Other_Charges_From_Manual('${tHead.id}')" />
             	<input type="button" value="Add Other SO From ERP" class="btn" href="/ar/add_si_so_erp?type=2&tHead_id=${tHead.id}&customer_code=${tHead.customer_code}&viewPager=1" id="${tHead.ref}_so" >
            % endif 
            <input type="button" value="Add Related SI From ERP" class="btn" href="/ar/add_related_si_erp?type=2&tHead_id=${tHead.id}&customer_code=${tHead.customer_code}&viewPager=1" id="${tHead.ref}_si" >
            <input type="button" class="btn" value="History" onclick="OpenDialog('/ar/view_history?type=T&id=${tHead.id}','#searchDialog','${tHead.ref} History')" href="javascript:void(0)" > 
        	<!--save a new charge-->
             <div class="none" id="Add_Other_Charges_From_Manual_${tHead.id}">
             <form action="/ar/add_other_charges_from_manual" method="post" id="form15_${tHead.id}">
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
   				<li class="li2"><input type="text" name="total" id="total" /></li>
   				<li class="li4" style="text-align:left">(e.g. 2000)</li>
			</ul>
			<ul>
   				<li class="li1">So No</li>
   				<li class="li2">
   								<select name="sales_contract_no" id="sales_contract_no" style="width:149px;">
   									<option  value=""></option>
   									 % for so in tHead.so_heads:
   										<option value="${so.sales_contract_no}">${so.sales_contract_no}</option>
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
                     <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form15_${tHead.id}','Success!','${tHead.id}','${tHead.ref}',checkNull('#form15_${tHead.id}'),'si_so_save')" />
                     <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
           </div>
           </form>
            </div>
            <!-- end show frame-->
        </div>
        <!---head bottom end -->
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
            <thead class="cl4">
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
    <div class="title1"><div class="toggle_down"></div>MSO Invoices</div>
    <div class="box4" id="check_ava_${tHead.id}">
	    %if tHead.status == const.VAT_THEAD_STATUS_NEW:
	    	<p><input type="button" class="btn"  value="Delete" onclick="deleteItem('/ar/ajax_delete_item','${tHead.ref}_item_list','SO','${tHead.id}', '${tHead.ref}')" />
	    	</p><br />
	    %endif
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
            	%if tHead.status == const.VAT_THEAD_STATUS_NEW:
                	<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'${tHead.ref}_item_list')" value="0"></th>
                %endif
                    <th class="head">So No</th>
                    <th>Department</th>
                    <th>Currency</th>
                    <th>AE</th>
                    <th>Cust Po No</th>
                    <th class="cl5">Order Amount</th>
                    <th class="cl5">Item Amount</th>
                    <th>Available  Amount</th>
                    <th>Order Amount(Without Tax)</th>
                    <th>Order Amount</th>
                    <th>Item Amount</th>
                    <th>Charge Amount</th>
                    <th>Create Time</th>
                </tr>
            </thead>
            <tbody class="${tHead.ref}_item_list">
                % for so in tHead.so_heads:
                <tr>
            	%if tHead.status == const.VAT_THEAD_STATUS_NEW:
                	<td class="head"><input type="checkbox"   value="${so.id}" class="dboxClass"></td>
                %endif
                    <td><a href="javascript:void(0)" onclick="toggleOne('tr2_'+${so.id})">${so.sales_contract_no}</a></td>
                    <td>${so.order_dept}</td>
                    <td>${so.currency}</td>
                    <td>${so.ae}</td>
                    <td>${b(so.cust_po_no)|n}</td>
                    <td>${round(so.order_amt,2)}</td>
                    <td>${round(so.item_amt,2)}</td>
                    <% so_amounts = so.available_amount()%>
                    <td>${so_amounts[1]}</td>
                    <td cate='order_amount_without_tax' id="order_amount_without_tax_${so.sales_contract_no}" invoice='${so.sales_contract_no}' Head_id='${so.id}' >${so_amounts[0]}</td>
                    <td class='payment' cate='order_amount' id="order_amount_${so.sales_contract_no}" invoice='${so.sales_contract_no}' Head_id='${so.id}'> &nbsp;</td>
                    <td class='payment' cate='item_amount' id="item_amount_${so.sales_contract_no}" invoice='${so.sales_contract_no}' Head_id='${so.id}'> &nbsp;</td>
                    <td class='payment' cate='charge' id="charge_${so.sales_contract_no}" invoice='${so.sales_contract_no}' Head_id='${so.id}' tHead_id='${tHead.id}'> &nbsp;</td>
                    <td>${pd(so.create_date)}</td>
                </tr>
                <tr class="toggle none" id="tr2_${so.id}">
                    <td colspan="100" class="gridInTd">
                        <div class="gridInDiv">
                            <form action="/ar/update_thead_details" method="post" id="_form_so${so.id}">
                                %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                <input type="submit" class="btn" onclick="ajaxForm('#_form_so${so.id}','Save Success!','${tHead.id}','${tHead.ref}',toSaveSISODetails('so','${so.id}'),'si_so_save')"  value="Save" />
                                %endif
                                <input type="hidden" name="id" value="${so.id}"/>
                                <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SO}"/>
                                <div class="title">Detail</div>
                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Item NO</th>
                                            <th>Qty</th>
                                            <th>Invoiced Qty</th>
                                            <th>Available Qty</th>
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
                                        % for j in so.find_details():
                                        <%
                                        if j.desc_zh:
                                        	zh = j.desc_zh
                                        else:
                                        	zh = j.description
                                        %>
                                        <tr name="detail_${j.id}" >
                                            <td class="head">${j.line_no}</td>
                                            <td>${j.item_no}</td>
                                            <td>${j.qty}</td>
                                            <td>${j.invoiced_qty}</td>
                                            <td class="available_qty">
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            	${pi(j.available_qty)}
                                            %else:
                                            	${pi(j.ava_qty)}
                                            %endif
                                            </td>
                                            <td>${j.mcn_qty}</td>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            	<td><input statement tax_rate='0.17' class="qty numeric" type="text" name="qty_${j.id}" value="${j.vat_qty}" cate='detail' ids='${j.id}' /></td>
                                            	<td><input statement tax_rate='0.17' class="price" type="text" name="price_${j.id}" value="${j.unit_price}" cate='detail' ids='${j.id}' /></td>
                                            	<td><input class="desc" tax_rate='0.17' type="text" name="desc_${j.id}" value="${zh}" cate='detail' ids='${j.id}'/></td>
                                            %else:
                                            	<td class="qty head">${j.vat_qty}</td>
                                            	<td>${j.unit_price}</td>
                                            	<td>${zh}
                                            </td>
                                            %endif
                                            <td id="rmb_amount_p_${j.id}">${round(j.vat_qty*j.unit_price,2)}</td>
	                                       	<td id="rmb_amount_${j.id}">${round(j.vat_qty*j.unit_price*Decimal("1.17"),2)}</td>
                                            <td>${j.unit}</td>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            	<td><input type="text" name="remark_${j.id}" value="${j.remark}"></td>
                                            %else:
                                            	<td>${j.remark}&nbsp;</td>
                                            %endif
                                        </tr>
                                        	<input class="tax" type="hidden" name="tax_${j.id}" value="17"  cate='detail' ids='${j.id}' />
                                        	<input type="hidden" tax_rate='0.17' name="item_amount_${j.id}" value="${round(j.vat_qty*j.unit_price,2)}" cate='item_amount' ids='${j.id}'  unit_price='${j.unit_price}'  invoice="${so.sales_contract_no}" Head_id='${so.id}'/>
											<input type="hidden" tax_rate='0.17' name="order_amount_${j.id}" value="${round(j.vat_qty*j.unit_price*Decimal("1.17"),2)}" cate='order_amount' ids='${j.id}'  unit_price='${j.unit_price}' invoice="${so.sales_contract_no}" Head_id='${so.id}'/>
                                        % endfor
                                    </tbody>
                                </table>
                                <% charges = so.find_charges() %>
                                % if len(charges) > 0:
                                <div class="title">Charge</div>
                                <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Total</th>
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
                                            <td class="available_qty">${pf(j.available_total)}</td>
                                            <td>${pf(j.mcn_total)}</td>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <td><input class="qty numeric"  type="text" name="total_${j.id}" value="${pf(j.vat_total)}" cate='charge' ids='${j.id}' /></td>
                                            %else:
                                            <td>${pf(j.vat_total)}</td>
                                            %endif
                                            <td>${j.charge_code}</td>
                                        </tr>
                                        <input type="hidden" name="charge_${j.id}" value="${pf(j.vat_total)}" cate='charge' ids='${j.id}' invoice="${so.sales_contract_no}" Head_id='${so.id}'/>
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
                <tr  id="${tHead.ref}_tr" style="display: table-row;">
                    <td class="gridInTd" colspan="100">
                        <div class="gridInDiv">
                        		<form action="/ar/update_other_charges_vat_total" method="POST" id="${tHead.ref}_update_other_charges_vat_total_so">
                        		<input type="hidden" name="id" value="${tHead.id}" />
                        		<input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_THEAD}" />
                          		<div class="title other_charge_tab">Other Charge</div>
  								<div class="other_charge_content" style="display:none" id="${tHead.ref}_charge" >
  								%if tHead.status == const.VAT_THEAD_STATUS_NEW:
  								    <input type="submit" class="btn"  id="save_other_charge" value="Save" style="float:left;margin-right:15px;clear:none;margin-left:15px;" name="save" onclick="ajaxForm('#${tHead.ref}_update_other_charges_vat_total_so','Save Success!','${tHead.id}','${tHead.ref}',toSaveSISOCharge('#${tHead.ref}_update_other_charges_vat_total_so'),'si_so_save')" > 
                        		    <input type="submit" class="btn" value="Delete" style="clear:none;margin-left:15px;" name="delete" onclick="ajaxForm('#${tHead.ref}_update_other_charges_vat_total_so','Delete Success!','${tHead.id}','${tHead.ref}',checkSelect('#${tHead.ref}_update_other_charges_vat_total_so'),'si_so_save')" >
                        		% endif
  								  <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                       <tr>
                                       %if tHead.status == const.VAT_THEAD_STATUS_NEW:     
                                       <th width="20px" class="head"><input type="checkbox" onclick="selectAll(this)" id="selectAlls"></th>
                                       %endif
                                            <th>Line NO</th>
                                            <th>Pending</th>
                                            <th>So NO</th>
                                            <th class="cl3">Total</th>
                                            <th>Vat Total</th>
                                            <th>Chg Discount Count</th>
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
                                            <td>&nbsp;${other_charge.sales_contract_no}</td>
                                            <td class='Total'>${other_charge.total}</td>
                                            <td>&nbsp;
											<% 
                                            if other_charge.vat_total == None:
                                            	vat_total = round(other_charge.total,2)
                                            else:
                                            	vat_total = round(other_charge.vat_total,2)
                                            %>
                                            %if tHead.status == const.VAT_THEAD_STATUS_NEW:
                                            	<input type="text" value="${vat_total}" name="vat_total_${other_charge.id}" thead_id="${tHead.id}" invoice="${other_charge.sales_contract_no}" class="qty numeric check_numbers" cate='other_charge' ids='${other_charge.id}' > 
											% else:
												<span cate='other_charge' thead_id="${tHead.id}" invoice="${other_charge.sales_contract_no}">${vat_total}</span>
											% endif
											</td>
                                            <td>${other_charge.charge_code}</td>
                                            <td> 
                                            <% 
                                            if other_charge.type =="T_ERP":
                                            	other_charge_type = "Customer" 
                                            else:
                                            	other_charge_type = "Manual"
                                            %>
                                            ${other_charge_type}
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
                               </div>
                           </form>
					</div>
				</td>
				   </tr>
				  % endif 
  				<!-- other charges list end  -->
            </tbody>
        </table>
    </div>
</div>
<!--si list -->
% if len(si_list)>0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>Related SI</div>
    <div class="box4" id="check_ava_${tHead.id}_si">
	    	<p><input type="button" class="btn"  value="Delete" onclick="relationSI('.${tHead.ref}_dboxClass','${tHead.id}','delete','${tHead.ref}')" />
	    	</p><br />
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                	<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'${tHead.ref}_item_list_si')" value="0"></th>
                    <th class="head">Invoice NO</th>
                    <th>Qty</th>
                    <th>CN Qty</th>
                    <th class="cl3">Available Qty</th>
                    <th class="cl3">MSI Qty</th>
                    <th class="cl4">MCN Qty</th>
                    <th>Department</th>
                    <th>Customer</th>
                    <th>SO Sales Contact</th>
                    <th>Currency</th>
                    <th>Order Amount</th>
                    <th>Item Amount</th>
                    <th>Create Time</th>
                </tr>
            </thead>
            <tbody class="${tHead.ref}_item_list_si">
            % for si in si_list:
                <tr>
                	<td class="head"><input type="checkbox"  value="${si.invoice_no}" class="${tHead.ref}_dboxClass"></td>
                    <td><a href="javascript:void(0)" onclick="viewSI('${si.invoice_no}')">${si.invoice_no}</a></td>
                    <td class="si_qty">${si.qty}</td>
                    <td>${si.ri_qty}</td>
                    <td>${si.available_qty}</td>
                    <td>${si.msi_qty}</td>
                    <td>${si.mcn_qty}</td>
                    <td>${si.department}</td>
                    <td>${si.customer}</td>
                    <td>${si.so_sales_contact}</td>
                    <td>${si.currency}</td>
                    <td>${pf(si.order_amt)}</td>
                    <td>${pf(si.item_amt)}</td>
                    <td>${si.create_date}</td>
                </tr>
                %endfor
            </tbody>
        </table>
    </div>
</div>
% endif 
<!--end si list-->
<!--sheet--->
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
                % for so_infos in tHead.so_heads:
                % for detail in so_infos.so_details:
                % if detail.vat_qty != 0:
                <tr  id="detail_${detail.id}">
                % else:
                <tr style="display:none" id="detail_${detail.id}">
                % endif
                    <td class="head">${detail.so_head.t_head.ref}</td>
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
                    <td>${detail.unit}&nbsp;</td>
                    <td>${detail.so_head.currency}</td>
                    <td id='unit_price_${detail.id}_detail' class="unit_price_detail">${detail.unit_price* Decimal("1.17")}
                    </td>
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
                % for so in tHead.so_heads:
       			<% charges = so.find_charges() %>
       			% for j in charges:
       			% if j.vat_total !=0: 
                <tr id="charge_${j.id}">
                % else:
                <tr style="display:none" id="charge_${j.id}">
                % endif
                    <td class="head">${j.t_head.ref}</td>
                    <td>${j.invoice_no}&nbsp;</td>
                    <td>${b(j.cust_po_no)|n}&nbsp;</td>
                    <td>${j.sales_contract_no}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td  class="quantity" >&nbsp;</td>
                    <td>${j.charge_code}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>${j.currency}</td>
                    <td>&nbsp;</td>
                    <td class="freights" >&nbsp;</td>
                    <td class="total_amount"  id="total_amount_${j.id}_charge">${round(j.vat_total*Decimal('1.17'), 2)}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax" id="total_amount_without_tax_${j.id}_charge">${round(j.vat_total, 2)}</td>
                    <td class="tax"  id="tax_${j.id}_charge">${round(j.vat_total*Decimal('1.17') - j.vat_total, 2)}</td>
                    <td class="total_amount_total_amount" id="total_amount_total_amount_${j.id}_charge">${round(j.vat_total*Decimal('1.17'), 2)}</td>
                </tr>
                % endfor
                % endfor
                <!-- charge list end -->
                <!-- other charge list start -->
                % for u,si_infos in enumerate(tHead.so_heads):
 				% if u == 0:
                % for k,detail in enumerate(si_infos.so_details):
                % if k == 0:
                % for c, other_charge in enumerate(other_charges_from_vat):
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
                    <td class="head">${detail.so_head.t_head.ref}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>${other_charge.sales_contract_no}&nbsp;</td>
                    <td>&nbsp;</td>
                    <td  class="quantity">&nbsp;</td>
                    <td>${other_charge.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${detail.so_head.currency}</td>
                    <td>&nbsp;</td>
                    <td class="freights"> &nbsp; </td>
					<td class="total_amount" id="total_amount_${other_charge.id}_other_charge">${round(vat_total*Decimal('1.17'), 2)}</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax" id="total_amount_without_tax_${other_charge.id}_other_charge">${round(vat_total, 2)}</td>
                    <td class="tax" id="tax_${other_charge.id}_other_charge">${round(vat_total*Decimal('0.17'), 2)}</td>
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
	                <td class="quantity_all" >&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td class="freights_all">&nbsp;</td>
					<td class="total_amount_all">&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax_all" >&nbsp;</td>
                    <td class="tax_all" >&nbsp;</td>
                    <td class="total_amount_total_amount_all" >&nbsp;</td>
	            </tr>
                <!-- statistics end   -->
            </tbody>
        </table>
    </div>
</div>
%endif
<!--end sheet-->
%endif
  