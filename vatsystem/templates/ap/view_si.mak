<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf,pt,get_cn_total
%>
%if flag==1:
<script>
    showError("Error");
</script>
%else:
	<script>
	$.fx.speeds._default = 1000;
	$(function() {
		$( "#dialog_${si.purchase_invoice_no}" ).dialog({
			autoOpen: false,
			show: "blind",
			hide: "explode",
			minWidth:'1200', 
			width:800,
			title:'SN'
		});

		$( "#showCN" ).click(function() {
			$( "#dialog_${si.purchase_invoice_no}" ).dialog( "open" );
			return false;
		});
	});
	</script>
<style type="text/css">
<!-- 
	.ui-dialog{width:800px;}
-->
</style>
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>PI Information</div>
    <div>
    <div class="toolbar">
    % if type == 0 or type == 1:
    	<div style="color:#ff0000;font-weight:blod;line-height:20px;height:20px;border:1px solid #e1e1e1;width:480px"><img src="/images/icon_alert.gif" style="width:13px;height:13px;margin-top:3px;">
			${const.TAX_RATE_MESSAGE}
		</div>
    % endif
    %if len(cn_details)>0:
    <input type="button"  value="SN" class="btn" id='showCN'>
    <!-- display cn charge -->
    <div id="dialog_${si.purchase_invoice_no}" class="none" style="width:800px;">
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
            </pHead>
            <tbody>
                % for u,i in enumerate(cn_details):
                <tr>
                	<td class="head">${u+1}</td>
                	<td>${i.item_no }</td>
                    <td >${i.pi_no}</td>
                    <td>${i.note_no} </td>
                    <td>${i.po_no}</td>
                    <td>${i.note_qty}</td>
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
                    <td>${v.chg_discount_code}</td>
                    <td>${v.percentage} &nbsp;</td>
                    <td>${v.amount} &nbsp;</td>
                    <td>${v.total}</td>
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
    %endif
    </div>
        <ul>
            <li class="li1">Invoice NO:</li>
            <li class="li2">${si.purchase_invoice_no}</li>
            <li class="li1">PO NO:</li>
            <li class="li2">
            % if len(collections)>0:
            	${collections[0].po_no}
            % endif
            </li>
        </ul><ul>
            <li class="li1">Department:</li>
            <li class="li2">${si.department}</li>
            <li class="li1">supplier:</li>
            <li class="li2">${si.supplier}</li>
        </ul><ul>
            <li class="li1">supplier Name:</li>
            <li class="li2 fcn" >${si.supplier_short_name}</li>
 			<li class="li1">Status:</li>
            <li class="li2" >${si.status}</li>
        </ul><ul>
            <li class="li1">Currency:</li>
            <li class="li2">${si.currency}</li>
            <li class="li1">Order Amount:</li>
            <li class="li2">${pf(si.order_amt)}</li>
        </ul><ul>
            <li class="li1">Item Amount:</li>
            <li class="li2">${pf(si.item_amt)}</li>
            <li class="li1">Create Time:</li>
            <li class="li2">${pt(si.create_date)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>
%if len(collections) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>PI Detail</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>Line NO</th>
                    <th>Item NO</th>
                    <th>Qty</th>
                    <th >SN Qty</th>
                    <th class="cl3">Available Qty</th>
                    <th class="cl3">MPI Qty</th>
                    <th class="cl4">MSN Qty</th>
                    <th>Unit</th>
                    <th>Unit Price</th>
                    <th>Description</th>
                </tr>
            </thead>
            <tbody>
                % for i in collections:
                <tr>
                    <td class="head">${i.line_no}</td>
                    <td>${i.item_no}</td>
                    <td>${pi(i.qty)}</td>
                    <td>${pi(i.cn_qty)}</td>
                    <td>${pi(i.ava_qty)}</td>
                    <td>${pi(i.mpi_qty)}</td>
                    <td>${pi(i.msn_qty)}</td>
                    <td>${i.unit}</td>
                    <td>${i.unit_price}</td>
                    <td>${i.item_desc}</td>
                </tr>
             % endfor
            </tbody>
        </table>
    </div>
</div>
%endif

 
%if len(si_charges) > 0 or len(ri_charges):
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>PI Charge</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>Line NO</th>
                    <th>Charge Code</th>
                    <th>Total</th>
                    <th>SN Total</th>
                    <th class="cl3">Available Total</th>
                    <th class="cl3">MPI Total</th>
                    <th class="cl4">MSN Total</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
                %if len(si_charges) > 0:
                %for i in si_charges:
                <tr>
                    <td class="head">${i.line_no}</td>
                    <td>${i.charge_code}</td>
                    <td>${pf(i.total)}</td>
                    <td>${pf(i.cn_total)}</td>
                    <td>${pf(i.ava_total)}</td>
                    <td>${pf(i.mpi_total)}</td>
                    <td>${pf(i.msn_total)}</td>
                    <td>${i.type}</td>
                </tr>
                %endfor
                %endif
                <!--this is the diaplay is not cn charge-->
                %if len(ri_charges) > 0:
                %for i in ri_charges:
                <tr style="display:none">
                    <td class="head">${i.line_no}</td>
                    <td>${i.chg_discount_code}</td>
                    <td>-${pf(i.total)}</td>
                    <td> </td>
                    <td> </td>
                    <td> </td>
                    <td> </td>
                </tr>
                %endfor
                %endif
            </tbody>
        </table>
    </div>
</div>
%endif
%if len(other_charges) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>Other Charge</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>Line NO</th>
                    <th>Note NO</th>
            
                    <th>Chg Dsicount Code</th>
                    <th>Ttotal</th>
                    <th>Note Date</th>
                    <th>Remark</th>
                </tr>
            </thead>
            <tbody>
                % for u,i in enumerate(other_charges):
                <tr>
                    <td class="head">${u+1}</td>
                    <td>${i.get("note_no")}</td>
               
                    <td>
                    % if i.get("chg_discount_code"):
                    	${i.get("chg_discount_code")}
                    % else:
                    	&nbsp;
                    % endif	
                    </td>
                    <td>${i.get("total")}</td>
                    <td>${i.get("create_date")}</td>
                    <td>
                    % if i.get("remark"):
                    	${i.get("remark")}
                    % else:
                    	&nbsp;
                    % endif	
                    	</td>
                </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>
%endif
%if len(pheads) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MPI</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                    <th>Ref</th>
                    <th>VAT No</th>
                    <th>Status</th>
                    <th>supplier Code</th>
                    <th>supplier Name</th>
                    <th>VAT Date</th>
                    <th>Export Date</th>
                    <th>Create Date</th>
                </tr>
            </thead>
            <tbody>
                % for i in pheads:
                <tr>
                    <td class="head"><a href="javascript:viewPhead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
                    <td>${b(i.vat_no)|n}</td>
                    <td>${b(i.status)|n}</td>
                    <td>${b(i.supplier)|n}</td>
                    <td>${b(i.supplier_short_name)|n}</td>
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
%if len(sheads) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MSN</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl4">
                <tr>
                    <th class="head">Ref</th>
                    <th>MSI/MSO Ref</th>
                    <th>VAT No</th>
                    <th>Status</th>
                    <th>supplier Code</th>
                    <th>supplier Name</th>
                    <th>VAT Date</th>
                    <th>Export Date</th>
                    <th>Create Date</th>
                </tr>
            </thead>
            <tbody>
                % for i in sheads:
                <tr>
                    <td class="head"><a href="javascript:viewShead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
                    <td>${b(i.phead_ref)|n}</td>
                    <td>${b(i.vat_no)|n}</td>
                    <td>${b(i.status)|n}</td>
                    <td>${b(i.supplier)|n}</td>
                    <td>${b(i.supplier_short_name)|n}</td>
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
%endif