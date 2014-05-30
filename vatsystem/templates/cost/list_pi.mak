<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf
%>
<script type="text/javascript">
		//initTr();
		initScroll();
		disableBtn('#btn_save_as_msi', true);
	    var resetBtn = function(){
	        var vals = getCboxArr();
	        var btnValidate = vals.length ? true : false;
	        var customer_code;
	        for(var i=0;i<vals.length;i++){
	            if(!customer_code) customer_code = vals[i].split('$')[1];
	            if(i>0 && customer_code!=vals[i].split('$')[1]){
	                btnValidate=false;
	                break; 
	            }
	        }
	        if(btnValidate){
	            disableBtn('#btn_save_as_msi', false)
	            $('#hid_customer_code').val(customer_code)
	        }else{
	            disableBtn('#btn_save_as_msi', true)
	            $('#hid_customer_code').val('')
	        }
	    }
</script>
<input type="hidden" name="cust" id="cust" value="${cust}"/>
<ul class="ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all" >
    <li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">PI</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search PI Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
								    <form action="/cost/ajax_add_new_pi" id="_form" method="post">
								        <input type="hidden" name="ids" id="ids"/>
								    	<input type="submit" class="btn" value="Save to CST" id="btn_save_as_msi" onclick="ajaxForm('#_form','Save Success!','0','0',saveAllToThead(),'save_to_cost')" />
								    	<input type="submit" style="display:none">
								    </form>
                                </div>
                                <div class="r" style="font-weight:bold" id="topSpace">
                                	 <a href="/cost?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr id="theadObj">
                                        <th class="head" width="20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
                        <th>CST Ref</th>
			            <th>Line NO</th>
			            <th>PO NO</th>
			            <th>PI NO</th>
			            <th>GRN NO</th>
			            <th>GRN Line NO</th>
			            <th>Supplier Code</th>
			            <th>Supplier Name</th>
			            <th>Item NO</th>
			            <th>Item Qty</th>
			            <th>Unit</th>
			            <th>CST Qty</th>
			            <th>PI Qty</th>
			            <th>Available PI Qty</th>
			            <th>Unit Price</th>
			            <th>Amount</th>
                    </tr>
                </thead>
                <tbody>
                     % for i in collections:
                     % if hasattr(i, 'variance_type'):
                     <tr id="tr1_" style="background-color:red">
                     % else:
                     <tr id="tr1_">
                     % endif
                        <td class="head">
							<input type="checkbox" class="cboxClass"  value="${i.co_detail_id}_${i.grn_no}_${i.grn_line_no}"  onclick="selectOne()">
		        		</td>
		        		<td class="head"><a href="javascript:viewOhead('${i.cst_id}', '${i.cst_ref}')">${i.cst_ref}</a></td>
			            <td class="head">${i.line_no}</td>
			            <td title="PO NO">${i.po_no}</td>
			           	<td title="PI NO">${i.pi_no}</td>
			           	<td title="Grn NO">${i.grn_no}</td>
			           	<td title="Grn Line NO">${i.grn_line_no}</td>
			           	<td title="Supplier Code">${i.supplier}</td>
			           	<td title="Supplier Name">${i.supplier_name}</td>
			            <td title="Item NO">${i.item_no}</td>
			            <td title="Item Qty">${i.item_qty}</td>
			            <td title="Unit">${i.unit}</td>
			            <td title="PO Qty">${i.po_qty}</td>
			    		<td title="PI Qty">${i.pi_qty}</td>
			    		<td title="Available PI Qty">${i.ava_pi_qty}</td>
			    	 	<td title="Unit Price">${i.unit_price}</td>
			            <td title="Amount">${i.pi_total} &nbsp;</td>
                    </tr>
                    %endfor
                    </tbody>
                    <tfoot>
             			<tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace">
             				 <a href="/cost?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
             				 </td></tr>
                    </tfoot>
            </table>
        </div>
    </div>
</div>

<table class="gridTableb" cellpadding="0" cellspacing="0" border="0" id="scroll" style="position:absolute;left:7px;top:0px;display:none">
    <thead>
        <tr id="scrollObj">
	     	<th class="head" width="20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
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
</table>