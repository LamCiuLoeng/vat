<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf
%>
<script type="text/javascript">
		initTr();
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
    <li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">SI</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search SI Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
								    <form action="/ar/save_all_to_thead" id="_form" method="post">
								        <input type="hidden" name="ids" id="ids"/>
								        <input type="hidden" name="customer_code" id="hid_customer_code"/>
								        <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SI}"/>
								    	<input type="submit" class="btn" value="Save as MSI" id="btn_save_as_msi" onclick="ajaxForm('#_form','Save Success!','0','0',saveAllToThead(),'save')" />
								    	<input type="submit" style="display:none">
								    </form>
                                </div>
                                %if kw.get('type') != const.SEARCH_TYPE_GROUP_SI:
                                <div class="r" style="font-weight:bold" id="topSpace">
                                	 <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
                                </div>
                                %endif
                            </div>
                        </td>
                    </tr>
                    <tr id="theadObj">
                        <th class="head" style="width:20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
                        <th>Invoice NO</th>
                        <th>SO No</th>
                        <th>Qty</th>
                        <th>CN Qty</th>
                        <th class="cl3">Available Qty</th>
                        <th class="cl3">MSI Qty</th>
                        <th class="cl3">MSO Qty</th>
                        <th class="cl4">MCN(MSO) Qty</th>
                        <th class="cl4">MCN Qty</th>
                        <th>Charge</th>
                        <th>CN Charge</th>
                        <th class="cl3">Available Charge</th>
                        <th class="cl3">MSI Charge </th>
                        <th class="cl4">MCN Charge</th>
                        <th>Status</th>
                        <th>Cust Code</th>
                        <th>Cust Name</th>
                        <th>Order Amt</th>
                        <th>Item Amt</th>
                        <th>Curr.</th>
                        <th>SO Sales Contact</th>
                        <th>Dept.</th>
                        <th>Create Time</th>
                    </tr>
                </thead>
                <tbody>
                    % for i in collections:
                    <tr>
                        <td class="head"><input type="checkbox" class="cboxClass" value="${i.invoice_no}$${i.customer}" onclick="selectOne()" /></td>
                        <td title="Invoice NO"><a href="javascript:void(0)" onclick="viewSI('${i.invoice_no}')">${i.invoice_no}</a></td>
                        <td title="SO No"><a href="javascript:void(0)" onclick="viewSO('${i.sc_no}')">${i.sc_no}</a></td>
                        <td title="Qty">${i.qty}</td>
                        <td title="CN Qty">${i.ri_qty}</td>
                        <td title="Available Qty">${i.available_qty}</td>
                        <td title="MSI Qty">${i.msi_qty}</td>
                        <td title="MSI Qty">${i.mso_qty}</td>
                        <td title="MSI Qty">${i.moc_qty}</td>
                        <td title="MCN Qty">${i.mcn_qty}</td>
                        <td title="Charge">${pf(i.charge_total)}</td>
                        <td title="CN Charge">${pf(i.ri_total)}</td>
                        <td title="Available Charge">${pf(i.available_total)}</td>
                        <td title="MSI Charge">${pf(i.msi_total)}</td>
                        <td title="MCN Charge">${pf(i.mcn_total)}</td>
                        <td title="Status">${i.status}</td>
                        <td title="Cust Code">${i.customer}</td>
                        <td class="fcn" title="Cust Name">${i.customer_short_name}</td>
                        <td title="Order Amt">${pf(i.order_amt)}</td>
                        <td title="Item Amt">${pf(i.item_amt)}</td>
                        <td title="Curr.">${i.currency}</td>
                        <td title="SO Sales Contact">${i.so_sales_contact}</td>
                        <td title="Dept.">${i.department}</td>
                        <td title="Create Time">${pd(i.create_date)}</td>
                    </tr>
                    % endfor
                    </tbody>
                    %if kw.get('type') != const.SEARCH_TYPE_GROUP_SI:
                    <tfoot>
             			<tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace"> <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a></td></tr>
                    </tfoot>
                    %endif
            </table>
        </div>
    </div>
</div>

<table class="gridTableb" cellpadding="0" cellspacing="0" border="0" id="scroll" style="position:absolute;left:7px;top:0px;display:none">
    <thead>
        <tr id="scrollObj">
           <th class="head" style="width:20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
            <th>Invoice NO</th>
            <th>SO No</th>
            <th>Qty</th>
            <th>CN Qty</th>
            <th class="cl3">Available Qty</th>
            <th class="cl3">MSI Qty</th>
            <th class="cl3">MSO Qty</th>
            <th class="cl4">MCN(MSO) Qty</th>
            <th class="cl4">MCN Qty</th>
            <th>Charge</th>
            <th>CN Charge</th>
            <th class="cl3">Available Charge</th>
            <th class="cl3">MSI Charge </th>
            <th class="cl4">MCN Charge</th>
            <th>Status</th>
            <th>Cust Code</th>
            <th>Cust Name</th>
            <th>Order Amt</th>
            <th>Item Amt</th>
            <th>Curr.</th>
            <th>SO Sales Contact</th>
            <th>Dept.</th>
            <th>Create Time</th>
        </tr>
    </thead>
</table>