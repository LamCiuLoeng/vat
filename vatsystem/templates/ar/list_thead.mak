<%
from vatsystem.util import const
from vatsystem.util.mako_filter import b,pd
%>
<script>
	initTr();
	initDate();
	initScroll();
	changeLine('payment_remark');
	disableBtn(['#btn_set_vat_info','#btn_to_new', '#btn_to_submit', '#btn_to_approve','#btn_to_confirm','#btn_to_reserve','#btn_to_post','#btn_to_cancel', '#btn_to_save'], true)
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
        disableBtn(['#btn_set_vat_info','#btn_to_new','#btn_to_confirm', '#btn_to_submit', '#btn_to_approve','#btn_to_reserve','#btn_to_post','#btn_to_cancel', '#btn_to_save'], true)
        if(vals.length && vals.length > 0) disableBtn(['#btn_to_save'], false);
        if(btnValidate){
            if(status=='${const.VAT_THEAD_STATUS_NEW}') disableBtn(['#btn_to_reserve','#btn_to_cancel'], false)
            else if(status=='${const.VAT_THEAD_STATUS_RESERVE}'){
            	/**
                var vatNoValidate = true;
                for(var i=0;i<vat_nos.length;i++){
                    if(vat_nos[i]=='&nbsp;'){
                        vatNoValidate = false;
                        break;
                    }
                }
                if(vatNoValidate) disableBtn(['#btn_set_vat_info','#btn_to_confirm','#btn_to_new','#btn_to_cancel'], false)
                else disableBtn(['#btn_set_vat_info','#btn_to_new','#btn_to_cancel'], false)
                */
                disableBtn(['#btn_to_new', '#btn_to_submit','#btn_to_cancel'], false)
                
            }
            else if(status=='${const.VAT_THEAD_STATUS_SUBMIT}'){
            	disableBtn(['#btn_to_approve', '#btn_to_cancel'], false)
            }
            else if(status=='${const.VAT_THEAD_STATUS_APPROVE}'){
            	var vatNoValidate = true;
                for(var i=0;i<vat_nos.length;i++){
                    if(vat_nos[i]=='&nbsp;'){
                        vatNoValidate = false;
                        break;
                    }
                }
                if(vatNoValidate) disableBtn(['#btn_set_vat_info','#btn_to_confirm','#btn_to_cancel'], false)
                else disableBtn(['#btn_set_vat_info','#btn_to_new','#btn_to_cancel'], false)
            }
            else if(status=='${const.VAT_THEAD_STATUS_CONFIRMED}') disableBtn(['#btn_to_post','#btn_to_cancel'], false)
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
            if(toStatus=='${const.VAT_THEAD_STATUS_CONFIRMED}' && ($('#vat_no_'+id).html()=='' || $('#vat_no_'+id).html()==null ||$('#vat_no_'+id).html()=='&nbsp;')){
                showError('Please input the VAT No before comfirm MSI/MSO!')
                return []
            }
        }
        if(ids.length>0){
            $('#ids1').val(ids.join(','));
            if(toStatus != '${const.VAT_CHEAD_STATUS_SAVE}'){
            	$('#_status').val(toStatus);
            	if(toStatus == '${const.VAT_THEAD_STATUS_RESERVE}'){
            		$.ajax({
					   type: "GET",
					   async: false,
					   url: "/ar/check_amount",
					   data: "id="+ids.join(','),
					   beforeSend:function(XMLHttpRequest) {
						    showWaiting();
						},
					   complete:function(XMLHttpRequest, textStatus){
					   		closeBlock();
					   },
					   success: function(data){
						    if(data.status == 1){
						    	$.get("/ar/update_all_thead_status", {status:toStatus, ids:ids.join(',')}, function(data){
						    		if(data.types == 0){
						    			showMsg(data.messages);
						    			for(var i=0;i<ids.length;i++){
						    				$("#tr1_"+ids[i]+"").find('.trStatus').html(toStatus);
						    				$("#tr1_"+ids[i]+"").children(".head").children(".cboxClass").val("${const.VAT_THEAD_STATUS_RESERVE}-"+ids[i]).removeAttr("checked");
						    			}
						    		}
						    		else{
						    			showError(data.messages);
						    		}
						    	})
	            			}else{
	            				showError("You can't reserve cause the SO Available Amount is more than the Order Amount(without Tax) !")
	            			}
					   }
					});
            	}else{
            		
            		ajaxForm('#form1','Save Success!','0','0',getCboxArr(),'saveStatus')
            	}
            }else{
            	ajaxForm('#form1','Save Success!','0','0',getCboxArr(),'saveSave')
            }
            //$('#form1').submit();
        }
    }
    var toNew=function(){saveStatus('${const.VAT_THEAD_STATUS_RESERVE}', '${const.VAT_THEAD_STATUS_NEW}', 'Only Reserve status MSI/MSO can revise!');}
    var toReserve=function(){saveStatus('${const.VAT_THEAD_STATUS_NEW}', '${const.VAT_THEAD_STATUS_RESERVE}', 'Only New status MSI/MSO can revert to Reserve!');}
    var toConfirm=function(){saveStatus('${const.VAT_THEAD_STATUS_RESERVE}', '${const.VAT_THEAD_STATUS_CONFIRMED}', 'Only Reserve status MSI/MSO can revert to Confirmed');}
    var toPost=function(){saveStatus('${const.VAT_THEAD_STATUS_CONFIRMED}', '${const.VAT_THEAD_STATUS_POST}', 'Only Confirmed status MSI/MSO can revert to Post!');}
    var toCancel = function(){saveStatus('', '${const.VAT_THEAD_STATUS_CANCELLED}', '');}
	var toSave = function(){saveStatus('', '${const.VAT_THEAD_STATUS_SAVE}', '');}
	var toSubmit = function(){saveStatus('', '${const.VAT_THEAD_STATUS_SUBMIT}')}
	var toApprove = function(){saveStatus('', '${const.VAT_THEAD_STATUS_APPROVE}')}
	var toExport = function(){
		if(!validateCbox()) return false;
        var ids = [];
        var arr = getCboxArr();
        for(var i=0;i<arr.length;i++){
            ids.push(arr[i].split('-')[1]);
        }
        $('#ids4').val(ids.join(','));
        $("#form5_export_ar_all").submit();
	}
	
 
