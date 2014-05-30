<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b,pd,pi,pf
%>
<script type="text/javascript">
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
    <li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">Charge</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search Charge Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
								    <form action="/cost/ajax_add_new_charge" id="_form" method="post">
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
			        	<th class="head"><input type="checkbox" onclick="selectAll(this)" value="0"></th>
			        	<th>CST Ref</th>
			            <th>Line NO</th>
			            <th>PO NO</th>
			            <th>CST Total</th>
			            <th>PI NO</th>
			            <th class="cl3">PI Total</th> 
			            <th class="cl3">Available PI Total</th> 
			            <th>Charge Code</th>
			            <th>Type</th> 
                    </tr>
                </thead>
                <tbody>
                     % for k in collections:
                     % if hasattr(k, 'variance_type'):
                     <tr id="tr1_" style="background-color:red">
                     % else:
                     <tr id="tr1_">
                     % endif
			            <td class="head">
							<input type="checkbox" class="cboxClass" value="${k.o_head_id}_${k.pi_no}_${k.line_no}"  name="checkd" onclick="selectOne()">
			        	</td>
			        	<td class="head"><a href="javascript:viewOhead('${k.cst_id}', '${k.cst_ref}')">${k.cst_ref}</a></td>
			            <td class="head">${k.line_no}</td>
			            <td title=">PO NO">${k.po_no}&nbsp;</td>
			            <td title="PO Total">${k.po_total}&nbsp;</td>
			            <td title="PI NO">${k.pi_no}&nbsp;</td>
			            <td title="Total">${k.total}&nbsp;</td> 
			            <td title="Total">${k.ava_total}&nbsp;</td> 
			            <td title="Charge Code">${k.charge_code}</td>
			            <td title="Type"> PI </td> 
                    </tr>
                    %endfor
                    </tbody>
                    <tfoot>
             			<tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace"> <a href="/cost?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a></td></tr>
                    </tfoot>
            </table>
        </div>
    </div>
</div>

<table class="gridTableb" cellpadding="0" cellspacing="0" border="0" id="scroll" style="position:absolute;left:7px;top:0px;display:none">
    <thead>
        <tr id="scrollObj">
	    	<th class="head"><input type="checkbox" onclick="selectAllDetail(this,'relation_charge')" value="0"></th>
	        <th>Line NO</th>
	        <th>PO NO</th>
	        <th>PO Total</th>
	        <th>PI NO</th>
	        <th class="cl3">Total</th> 
	        <th>Charge Code</th>
	        <th>Type</th> 
        </tr>
    </thead>
</table>