<%
from vatsystem.util import const
from vatsystem.util.mako_filter import b,pd
%>
<script>
	initTr();
	initDate();
	initScroll();
	disableBtn(['.btn_set_vat_info','.btn_to_new','.btn_to_confirm','.btn_to_reserve','.btn_to_post','.btn_to_cancel'], true)
    var resetBtn = function(){
        var vals = getCboxArr();
        var btnValidate = vals.length ? true : false;
        var status;
        var vat_nos = [];
        for(var i=0;i<vals.length;i++){
            status=vals[i].split('-')[0]
            var id=vals[i].split('-')[1]
            vat_nos.push($('#vat_no_'+id).html());
            if(i>0 && vals[i-1].split('-')[0]!=status){
                btnValidate=false; 
                status='';
                break;
            }
        }
        disableBtn(['.btn_set_vat_info','.btn_to_new','.btn_to_confirm','.btn_to_reserve','.btn_to_post','.btn_to_cancel'], true)
        if(btnValidate){
            if(status=='${const.VAT_CHEAD_STATUS_NEW}') disableBtn(['.btn_to_reserve','.btn_to_cancel'], false)
            else if(status=='${const.VAT_CHEAD_STATUS_RESERVE}'){
                var vatNoValidate = true;
                for(var i=0;i<vat_nos.length;i++){
                    if(vat_nos[i]=='&nbsp;'){
                        vatNoValidate = false;
                        break;
                    }
                }
                if(vatNoValidate) disableBtn(['.btn_set_vat_info','.btn_to_confirm','.btn_to_new','.btn_to_cancel'], false)
                else disableBtn(['.btn_set_vat_info','.btn_to_new','.btn_to_cancel'], false)
            }
            else if(status=='${const.VAT_CHEAD_STATUS_CONFIRMED}') disableBtn(['.btn_to_post','.btn_to_cancel'], false)
        }
    }
    var saveStatus=function(fromStatus, toStatus, msg){
        if(!validateCbox()) return false;
        var arr = getCboxArr();
        var ids = [];
        var preStatus='';
        for(var i=0;i<arr.length;i++){
            var status = arr[i].split('-')[0];
            var id = arr[i].split('-')[1];
            /*if(fromStatus==''&&toStatus==status){
                showError("You can't change status again!");
                return [];
            }
            if(fromStatus!=''&&fromStatus!=status){
                showError(msg);
                return [];
            }*/
            ids.push(id);
            if(preStatus=='') preStatus = status;
            /*else if(status!=preStatus){
                showError('Please check, you can only submit the same status MSI/MSO')
                return [];
            }*/
    
        }
        if(ids.length>0){
            $('#ids1').val(ids.join(','));
            $('#_status').val(toStatus);
            ajaxForm('#form1','Save Success!','0','0',getCboxArr(),'saveStatus')

        }
    }
    var toNew=function(){saveStatus('${const.VAT_CHEAD_STATUS_RESERVE}', '${const.VAT_CHEAD_STATUS_NEW}', 'Only Reserve status MSI/MSO can revise!');}
    var toReserve=function(){saveStatus('${const.VAT_CHEAD_STATUS_NEW}', '${const.VAT_CHEAD_STATUS_RESERVE}', 'Only New status MSI/MSO can revert to Reserve!');}
    var toConfirm=function(){saveStatus('${const.VAT_CHEAD_STATUS_RESERVE}', '${const.VAT_CHEAD_STATUS_CONFIRMED}', 'Only Reserve status MSI/MSO can revert to Confirmed');}
    var toPost=function(){saveStatus('${const.VAT_CHEAD_STATUS_CONFIRMED}', '${const.VAT_CHEAD_STATUS_POST}', 'Only Confirmed status MSI/MSO can revert to Post!');}
    var toCancel=function(){saveStatus('', '${const.VAT_CHEAD_STATUS_CANCELLED}', '');}

</script>
<input type="hidden" name="cust" id="cust" value="${cust}"/>
<ul class="ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all" >
    <li class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">CCN</a></li>
</ul>