</script>
<input type="hidden" name="cust" id="cust" value="${cust}"/>
<ul class="ui-tabs-nav ui-helper-reset ui-helper-clearfix ui-widget-header ui-corner-all" >
 	<li  class="ui-state-default ui-corner-top ui-tabs-selected ui-state-active" ><a href="#tabs-0">MSI/MSO</a></li>
</ul>
<div id="tabs-0" class="ui-tabs-panel ui-widget-content ui-corner-bottom" >
    <div class="none" id="vatDialog">
        <form action="/ar/update_all_thead_vat_info" method="post" id="form2">
            <input type="hidden" name="ids" id="ids2"/>
            <div class="box6"> 
                <ul>
                    <li class="li1">VAT No Range</li>
                    <li class="li2"><input type="text" name="vat_no" id="vat_no2" /></li>
                    <li class="li4" style="text-align:left">(e.g. 00000001~00000010,00000099)</li>
                </ul>
                <ul>
                    <li class="li1">VAT Date</li>
                    <li class="li2"><input type="text" class="datePickerNoImg" name="vat_date" id="vat_date2"/></li>
                    <li class="li4" >(YYYY-MM-DD)</li>
                </ul>
                <div class="clear"></div>
            </div>
            <div class="box7">
                <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form2','Save Success!','0','0',saveVatForm(),'saveVat')"/>
                <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
            </div>
        </form>
    </div>
    <form action="/ar/export_all_thead" mehotd="post" id="form3">
        <input type="hidden" name="ids" id="ids3"/>
    </form>
    <form action="/report/export_ar_all" method="post" id="form5_export_ar_all">
    	 <input type="hidden" name="ids" id="ids4"/>
    </form>
    <form action="/ar/update_all_thead_status" method="post" id="form1">
        <input type="hidden" name="ids" id="ids1"/>
        <input type="hidden" name="status" id="_status"/>
        <input type="submit" style="display:none">
    	<div class="box2">
        <div class="title1"><div class="toggle_down"></div>Search MSI/MSO Result</div>
        <div class="box4">
            <table class="gridTable" cellpadding="0" cellspacing="0" border="0">
                <thead>
                    <tr>
                        <td colspan="100" style="border-right:0px;border-bottom:0px">
                            <div class="toolbar">
                                <div class="l">
                                    <input type="button" class="btn" id="btn_set_vat_info" onclick="openVatForm()" value="Set VAT Info"/>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
                                    <input type="button" class="btn" id="btn_to_reserve" onclick="toReserve()" value="Reserve"/>
                                    <input type="submit" class="btn" id="btn_to_new" onclick="toNew()" value="Revise"/>
                                    <input type="submit" class="btn" id="btn_to_submit" onclick="toSubmit()" value="Submit"/>
                                    <input type="submit" class="btn" id="btn_to_approve" onclick="toApprove()" value="Approve"/>
                                    <input type="submit" class="btn" id="btn_to_confirm" onclick="toConfirm()" value="Confirm"/>
                                    <input type="submit" class="btn" id="btn_to_post" onclick="toPost()" value="Post"/>
                                    <input type="submit" class="btn" id="btn_to_cancel" onclick="toCancel()" value="Cancel"/>
                                    <input type="submit" class="btn" id="btn_to_save" onclick="toSave()" value="Save"/>
                                    <input type="button" class="btn" id="btn_to_export" onclick="toExport()" value="Export"/>
                                </div>
                                <div class="r" style="font-weight:bold" id="topSpace">
                                	 <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a>
                                </div>
                            </div>
                        </td>
                    </tr>
                    <tr id="theadObj">
                        <th class="head" width="20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
                        <th>Action</th>
                        <th>Ref</th>
                        <th>VAT No</th>
                        <th>Status</th>
                        <th>Customer Code</th>
                        <th>Customer Name</th>
                        <th>VAT Date</th>
                        <th>Export Date</th>
                        <th>Created By</th>
                        <th>Create Date</th>
                        <th>Express No.</th>
            			<th>Express Date</th>
                       	<th>Remark</th>
                       	<th>对帐月份</th>
                       	<th>付款</th>
                       	<th>付款备注</th>
                    </tr>
                </thead>
                <tbody>
                   % for i in collections:
                    <tr id="tr1_${i.id}">
                        <td class="head" width="20px"><input type="checkbox" class="cboxClass" value="${i.status}-${i.id}" onclick="selectOne()" /></td>
                        <td class="action" title="Action">
                            <a href="javascript:exportData('${i.id}')" class="west" title="Export Report"><img alt="Export Report" src="/images/icon/xls_16.gif"></a>
                            %if i.status == const.VAT_THEAD_STATUS_POST:
                            &nbsp;
                            <a href="javascript:openNewMcnForm('${i.id}')" class="west" title="Create MCN"><img alt="Export Report" src="/images/icon/add_16.gif"></a>
                            %endif
                        </td>
                        <td title="Ref"><a href="javascript:viewThead('${i.id}', '${i.ref}')">${b(i.ref)|n}</a></td>
                        <td title="VAT No" id="vat_no_${i.id}" class="vat_no">${b(i.vat_no)|n}</td>
                        <td title="Status" class="trStatus">${b(i.status)|n}</td>
                        <td title="Customer Code" >${b(i.customer_code)|n}</td>
                        <td title="Customer Name" class="fcn">${b(i.customer_short_name)|n}</td>
                        <td title="VAT Date" class="vatDate">${pd(i.vat_date)|n}</td>
                        <td title="Export Date" >${pd(i.export_time)|n}</td>
                        <td title="Created By" >${i.create_by}</td>
                        <td title="Create Date" >${pd(i.create_time)|n}</td>
                        <td><input type="text" name="express_no-${i.id}" value="${i.express_no}"/></td>
                        <td><input type="text" name="express_date-${i.id}" value="${i.express_date}"  class="datePickerNoImg"/></td>
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
                        <td><select name='rec_month-${i.id}'>
                        		% for r in range(0, 13):
                        			%if i.rec_month and r == int(i.rec_month):
                        				"<option value='${r}'  selected="selected">${r}</option>"  
                        			%else:
                        				%if r == 0:
                        				"<option value=''></option>"
                        				%else:
                        				"<option value='${r}'>${r}</option>"
                        				%endif
                        				
                        			%endif 
                        		% endfor
                        </select></td>
                        <td><select name='payment_status-${i.id}'>
                        		%for c, r in enumerate(['', u'未付', u'已付', u'部分付款']):
                        			%if i.payment_status and c == int(i.payment_status):
                        				<option value='${c}'  selected="selected">${r}</option>
                        			%else:
                        				<option value='${c}'>${r}</option>
                        			%endif
                        		%endfor
                        	</select></td>
                        <td><textarea rows="1" cols="6" name='payment_remark-${i.id}' style="width: 178px; height: 20px;" onkeyup="changeLine(this)">${i.payment_remark}</textarea></td>
                    </tr>
                    %endfor
                
                </tbody>
                <tfoot>
         			<tr><td colspan="22" style="border-right:0px;border-bottom:0px;text-align:left;font-weight:bold" id="pageSpace"> <a href="/ar?page=${offset}" class="pager_link" next="${offset}" cate="next" limit="${limit}" offset="${offset}">next&nbsp;page</a></td></tr>
                </tfoot>
            </table>
        </div>
    </div>
    </form>
