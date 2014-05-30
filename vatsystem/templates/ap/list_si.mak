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
	        var supplier_code;
	        for(var i=0;i<vals.length;i++){
	            if(!supplier_code) supplier_code = vals[i].split('$')[1];
	            if(i>0 && supplier_code!=vals[i].split('$')[1]){
	                btnValidate=false;
	                break; 
	            }
	        }
	        if(btnValidate){
	            disableBtn('#btn_save_as_msi', false)
	            $('#hid_supplier_code').val(supplier_code)
	        }else{
	            disableBtn('#btn_save_as_msi', true)
	            $('#hid_supplier_code').val('')
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
								    <form action="/ap/save_all_to_phead" id="_form" method="post">
								        <input type="hidden" name="ids" id="ids"/>
								        <input type="hidden" name="supplier" id="hid_customer_code"/>
								        <input type="hidden" name="head_type" value="${const.CHARGE_TYPE_P_PI}"/>
								    	<input type="submit" class="btn" value="Save as MPI" id="btn_save_as_msi" onclick="ajaxForm('#_form','Save Success!','0','0',saveAllToThead(),'save')" />
								    	<input type="submit" style="display:none">
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
                        <th>Invoice NO</th>
                        <th>PO NO</th>
                        <th>Qty</th>
                        <th>SN Qty</th>
                        <th class="cl3">Available Qty</th>
                        <th class="cl3">MPI Qty</th>
                        <th class="cl4">MSN Qty</th>
                        <th>Charge</th>
                        <th>SN Charge</th>
                        <th class="cl3">Available Charge</th>
                        <th class="cl3">MPI Charge </th>
                        <th class="cl4">MSN Charge</th>
                        <th>Status</th>
                        <th>Supplier</th>
                        <th>Supplier Name</th>
                        <th>Order Amt</th>
                        <th>Item Amt</th>
                        <th>Curr.</th>
                        <th>Dept.</th>
                        <th>Create Time</th>
                    </tr>
                </thead>
                <tbody>
                    % for i in collections:
                    <tr>
                        <td class="head"><input type="checkbox" class="cboxClass" value="${i.purchase_invoice_no}$${i.supplier}" onclick="selectOne()" /></td>
                        <td><a href="javascript:void(0)" onclick="viewPI('${i.purchase_invoice_no}')">${i.purchase_invoice_no}</a></td>
                        <td>${i.po_no}</td>
                        <td>${pi(i.qty)}</td>
                        <td>${pi(i.ri_qty)}</td>
                        <td>${pi(i.available_qty)}</td>
                        <td>${pi(i.mpi_qty)}</td>
                        <td>${pi(i.mcn_qty)}</td>
                        <td>${pf(i.charge_total)}</td>
                        <td>${pf(i.ri_total)}</td>
                        <td>${pf(i.available_total)}</td>
                        <td>${pf(i.mpi_total)}</td>
                        <td>${pf(i.mcn_total)}</td>
                        <td>${i.status}</td>
                        <td>${i.supplier}</td>
                        <td class="fcn">${i.supplier_short_name}</td>
                        <td>${pf(i.order_amt)}</td>
                        <td>${pf(i.item_amt)}</td>
                        <td>${i.currency}</td>
                        <td>${i.department}</td>
                        <td>${pd(i.create_date)}</td>
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
        <th>Invoice NO</th>
        <th>PO NO</th>
        <th>Qty</th>
        <th>SN Qty</th>
        <th class="cl3">Available Qty</th>
        <th class="cl3">MPI Qty</th>
        <th class="cl4">MSN Qty</th>
        <th>Charge</th>
        <th>SN Charge</th>
        <th class="cl3">Available Charge</th>
        <th class="cl3">MPI Charge </th>
        <th class="cl4">MSN Charge</th>
        <th>Status</th>
        <th>Supplier</th>
        <th>Supplier Name</th>
        <th>Order Amt</th>
        <th>Item Amt</th>
        <th>Curr.</th>
        <th>Dept.</th>
        <th>Create Time</th>
        </tr>
    </thead>
</table>