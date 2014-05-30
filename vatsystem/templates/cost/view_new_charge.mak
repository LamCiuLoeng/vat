<form action='/cost/ajax_add_new_charge?id=${id}' method='post' id='add_new_charge_${id}'>
 <p><input type='submit' value='Add' class='btn' 
 	onclick="ajaxForm('#add_new_charge_${id}', 'Save Success!', '${oHead.id}', '${oHead.ref}', closeDialog('#add_new_charge_${id}'), 'cst_add_new_charge')"></p>
 					<br />
 <table class="gridTable" style="width:800px;" cellpadding="0" cellspacing="0" border="0" width="100%">
    <thead class="cl3">
       <tr>
        	<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'relation_charge_${oHead.id}')" value="0"></th>
            <th>Line NO</th>
            <th>PO NO</th>
            <th>PO Total</th>
            <th>PI NO</th>
            <th class="cl3">Total</th> 
            <th>Charge Code</th>
            <th>Type</th> 
        </tr>
    </thead>
    <tbody class="relation_charge_${oHead.id}">
    % for k in picharges:
        <tr>
        	<td class="head">
				<input type="checkbox" value="${k.pi_no}_${k.line_no}" class="dboxClass" name="checkd">
        	</td>
            <td class="head">${k.line_no}</td>
            <td>${k.po_no}&nbsp;</td>
            <td>${k.po_total}&nbsp;</td>
            <td>${k.pi_no}&nbsp;</td>
            <td>${k.total}&nbsp;</td> 
            <td>${k.charge_code}</td>
            <td> PI </td> 
        </tr>
    % endfor  
    </tbody>
</table>
</form>