</div>				
    % for v in collections:
        <form action="/report/export" method="post" id="form5_${v.id}">
            <input type="hidden" name="id" value="${v.id}"/>
            <input type="hidden" name="head_type" value="tHead"/>
        </form>
        %if v.status == const.VAT_THEAD_STATUS_POST:
        <div class="none" id="vatDialog4_${v.id}">
            <form action="/ar/save_to_chead" method="post" id="form4_${v.id}">
                <input type="hidden" name="id" value="${v.id}"/>
                <div class="box6">
                    <ul>
                        <li class="li1">VAT No Range</li>
                        <li class="li2"><input type="text" name="vat_no" id="vat_no4_${v.id}" /></li>
                        <li class="li4">(e.g. 00000001~00000010,00000099)</li>
                    </ul>
                    <div class="clear"></div>
                </div>
                <div class="box7">
                	<div style="display:none"><input type="text"  id="vat_no4_${v.id}" /></div>
                    <input type="submit" class="btn" value="Submit" onclick="ajaxForm('#form4_'+${v.id},'Save Success!','0','0',saveNewMcnForm('${v.id}', '${v.vat_no}'),'listMcn')"/>
                    <input type="button" class="btn" value="Cancel" onclick="closeBlock()"/>
                </div>
            </form>
        </div>
        %endif
    % endfor
    
  <table class="gridTableb" cellpadding="0" cellspacing="0" border="0" id="scroll" style="position:absolute;left:7px;top:0px;display:none">
    <thead>
        <tr id="scrollObj">
           <th class="head" width="20px"><input type="checkbox" value="0" onclick="selectAll(this)" /></th>
            <th>Action</th>
            <th>Ref</th>
            <th>VAT No</th>
            <th>Status</th>
            <th>Customer Code</th>
            <th>Customer Name</th>
            <th>VAT Date</th>
            <th>Export Date</th>
            <th>Created By</th>
            <th>Create Date</th>
            <th>Express No.</th>
            <th>Express Date</th>
           	<th>Remark</th>
        </tr>
    </thead>
</table>