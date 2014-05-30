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
	// increase the default animation speed to exaggerate the effect
	$.fx.speeds._default = 1000;
	$(function() {
		$( "#dialog" ).dialog({
			autoOpen: false,
			show: "blind",
			hide: "explode",
			minWidth:'1200', 
			width:800,
			title:'CN'
		});

		$( "#showCN" ).click(function() {
			$( "#dialog" ).dialog( "open" );
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
    <div class="title1"><div class="toggle_down"></div>SI Information</div>
    <div>
    <div class="toolbar">
    %if len(cn_details)>0:
    <input type="button"  value="CN" class="btn" id='showCN'>
    <!-- display cn charge -->
    <div id="dialog" class="none" style="width:800px;">
	<div class="box2">
    <div class="title1" style='text-align:left'><div class="toggle_down"></div>CN Detail</div>
    <div class="box4">
        <table cellspacing="0" cellpadding="0" border="0" class="gridTable">
            <thead class="cl3">
                <tr>
                    <th class="head">Invoice NO</th>
                    <th>Item No</th>
                    <th>Note No</th>
                    <th>SC No</th>
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
                    <td class="head">${i.invoice_no}</td>
                    <td>${i.item_no }</td>
                    <td>${i.note_no} </td>
                    <td>${i.sc_no}</td>
                    <td>${int(i.note_qty)}</td>
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
    <div class="title1"><div class="toggle_down"></div>CN Charge</div>
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
                    <td>${v.chg_discount_code.decode("utf-8") }</td>
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
            <li class="li2">${si.invoice_no}</li>
            <li class="li1">Sales Contract No:</li>
            <li class="li2">${si.sc_no}</li>
        </ul><ul>
            <li class="li1">Department:</li>
            <li class="li2">${si.department}</li>
            <li class="li1">Customer:</li>
            <li class="li2">${si.customer}</li>
        </ul><ul>
            <li class="li1">Customer Name:</li>
            <li class="li2 fcn" >${si.customer_short_name}</li>
            <li class="li1">SO Sales Contact:</li>
            <li class="li2">${si.so_sales_contact}</li>
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
    <div class="title1"><div class="toggle_down"></div>SI Detail</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>Line NO</th>
                    <th>Item NO</th>
                    <th>Qty</th>
                    <th >CN Qty</th>
                    <th class="cl3">Available Qty</th>
                    <th class="cl3">MSI Qty</th>
                    <th class="cl3">MSO Qty</th>
                    <th class="cl4">MCN Qty</th>
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
                    <td>${pi(i.ri_qty)}</td>
                    <td>${pi(i.available_qty)}</td>
                    <td>${pi(i.msi_qty)}</td>
                    <td>${pi(i.mso_qty)}</td>
                    <td>${pi(i.mcn_qty)}</td>
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
    <div class="title1"><div class="toggle_down"></div>SI Charge</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>Line NO</th>
                    <th>Charge Code</th>
                    <th>Total</th>
                    <th>CN Total</th>
                    <th class="cl3">Available Total</th>
                    <th class="cl3">MSI Total</th>
                    <th class="cl4">MCN Total</th>
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
                    <td>${pf(get_cn_total(i.invoice_no,i.charge_code))}</td>
                    <td>${pf(i.available_total)}</td>
                    <td>${pf(i.msi_total)}</td>
                    <td>${pf(i.mcn_total)}</td>
                    <td>${i.type}</td>
                </tr>
                %endfor
                %endif
                <!--this is the diaplay is not cn charge-->
                %if len(ri_charges) > 0:
                %for i in ri_charges:
                <tr style="display:none">
                    <td class="head">${i.line_no}</td>
                    <td>${i.chg_discount_code.decode("utf-8")}</td>
                    <td>-${pf(i.total)}</td>
                    <td>${pf(i.available_total)}</td>
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
                    <th>Note Type</th>
                    <th>Status</th>
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
                    <td>${i.note_no}</td>
                    <td>${i.note_type}</td>
                    <td>${i.status}</td>
                    <td>${i.chg_discount_code}</td>
                    <td>${i.total}</td>
                    <td>${i.create_date}</td>
                    <td>${i.remark}&nbsp;</td>
                </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>
%endif
%if len(theads) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MSI</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl3">
                <tr>
                    <th>Ref</th>
                    <th>VAT No</th>
                    <th>Status</th>
                    <th>Customer Code</th>
                    <th>Customer Name</th>
                    <th>VAT Date</th>
                    <th>Export Date</th>
                    <th>Create Date</th>
                </tr>
            </thead>
            <tbody>
                % for i in theads:
                <tr>
                    <td class="head"><a href="javascript:viewThead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
                    <td>${b(i.vat_no)|n}</td>
                    <td>${b(i.status)|n}</td>
                    <td>${b(i.customer_code)|n}</td>
                    <td>${b(i.customer_short_name)|n}</td>
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
%if len(cheads) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MCN</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead class="cl4">
                <tr>
                    <th class="head">Ref</th>
                    <th>MSI/MSO Ref</th>
                    <th>VAT No</th>
                    <th>Status</th>
                    <th>Customer Code</th>
                    <th>Customer Name</th>
                    <th>VAT Date</th>
                    <th>Export Date</th>
                    <th>Create Date</th>
                </tr>
            </thead>
            <tbody>
                % for i in cheads:
                <tr>
                    <td class="head"><a href="javascript:viewChead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
                    <td>${b(i.thead_ref)|n}</td>
                    <td>${b(i.vat_no)|n}</td>
                    <td>${b(i.status)|n}</td>
                    <td>${b(i.customer_code)|n}</td>
                    <td>${b(i.customer_short_name)|n}</td>
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
%if mso:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>MSO</div>
    <div class="box4">
		<table class="gridTable" cellpadding="0" cellspacing="0" border="0">
		            <thead class="cl3">
		                <tr>
		                    <th>Ref</th>
		                    <th>VAT No</th>
		                    <th>Status</th>
		                    <th>Customer Code</th>
		                    <th>Customer Name</th>
		                    <th>VAT Date</th>
		                    <th>Export Date</th>
		                    <th>Create Date</th>
		                </tr>
		            </thead>
		            <tbody>
		                
		                <tr>
		                    <td class="head"><a href="javascript:viewThead('${mso.id}', '${mso.ref}')">${b(mso.ref)|n}</a></td>
		                    <td>${b(mso.vat_no)|n}</td>
		                    <td>${b(mso.status)|n}</td>
		                    <td>${b(mso.customer_code)|n}</td>
		                    <td>${b(mso.customer_short_name)|n}</td>
		                    <td>${pd(mso.vat_date)|n}</td>
		                    <td>${pd(mso.export_time)|n}</td>
		                    <td>${pd(mso.create_time)|n}</td>
		                </tr>
		               
		            </tbody>
		</table>
    </div>
</div>
%endif
%endif