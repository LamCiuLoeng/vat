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
	            if(i>0){
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
    <li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">MSI/MSO</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search MSI/MSO Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
								    <form action="/cost/save_to_othead" id="_form" method="post">
								        <input type="hidden" name="ids" id="ids"/>
								        <input type="hidden" name="customer_code" id="hid_customer_code"/>
								        <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_CST}"/>
								    	<input type="submit" class="btn" value="Save as CST" id="btn_save_as_msi" onclick="ajaxForm('#_form','Save Success!','0','0',saveAllToThead(),'save_to_cost')" />
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
                        <th class="head" width="20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
                        <th>Ref</th>
                        <th>VAT No</th>
                        <th>Status</th>
                        <th>Customer Code</th>
                        <th>Customer Name</th>
                        <th>VAT Date</th>
                        <th>Export Date</th>
                        <th>Created By</th>
                        <th>Create Date</th>
                       	<th>Remark</th>
                    </tr>
                </thead>
                <tbody>
                     % for i in collections:
                    <tr id="tr1_${i.id}">
                        <td class="head" width="20px"><input type="checkbox" class="cboxClass" value="${i.id}$${b(i.customer_code)|n}" onclick="selectOne()" /></td>
                        <td title="Ref"><a href="javascript:viewThead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
                        <td title="VAT No" id="vat_no_${i.id}" class="vat_no">${b(i.vat_no)|n}</td>
                        <td title="Status" class="trStatus">${b(i.status)|n}</td>
                        <td title="Customer Code" >${b(i.customer_code)|n}</td>
                        <td title="Customer Name" class="fcn">${b(i.customer_short_name)|n}</td>
                        <td title="VAT Date" class="vatDate">${pd(i.vat_date)|n}</td>
                        <td title="Export Date" >${pd(i.export_time)|n}</td>
                        <td title="Created By" >${i.create_by}</td>
                        <td title="Create Date" >${pd(i.create_time)|n}</td>
                        <td title="Remark" class="trRemark">&nbsp;
                        	%if i.remark:
                        		<input type='text' value='${i.remark}'>
                        	%else:
                        		%if i.status == 'Cancelled' or i.status == 'Posted':
                        			&nbsp;
                        		%else:
                        			<input type='text' name='remark-${i.id}'>
                        		%endif
                        	%endif
                        	</td>
                    </tr>
                    %endfor
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
		    <th class="head" width="20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
		    <th>Ref</th>
		    <th>VAT No</th>
		    <th>Status</th>
		    <th>Customer Code</th>
		    <th>Customer Name</th>
		    <th>VAT Date</th>
		    <th>Export Date</th>
		    <th>Created By</th>
		    <th>Create Date</th>
		   	<th>Remark</th>
        </tr>
    </thead>
</table>