<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf
%>
<script>
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
    <li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">SO</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search SO Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div id="toolbar">
                                <div class="l">
							    <form action="/ar/save_all_to_thead" id="_form" method="post">
							        <input type="hidden" name="ids" id="ids"/>
							        <input type="hidden" name="customer_code" id="hid_customer_code"/>
							        <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SO}"/>
							        <input type="submit" style="display:none">
							    	<input type="submit" class="btn" value="Save as MSO" id="btn_save_as_msi" onclick="ajaxForm('#_form','Save Success!','0','0',saveAllToThead(),'save')" />
							    </form>
                                </div>
                                <div class="r" style="font-weight:bold" id="topSpace">
                                	 <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr id="theadObj">
                        <th class="head" style="width:20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
                        <th>SO No</th>
                        <th>Qty</th>
                        <th>Invoiced Qty</th>
                        <th class="cl3">Available Qty</th>
                        <th class="cl3">MSO Qty</th>
                        <th class="cl4">MCN Qty</th>
                        <th>Charge</th>
                        <th class="cl3">Available Charge</th>
                        <th class="cl3">MSO Charge</th>
                        <th class="cl4">MCN Charge</th>
                        <th>Status</th>
                        <th>Cust Code</th>
                        <th>Cust Name</th>
                        <th>Cust Po No</th>
                        <th>Order Amt</th>
                        <th>Item Amt</th>
                        <th>Curr.</th>
                        <th>AE</th>
                        <th>Dept.</th>
                        <th>Create Time</th>
                    </tr>
                </thead>
                <tbody>
                    % for i in collections:
                    <tr>
                        <td class="head"><input type="checkbox" class="cboxClass" value="${i.sales_contract_no}$${i.customer_code}" onclick="selectOne()" /></td>
                        <td title="SO No"><a href="javascript:void(0)" onclick="viewSO('${i.sales_contract_no}')">${i.sales_contract_no}</a></td>
                        <td title="Qty">${i.qty}</td>
                        <td title="Invoiced Qty">${i.invoiced_qty}</td>
                        <td title="Available Qty">${i.available_qty}</td>
                        <td title="MSO Qty">${i.mso_qty}</td>
                        <td title="MCN Qty">${i.mcn_qty}</td>
                        <td title="Charge">${pf(i.charge_total)}</td>
                        <td title="Available Charge">${pf(i.available_total)}</td>
                        <td title="MSO Charge">${pf(i.mso_total)}</td>
                        <td title="MCN Charge">${pf(i.mcn_total)}</td>
                        <td title="Status">${i.status}</td>
                        <td title="Cust Code">${i.customer_code}</td>
                        <td class="fcn" title="Cust Name">${i.customer_short_name}</td>
                        <td title="Cust Po No">${b(i.cust_po_no)|n}</td>
                        <td title="Order Amt">${pf(i.order_amt)}</td>
                        <td title="Item Amt">${pf(i.item_amt)}</td>
                        <td title="Curr.">${i.currency}</td>
                        <td title="AE">${i.ae}</td>
                        <td title="Dept.">${i.order_dept}</td>
                        <td title="Create Time">${pd(i.create_date)}</td>
                    </tr>
                    % endfor
                     </tbody>
                <tfoot>
         			<tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace"> <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a></td></tr>
                </tfoot>
            </table>
        </div>
    </div>
</div>
<table class="gridTableb" cellpadding="0" cellspacing="0" border="0" id="scroll" style="position:absolute;left:7px;top:0px;display:none">
    <thead>
        <tr id="scrollObj">
            <th class="head" style="width:20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
            <th>SO No</th>
            <th>Qty</th>
            <th>Invoiced Qty</th>
            <th class="cl3">Available Qty</th>
            <th class="cl3">MSO Qty</th>
            <th class="cl4">MCN Qty</th>
            <th>Charge</th>
            <th class="cl3">Available Charge</th>
            <th class="cl3">MSO Charge</th>
            <th class="cl4">MCN Charge</th>
            <th>Status</th>
            <th>Cust Code</th>
            <th>Cust Name</th>
            <th>Cust Po No</th>
            <th>Order Amt</th>
            <th>Item Amt</th>
            <th>Curr.</th>
            <th>AE</th>
            <th>Dept.</th>
            <th>Create Time</th>
        </tr>
    </thead>
</table>