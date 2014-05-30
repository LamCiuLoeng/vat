<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pt,pi,pf
%>
%if flag==1:
<script>
    showError("");
</script>
%else:
<div class="box1">
    <div class="title1"><div class="toggle_down"></div>SO Information</div>
    <div>
        <ul> 
            <li class="li1">So No:</li>
            <li class="li2">${so.sales_contract_no}</li>
            <li class="li1">Department:</li>
            <li class="li2">${so.order_dept}</li>
        </ul><ul>
            <li class="li1">Customer:</li>
            <li class="li2">${so.customer_code}</li>
            <li class="li1">Customer Name:</li>
            <li class="li2 fcn" >${so.customer_name}</li>
        </ul><ul>
            <li class="li1">Currency:</li>
            <li class="li2">${so.currency}</li>
            <li class="li1">AE:</li>
            <li class="li2">${so.ae} </li>
        </ul><ul>
            <li class="li1">Cust Po No:</li>
            <li class="li2">${b(so.cust_po_no)|n}</li>
            <li class="li1">Order Amount:</li>
            <li class="li2">${pf(so.order_amt)}</li>
        </ul><ul>
            <li class="li1">Item Amount:</li>
            <li class="li2">${pf(so.item_amt)}</li>
            <li class="li1">Create Time:</li>
            <li class="li2">${pt(so.create_date)}</li>
        </ul>
    </div>
    <div class="clear"></div>
</div>
%if len(collections) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>SO Detail</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>Line NO</th>
                    <th>Item NO</th>
                    <th>Qty</th>
                    <th>Invoiced Qty</th>
                    <th class="cl3">Available Qty</th>
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
                    <td>${pi(i.invoiced_qty)}</td>
                    <td>${pi(i.available_qty)}</td>
                    <td>${pi(i.mso_qty)}</td>
                    <td>${pi(i.mcn_qty)}</td>
                    <td>${i.unit}</td>
                    <td>${i.unit_price}</td>
                    <td>${i.description}</td>
                </tr>
                % endfor
            </tbody>
        </table>
    </div>
</div>
%endif
%if len(so_charges) > 0:
<div class="clear"></div>
<div class="box2">
    <div class="title1"><div class="toggle_down"></div>SO Charge</div>
    <div class="box4">
        <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
            <thead>
                <tr>
                    <th>Line NO</th>
                    <th>Charge Code</th>
                    <th>Total</th>
                    <th class="cl3">Available Total</th>
                    <th class="cl3">MSO Total</th>
                    <th class="cl4">MCN Total</th>
                    <th>Type</th>
                </tr>
            </thead>
            <tbody>
                % for i in so_charges:
                <tr>
                    <td class="head">${i.line_no}</td>
                    <td>${i.charge_code}</td>
                    <td>${pf(i.total)}</td>
                    <td>${pf(i.available_total)}</td>
                    <td>${pf(i.mso_total)}</td>
                    <td>${pf(i.mcn_total)}</td>
                    <td>${i.type}</td>
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
                % for i in theads:
	                % if i.head_type == 'SO':
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
	                % endif
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
	                % if i.head_type == 'SO':
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
	                % endif
                % endfor
            </tbody>
        </table>
    </div>
</div>
%endif
%endif