<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="none" id="vatDialog">
        <form action="/cost/update_all_nhead_vat_info" method="post" id="form2">
            <input type="hidden" name="ids" id="ids2"/>
            <div class="box6">
                <ul>
                    <li class="li1">VAT No Range</li>
                    <li class="li2"><input type="text" name="vat_no" id="vat_no2" /></li>
                    <li class="li4">(e.g. 00000001~00000010,00000099)</li>
                </ul>
                <ul>
                    <li class="li1">VAT Date</li>
                    <li class="li2"><input type="text" class="datePickerNoImg" name="vat_date" id="vat_date2" /></li>
                    <li class="li4" >(YYYY-MM-DD)</li>
                </ul>
                <div class="clear"></div>
            </div>
            <div class="box7">
                <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form2','Save Success!','0','0',saveVatForm(),'saveVat')" />
                <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
            </div>
        </form>
    </div>
    <form action="/cost/export_all_chead" mehotd="post" id="form3">
        <input type="hidden" name="preUrl" id="preUrl3"/>
        <input type="hidden" name="ids" id="ids3"/>
    </form>
    % for v in collections:
        <form action="/report/export_cst" method="post" id="form5_${v.id}">
            <input type="hidden" name="id" value="${v.id}"/>
            <input type="hidden" name="head_type" value="${const.ERP_HEAD_TYPE_CCN}"/>
        </form>
    % endfor
    <form action="/cost/update_all_nhead_status" method="post" id="form1">
        <input type="hidden" name="ids" id="ids1"/>
        <input type="hidden" name="status" id="_status"/>
        <input type="submit" style="display:none">
    <div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search CCN Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
                                    <input type="submit" class="btn btn_to_reserve"  onclick="toReserve()" value="Reserve"/>
                                    <input type="submit" class="btn btn_to_new"  onclick="toNew()" value="Revise"/>
                                    <input type="submit" class="btn btn_to_confirm"  onclick="toConfirm()" value="Confirm"/>
                                    <input type="submit" class="btn btn_to_post"  onclick="toPost()" value="Post"/>
                                    <input type="submit" class="btn btn_to_cancel"  onclick="toCancel()" value="Cancel"/>
                                </div>
                                <div class="r" style="font-weight:bold" id="topSpace">
                                	 <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr id="theadObj">
                        <th width="20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
                        <th>Action</th>
                        <th>Ref</th>
                        <th>MCN Ref</th>
                        <th>Status</th>
                        <th>Customer Code</th>
                        <th>Customer Name</th>
                        <th>Export Date</th>
                        <th>Created By</th>
                        <th>Create Date</th>
                        <th>Remark</th>
                    </tr>
                </thead>
                <tbody>
                    % for i in collections:
                    <tr id="tr1_${i.id}">
                        <td width="20px" class="head"><input type="checkbox" class="cboxClass" value="${i.status}-${i.id}" onclick="selectOne()" /></td>
                        <td title="Action">
                            <a href="javascript:exportData('${i.id}')" class="west" title="Export Report"><img alt="Export Report" src="/images/icon/xls_16.gif"></a>
                        </td>
                        <td title="Ref" ><a href="javascript:viewNhead('${i.id}','${i.ref}')">${b(i.ref)|n}</a></td>
                        <td title="MCN Ref" ><a href="javascript:viewChead('${i.chead_id}','${i.chead_ref}')">${i.chead_ref}</a>&nbsp;</td>
                        <td title="Status" class="trStatus" >${b(i.status)|n}</td>
                        <td title="Customer Code" >${b(i.customer_code)|n}</td>
                        <td title="Customer Name" class="fcn">${b(i.customer_short_name)|n}</td>
                        <td title="Export Date" >${pd(i.export_time)|n}</td>
                        <td title="Created By" >${i.create_by}</td>
                        <td title="Create Date" >${pd(i.create_time)|n}</td>
                        <td title="Remark" class="trRemark">
							%if i.remark:
                        		<input type='text' value='${i.remark}'>
                        	%else:
                        		%if i.status == 'Cancelled':
                        			&nbsp;
                        		%else:
	                        		%if i.status == 'Cancelled' or i.status == 'Posted':
	                        			&nbsp;
	                        		%else:
	                        			<input type='text' name='remark-${i.id}'>
	                        		%endif
                        		%endif
                        	%endif
                        	</td>
						</td>
                    </tr>
                    %endfor
 
                </tbody>
                 <tfoot class="tfoot">
         			<tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace"> <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a></td></tr>
                </tfoot>
            </table>
        </div>
        <div class="clear"></div>
    </div>
        </form>
</div>
  <table class="gridTableb" cellpadding="0" cellspacing="0" border="0" id="scroll" style="position:absolute;left:7px;top:0px;display:none">
    <thead>
        <tr id="scrollObj">
            <th width="20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
            <th>Action</th>
            <th>Ref</th>
            <th>MCN Ref</th>
            <th>Status</th>
            <th>Customer Code</th>
            <th>Customer Name</th>
            <th>Export Date</th>
            <th>Created By</th>
            <th>Create Date</th>
            <th>Remark</th>
        </tr>
    </thead>
</table>					 

			 

 