<form action='/cost/ajax_add_new_pi?id=${id}' method='post' id='add_new_pi_${id}'>
 <p><input type='submit' value='Add' class='btn' 
 					onclick="ajaxForm('#add_new_pi_${id}', 'Save Success!', '${oHead.id}', '${oHead.ref}', closeDialog('#add_new_pi_${id}'), 'cst_add_new_pi')"></p>
 <br />
 <table class="gridTable" cellpadding="0" cellspacing="0" border="0" width="100%">
    <thead class='cl3'>
        <tr>
        	<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'relation_pi_')" value="0"></th>
            <th>Line NO</th>
            <th>PO NO</th>
            <th>PI NO</th>
            <th>Supplier Code</th>
            <th>Supplier Name</th>
            <th>Item NO</th>
            <th>Item Qty</th>
            <th>Unit</th>
            <th>PO Qty</th>
            <th>Qty</th>
            <th>Unit Price</th>
            <th>Amount</th>
        </tr>
    </thead>
    <tbody>
        % for i in pidetails:
        <tr class="relation_pi_">
        	<td class="head">
				<input type="checkbox" value="${i.grn_no}_${i.grn_line_no}" class="dboxClass" name="checkd">
        	</td>
            <td class="head">${i.line_no}</td>
            <td>${i.po_no}</td>
           	<td>${i.pi_no}</td>
           	<td>${i.supplier}</td>
           	<td>${i.supplier_name}</td>
            <td>${i.item_no}</td>
            <td>${i.item_qty}</td>
            <td>${i.unit}</td>
            <td>${i.po_qty}</td>
    		<td>${i.pi_qty}</td>
    	 	<td>${i.unit_price}</td>
            <td>${i.pi_total} &nbsp;</td>
        </tr>
     % endfor
    </tbody>
</table>
</form>