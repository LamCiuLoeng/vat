<%
    from decimal import Decimal
    from vatsystem.model import RID,RICharge,UID,UICharge,PI
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
	initGetAll('#${pHead.ref}');
	$("#charge_code").autocomplete(data);
	$(document).ready(function() {
		$("#${pHead.ref}_erp").fancybox({ 
			'width'				: '80%',
			'height'			: '80%',
			'autoScale'			: false,
			'transitionIn'		: 'none',
			'transitionOut'		: 'none',
			'type'				: 'iframe',
			onClosed	        :  function() {viewPhead('${pHead.id}','${pHead.ref}')}
			
		})
		$("#${pHead.ref}_pi").fancybox({ 
			'width'				: '80%',
			'height'			: '80%',
			'autoScale'			: false,
			'transitionIn'		: 'none',
			'transitionOut'		: 'none',
			'type'				: 'iframe',
			onClosed	        :  function() {viewPhead('${pHead.id}','${pHead.ref}')}
		})

	});
</script>
<style type="text/css">
<!--
.iframe{border: 1px solid #336633; padding: 4px; background-color:#ffeedd;color:#336633;font-weight:bold;margin:0}
-->
</style>
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>MPI Information</div>
    <div>
        <div class="toolbar">
            %if pHead.status == const.VAT_THEAD_STATUS_POST:
            <input type="button" class="btn" Value="Create MSN" onclick="javascript:openNewMsnForm3('${pHead.id}','${pHead.vat_no}')" />
	            <!--start show frame-->
	            <div class="none" id="vatDialog5_${pHead.id}">
	            <form action="/ap/save_to_shead" method="post" id="form25_${pHead.id}">
	                <div class="box6">
	                    <ul>
	                        <li class="li1">VAT No Range </li>
	                        <li class="li2"><input type="text" name="vat_no" id="vat_no25_${pHead.id}" /></li>
	                        <li class="li4">(e.g. 00000001~00000010,00000099)</li>
	                    </ul>
	                    <div class="clear"></div>
	                </div>
	                <div class="box7">
	                	<input type="hidden" id="vat_no25" value="${pHead.vat_no}">
	                    <input type="hidden" value=${pHead.id}  name="id">
	                    <div style="display:none"><input type="text"/></div>
	                    <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form25_'+${pHead.id},'Save Success!','${pHead.id}','${pHead.ref}',saveNewMcnForm2('${pHead.id}', '${pHead.vat_no}', '${pHead.ref}'),'pi_po_save')" />
	                    <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
	                </div>
	            </form>
	            </div>
				<!-- end show frame-->
            <input type="hidden" onclick="javascript:openNewMfForm('${pHead.id}','${const.CHARGE_TYPE_P_PI}')" value="Create MF" class="btn">
	            <!--start show frame-->
	            <div class="none" id="vatDialog26_${pHead.id}">
	            <form action="/ap/save_to_mf" method="post" id="form26_d_${pHead.id}">
	                <div class="box6">
	                    <ul>
	                        <li class="li1">VAT No Range </li>
	                        <li class="li2"><input type="text" name="vat_no" id="vat_no26_d_${pHead.id}" /></li>
	                        <li class="li4">(e.g. 00000001~00000010,00000099)</li>
	                    </ul>
	                    <div class="clear"></div>
	                </div>
	                <div class="box7">
	                	<input type="hidden" id="vat_no26" value="${pHead.vat_no}">
	                    <input type="hidden" value=${pHead.id}  name="id">
	                    <input type="hidden" value="t_head_id"  name="type">
	                    <div style="display:none"><input type="text"/></div>
	                    <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form26_d_${pHead.id}','Save Success!','${pHead.id}','${pHead.ref}',saveNewMfForm2('d_${pHead.id}', '${pHead.vat_no}'),'pi_po_save')" />
	                    <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
	                </div>
	            </form>
	            </div>
				<!-- end show frame-->
            %endif
             <input type="button" onclick="javascript:exportData('phead_pi_${pHead.id}')" value="Export" class="btn">
                
	        	<form action="/report/export" method="post" id="form5_phead_pi_${pHead.id}" style="display:none">
	            <input type="hidden" name="id" value="${pHead.id}"/>
	            <input type="hidden" name="head_type" value="pHead"/>
	            </form>
             %if pHead.status == const.VAT_THEAD_STATUS_NEW:
             <input type="button" class="btn iframe" value="Add Other Charges From ERP" href="/ap/search_charge_erp?pHead_id=${pHead.id}&supplier=${pHead.supplier}" id="${pHead.ref}_erp" />
             <input type="button" class="btn" Value="Add Other Manual Charges" onclick="javascript:Add_Other_Charges_From_Manual('${pHead.id}')" />
        	 <input type="button" value="Add Other PI From ERP" class="btn" href="/ap/add_pi_po_erp?type=1&pHead_id=${pHead.id}&supplier=${pHead.supplier}&viewPager=1" id="${pHead.ref}_pi" >
        	% endif
        	<input type="button" class="btn" value="History" onclick="OpenDialog('/ar/view_history?type=P&id=${pHead.id}','#searchDialog','${pHead.ref} History')" href="javascript:void(0)" > 
        	<!--save a new charge-->
             <div class="none" id="Add_Other_Charges_From_Manual_${pHead.id}">
             <form action="/ap/add_other_charges_from_manual" method="POST" id="form15_${pHead.id}"  >
             <div class="box6">
           	<ul style="display:none">
   				<li class="li1">Line No</li>
   				<li class="li2"><input type="hidden"  name="line_no" value="${get_last_line_no(pHead.id)}" /></li>
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
			    <input type="hidden" name="p_head_id" value=${pHead.id} /> 
             <div class="clear"></div>
             </div>
            <div class="box7">
                     <input type="hidden" name="active" value="0"/>
                     <input type="hidden" name="company_code" value="RPACSZ"/>
                     <input type="hidden" name="type" value="${const.CHARGE_TYPE_P_MAN}"/>
                     <input type="hidden" name="vat_total" value="" />
                     <input type="submit" class="btn" value="Submit" id="form15_btn_${pHead.id}"  onclick="ajaxForm('#form15_${pHead.id}','Success!','${pHead.id}','${pHead.ref}',checkNull('#form15_${pHead.id}'),'pi_po_save')"/>
                     <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
           </div>
           </form>
            </div>
            <!-- end show frame-->
        </div>
        <ul>
            <li class="li1">Supplier:</li>
            <li class="li2">${pHead.supplier}</li>
            <li class="li1">Supplier Name:</li>
            <li class="li2 fcn" style="float:left;width:400px;" >${pHead.supplier_name}</li>
        </ul><ul>
            <li class="li1">Status:</li>
            <li class="li2">${pHead.status}</li>
            <li class="li1">Ref No:</li>
            <li class="li2">${pHead.ref}</li>
        </ul>
        %if pHead.vat_no or pHead.vat_date:
        <ul>
            <li class="li1">VAT No:</li>
            <li class="li2"  id='vat_no_${pHead.id}'>${pHead.vat_no}</li>
            <li class="li1">VAT Date:</li>
            <li class="li2">${pt(pHead.vat_date)}</li>
        </ul>
        %endif
        <ul>
            <li class="li1">Create Date:</li>
            <li class="li2">${pt(pHead.create_time)}</li>
            <li class="li1">Update Date:</li>
            <li class="li2">${pt(pHead.update_time)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>

%if len(pHead.s_heads) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MSN</div>
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
                % for i in pHead.s_heads:
                <tr>
                    <td class="head"><a href="javascript:viewShead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
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
%if len(pHead.m_heads) > 0:
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
                % for i in pHead.m_heads:
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
    <div class="box4" id="check_ava_$${pHead.id}">	
     %if pHead.status == const.VAT_THEAD_STATUS_NEW:
    	<p><input type="button" class="btn"  value="Delete" onclick="deleteItem('/ap/ajax_delete_item','${pHead.ref}_item_list','PI','${pHead.id}','${pHead.ref}')" />
    </p><br />
    %endif
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                	%if pHead.status == const.VAT_THEAD_STATUS_NEW:
                	<th  class="head"><input type="checkbox" onclick="selectAllDetail(this,'${pHead.ref}_item_list')" value="0"></th>
                     % endif
                    <th class="head">Invoice NO</th>
                    <th>PO No</th>
                    <th>Department</th>
                    <th>Supplier</th>
                    <th>Currency</th>
                    <th class="cl5">Order Amount</th>
                    <th class="cl5">Item Amount</th>
                    <th>Order Amount</th>
                    <th>Item Amount</th>
                    <th>Create Time</th>
                    <th>SN</th>
                </tr>
            </thead>
            <tbody class="${pHead.ref}_item_list">
                % for si in pHead.pi_heads:
                <tr>
                	%if pHead.status == const.VAT_THEAD_STATUS_NEW:
                	<td class="head"><input type="checkbox"   value="${si.id}" class="dboxClass"></td>
                    % endif
                    <td>
                    <a href="javascript:void(0)" onclick="toggleOne('tr2_'+${si.id})">${si.invoice_no}</a></td>
                    <td>${si.po_no}&nbsp;</td>
                    <td>${si.department}</td>
                    <td>${si.supplier}</td>
                    <td>${si.currency}</td>
                    <td>${round(si.order_amt,2)}</td>
                    <td>${round(si.item_amt,2)}</td>
                    <td class='payment' cate='order_amount' id="order_amount_${si.invoice_no}" invoice='${si.invoice_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td class='payment' cate='item_amount' id="item_amount_${si.invoice_no}" invoice='${si.invoice_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td>${pd(si.create_time)}</td>
                    <td>
                    <!--CN Detail Start-->
                    <% cn_list    =  PI.parse_data(si.invoice_no) %>
	                <% cn_details =  cn_list[2] %>
	                <% cn_charges =  cn_list[3] %>
				    %if len(cn_details)>0:
				    <a class="west" href="javascript:openDialogSN('${si.invoice_no}')" original-title="SN">
				    <img src="/images/icon-yes.gif" border="0"  alt="CN" />
				    </a>
				    <!-- display cn charge -->
				    <div id="dialog_${si.invoice_no}" class="none" style="width:800px;">
					<div class="box2">
				    <div class="title1" style='text-align:left'><div class="toggle_down"></div>SN Detail</div>
				    <div class="box4">
				        <table cellspacing="0" cellpadding="0" border="0" class="gridTable">
				            <thead class="cl3">
				                <tr>
				                	<th class="head">Line NO</th>
				                	<th>Item No</th>
				                    <th>Invoice NO</th>
				                    <th>Note No</th>
				                    <th>PO No</th>
				                    <th>Note Qty</th>
				                    <th>Unit</th>
				                    <th>Price</th>
				                    <th>Total</th>
				                    <th>Create Time</th>
				                </tr>
				            </thead>
				            <tbody>
				                % for u,i in enumerate(cn_details):
				                <tr>
				                	<td class="head">${u+1}</td>
				                	<td>${i.item_no }</td>
				                    <td >${i.pi_no}</td>
				                    <td>${i.note_no} </td>
				                    <td>${i.po_no}</td>
				                    <td>${pi(i.note_qty)}</td>
				                    <td>${i.unit}</td>
				                    <td>${i.unit_price}</td>
				                    <td>${pf(i.item_total)}</td>
				                    <td>${pd(i.create_date)}</td>
				                </tr>
				                  % endfor
				               <!-- other charges list start-->
				  			   <!-- other charges list end  -->
				            </tbody>
				        </table>
				        
				    </div>
				</div>
				% if len(cn_charges)>0:
				      <div class="box2">
					    <div class="title1"><div class="toggle_down"></div>SN Charge</div>
					    <div class="box4" style="display: block;">
					        <table cellspacing="0" cellpadding="0" border="0" class="gridTable">
					          <thead class="cl3">
					                <tr>
					                    <th>Line NO</th>
					                    <th>Chg Discount Code</th>
					                    <th>Percentage</th>
					                    <th>Amount</th>
					                    <th>Total</th>
					                    <th>Create Time</th>
					                </tr>
					            </thead>
					            <tbody>
					             % for t,v in enumerate(cn_charges):
					                <tr>
					                    <td class="head">${t+1}</td>
					                    <td>${v.chg_discount_code }</td>
					                    <td>${v.percentage} &nbsp;</td>
					                    <td>${pf(v.amount)} &nbsp;</td>
					                    <td>${pf(v.total)}</td>
					                    <td>${pd(v.create_date)}</td>
					                </tr>
					              %endfor 
					            </tbody>
					        </table>
					    </div>
					</div> 
				% endif 
				</div>
				<!--end display the cn charges-->
				%else:
				<img src="/images/icon_deletelink.gif" border="0" > 
				%endif
	           <!--CN Detail end  --></td>
                </tr>
                <tr class="toggle none" id="tr2_${si.id}">
                    <td colspan="100" class="gridInTd">
                        <div class="gridInDiv">
                            <form action="/ap/update_phead_details" method="post" id="_form_si${si.id}">
                                %if pHead.status == const.VAT_THEAD_STATUS_NEW:
                                <input type="submit" class="btn"  value="Save" onclick="ajaxForm('#_form_si${si.id}','Save Success!','${pHead.id}','${pHead.ref}',toSaveSISODetails('si','${si.id}'),'pi_po_save')" style="clear:none;margin-right:10px;"/>
                                <input type="button" class="btn"  value="Set All Details Tax" onclick="set_tax('#tr2_${si.id}')" style="clear:none"/>
                                %endif
                                <input type="hidden" name="id" value="${si.id}"/>
                                <input type="hidden" name="head_type" value="${const.CHARGE_TYPE_P_PI}"/>
                                <div class="title">Detail
                                %if pHead.status == const.VAT_THEAD_STATUS_NEW:
                                % if cn_list[4] == 0 or cn_list[4] == 1:
    								<div style="color:#ff0000;font-weight:blod;line-height:20px;height:20px;border:1px solid #e1e1e1;width:480px"><img src="/images/icon_alert.gif" style="width:13px;height:13px;margin-top:3px;"> 
    									${const.TAX_RATE_MESSAGE}
    								</div>
                                % endif 
                                % endif
                                </div>
                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Item NO</th>
                                            <th>Qty</th>
                                            <th>SN Qty</th>
                                            <th>Available Qty</th>
                                            <th class="cl4">MSN Qty</th>
                                            <th>VAT Qty</th>
                                            <th>Unit Price</th>
                                            <th>Tax(%)</th>
                                            <th>Description</th>
                                            <th>Item Amount</th>
                                            <th style='display:none'>Item Amount</th>
                                            <th>Unit</th>
                                            <th>Remark</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in si.find_details(cn_details):
                                        <tr name="detail_${j.id}" >
                                            <td class="head">${j.line_no}</td>
                                            <td>${j.item_no}</td>
                                            <td>${j.qty}</td>
                                            <td>${j.cn_qty}</td>
                                            <td class="available_qty">${j.ava_qty}</td>
                                            <td>${j.msn_qty}</td>
                                            %if pHead.status == const.VAT_THEAD_STATUS_NEW:
	                                            <td><input statement class="qty numeric" type="text" name="qty_${j.id}" value="${j.vat_qty}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' /></td>
	                                            <td><input statement class="price" type="text" name="price_${j.id}" value="${j.unit_price}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}'/></td>
	                                         	<td><input statement class="tax" type="text" name="tax_${j.id}" value="${float(j.tax_rate*100)}" tax_rate='${j.tax_rate}'  unit_price='${j.unit_price}' include_tax='${j.include_tax}' cate='detail' ids='${j.id}' /></td>
	                                            <td><input class="desc" type="text" name="desc_${j.id}" value="${j.desc_zh}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}'/></td>
                                            	<td id="rmb_amount_p_${j.id}">${round(j.vat_qty*j.unit_price,2)}</td>
	                                            <td id="rmb_amount_${j.id}">${round(j.vat_qty*j.unit_price*(1+j.tax_rate),2)}</td>
                                            %else:
                                            <td>${j.vat_qty}</td>
                                            <td>${j.unit_price}</td>
                                            <td>${int(j.tax_rate*100)}</td>
                                            <td>${j.desc_zh}</td>
                                            <td id="rmb_amount_p_${j.id}" >${round(j.vat_qty*j.unit_price,2)}</td>
	                                        <td id="rmb_amount_${j.id}" style='display:none'>${round(j.vat_qty*j.unit_price*(1+j.tax_rate),2)}</td>
                                            %endif
                                            <td>${j.unit}</td>
                                            %if pHead.status == const.VAT_THEAD_STATUS_NEW:
                                            	<td><input type="text" name="remark_${j.id}" value="${j.remark}"></td>
                                            %else:
                                            	<td>${j.remark}&nbsp;</td>
                                            %endif
                                        </tr>
                                        	<input  type="hidden" name="item_amount_${j.id}" value="${round(j.vat_qty*j.unit_price,2)}" cate='item_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.invoice_no}" Head_id='${si.id}'/>
											<input  type="hidden" name="order_amount_${j.id}" value="${round(j.vat_qty*j.unit_price,2)}" cate='order_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.invoice_no}" Head_id='${si.id}'/>
                                        % endfor
                                    </tbody>
                                </table>
                                <!--this is the other charges list -->
                                <% charges = si.find_charges(cn_charges) %>
                                % if len(charges) > 0:
                                <div class="title">Charge</div>
                                <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Total</th>
                                            <th>SN Total</th>
                                            <th>Available Total</th>
                                            <th class="cl4">MSN Total</th>
                                            <th>VAT Total</th>
                                            <th>Charge Code</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        % for j in charges:
                                        <tr name="charge_${j.id}">
                                            <td class="head">${j.line_no}</td>
                                            <td>${pf(j.total)}</td>
                                            <td>${pf(j.cn_total)}</td>
                                            <td class="available_qty">${pf(j.ava_total)}</td>
                                            <td>${pf(j.msn_total)}</td>
                                            %if pHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <td><input class="qty numeric" type="text" name="total_${j.id}" value="${pf(j.vat_total)}"  cate='charge' ids='${j.id}'  forid="total_${j.id}_charge_1"/></td>
                                            %else:
                                            <td  id="rmb_amount_p_${j.id}" >${pf(j.vat_total)}</td>
                                            %endif
                                            <td>${j.charge_code}
                                            	<input  type="hidden" name="item_amount_${j.id}" value="${pf(j.vat_total)}" cate='order_amount'  invoice="${si.invoice_no}" Head_id='${si.id}'/>
                                            </td>
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
                % if len(Other_Charges_From_vats) > 0:
                	<tr id="${pHead.ref}_tr">
                % else:
                	<tr id="${pHead.ref}_tr" style="display:none">
                % endif
                    <td class="gridInTd" colspan="100" >
                        <div class="gridInDiv">
                        <form action="/ap/update_other_charges_vat_total" method="POST" id="${pHead.ref}_update_other_charges_vat_total_si">
                          		<div class="title other_charge_tab">Other Charge</div>
  								<div class="other_charge_content" style="display:none" id="${pHead.ref}_charge" >
  								% if len(Other_Charges_From_vats) > 0:
  								% if pHead.status == const.VAT_THEAD_STATUS_NEW:
  								    <input type="submit" class="btn"  id="save_other_charge" value="Save" style="float:left;margin-right:15px;clear:none;margin-left:15px;" name="save" onclick="ajaxForm('#${pHead.ref}_update_other_charges_vat_total_si','Save Success!','${pHead.id}','${pHead.ref}',toSaveSISOCharge('#${pHead.ref}_update_other_charges_vat_total_si'),'pi_po_save')"> 
                        			<input type="submit" class="btn" value="Delete" style="clear:none;margin-left:15px;" name="delete" onclick="ajaxForm('#${pHead.ref}_update_other_charges_vat_total_si','Delete Success!','${pHead.id}','${pHead.ref}',checkSelect('#${pHead.ref}_update_other_charges_vat_total_si'),'pi_po_save')" >
  								% endif
  								  <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                       <tr>
                                            %if pHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <th width="20px" class="head"><input type="checkbox" onclick="selectAll(this)" id="selectAlls"></th>
                                            %endif
                                            <th>Line NO</th>
                                            <th class="cl3">Total</th>
                                            <th>Vat Total</th>
                                            <th>Chg Discount Code</th>
                                            <th>Type</th>
                                            <th>Note No</th>
                                            <th>Create Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                    % for v,k in enumerate(Other_Charges_From_vats):
                                        <tr name="other_charge_${k.id}">
                                        	%if pHead.status == const.VAT_THEAD_STATUS_NEW:
	                                            <td width="20px" class="head">
	                                            	<input type="checkbox"  value="${k.id}" class="cboxClass"  name="checkbox_list">
	                                            </td>
                                            %endif
                                            <td class="head">${v+1}</td>
                                            %if not k.note_no:
                                            <td  class='available_qty' >
                                            %else:
                                             <td id="no_check">
                                            % endif
                                            ${k.total}
                                            </td>
                                            <td>&nbsp;
                                            %if pHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <input type="text" value="${k.vat_total}" name="${k.id}" class="qty numeric check_numbers" cate='other_charge' ids='${k.id}' forid="${k.id}_other_charge_1"  > 
											% else:
											${k.vat_total}
											% endif
											</td>
                                            <td>
                                            ${k.charge_code}</td>
                                            <td> 
                                            %if k.type == const.CHARGE_TYPE_P_ERP:
                                            	Supplier
                                            %else:
                                            	Manual
                                            %endif 
                                            </td>
                                            <td>${k.note_no} &nbsp;</td>
                                            <td>${pd(k.create_time)}</td>
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
%if pHead.status!=const.VAT_THEAD_STATUS_CANCELLED:
<div class="clear"></div>
<div class="box3">
    <div class="title1"><div class="toggle2 toggle_right"></div>Sheet</div>
    <div class="box4" id="${pHead.ref}">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                    <th>MPI No.</th>
                    <th>Invoice No.</th>
                    <th>PO No.</th>
                    <th>Supplier</th>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Item Desc(Chinese)</th>
                    <th>Unit</th>
                    <th>Currency</th>
                    <th style='display:none'>Unit Price</th>
                    <th>Freight</th>
                    <th style='display:none'>Total Amount</th>
                    <th>Unit Price(without tax)</th>
                    <th>Total Amount(without tax)</th>
                    <th style='display:none'>Tax</th>
                    <th>Total Amount</th>
                </tr>
            </thead>
            <tbody>
                % for si_infos in pHead.pi_heads:
                % for detail in si_infos.pi_details:
                % if detail.vat_qty != 0:
                <tr  id="detail_${detail.id}">
                % else:
                <tr style="display:none" id="detail_${detail.id}">
                % endif
                    <td class="head">${detail.pi_head.p_head.ref}</td>
                    <td>${detail.invoice_no}</td>
                    <td>${detail.pi_head.po_no}&nbsp;</td>
                    <td>${detail.pi_head.supplier}</td>
                    <td>${detail.item_no}</td>
                    <td class="quantity" id="qty_${detail.id}_detail">${detail.vat_qty}</td>
                    <td id="desc_${detail.id}_detail">
                    <%
                    tax_rate          = 1 + detail.tax_rate
                    tax_rate_out_self = detail.tax_rate 
                    if detail.include_tax == 0:
                    	unit_price        = detail.unit_price
                    	total_amount      = round(detail.vat_qty * unit_price, 2)
                    	unit_price_tax    = round(detail.unit_price/tax_rate,6)
                    	total_amount_without_tax  = round(detail.vat_qty * unit_price_tax, 2)
                    else:
                    	unit_price        = detail.unit_price*tax_rate
                    	total_amount      = round(detail.vat_qty * detail.unit_price*tax_rate, 2)
                    	unit_price_tax    = round(detail.unit_price,6)
                    	total_amount_without_tax = round(detail.vat_qty * detail.unit_price, 2)
                    
                    if detail.desc_zh:
                    	zh = detail.desc_zh
                    else:
                    	zh = detail.item_desc
                    %>
                    ${zh}&nbsp;</td>
                    <td>${detail.unit}</td>
                    <td>${detail.pi_head.currency}</td>
                    <td style='display:none' id='unit_price_${detail.id}_detail' class="unit_price_detail" >${unit_price}</td>
                    <td>&nbsp;</td>
                    <td style='display:none' class="total_amount" id="total_amount_${detail.id}_detail">${total_amount}</td>
                    <td id='unit_price_tax_${detail.id}_detail' >${unit_price_tax}</td>
                    <td class="total_amount_without_tax" id="total_amount_without_tax_${detail.id}_detail">${total_amount_without_tax}</td>
                    <td style='display:none' class="tax" id="tax_${detail.id}_detail" >${round(total_amount - total_amount_without_tax , 2)}</td>
                    <td class="total_amount_total_amount" id="total_amount_total_amount_${detail.id}_detail">${total_amount_without_tax}</td>
                </tr>
                % endfor
                % endfor
                <!-- charge list -->
 				% for u,si_infos in enumerate(pHead.pi_heads):
                % for k,detail in enumerate(si_infos.pi_details):
                % if k == 0:
                % for si in pHead.pi_heads:
                <% charges = si.find_charges(cn_charges) %>
       			% for j in charges:
       			% if detail.pi_head_id == j.pi_head_id:
       			% if j.type== const.CHARGE_TYPE_P_PI:
	       			% if j.vat_total !=0: 
	                <tr id="charge_${j.id}">
	                % else:
	                <tr style="display:none" id="charge_${j.id}">
	                % endif
                    <td class="head">${detail.pi_head.p_head.ref}</td>
                    <td>${j.invoice_no}</td>
                    <td>${detail.pi_head.po_no}&nbsp;</td>
                    <td>${detail.pi_head.supplier}</td>
                    <td>&nbsp;</td>
                    <td class="quantity">&nbsp;</td>
                    <td>${j.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${detail.pi_head.currency}</td>
                    <td style='display:none'>&nbsp;</td>
                    <td class="freights" id="total_${j.id}_charge_1">${pf(j.vat_total)}</td>
                    <td style='display:none' class="total_amount">&nbsp;</td>
                    <td >&nbsp;</td>
                    <td class="total_amount_without_tax">&nbsp;</td>
                    <td style='display:none' class="tax" >&nbsp;</td>
                    <td class="total_amount_total_amount" id="total_${j.id}_charge">${pf(j.vat_total)}</td>
                </tr>
                % endif
                % endif
                % endfor
                % endfor
               
                % endif
                % endfor
                % endfor
                <!-- charge list end -->
                <!-- other charge list start -->
                % for u,si_infos in enumerate(pHead.pi_heads):
 				% if u == 0:
                % for k,detail in enumerate(si_infos.pi_details):
                % if k == 0:
                % for c,v in enumerate(Other_Charges_From_vats):
                % if v.total != 0:
                <tr id='other_charge_${v.id}'>
                % else:
                <tr style="display:none" id='other_charge_${v.id}'>
                % endif
                	<% 
                    if v.vat_total ==None:
                    	vat_total = v.total
                    else:
                    	vat_total = v.vat_total
                    %>
                    <td class="head">${detail.pi_head.p_head.ref}</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="quantity" >&nbsp;</td>
                    <td>${v.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${detail.pi_head.currency}</td>
                    <td style='display:none'>&nbsp;</td>
                    <td class="freights" id='${v.id}_other_charge_1'>${vat_total}</td>
					<td style='display:none' class="total_amount">&nbsp;</td>
                    <td >&nbsp;</td>
                    <td class="total_amount_without_tax" >&nbsp;</td>
                    <td style='display:none' class="tax" >&nbsp;</td>
                    <td class="total_amount_total_amount"  id='${v.id}_other_charge'> ${vat_total}</td>
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
	                <td >&nbsp;</td>
	                <td>&nbsp;</td>
	                <td style='display:none'>&nbsp;</td>
	                <td class="freights_all">&nbsp;</td>
					<td style='display:none' class="total_amount_all">&nbsp;</td>
                    <td>&nbsp;</td>
                    <td class="total_amount_without_tax_all">&nbsp;</td>
                    <td style='display:none' class="tax_all" >&nbsp;</td>
                    <td class="total_amount_total_amount_all" >&nbsp;</td>
	            </tr>
                <!-- statistics end   -->
            </tbody>
        </table>
    </div>
</div>
%endif
%endif
 
 