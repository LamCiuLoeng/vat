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
    <li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">Statement</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search Statement Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
								    <form action="/ap/save_to_phead_statement" id="_form" method="post">
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
                        <th>Ref</th>
                        <th style='display:none'>MPI Ref</th>
                        <th>Name</th>
                        <th>PI Amount</th>
                        <th>DN Amount</th>
                        <th>Created By</th>
                        <th>Create Date</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody>
                    % for i in collections:
                    <tr>
                        <td class="head"><input type="checkbox" class="cboxClass" value="${i.id}$${i.ref}" onclick="selectOne()" /></td>
                        <td><a href="javascript:void(0)" onclick="viewStatement('${i.id}','${i.ref}')">${i.ref}</a></td>
                        <td  style='display:none'><a href="javascript:viewPhead('${i.p_head_id}', '${i.p_head.ref if i.p_head_id else ''}')">${i.p_head.ref if i.p_head_id else ' '}</a></td>
                        <td>${i.upload_name}&nbsp;</td>
                        <td>${i.pi_amount}</td>
                        <td>${i.dn_amount}</td>
                        <td title="Created By" >${i.create_by}</td>
                        <td title="Create Date" >${pd(i.create_time)|n}</td>
                        <td title="Create Date" >${i.status}</td>
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
            <th>Ref</th>
            <th style='display:none'>MPI Ref</th>
            <th>Name</th>
            <th>PI Amount</th>
            <th>DN Amount</th>
            <th>Created By</th>
            <th>Create Date</th>
            <th>Status</th>
        </tr>
    </thead>
</table>