<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf
%>
<script type="text/javascript">
		initTr();
		disableBtn('#btn_save_as_msi_customer', true);
	    var resetBtn = function(){
	        var vals = getCboxArr2('#customer_list');
	        var btnValidate = vals.length ? true : false;
	        var ids = [];
	        for(var i=0;i<vals.length;i++){
	            ids.push(vals[i].split('$')[1])
	        }
	        if(btnValidate){
	            disableBtn('#btn_save_as_msi_customer', false)
	            $('#ids_customer').val(ids.join(','))
	        }else{
	            disableBtn('#btn_save_as_msi_customer', true)
	        }
	    }

</script>
<ul class="ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all" >
    <li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">Customer</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search Customer Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
								    <form action="/ar/save_all_to_thead_by_customer" id="_form_customer" method="post">
								        <input type="hidden" name="ids" id="ids_customer"/>
								      	<input type="hidden" name="date_from" value="${kw.get('date_from')}"/>
								        <input type="hidden" name="date_to" value="${kw.get('date_to')}"/>
								        %if kw.get('type') == const.SEARCH_TYPE_GROUP_SI:
								        	<input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SI}"/>
								    		<input type="submit" class="btn" value="Save as MSI" id="btn_save_as_msi_customer" onclick="ajaxForm('#_form_customer','Save Success!','0','0',returnTrue(), 'save_customer')" />
								    	%else:
								    		<input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_SO}"/>
								    		<input type="submit" class="btn" value="Save as MSO" id="btn_save_as_msi_customer" onclick="ajaxForm('#_form_customer','Save Success!','0','0',returnTrue(), 'save_customer')" />
								    	%endif
								    	<input type="submit" style="display:none">
								    </form>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr id="theadObj">
			           	<th class="head" style="width:20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
			            <th>Customer Code</th>
			            <th>Customer Name</th>
			            <th>Adress</th>
                    </tr>
                </thead>
                <tbody id="customer_list">
                    % for i in collections:
                    <tr>
                        <td class="head"><input type="checkbox" class="cboxClass" value="${i.cust_code}$${i.cust_code}" onclick="selectOne()" /></td>
                        <td title="Customer Code"><a href="javascript:void(0)" onclick="javascript:viewCustomer('${i.cust_code}', '${kw.get('type')}','${kw.get('date_from')}', '${kw.get('date_to')}')">${i.cust_code}</a></td>
                        <td title="Customer Name">${i.cust_short_name}</td>
                        <td title="Adress">${i.address_1}</td>
                    </tr>
                    % endfor
                    </tbody>
            </table>
        </div>
    </div>
</div>
 