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
	initPayment();
	initChangeVal();
	intiParsePrice();
	initStatement();
	initGetAll('#${mHead.ref}');
	$("#charge_code").autocomplete(data);
	$(document).ready(function() {
		$("#${mHead.ref}_erp").fancybox({ 
			'width'				: '80%',
			'height'			: '80%',
			'autoScale'			: false,
			'transitionIn'		: 'none',
			'transitionOut'		: 'none',
			'type'				: 'iframe',
			onClosed	        :  function() {viewmHead('${mHead.id}','${mHead.ref}')}
			
		})
		$("#${mHead.ref}_pi").fancybox({ 
			'width'				: '80%',
			'height'			: '80%',
			'autoScale'			: false,
			'transitionIn'		: 'none',
			'transitionOut'		: 'none',
			'type'				: 'iframe',
			onClosed	        :  function() {viewmHead('${mHead.id}','${mHead.ref}')}
		})

	});
</script>
<style type="text/css">
<!--
.iframe{border: 1px solid #336633; padding: 4px; background-color:#ffeedd;color:#336633;font-weight:bold;margin:0}
-->
</style>
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>MF Information</div>
    <div>
        <div class="toolbar">
            %if mHead.status == 'const.VAT_THEAD_STATUS_POST':
            <input type="button" class="btn" Value="Create MSN" onclick="javascript:openNewMsnForm3('${mHead.id}','${mHead.vat_no}')" />
	            <!--start show frame-->
	            <div class="none" id="vatDialog5_${mHead.id}">
	            <form action="/ap/save_to_shead" method="post" id="form25_${mHead.id}">
	                <div class="box6">
	                    <ul>
	                        <li class="li1">VAT No Range </li>
	                        <li class="li2"><input type="text" name="vat_no" id="vat_no25_${mHead.id}" /></li>
	                        <li class="li4">(e.g. 00000001~00000010,00000099)</li>
	                    </ul>
	                    <div class="clear"></div>
	                </div>
	                <div class="box7">
	                	<input type="hidden" id="vat_no25" value="${mHead.vat_no}">
	                    <input type="hidden" value=${mHead.id}  name="id">
	                    <div style="display:none"><input type="text"/></div>
	                    <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form25_'+${mHead.id},'Save Success!','${mHead.id}','${mHead.ref}',saveNewMcnForm2('${mHead.id}', '${mHead.vat_no}', '${mHead.ref}'),'pi_po_save')" />
	                    <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
	                </div>
	            </form>
	            </div>
				<!-- end show frame-->
            <input type="button" onclick="javascript:openNewMfForm('${mHead.id}','${mHead.vat_no}')" value="Create MF" class="btn">
	            <!--start show frame-->
	            <div class="none" id="vatDialog6_${mHead.id}">
	            <form action="/ap/save_to_mf" method="post" id="form26_${mHead.id}">
	                <div class="box6">
	                    <ul>
	                        <li class="li1">VAT No Range </li>
	                        <li class="li2"><input type="text" name="vat_no" id="vat_no26_${mHead.id}" /></li>
	                        <li class="li4">(e.g. 00000001~00000010,00000099)</li>
	                    </ul>
	                    <div class="clear"></div>
	                </div>
	                <div class="box7">
	                	<input type="hidden" id="vat_no26" value="${mHead.vat_no}">
	                    <input type="hidden" value=${mHead.id}  name="id">
	                    <div style="display:none"><input type="text"/></div>
	                    <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form26_${mHead.id}','Save Success!','${mHead.id}','${mHead.ref}',saveNewMfForm('${mHead.id}', '${mHead.vat_no}', '${mHead.ref}'),'pi_po_save')" />
	                    <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
	                </div>
	            </form>
	            </div>
				<!-- end show frame-->
            %endif
        	<input type="button" class="btn" value="History" onclick="OpenDialog('/ar/view_history?type=M&id=${mHead.id}','#searchDialog','${mHead.ref} History')" href="javascript:void(0)" > 
        	<!--save a new charge-->
             <div class="none" id="Add_Other_Charges_From_Manual_${mHead.id}">
             <form action="/ap/add_other_charges_from_manual" method="POST" id="form15_${mHead.id}"  >
             <div class="box6">
           	<ul style="display:none">
   				<li class="li1">Line No</li>
   				<li class="li2"><input type="hidden"  name="line_no" value="${get_last_line_no(mHead.id)}" /></li>
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
			    <input type="hidden" name="p_head_id" value=${mHead.id} /> 
             <div class="clear"></div>
             </div>
            <div class="box7">
                     <input type="hidden" name="active" value="0"/>
                     <input type="hidden" name="company_code" value="RPACSZ"/>
                     <input type="hidden" name="type" value="${const.CHARGE_TYPE_S_MAN}"/>
                     <input type="hidden" name="vat_total" value="" />
                     <input type="submit" class="btn" value="Submit" id="form15_btn_${mHead.id}"  onclick="ajaxForm('#form15_${mHead.id}','Success!','${mHead.id}','${mHead.ref}',checkNull('#form15_${mHead.id}'),'pi_po_save')"/>
                     <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
           </div>
           </form>
            </div>
            <!-- end show frame-->
        </div>
        <ul>
            <li class="li1">Supplier:</li>
            <li class="li2">${mHead.supplier}</li>
            <li class="li1">Supplier Name:</li>
            <li class="li2 fcn" style="float:left;width:400px;" >${mHead.supplier_name}</li>
        </ul><ul>
            <li class="li1">Status:</li>
            <li class="li2">${mHead.status}</li>
            <li class="li1">Ref No:</li>
            <li class="li2">${mHead.ref}</li>
        </ul>
        %if mHead.vat_no or mHead.vat_date:
        <ul>
            <li class="li1">VAT No:</li>
            <li class="li2">${mHead.vat_no}</li>
            <li class="li1">VAT Date:</li>
            <li class="li2">${pt(mHead.vat_date)}</li>
        </ul>
        %endif
        <ul>
        	% if mHead.p_head_id:
	            <li class="li1">MPI VAT No:</li>
	            <li class="li2">${mHead.p_head.vat_no}</li>
	            <li class="li1">MPI Ref No:</li>
	            <li class="li2">${mHead.phead_ref}</li>
	        % elif mHead.s_head_id:
	            <li class="li1">MSN VAT No:</li>
	            <li class="li2">${mHead.s_head.vat_no}</li>
	            <li class="li1">MSN Ref No:</li>
	            <li class="li2">${mHead.phead_ref}</li>
	        % endif 
        </ul>
        <ul>
            <li class="li1">Create Date:</li>
            <li class="li2">${pt(mHead.create_time)}</li>
            <li class="li1">Update Date:</li>
            <li class="li2">${pt(mHead.update_time)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>

%if mHead.p_head:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MPI</div>
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
                <tr>
                    <td class="head"><a href="javascript:viewPhead('${mHead.p_head.id}', '${mHead.p_head.ref}')">${b(mHead.p_head.ref)|n}</a></td>
                    <td>${b(mHead.p_head.vat_no)|n}</td>
                    <td>${b(mHead.p_head.status)|n}</td>
                    <td>${pd(mHead.p_head.vat_date)|n}</td>
                    <td>${pd(mHead.p_head.export_time)|n}</td>
                    <td>${pd(mHead.p_head.create_time)|n}</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
%endif
<!--
%if mHead.s_head:
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
                <tr>
                    <td class="head"><a href="javascript:viewShead('${mHead.s_head.id}', '${mHead.s_head.ref}')">${b(mHead.s_head.ref)|n}</a></td>
                    <td>${b(mHead.s_head.vat_no)|n}</td>
                    <td>${b(mHead.s_head.status)|n}</td>
                    <td>${pd(mHead.s_head.vat_date)|n}</td>
                    <td>${pd(mHead.s_head.export_time)|n}</td>
                    <td>${pd(mHead.s_head.create_time)|n}</td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
%endif
-->
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>PI</div>
    <div class="box4" id="check_ava_$${mHead.id}">	
     %if mHead.status == const.VAT_THEAD_STATUS_NEW:
    	<p><input type="button" class="btn"  value="Delete" onclick="deleteItem('/ap/ajax_delete_item','${mHead.ref}_item_list','${const.CHARGE_TYPE_S_MF if mHead.p_head_id else const.CHARGE_TYPE_S_NMF }','${mHead.id}','${mHead.ref}')" />
    </p><br />
    %endif
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                	%if mHead.status == const.VAT_THEAD_STATUS_NEW:
                	<th  class="head"><input type="checkbox" onclick="selectAllDetail(this,'${mHead.ref}_item_list')" value="0"></th>
                    %endif
                    <th class="head">Invoice NO</th>
                    <th>PO No</th>
                    <th>Department</th>
                    <th>Supplier</th>
                    <th>Currency</th>
                    <th  class="cl5">Order Amount</th>
                    <th  class="cl5">Item Amount</th>
                    <th>Order Amount</th>
                    <th>Item Amount</th>
                    % if mHead.head_type == const.ERP_HEAD_TYPE_MF:
                    	<th class="cl3">Payment Amount</th>
                    	<th class="cl3">Payment Total</th>
                    % else:
                    	<th class="cl4">Payment Amount</th>
                    	<th class="cl4">Payment Total</th>
                    % endif
                    <th>Create Time</th>
                    <th>SN</th>
                </tr>
            </tHead>
            <tbody class="${mHead.ref}_item_list">
                % for si in mHead.pi_heads:
                <tr>
                	%if mHead.status == const.VAT_THEAD_STATUS_NEW:
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
                    <td class='payment' cate='payment_amount' id="payment_amount_${si.invoice_no}" invoice='${si.invoice_no}' Head_id='${si.id}'> &nbsp;</td>
                    <td class='payment' cate='charge' id="payment_total_${si.invoice_no}" invoice='${si.invoice_no}'  Head_id='${si.id}'> &nbsp;</td>
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
				            </tHead>
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
                            <form action="/ap/update_mhead_details" method="post" id="_form_si${si.id}">
                                %if mHead.status == const.VAT_THEAD_STATUS_NEW:
                                <input type="submit" class="btn"  value="Save" onclick="ajaxForm('#_form_si${si.id}','Save Success!','${mHead.id}','${mHead.ref}',toSaveSheadDetails('si','${si.id}'),'si_so')" style="clear:none;margin-right:10px;"/>
                                %endif
                                <input type="hidden" name="id" value="${si.id}"/>
                                <input type="hidden" name="head_type" value="${const.CHARGE_TYPE_P_PI}"/>
                                <div class="title">Detail</div>
                                <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                        <tr>
                                            <th>Line NO</th>
                                            <th>Item NO</th>
                                            <th>Item Amount(Without Tax)</th>
                                            <th>Item Amount</th>
                                            <th>Available Amount</th>
                                            <th>MF Amount</th>
                                            % if mHead.head_type == const.ERP_HEAD_TYPE_MF:
                                            	<th  class="cl3">Payment Amount</th>
                                            % else:
                                            	<th  class="cl4">Payment Amount</th>
                                            % endif
                                            <th>Description</th>
                                            <th>Unit</th>
                                            <th>Remark</th>
                                        </tr>
                                    </tHead>
                                    <tbody>
                                        % for j in si.find_details(cn_details):
	                                        <tr name="detail_${j.id}" >
	                                            <td class="head">${j.line_no}</td>
	                                            <td>${j.item_no}</td>
	                                            <td>${pf(j.item_total)}<input  type="hidden" name="item_amount_${j.id}" value="${pf(j.item_total)}" cate='item_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.invoice_no}" Head_id='${si.id}'/></td>
	                                            <td>${pf(j.item_total*(1+j.tax_rate))}<input  type="hidden" name="order_amount_${j.id}" value="${pf(j.item_total*(1+j.tax_rate))}" cate='order_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.invoice_no}" Head_id='${si.id}'/></td>
	                                            <td class="available_qty">${pf(j.ava_total)}</td>
	                                            <td>${pf(j.msn_total)}</td>
	                                            %if mHead.status == const.VAT_THEAD_STATUS_NEW:
		                                            <td><input class="qty numeric" type="text" name="vat_total_${j.id}" value="${pf(j.vat_total)}" cate='payment_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.invoice_no}" Head_id='${si.id}'/></td>
		                                            <td><input class="desc" type="text" name="desc_${j.id}" value="${j.desc_zh}" cate='detail' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}'/></td>
	                                            	<input class="tax" type="hidden" name="tax_${j.id}" value="${float(j.tax_rate*100)}" tax_rate='${j.tax_rate}'  unit_price='${j.unit_price}' include_tax='${j.include_tax}' cate='detail' ids='${j.id}' />
	                                            %else:
	                                            <td>${pf(j.vat_total)}<input class="qty numeric" type="hidden" name="vat_total_${j.id}" value="${pf(j.vat_total)}" cate='payment_amount' ids='${j.id}' tax_rate='${j.tax_rate}' unit_price='${j.unit_price}' include_tax='${j.include_tax}' invoice="${si.invoice_no}" Head_id='${si.id}'/></td>
	                                            <td>${j.desc_zh}</td>
	                                            %endif
	                                            <td>${j.unit}</td>
	                                            %if mHead.status == const.VAT_THEAD_STATUS_NEW:
	                                            	<td><input type="text" name="remark_${j.id}" value="${j.remark}"></td>
	                                            %else:
	                                            	<td>${j.remark}</td>
	                                            %endif
	                                        </tr>
	                                    
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
                                            <th>Available Total</th>
                                            <th>MF Total</th>
                                            <th>Payment Total</th>
                                            <th>Charge Code</th>
                                        </tr>
                                    </tHead>
                                    <tbody>
                                        % for j in charges:
                                        <tr name="charge_${j.id}">
                                            <td class="head">${j.line_no}</td>
                                            <td>${pf(j.total)}</td>
                                            <td class="available_qty">${pf(j.ava_total)}</td>
                                            <td>${pf(j.msn_total)}</td>
                                            %if mHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <td><input class="qty numeric" type="text" name="total_${j.id}" value="${pf(j.vat_total)}"  cate='charge' ids='${j.id}'  forid="total_${j.id}_charge_1" invoice="${si.invoice_no}" Head_id='${si.id}'/></td>
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
                % if len(Other_Charges_From_vats) > 0:
                	<tr id="${mHead.ref}_tr">
                % else:
                	<tr id="${mHead.ref}_tr" style="display:none">
                % endif
                    <td class="gridInTd" colspan="100" >
                        <div class="gridInDiv">
                        <form action="/ap/update_other_charges_vat_total" method="POST" id="${mHead.ref}_update_other_charges_vat_total_si">
                          		<div class="title other_charge_tab">Other Charge</div>
  								<div class="other_charge_content" style="display:none" id="${mHead.ref}_charge" >
  								% if len(Other_Charges_From_vats) > 0:
  								% if mHead.status == const.VAT_THEAD_STATUS_NEW:
  								    <input type="submit" class="btn"  id="save_other_charge" value="Save" style="float:left;margin-right:15px;clear:none;margin-left:15px;" name="save" onclick="ajaxForm('#${mHead.ref}_update_other_charges_vat_total_si','Save Success!','${mHead.id}','${mHead.ref}',toSaveSISOCharge('#${mHead.ref}_update_other_charges_vat_total_si'),'m_pi_save')"> 
                        			<input type="submit" class="btn" value="Delete" style="clear:none;margin-left:15px;" name="delete" onclick="ajaxForm('#${mHead.ref}_update_other_charges_vat_total_si','Delete Success!','${mHead.id}','${mHead.ref}',checkSelect('#${mHead.ref}_update_other_charges_vat_total_si'),'m_pi_save')" >
  								% endif
  								  <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0">
                                    <thead class="cl3">
                                       <tr>
                                            %if mHead.status == const.VAT_THEAD_STATUS_NEW:
                                            <th width="20px" class="head"><input type="checkbox" onclick="selectAll(this)" id="selectAlls"></th>
                                            %endif
                                            <th>Line NO</th>
                                            <th class="cl3">Total</th>
                                            <th class="cl3">Available Total</th>
                                            % if mHead.head_type == const.ERP_HEAD_TYPE_MF:
                                            	<th class="cl3">MF Total</th>
                                            % else:
                                            	<th class="cl4">MF Total</th>
                                            % endif
                                            <th>Payment Total</th>
                                            <th>Chg Discount Code</th>
                                            <th>Type</th>
                                            <th>Note No</th>
                                            <th>Create Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                    % for v,k in enumerate(Other_Charges_From_vats):
                                        <tr name="other_charge_${k.id}">
                                        	%if mHead.status == const.VAT_THEAD_STATUS_NEW:
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
                                            	${pf(k.total)}
                                            </td>
                                            <td>${pf(k.ava_total)}</td>
                                            <td>${pf(k.msn_total)}</td>
                                            <td>&nbsp;
	                                            %if mHead.status == const.VAT_THEAD_STATUS_NEW:
	                                            	<input type="text" value="${pf(k.vat_total)}" name="${k.id}" class="qty numeric check_numbers" cate='other_charge' ids='${k.id}' > 
												% else:
													${pf(k.vat_total)}
												% endif
											</td>
                                            <td>
                                            ${k.charge_code}</td>
                                            <td> 
                                            %if k.type in [const.CHARGE_TYPE_PM_ERP, const.CHARGE_TYPE_SM_ERP]:
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
%if mHead.status!=const.VAT_THEAD_STATUS_CANCELLED:
<div class="clear"></div>
<div class="box3">
    <div class="title1"><div class="toggle2 toggle_right"></div>Sheet</div>
    <div class="box4" id="${mHead.ref}"><table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                    <th>MF No.</th>
                    <th>Invoice No.</th>
                    <th>PO No.</th>
                    <th>Supplier</th>
                    <th>Item</th>
                    <th>Item Desc(Chinese)</th>
                    <th>Unit</th>
                    <th>Currency</th>
                    <th>Total Amount</th>
                    <th>payment Amount</th>
                </tr>
            </thead>
            <tbody>
                % for si_infos in mHead.pi_heads:
                % for detail in si_infos.pi_details:
                % if detail.vat_total != 0:
                <tr  id="detail_${detail.id}">
                % else:
                <tr  id="detail_${detail.id}" style='display:none'>
                % endif
                    <td class="head">${detail.pi_head.m_head.ref}</td>
                    <td>${detail.invoice_no}</td>
                    <td>${detail.pi_head.po_no}&nbsp;</td>
                    <td>${detail.pi_head.supplier}</td>
                    <td>${detail.item_no}</td>
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
                    <td class="item_total" id="item_total_${detail.id}_detail">${pf(detail.item_total*(1+detail.tax_rate))}</td>
                    <td class="total_vat_total_amount" id="total_vat_total_amount_${detail.id}_payment_amount">${pf(detail.vat_total)}</td>
                </tr>
                % endfor
                % endfor
                <!-- charge list -->
 				% for u,si_infos in enumerate(mHead.pi_heads):
                % for k,detail in enumerate(si_infos.pi_details):
                % if k == 0:
                % for si in mHead.pi_heads:
                <% charges = si.find_charges(cn_charges) %>
       			% for j in charges:
       			% if detail.pi_head_id == j.pi_head_id:
       			% if j.type in [const.CHARGE_TYPE_S_MF, const.CHARGE_TYPE_S_NMF]:
	       			% if j.vat_total !=0: 
	                <tr id="charge_${j.id}">
	                % else:
	                <tr id="charge_${j.id}" style='display:none'>
	                % endif
                    <td class="head">${detail.pi_head.m_head.ref}</td>
                    <td>${detail.invoice_no}</td>
                    <td>${detail.pi_head.po_no}&nbsp;</td>
                    <td>${detail.pi_head.supplier}</td>
                    <td>&nbsp;</td>
                    <td>${j.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${detail.pi_head.currency}</td>
                    <td class="item_total" id="item_total_${j.id}_charge">${pf(j.total)}</td>
                    <td class="total_vat_total_amount" id="total_total_amount_${j.id}_charge">${pf(j.vat_total)}</td>
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
                % for c,v in enumerate(Other_Charges_From_vats):
                % if v.vat_total != 0:
                <tr id='other_charge_${v.id}'>
                % else:
                <tr id='other_charge_${v.id}' style='display:none'>
                % endif
                	<% 
                    if v.vat_total ==None:
                    	vat_total = v.total
                    else:
                    	vat_total = v.vat_total
                    pihead = v.m_head.pi_heads
                    pihead = pihead[0] if len(pihead)>0 else None
                    %>
                    <td class="head">${v.m_head.ref}</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>&nbsp;</td>
                    <td>${v.charge_code}</td>
                    <td>&nbsp;</td>
                    <td>${pihead.currency}</td>
                    <td class="item_total" id="item_total_${v.id}_other_charge">${pf(v.total)}</td>
                    <td class="total_vat_total_amount" id="${v.id}_other_charge">${pf(v.vat_total)}</td>
					</td>
                </tr>
                % endfor 
                <!-- other charge list end   -->
                <!-- statistics start -->
	            <tr>
	                <td class="head">&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>Total</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
	                <td>&nbsp;</td>
					<td class="item_total_all">&nbsp;</td>
					<td class="total_vat_total_amount_all" >&nbsp;</td>
	            </tr>
                <!-- statistics end   -->
            </tbody>
        </table>
    </div>
</div>
%endif
%endif
<h1 id='test'></h1>
 
 