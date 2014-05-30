var $tabs
var tab_title, tab_content;
var tab_counter = 1;
var sub_type = 0
var posted;

var data = "OTHER,DISCOUNT,FREIGHT CHARGE,REMARK".split(",");
$('#tabs span.ui-icon-close').live('click', function() {
    var index = $('li',$tabs).index($(this).parent());
    $tabs.tabs('remove', index);
})

function removeTab(index){
	if($tabs!=undefined)$tabs.tabs('remove', index);
}

function addTab() {
    tab_counter++;
    if($('#tabs span.ui-icon-close').length == 0){
    	$('#tabs').tabs( "destroy" );
    }
    $tabs = $('#tabs').tabs({
        tabTemplate: '<li><a class="ui-href" href="#{href}">#{label}</a> <span class="ui-icon ui-icon-close">Remove Tab</span></li>',
        add: function(event, ui) {
            var flag = 0; 
            var index;
            $('#tabs span.ui-icon-close').each(function() {
                if(tab_title==$(this).prev().html()){
                    flag++;
                    if(flag==1){
                        index = $('li',$tabs).index($(this).parent());
                    }else if(flag>1){ 
                        $tabs.tabs('remove', index);
                    }
                }
             
        });  
        $(ui.panel).append('<p>'+tab_content+'</p>');
        $tabs.tabs('select', '#' + ui.panel.id);
        }
    });
    $('#tabs').tabs('add', '#tabs-'+tab_counter, tab_title);
}

var saveAllToThead = function(){
    if(!validateCbox()) return false;
    $('#ids').val(getCboxStr());
    $('#customer_code').val();
    //$('#_form').submit()
    return true;
}
var saveAllToTheadByCustomer = function(obj){
	var q = [];
	var customer_code;
	$(".dboxClass").each(function(){
		var v = $(this).val();
		if($(this).attr('checked')){
			customer_code = v.split("$")[1];
			q.push(v);
		}
	})
	if(q.join().length == 0){
		showError('Please select at least one checkbox!');return false;
	}
	$(obj).siblings("input[name='customer_code']").val(customer_code);
	$(obj).siblings("input[name='ids']").val(q.join());
}
var saveToCHead = function(){
    if(!validateCbox()) return false;
    $('#ids').val(getCboxStr());
    $('#customer_code').val();
    $('#_form').submit()
    return true;
}

var toCheckSearch = function(id){ 
	var head_type = false;
	var forms = $("#_form"+id+" input[type!='button'][type!='hidden'], select")
	forms.each(function(){
		if($(this).val() && $(this).val().length > 0)head_type = true;
	})
	
	if(head_type){
		toSearch(id);
	}else{
		showError("You must input at least one in the form!");
	}
}

var toSearch = function(id){
    //$("#tabs").empty();
	var bool          = true;
    var startTime     = $("#_form"+id+" .datePicker").eq(0).val();
    var endTime       = $("#_form"+id+" .datePicker").eq(1).val();
    if(startTime){
    	if(checkTime(startTime)){
    		var startTime = startTime.split("-");
            var startTime = new Date(startTime[0],startTime[1],startTime[2]);
    	}
    	else{
    		showError("the Start Create Date Error!");
    		var bool = false;
    	}
    }
    if(endTime){
    	if(checkTime(endTime)){
    		var endTime   = endTime.split("-");
        	var endTime   = new Date(endTime[0],endTime[1],endTime[2]);
    	}
    	else{
    		showError("the End Create Date Error!");
    		var bool  = false;
    	}
    }
    if(startTime && endTime){
	    if(startTime>endTime){
	    	showError("the Start Create Date must't more than the End Create Date!");
	    	var bool = false;
	    }
    }
    if(bool){
		var queryString = $('#_form'+id).attr("action")+"?"+$('#_form'+id).serialize();
		ajaxGet(queryString,"#tabs",queryString);
    }
}

var checkDate = function(id){
	var bool          = true;
    var startTime     = $("#_form"+id+" .datePicker").eq(0).val();
    var endTime       = $("#_form"+id+" .datePicker").eq(1).val();
    if(startTime){
    	if(checkTime(startTime)){
    		var startTime = startTime.split("-");
            var startTime = new Date(startTime[0],startTime[1],startTime[2]);
    	}
    	else{
    		showError("the Start Create Date Error!");
    		bool = false;
    	}
    }
    if(endTime){
    	if(checkTime(endTime)){
    		var endTime   = endTime.split("-");
        	var endTime   = new Date(endTime[0],endTime[1],endTime[2]);
    	}
    	else{
    		showError("the End Create Date Error!");
    		bool  = false;
    	}
    }
    if(id == '1'){
    	if(!$("#_form"+id+" #item_code").val()){
    		showError("you must input the Item Code input!")
    		bool = false;
    	};
    }
    if(startTime && endTime){
	    if(startTime>endTime){
	    	showError("the Start Create Date must't more than the End Create Date!");
	    	var bool = false;
	    }
    }else{
    	bool = false;
    	showError("you must input the Date form!");
    }
    if(bool){ 
    	$("#_form"+id).submit();
    }
}

var toReset = function(id){
    $('#_form'+id+' :text').val('')
    $('#_form'+id+' select').val('')
}

var viewAll = function(queryString){
    ajaxGet(queryString,"#tabs",queryString);
    closeMsg();
}

var viewPage = function(queryString,count){
    $.ajax({
		type: "get",
		url: queryString,
		beforeSend: function(XMLHttpRequest){
			showWaiting();
		},
		success: function(data, textStatus){
	       $(".gridTable tbody").append($(data).find(".gridTable tbody").html());
		   $("#pageSpace").replaceWith($(data).find("#pageSpace"));
		   $("#topSpace").replaceWith($(data).find("#topSpace"));
		},
		complete: function(XMLHttpRequest, textStatus){
		    initTr();
		    replayLink(queryString,".pager_link");
			closeBlock();
			
		},
		error: function(){
			showError("Error!");
		}
    })
}

var viewChead = function(id, ref){
    showWaiting();
	$("#scroll").hide();
    $.get("/ar/ajax_view_chead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewThead = function(id, ref){
    showWaiting();
    $("#scroll").hide();
    $.get("/ar/ajax_view_thead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewOhead = function(id, ref){
    showWaiting();
    $("#scroll").hide();
    $.get("/cost/ajax_view_ohead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewNhead = function(id, ref){
    showWaiting();
    $("#scroll").hide();
    $.get("/cost/ajax_view_nhead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewCheadNoWaiting = function(id, ref){
    $.get("/ar/ajax_view_chead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewTheadNoWaiting = function(id, ref){
    $.get("/ar/ajax_view_thead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });    
}

var viewSI = function(invoice_no){
    showWaiting();
    $("#scroll").hide();
    $.get("/ar/ajax_view_si",{invoice_no:invoice_no}, function(html){
        tab_title = invoice_no;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewCustomer = function(customer_code, type, date_from, date_to){
    showWaiting();
    if(type == 10){
    	type = 1;
    }else{
    	type = 2;
    }
    $.get("/ar", {type:type, customer_code:customer_code, date_from:date_from, date_to:date_to, limit:0, offset:10000, all:'all'}, function(data){
    	for(i=1; i<= tab_counter; i++){
        	removeTab(i);
    	}
        tab_title = customer_code;
        var data = data.replace("<tbody>", "<tbody id='customer_ar_list'>")
        										.replace("selectAll(this)", "selectAllDetail(this, 'dboxClass')")
        										.replace(new RegExp("cboxClass","gm"), "dboxClass")
        										.replace('saveAllToThead()', "saveAllToTheadByCustomer(this)")
        var content = $(data).find(".box2")
        if(type == 2){
	        content.find("input[value='Save as MSO']")
	    }else{
	    	content.find("input[value='Save as MSI']")
	    }
        content.find("#topSpace").html("")
        content.find("#pageSpace").html("")
        tab_content = "<div class='box2'>"+content.html()+"</div>";
        addTab();
        resetLink();
        closeBlock();
        initTr();
    });
}

var viewSO = function(sales_contract_no){
    showWaiting();
    $("#scroll").hide();
    $.get("/ar/ajax_view_so",{sales_contract_no:sales_contract_no}, function(html){
        tab_title = sales_contract_no;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var toSaveSISOCharge = function(id){
    var qty_vals = [];
    var available_qty_vals = [];
    
    $(id+' .qty').each(function(){
    	if($(this).val()==""){
    		$(this).val("0");
    	}
    	if($(this).parent("td").prev(".available_qty").html()){
    		qty_vals.push($(this).val())
    	}
    })
    $(id+' .available_qty').each(function(){
        available_qty_vals.push($(this).html())
    })
    var validate = true;
    for(var i=0;i<qty_vals.length;i++){
    	if(Math.abs(parseInt(qty_vals[i]))>Math.abs(parseInt(available_qty_vals[i]))){
            validate = false;
            break;
        }
    }
    if(validate){
        return true;
    }
    else{
        showError("The input ' VAT Total ' can't more than ' Total '");
    	return false;
    }
}

var toSaveSISODetails = function(pre, id){
	var types    = []
    var qty_vals = [];
    var available_qty_vals = [];
    $('#_form_'+pre+id+' .qty').each(function(){
    	if($(this).val()==""){
    		$(this).val(0)
    	}
        qty_vals.push($(this).val())
        types.push($(this).attr("cate"))
    })
    $('#_form_'+pre+id+' .available_qty').each(function(){
        available_qty_vals.push($(this).html())
    })
    var validate = [];
    for(var i=0;i<qty_vals.length;i++){
    	if(parseFloat(available_qty_vals[i])>0 && parseFloat(qty_vals[i])>parseFloat(available_qty_vals[i])){
            validate.push(types[i]);
        }
    }
    
    if(validate.length == 0){
        return true;
    }
    else{
    	var detailIndex = 0;
    	var chargeIndex = 0;
    	var message = [];
    	for(var i=0;i<validate.length;i++){
    		if(validate[i] == 'detail' && detailIndex == 0){
    			message.push("The input ' Qty ' can't more than ' Available Qty '")
    			detailIndex++;
    		}
    		if(validate[i] == 'charge' && chargeIndex == 0){
    			message.push("The input ' Total ' can't more than ' Available Total '")
    			chargeIndex++;
    		}
    	}
        showError(message.join("<br />"));
    	return false;
    }
}

var toSaveCheadDetails = function(pre, id){
	var types    = []
    var qty_vals = new Array();
    var available_qty_vals = new Array();
    $('#_form_'+pre+id+' .qty').each(function(){
    	if($(this).val()==""){
    		$(this).val(0)
    	} 
        qty_vals.push($(this).val())
        types.push($(this).attr("cate"))
    })
    
    $('#_form_'+pre+id+' .available_qty').each(function(){
    	 
        available_qty_vals.push($(this).html())
    })
    var validate = [];
    for(var i=0;i<qty_vals.length;i++){
        if(parseFloat(available_qty_vals[i])>0 && parseFloat(qty_vals[i])>parseFloat(available_qty_vals[i])){
        	validate.push(types[i]);
        }
    }
    if(validate.length == 0){
        return true;
    }
    else{
    	var detailIndex = 0;
    	var chargeIndex = 0;
    	var message = [];
    	for(var i=0;i<validate.length;i++){
    		if(validate[i] == 'detail' && detailIndex == 0){
    			message.push("The input ' Qty ' can't more than ' Available Qty '")
    			detailIndex++;
    		}
    		if(validate[i] == 'charge' && chargeIndex == 0){
    			message.push("The input ' Total ' can't more than ' Available Total '")
    			chargeIndex++;
    		}
    	}
        showError(message.join("<br />"));
    	return false;
    }
}

var toSaveSheadDetails = function(pre, id){
	var types    = []
    var qty_vals = new Array();
    var available_qty_vals = new Array();
    $('#_form_'+pre+id+' .qty').each(function(){
    	if($(this).val()==""){
    		$(this).val(0)
    	} 
        qty_vals.push($(this).val())
        types.push($(this).attr("cate"))
    })
    
    $('#_form_'+pre+id+' .available_qty').each(function(){
    	 
        available_qty_vals.push($(this).html())
    })
    var validate = [];
    for(var i=0;i<qty_vals.length;i++){
        if(parseFloat(available_qty_vals[i])>0 && parseFloat(qty_vals[i])>parseFloat(available_qty_vals[i])){
        	validate.push(types[i]);
        }
    }
    if(validate.length == 0){
        return true;
    }
    else{
    	var detailIndex = 0;
    	var chargeIndex = 0;
    	var message = [];
    	for(var i=0;i<validate.length;i++){
    		if((validate[i] == 'detail' || validate[i] == 'payment_amount') && detailIndex == 0){
    			message.push("The input ' Payment Amount ' can't more than ' Available Amount '")
    			detailIndex++;
    		}
    		if(validate[i] == 'charge' && chargeIndex == 0){
    			message.push("The input ' Payment Total ' can't more than ' Available Total '")
    			chargeIndex++;
    		}
    	}
        showError(message.join("<br />"));
    	return false;
    }
}

var openVatForm=function(){
	$("#form2 #vat_no2").val("");
	$("#form2 #vat_date2").val("");
    if(!validateCbox()) return false;
    //$.prompt($('#vatDialog').html(),{ buttons:{Submit:saveVatForm,Cancel:false}, prefix:'jqismooth' });
    $.blockUI({
        theme:false,
        title:'Set VAT Info',
        message:$('#vatDialog'),
        baseZ: 100,
        css:{width: '350px'}
    });
}

var saveVatForm = function(){
    var vat_date = $('#vat_date2').val();
    var vat_no = $('#vat_no2').val();
    if(!vat_no){
        showError("Please input the 'VAT NO'!");
        return false;
    }
    if(!vat_date){
        showError("Please input the 'VAT Date'!");
        return false;
    }
    if(!validate_vat_no_range(vat_no, null)) return false;
    else{
        var ids = [];
        var arr = getCboxArr();
        for(var i=0;i<arr.length;i++){
            ids.push(arr[i].split('-')[1]);
        }
        $('#ids2').val(ids.join(','));
    }
}

var openNewMcnForm=function(thead_id){
	$("#form4_"+thead_id+" #vat_no4_"+thead_id).val($("#tr1_"+thead_id+" #vat_no_"+thead_id).html());
	var data = $("#tr1_"+thead_id+" #vat_no_"+thead_id).html().split(",");
	$("#form4_"+thead_id+" #vat_no4_"+thead_id).autocomplete(data);
	$.get("/ar/ajax_check_mcn",{id:thead_id}, function(data){
		  if(data.Msg == 0){
			showError("You can't create MCN!");
			return false;
		  }else{
			$.blockUI({
		        theme:false,
		        title:'Set VAT Info',
		        message:$('#vatDialog4_'+thead_id),
		        baseZ: 100,
		        css:{width: '350px'}
		    }); 
		  }
	},'json');
}

var openNewMcnForm2=function(thead_id,vat_no){
	var data = vat_no.split(",");
	$("#form25_"+thead_id+" #vat_no25_"+thead_id).autocomplete(data);
	$.get("/ar/ajax_check_mcn",{id:thead_id}, function(data){
		  if(data.Msg == 0){
			showError("You can't create MCN!");
			return false;
		  }else{
		    $.blockUI({
		        theme:false,
		        title:'Set VAT Info',
		        message:$('#vatDialog5_'+thead_id),
		        baseZ: 100,
		        css:{width: '350px'}
		    });
		  }
	},'json');
}

var Add_Other_Charges_From_Manual=function(thead_id){
    $.blockUI({
        theme:false,
        title:'Add Other Charges From Manual',
        message:$('#Add_Other_Charges_From_Manual_'+thead_id),
        baseZ: 100,
        css:{width: '350px'}
    });
}

var Cn_Charge_List=function(invoice_no){
    $.blockUI({
        theme:false,
        title:'Cn Charge List',
        message:$('#Cn_Charge_List_'+invoice_no),
        baseZ: 100,
        css:{width: '800px'}
    });
}

var saveNewMcnForm = function(thead_id, thead_vat_no){
    var vat_no = $('#vat_no4_'+thead_id).val();
    if(!vat_no){
        showError("Please input the 'VAT NO'!");
        return false;
    }
    if(!validate_vat_no_range(vat_no, thead_vat_no)) return false;
    else{
        var ids = [];
        var arr = getCboxArr();
        for(var i=0;i<arr.length;i++){
            ids.push(arr[i].split('-')[1]);
        }
    }
}

var saveNewMfForm2 = function(thead_id, thead_vat_no){
    var vat_no = $('#vat_no26_'+thead_id).val();
    if(!vat_no){
        showError("Please input the 'VAT NO'!");
        return false;
    }
    if(!validate_vat_no_range(vat_no, thead_vat_no)) return false;
    else{
        var ids = [];
        var arr = getCboxArr();
        for(var i=0;i<arr.length;i++){
            ids.push(arr[i].split('-')[1]);
        }
    }
}

var saveNewMcnForm2 = function(thead_id, thead_vat_no,tHead_ref){
    var vat_no = $("#vat_no25_"+thead_id).val();
    if(!vat_no){
        showError("Please input the 'VAT NO'!");
        return false;
    }
    if(!validate_vat_no_range(vat_no, thead_vat_no)) return false;
    else{
        var ids = [];
        var arr = getCboxArr();
        for(var i=0;i<arr.length;i++){
            ids.push(arr[i].split('-')[1]);
        }
    }
}

var saveNewMfForm = function(thead_id, thead_vat_no,tHead_ref){
    var vat_no = $("#vat_no26_"+thead_id).val();
    if(!vat_no){
        showError("Please input the 'VAT NO'!");
        return false;
    }
    if(!validate_vat_no_range(vat_no, thead_vat_no)) return false;
    else{
        var ids = [];
        var arr = getCboxArr();
        for(var i=0;i<arr.length;i++){
            ids.push(arr[i].split('-')[1]);
        }
    }
}

var saveNewDateForm = function(id, ref, pi, dn, a1, b1, c1){
	var dzd_search = $("*[cid='dzd_search']")
    var billing_month = $("#billing_month_"+id).val();
    var kingdee_date  = $("#kingdee_date_"+id).val();
    var reconciliation_lot = $("#reconciliation_lot_"+id).val();
    var payment_date = $("#payment_date_"+id).val();
    dzd_search.each(function(){
    	var value = $(this).val();
    	var name  = $(this).attr('name')
    	if( name == "billing_month"){
    		if(String(a1).search(value) == -1){
    			$("*[cid='dzd_search'][name='billing_month_complete']").val("");
    		}
    	}
    	if(name == "kingdee_date"){
    		if(String(b1).search(value) == -1){
    			$("*[cid='dzd_search'][name='kingdee_date_complete']").val("");
    		}
    	}
    	if(name == "payment_date"){
    		if(String(c1).search(value) == -1){
    			$("*[cid='dzd_search'][name='payment_date_complete']").val("");
    		}
    	}
    })
    dzd_search.each(function(){
    	if($(this).attr('name') == "supplier_code" && $(this).val().length == 0){
    		showError("Please select the supplier code!");
    	}
    	if($(this).attr('name') == "reconciliation_lot" && $(this).val().length == 0){
    		showError("Please select the 对帐批号!");
    	}
    })
    var queryString = $("*[cid='dzd_search']").serialize()+"&id="+id+"&type="+setDateType;
    $.ajax({
		type:"GET",
		dataType:"json",
		data:queryString,
		url: "/ap/ajax_update_dzd",
		success: function(data, textStatus){
			if(data.types == '0'){
				showMsg(data.messages);
			}else{
				showError(data.messages);
			}
			viewStatement1(id, ref, pi, dn);
		},
		error: function(){
			showError("Save Failure!");
		}
	});
}

var Save_Other_Charges_From_Manual = function(thead_id){
    $('#form15_'+thead_id).submit();
}

var validate_vat_no_range = function(vat_no, thead_vat_no){
    var patrn=/^(((\d{8}|(\d{8}[~]\d{8})),)*)*(\d{8}|(\d{8}[~]\d{8}))$/
    if(!vat_no){
        showError("Please input the 'VAT No Range'!");
        return false;
    }else if(!patrn.exec(vat_no)){
        showError("Error: The format of 'VAT No Range' should like:<br/> 00000001~00000010,00000099");
        return false;
    }else if(thead_vat_no==null){
        return true;
    }else{
        var thead_vat_no_range = []
        for(var i=0;i<thead_vat_no.split(',').length;i++){
            thead_vat_no_range.push(thead_vat_no.split(',')[i])
        }
        var vat_no_range = []
        for(var i=0;i<vat_no.split(',').length;i++){
            vat_no_range.push(vat_no.split(',')[i])
        }
        
        for(var i=0;i<vat_no_range.length;i++){
            var m = vat_no_range[i].split('~')
            var validate = false;
            for(var j=0;j<thead_vat_no_range.length;j++){
                var n = thead_vat_no_range[j].split('~')
                if(m.length==1){
                    var m1 = Number(m)
                    if(n.length==1){
                        var n1 = Number(n)
                        if(m1==n1){
                            validate=true;
                            break;
                        }
                    }else if(n.length==2){
                        var n1 = Number(n[0])
                        var n2 = Number(n[1])
                        if(m1>=n1 && m1<=n2){
                            validate=true;
                            break;
                        }
                    }
                }else if(m.length==2 && n.length==2){
                    var m1 = Number(m[0])
                    var m2 = Number(m[1])
                    var n1 = Number(n[0])
                    var n2 = Number(n[1])
                    if(m1>=n1 && m2<=n2){
                        validate=true;
                        break;
                    }
                }
            }
            if(!validate){
            	if(initType()==2){
            		showError('Error: MPI VAT No. out of range!');
            	}
            	else{
            		showError('Error: MSI/MSO VAT No. out of range!');
            	}
                return false;
            }
        }
        return true;
    }
}


var exportData = function(id){
	$("#form5_"+id).submit();
}

var checkSelect = function(id){
	var type = false
	var selectStr = "";
    $(id+' .cboxClass').each(function(){
        if($(this).attr("checked")){
            type = true;
            selectStr += $(this).val()+",";
        }
    })
    if(id=="#update_other_charges_vat_total"){
    	$("#select_id").val(selectStr)
    }
    if(type==false){
            showError("You must be select one");
        	return false;
    }
}

var checkCstChargeSelect = function(id){
	var type = false
    $(id+' .dboxClass').each(function(){
        if($(this).attr("checked")){
            type = true;
        }
    })

    if(type==false){
        showError("You must be select one");
    	return false;
    }
    else{
    	return true;
    }
}

var checkNull = function(id){
	if($(id+" #charge_code").val()==''){
		showError("The Charge Code can't null");
    	return false;
	}
	if($(id+" #total").val()==''){
		showError("The Total can't null");
    	return false;
	}
	if(isNaN($(id+" #total").val())){
		showError("The Total must be digital");
    	return false;
	}
}

var searchErp = function(){
	
}

var openDialog = function(id){
	$.fx.speeds._default = 1000;
	$(function() {
		$( "#dialog_"+id).dialog({
			autoOpen: false,
			show: "blind",
			hide: "explode",
			maxWidth:1200,
			width:800,
			title:'CN',
			height:400,
			minHeight:300
		});
		$( "#dialog_"+id ).dialog( "open" );
		return false;
	});
}

var isStart = true;
function ifOKReturnTrue(v, m, f){
	if(v){
			if(sub_type == 1){
			  	showError("The sum MSI Qty is going to save more than the sum SO Qty，please check your data!")
				closeBlock();
				
			}else{
				isStart = false;	
				$("#_form").submit();
			}
		}
}

function returnTrue(){
	return true;
}


var ajaxForm  = function(id, message, tHeadId, tHeadRef, validate, type){
    $(id).ajaxForm({ 
        dataType:  'json', 
        beforeSubmit: function(arr, $form, options) {
        	if(type == 'saveStatus'){
            	var go = false;
            	var _status = $('#_status').val();
        		if( _status == "Cancelled"){
        			go = 'Are you sure to Cancel?'
        		}
        		else if(_status == "Posted"){
        			go = 'Are you sure to Post?'
        		}
        		if(go){
	    			if(!confirm(go)){
	    				closeBlock();
	    				return false;
	    			}else{
	    				return true;
	    			}
    			}
        	}
        	else if(type == 'save' && isStart){
        		var isEnd = true;
        		//var dataName = getCboxStr();
        		var dataName = $(id+" input[name='ids']").val();
        		var headType = $(id+" input[name='head_type']").val();
        		if(headType == 'SI'){
        			$.ajax({
            			type:"GET",
            			url: "/ar/ajax_check_hava_mso",
            			data:{name:dataName},
        				async:false,
        				dataType:"json",
            			beforeSend: function(XMLHttpRequest){
                    		showWaiting();
            			},
            			success:function(data, textStatus){
	              			  if(data.type == 2){
	              				  showMsgBoolForSI("MSO related the SI, You can save it or click(<a href='javascript:void(0)' onclick=viewAll('/ar?type=3&ref="+data.ref+"')>"+data.sc_no+"</a>) and modifly it!")
	            				  closeBlock();
	            				  isEnd = false;
	            			  }
	              			  if(data.type == 1){
	              				  showMsgBoolForSI("The SI has MSO, please click on the (<a href='javascript:void(0)' onclick=viewAll('/ar?type=3&sales_contract_no="+data.sc_no+"')>"+data.sc_no+"</a>)  and relate the SI for MSO!")
	            				  closeBlock();
	            				  isEnd = false;
	              			  }
	              			  sub_type = data.sub_type
	              			  if(data.type == 0){
	              				  isEnd = true; 
	              			  } 
            			 }
            		})
        		}
        		return isEnd;
        	}
        },
        beforeSerialize: function(){
        	if(validate == undefined || validate){
        		showWaiting();
        	}
        	return validate;
        },
        success: function(data){
        	isStart = true;
        	if(type=='search_erp'){
        		showMsg("Search Success!");
        	}
        	else if(type=='si_search'){
        		if(data.types == 0){
        			parent.$.fancybox.close();
        		}
            }
        	else if(type=='si_so_save'){
            	viewTheadNoWaiting(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='pi_po_save'){
            	viewPhead(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='s_pi_save'){
            	viewShead(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='m_pi_save'){
            	viewMhead(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='statement'){
            	viewStatement(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='si_so'){
            	closeBlock();
            }
        	else if(type=='mcn'){
            	viewChead(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='msn'){
            	viewShead(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='cst_save' || type=='cst_add_new_pi' || type == 'cst_add_new_charge'){
            	viewOhead(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='cst_update'){
            	viewOhead(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='ccn_save'){
            	viewNhead(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='dzd_import'){
            	viewStatement(tHeadId,tHeadRef);
            	closeBlock();
            }
        	else if(type=='save' || type=='save_to_cost'){
            	if(data.types == 0){
            	    $(".cboxClass,.dboxClass").each(function(i, obj){
            	        var jq = $(obj)
            	        if(jq.attr('checked')){
            	        	$(this).parent().parent("tr").remove();
            	        }   
            	    })
            	}
            }
        	else if(type == 'save_customer'){
        		var customers = data.customers
        		var error_customers = data.error_customers
            	if(data.types == 0){
            	    $(".cboxClass").each(function(i, obj){
            	        var jq = $(obj)
            	        var jqVal = jq.val().split("$")[0]
            	        if(jq.attr('checked') && customers.search(jqVal) > -1){
            	        	$(this).parent().parent("tr").remove();
            	        }   
            	    })
            	}
        	}
        	else if(type == 'save_variance'){
        		var queryString = $('#_form6').attr("action")+"?"+$('#_form6').serialize();
        		ajaxGet(queryString,"#tabs",queryString);
        	}
        	else if(type=='saveStatus'){
            	if(data.types==0){
            		var systemType = initType()
            		var ids  = data.kws.ids.split(",");
            		for(var i=0;i < ids.length; i++){
            			remark = "remark-"+ids[i]
            			$("#tr1_"+ids[i]).children(".trStatus").html(data.kws.status);
            			$("#tr1_"+ids[i]).children(".head").children(".cboxClass").val(data.kws.status+"-"+ids[i])
            			if(data.kws.status=="Cancelled"){
            				if(data.kws[remark].length==0){
            					data.kws[remark] = "&nbsp;";
            				} 
                			$("#tr1_"+ids[i]).children(".trRemark").html(data.kws[remark]);
            			}
            			if(data.kws.status=="Posted"){
                			$("#tr1_"+ids[i]).children(".trRemark").html("&nbsp;");
                			if(systemType == 1){
                				$("#tr1_"+ids[i]).children(".action").append("&nbsp;<a title='Create MCN' class='west' href=javascript:openNewMcnForm('"+ids[i]+"')><img src='/images/icon/add_16.gif' alt='Create MCN'></a>");
                			}
                			if(systemType == 2){
                				if(data.kws.head_type=="cHead"){
                					$("#tr1_"+ids[i]).children(".action").prepend("&nbsp;<a title='Create MF' style='display:none' class='west' href=javascript:openNewMfForm('"+ids[i]+"','S_PI')><img src='/images/icon/add_16.gif' alt='Create MF'></a>");
                				}else{
                					$("#tr1_"+ids[i]).children(".action").prepend("&nbsp;<a title='Create MSN' class='west' href=javascript:openNewMsnForm('"+ids[i]+"')><img src='/images/icon/add_16.gif' alt='Create MSN'></a>&nbsp;<a title='Create MF' class='west' style='display:none' href=javascript:openNewMfForm('"+ids[i]+"','P_PI')><img src='/images/icon/add_16.gif' alt='Create MF'></a>&nbsp;");
                				}
                			}
                			var vat_no = $("#tr1_"+ids[i]).children(".vat_no").html();
                			var temp = [];
                			temp.push("<div class='none' id='vatDialog4_"+ids[i]+"'>");
                			if(systemType == 1){
                				temp.push("<form action='/ar/save_to_chead' method='post' id='form4_"+ids[i]+"'>");
                			}
                			if(systemType == 2){
                				temp.push("<form action='/ap/save_to_shead' method='post' id='form4_"+ids[i]+"'>");
                			}
                			temp.push("<input type='hidden' name='id' value='"+ids[i]+"'/>");
                			temp.push("<div class='box6'>");
                			temp.push("<ul>");
                			temp.push("<li class='li1'>VAT No Range</li>");
                			temp.push("<li class='li2'><input type='text' name='vat_no' id='vat_no4_"+ids[i]+"' /></li>");
                			temp.push("<li class='li4'>(e.g. 00000001~00000010,00000099)</li>");
                			temp.push("</ul>");
                			temp.push("<div class='clear'></div>");
                			temp.push("</div>");
                			temp.push("<div class='box7'>");
                			temp.push("<div style='display:none'><input type='text' /></div>");
                			temp.push("<input type=submit class=btn value=Submit onclick=ajaxForm('#form4_"+ids[i]+"','Save&nbsp;Success!','0','0',saveNewMcnForm('"+ids[i]+"','"+vat_no+"'),'listMcn')>");
                			temp.push("&nbsp;<input type='button' class='btn' value='Cancel' onclick='closeBlock()'/>");
                			temp.push("</div>");
                			temp.push("</form>");
                			temp.push("</div>");
                			str  = temp.join("");
                			$("#tabs-0").append(str);
            			}
            			$("#tr1_"+ids[i]).children(".head").children(".cboxClass").attr("checked",false)
            			disableBtn(['#btn_set_vat_info','#btn_to_new','#btn_to_confirm','#btn_to_reserve','#btn_to_post','#btn_to_cancel'], true)
            		}
            	}
            	closeBlock();
            }
        	else if(type=='saveVat'){
            	if(data.types==0){
	            	var ids  = data.kws.ids.split(",");
	        		for(var i=0;i<ids.length;i++){
	        			$("#tr1_"+ids[i]).children("#vat_no_"+ids[i]).html(data.kws.vat_no);
	        			$("#tr1_"+ids[i]).children(".vatDate").html(data.kws.vat_date);
	        			$("#tr1_"+ids[i]).children(".head").children(".cboxClass").attr("checked",false);
	        		}
	        		disableBtn(['#btn_set_vat_info','#btn_to_new','#btn_to_confirm','#btn_to_reserve','#btn_to_post','#btn_to_cancel'], true)
            	}
        		closeBlock();
            }
        	else if(type=='paymentDate'){
            	if(data.types == 0){
	            	var ids  = data.ids.split(",");
	        		for(var i=0;i<ids.length;i++){
	        			$("#tr1_"+ids[i]).children(".payment_date").html(data.payment_date);
	        			$("#tr1_"+ids[i]).children(".head").children(".cboxClass").attr("checked",false);
	        		}
	        		disableBtn(['#btn_set_vat_info','#btn_to_new','#btn_to_confirm','#btn_to_reserve','#btn_to_post','#btn_to_cancel'], true)
            	}
        		closeBlock();
            }
            if(data.types==0){
            	closeBlock();
            	showMsg(data.messages);
            }
            else{
            	closeBlock();
            	showError(data.messages);
            }
        } 
    }); 
}

var ajaxGet = function(hrefs, id, queryString){
	$.ajax({
		type: "get",
		url: hrefs,
		beforeSend: function(XMLHttpRequest){
			showWaiting();
		},
		success: function(data,textStatus){
			if(queryString == "sheet"){
				var data = $(data).find(id).html();
			}
			$(id).html(data);
		},
		complete: function(XMLHttpRequest, textStatus){
			if(id=="#tabs"){
				replayLink(queryString,".pager_link");
			}
			closeBlock();
		},
		error: function(){
			showError("Error!");
		}
	});
} 

var ajaxPage = function(hrefs,id,queryString,pageSpace,topSpace,cate){
	$.ajax({
		type: "get",
		url: hrefs,
		beforeSend: function(XMLHttpRequest){
			showWaiting();
		},
		success: function(data,textStatus){
			if(queryString == "sheet"){
				var data = $(data).find(id).html();
			}
			$(id).html(data);
		},
		complete: function(XMLHttpRequest, textStatus){
			if(id=="#tabs"){
				replayLink(queryString,".pager_link");
			}
			if(pageSpace&&topSpace){
				if(cate == 1){
					$("#pageSpace").prepend(pageSpace);
					$("#topSpace").prepend(topSpace);
				}
				else{
					$("#pageSpace").replaceWith("<td id=\"pageSpace\" style=\"border-right: 0px none; border-bottom: 0px none; text-align: left; font-weight: bold;\" colspan=\"22\">"+pageSpace+"</td>");
					$("#topSpace").replaceWith("<div id=\"topSpace\" style=\"font-weight: bold;\" class=\"r\">"+topSpace+"</div>");
				}
			}
			closeBlock();
		},
		error: function(){
			showError("Error!");
		}
	});
}

var goPage = function(queryString){
	cate = 1
	if(queryString.search("pre")>-1){
		cate = 0
	}else{
		$("#pageSpace").children("a").each(function(index){
			$(this).html(index+1);
			var limit  = $(this).attr("limit");
			var offset = $(this).attr("offset");
			$(this).replaceWith("<a href='javascript:void(0)' class='pager_link' onclick=goPage('"+queryString+'&cate=pre'+'&limit='+limit+'&offset='+offset+"') cate='pre' limit='"+limit+"' offset='"+offset+"' >"+$(this).html()+"</a>");
		})
		$("#topSpace").children("a").each(function(index){
			$(this).html(index+1);
			var limit  = $(this).attr("limit");
			var offset = $(this).attr("offset");
			$(this).replaceWith("<a href='javascript:void(0)' class='pager_link' onclick=goPage('"+queryString+'&cate=pre'+'&limit='+limit+'&offset='+offset+"') cate='pre' limit='"+limit+"' offset='"+offset+"' >"+$(this).html()+"</a>");
		})
	}
	var pageSpace = $("#pageSpace").html();
	var topSpace  = $("#topSpace").html();
	ajaxPage(queryString, "#tabs", queryString, pageSpace, topSpace, cate);
}

var replayLink = function(queryString,pager_link){
	$(pager_link).each(function(){
		//$(this).attr("href",$(this).attr("href")+"&"+queryString);
		indexCount = queryString.indexOf("&page")
		if(indexCount>0){
			queryString = queryString.substring(0,queryString.indexOf("&page"));
		}
		var count = $(this).attr("next");
		var cate  = $(this).attr("cate");
		var limit = $(this).attr("limit");
		var offset = $(this).attr("offset");
		//var title = $("#tabs").find("a[href='#tabs-0']").html()+'&nbsp;page'+count;
		if($("#cust").val()==1){
			$(this).replaceWith("<a href='javascript:void(0)' class='pager_link' onclick=viewPage('"+queryString+'&page='+count+'&viewPager='+count+"','"+count+"') >"+$(this).html()+"</a>");
		}else{
			$(this).replaceWith("<a href='javascript:void(0)' class='pager_link' onclick=goPage('"+queryString+'&page='+count+'&viewPager='+count+"') cate='"+cate+"' limit='"+limit+"' offset='"+offset+"' >"+$(this).html()+"</a>");
		}
		
		//$(this).attr({href:'javascript:void(0)',onclick:"javascript:viewAll('"+queryString+'&page='+$(this).html()+"')"})
	})
}

var deleteItem = function(url,id,type,ids,ref){
    var str = []
    $("."+id+" .dboxClass").each(function(i, obj){
        var jq=$(obj)
        if(jq.attr('checked'))
            str.push(jq.val())
    })
    if(str == ""){
    	showError("You must select one");
    	return false;
    }
    var tuple = {
    	'id':str.join(','),
    	'type':type
    };
	$.ajax({
		type: "get",
		url: url,
		data:tuple,
		beforeSend: function(XMLHttpRequest){
			showWaiting();
		},
		success: function(data,textStatus){
			
		},
		complete: function(XMLHttpRequest, textStatus){
			if(type == "PI"){
				viewPhead(ids, ref)
			}else if(type == "SI"){
				viewThead(ids, ref)
			}else if(type == "MF" || type == "NMF"){
				viewMhead(ids, ref)
			}
			else if(type == "CST"){
				viewOhead(ids, ref)
			}
			else if(type == "CCN"){
				viewNhead(ids, ref)
			}
			closeBlock();
		},
		error: function(){
			showError("Error!");
		}
	});
}


var viewPhead = function(id, ref){
    showWaiting();
    $("#scroll").hide();
    $.get("/ap/ajax_view_phead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewPI = function(invoice_no){
    showWaiting();
    $("#scroll").hide();
    $.get("/ap/ajax_view_pi",{invoice_no:invoice_no}, function(html){
        tab_title = invoice_no;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var searchQuery;
var viewStatement = function(id, ref){
	searchQuery = {};
    showWaiting();
    $("#scroll").hide();
    $.get("/ap/ajax_view_statement",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewStatement1 = function(id, ref, pi_pager, dn_pager){
	var data = "id="+id+"&pi_pager="+pi_pager+"&dn_pager="+dn_pager+""
	jQuery.each(searchQuery, function(i, field){
		  if (field.name == "dn_pager" || field.name == "pi_pager" || field.name == "id"){
		  }
		  else{
			  data = data+"&"+field.name+"="+field.value;
		  }
		});
	showWaiting();
    $("#scroll").hide();
    $.get("/ap/ajax_view_statement", data, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var openNewMsnForm3=function(thead_id,vat_no){
	var data = vat_no.split(",");
	$("#form25_"+thead_id+" #vat_no25_"+thead_id).autocomplete(data);
	$.get("/ap/ajax_check_msn",{id:thead_id}, function(data){
		  if(data.Msg == 0){
			showError("You can't create MSN!");
			return false;
		  }else{
		    $.blockUI({
		        theme:false,
		        title:'Set VAT Info',
		        message:$('#vatDialog5_'+thead_id),
		        baseZ: 100,
		        css:{width: '350px'}
		    });
		  }
	},'json');
}

var openNewMfForm=function(thead_id,types){
	var vat_no = $("#tr1_"+thead_id+" #vat_no_"+thead_id).html();
	if(vat_no =='' || vat_no==null || vat_no=='&nbsp;'){
		vat_no = $("#vat_no_"+thead_id).html();
	}
	if(vat_no=='&nbsp;') vat_no = ''
	$("#form26_"+thead_id+" #vat_no26_"+thead_id).val(vat_no);
	$("#form26_"+thead_id+" #vat_no26_"+thead_id).autocomplete(vat_no);
	$.get("/ap/ajax_check_mf",{id:thead_id,type:types}, function(data){
		  if(data.Msg == 0){
		    var msg;
		    if(data.type == 'P_PI'){
				msg = "You have finished the payment of this MPI, so you can't issue any MF!";
		    }else{
		    	msg = "You have finished the payment of this MSN, so you can't issue any MF!";
		    }
			showError(msg);
			return false;
		  }else{
			$.blockUI({
		        theme:false,
		        title:'Set VAT Info',
		        message:$('#vatDialog26_'+thead_id),
		        baseZ: 100,
		        css:{width: '350px'}
		    }); 
		  }
	},'json');
}

var openNewPaymentForm=function(thead_id){
	$.blockUI({
        theme:false,
        title:'Set VAT Info',
        message:$('#vatDialog27_'+thead_id),
        baseZ: 100,
        css:{width: '350px'}
    });
}

var openNewDateForm=function(id){
	$.blockUI({
        theme:false,
        title:'Set Date Info',
        message:$('#vatDialog27_'+id),
        baseZ: 100,
        css:{width: '350px'}
    });
}

var changeParseDate = function(obj, ids){
	var id = obj.attr("id")
	var name = obj.attr("name");
	var queryFiled = "supplier_code";
	if(id == "supplier_code"){
		queryFiled = "reconciliation_lot";
	}
	if(id == "reconciliation_lot"){
		queryFiled = "billing_month,kingdee_date,payment_date"
	}
	getSupplier(name, $("*[cid='dzd_search']").serialize(), queryFiled, ids);
}

var setDateType;
var openNewSetDateForm=function(id, type){
	setDateType = type;
	var supplier_code = $("input[name='supplier_code'][cid='dzd_search']")
	$("*[cid='dzd_search']").each(function(){
		if($(this).attr("name") != "supplier_code"){
			if($(this).attr("name") == "reconciliation_lot"){
				$(this).html("")
			}else{
				$(this).val("")
			}
		}else{
			$(this).val("")
		}	
	})
	changeParseDate(supplier_code, id);
	$.blockUI({
        theme:false,
        title:'Set Date Info',
        message:$('#vatDialog27_'+id),
        baseZ: 100,
        css:{width: '480px'}
    }); 
}

var saveNewPaymentForm = function(thead_id){
	var payment_date = $("#"+thead_id+"").val();
	$("#ids2").val(getCboxStr);
	if(payment_date.length == 0){
		showError("Please input the Payment Date!");
		return false;
	}
}

var viewShead = function(id, ref){
    showWaiting();
	$("#scroll").hide();
    $.get("/ap/ajax_view_shead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var viewMhead = function(id, ref){
    showWaiting();
	$("#scroll").hide();
    $.get("/ap/ajax_view_mhead",{id:id}, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        resetLink();
        closeBlock();
    });
}

var openNewMsnForm=function(thead_id){
	var vat_no = $("#tr1_"+thead_id+" #vat_no_"+thead_id).html()
	if(vat_no=='&nbsp;') vat_no = ''
	$("#form4_"+thead_id+" #vat_no4_"+thead_id).val(vat_no);
	var data = $("#tr1_"+thead_id+" #vat_no_"+thead_id).html().split(",");
	$("#form4_"+thead_id+" #vat_no4_"+thead_id).autocomplete(data);
	$.get("/ap/ajax_check_msn",{id:thead_id}, function(data){
		  if(data.Msg == 0){
			showError("You can't create MSN!");
			return false;
		  }else{
			$.blockUI({
		        theme:false,
		        title:'Set VAT Info',
		        message:$('#vatDialog4_'+thead_id),
		        baseZ: 100,
		        css:{width: '350px'}
		    }); 
		  }
	},'json');
}

var changeHeadFont = function(){
	if(initType() == 2) {
		var html1 = "ERP Data:<span class=\"cl5\">&nbsp;&nbsp;&nbsp;&nbsp;</span> MPI Data:<span class=\"cl3\">&nbsp;&nbsp;&nbsp;&nbsp;</span> MSN Data:<span class=\"cl4\">&nbsp;&nbsp;&nbsp;&nbsp;</span>"
		$("#change-head-font").html(html1)
	}
	else if(initType() == 3){
		var html2 = "ERP Data:<span class=\"cl5\">&nbsp;&nbsp;&nbsp;&nbsp;</span> CST Data:<span class=\"cl3\">&nbsp;&nbsp;&nbsp;&nbsp;</span> CCN Data:<span class=\"cl4\">&nbsp;&nbsp;&nbsp;&nbsp;</span>"
		$("#change-head-font").html(html2)
	}
}

var openDialogSN = function(id){
	$.fx.speeds._default = 1000;
	$(function() {
		$( "#dialog_"+id).dialog({
			autoOpen: false,
			show: "blind",
			hide: "explode",
			maxWidth:'1200',
			width:800,
			title:'SN',
			minHeight:200,
			height:500
			
		});
		$("#dialog_"+id).dialog("open");
		return false;
	});
}

var autoDialog = function(id, title){
	$.fx.speeds._default = 1000;
	$(function() {
		$( "#dialog_"+id).dialog({
			autoOpen: false,
			show: "blind",
			hide: "explode",
			maxWidth:'1200',
			width:800,
			title:title,
			minHeight:200,
			height:500
			
		});
		$("#dialog_"+id).dialog("open");
		return false;
	});
}

var set_tax = function(id){
	var tax = $(id).find(".tax")
	tax.each(function(){
		$(this).val(tax.eq(0).val());
	})
}
var head_id, head_query, head_type;

var relationSI = function(id, t_head_id, type, ref){
	temp1 = []
	temp2 = []
	$(id).each(function(){
		if($(this).attr("checked")){
			temp1.push($(this).val());
		}
		else{
			temp2.push($(this).val());
		}
	})
	var query, suc, fai;
	if(type == "delete"){
		query = temp2.join(",");
		suc = "Delete Success!";
		fai = "Delete Failure!";
	}else{
		query = temp1.join(",");
		suc = "Save Success!";
		fai = "Over the MSO VAT Qty! Are you Sure related it? ";
	}
	
	head_id = t_head_id;
	head_query = query;
	head_type = type;
	
	$.get("/ar/relation_si",{relation:query,t_head_id:t_head_id,type:type}, function(data){
		  if(data.status == 1){
			showErrorQuestion(fai);
			return false;
		  }else{
			  showMsg(suc)
			  if(type == "delete"){
				  viewThead(t_head_id, ref)
			  }
			  return false;
		  }
	},'json');
}

var relatedPIPO = function(id, type){
	var str = []
	$(id+" .dboxClass").each(function(i, obj){
        var jq = $(obj);
        var tr = jq.parent("td").parent("tr");
        if(jq.attr('checked') == true && type == '3'){
        	tr.hide();
        	tr.attr('p', '3');
        }
        if(tr.attr('p') == '3' && type == '2'){
        	tr.show();
        	tr.attr('p', '0')
        }
        if(type == 1){
        	if(tr.attr('p') == '2' || tr.attr('p') == '0'){
        		jq.attr('checked', true);
        	}else{
        		jq.attr('checked', false);
        	}
        }
    })
}

var piSearchInput
var dnSearchInput
var dzdSearch = function(cls, ref, cid){
	var id = cls.substring(cls.indexOf("_")+1, cls.length);
	var serial = $(""+cls+"").find("*[cid='"+cid+"']").serializeArray();
	searchQuery = serial;
	piSearchInput = $(".piSearch_"+id+"").find("input[cid='piSearch'], select[cid='piSearch']").serializeArray();
	dnSearchInput = $(".dnSearch_"+id+"").find("input[cid='dnSearch'], select[cid='dnSearch']").serializeArray(); 
	showWaiting();
    $.get("/ap/ajax_view_statement", serial, function(html){
        tab_title = ref;
        tab_content = html;
        addTab();
        closeBlock();
    });	
}


var parseDzdInput = function(id){
	$.each(piSearchInput, function(i, n){
		$(".piSearch_"+id+"").find("*[type!='hidden'][cid='piSearch'][name='"+n.name+"']").val(n.value);
	});
	$.each(dnSearchInput, function(i, n){
		$(".dnSearch_"+id+"").find("*[type!='hidden'][cid='dnSearch'][name='"+n.name+"']").val(n.value);
	});
}

var resetDzdSearch = function(cls, id){
	var search = $(""+cls+"").find("*[cid='"+id+"']");
	$.each(search, function(i, n){
		var obj = $(this);
		var name = obj.attr('name');
		if(name="status" || name == 'supplier_code' || name =='invoice_no'|| name=='mpi_ref'|| name=='billing_month'|| name=='kingdee_date'|| name=='reconciliation_lot' || name =='payment_date'|| name=='number'|| name=='msn_ref'){
			obj.val("");
		}
	})
	piSearchInput = null;
	dnSearchInput = null;
}

var dzdImport = function(id){
	window.open("/ap/import_statement?id="+id+"");
}

var parseDate = function(obj, list, ids){
	var is_type = null;
	var supplier_code;
	if(obj.attr('name') == 'supplier_code'){
		if(setDateType == "pi"){
			supplier_code = $("input[name='supplier_code'][cid='piSearch']").val()
		}else{
			supplier_code = $("input[name='supplier_code'][cid='dnSearch']").val()
		}
	}
	var temp = ["<option value=''></option>"] 
	for(i=0; i<= list.length; i++){
		var v = list[i]
	    if(v != null && v != undefined){
	    	if(supplier_code != undefined && supplier_code.length > 0 && supplier_code.replace(/(^\s*)|(\s*$)/g, "") == list[i]){
	    		temp.push("<option value='"+list[i]+"' selected='selected'>"+list[i]+"</option>")
	    		is_type = true;
	    	}else{
	    		temp.push("<option value='"+list[i]+"'>"+list[i]+"</option>")
	    	}
	    }
	}
	options = temp.join("");
	obj.html(options);
	if(is_type){
		changeParseDate(obj, ids);
	}
}
 
var billing_month_data;
var kingdee_date_data;
var payment_date_data;
var getSupplier = function(name, value, nextObj, ids){
		var obj;
		$.ajax({
			type:"GET",
			dataType:"json",
			data:{name:name, value:value, type : setDateType, id:ids, nextChangeObj : nextObj},
			url: "/ap/ajax_get_date",
			success: function(data,textStatus){
				if(nextObj == "supplier_code"){
					obj = $("select[name='supplier_code'][cid='dzd_search']")
					parseDate(obj, data.supplier_code, ids);
				}
				if(nextObj == "reconciliation_lot"){
					obj = $("select[name='reconciliation_lot'][cid='dzd_search']")
					parseDate(obj, data.reconciliation_lot, ids);
				}
				if(nextObj == "billing_month,kingdee_date,payment_date"){
					$("input[name='billing_month_complete'][cid='dzd_search']").val('')
					obj = $("input[name='billing_month'][cid='dzd_search']");
					billing_month_data = data.billing_month;
					obj.autocomplete(data.billing_month).result(function(event, data, formatted){
			                //changeParseDate(obj);
			                $("input[name='billing_month_complete'][cid='dzd_search']").val('1')
			        });
			        
			        obj = $("input[name='kingdee_date'][cid='dzd_search']");
					kingdee_date_data = data.kingdee_date;
					obj.autocomplete(data.kingdee_date).result(function(event, data, formatted){
			                //changeParseDate(obj);
			                $("input[name='kingdee_date_complete'][cid='dzd_search']").val('1')
			        });
			        
			        $("input[name='payment_date_complete'][cid='dzd_search']").val('')
					obj = $("input[name='payment_date'][cid='dzd_search']");
					payment_date_data = data.payment_date;
					obj.autocomplete(data.payment_date).result(function(event, data, formatted){
			                $("input[name='payment_date_complete'][cid='dzd_search']").val('1')
			        });
			        
			 
				}
			},
			error: function(){
				//alert(data.Msg)
			}
		});
}

var checkSelectNoComplete = function(id, type){
    //showWaiting();
	var status;
	var check = false;
	var checkType = false;
	var selectStr = "";
    $(id+' .cboxClass').each(function(){
        if($(this).attr("checked")){
        	if(type == 'pi'){
        		status = $("input[name='mpi_b_"+$(this).val()+"']").val();
        	}else{
        		status = $("input[name='msn_b_"+$(this).val()+"_']").val();
        	}
        	check = true;
        	if(status.length > 0){
        		checkType = true;
        	}
        }
    })
    if(checkType == true){
    	showError("You can just delete the item which the item no MPI/MSN!")
    	return false;
    }
    if(check == false){
            showError("You must be select one");
        	return false;
    }
}

var openIframe = function(id, thead_id, thead_ref){
	$(id).fancybox({ 
		'width'				: '80%',
		'height'			: '80%',
		'autoScale'			: false,
		'transitionIn'		: 'none',
		'transitionOut'		: 'none',
		'type'				: 'iframe',
		onClosed	        :  function() {viewThead(thead_id, thead_ref)}
	})
}

var checkRelated = function(id){
	var parent = $("#"+id);
	var po_qty = parseInt(parent.find("input[po_qty]").attr('po_qty'));
	var unit_price;
	var idss = []
	var qty = 0;
	var arr = getCboxArr2("#"+id)
	parent.find("input[name='pi_qty']").each(function(){
		var ids = $(this).attr('ids');
		for (i = 0; i <= arr.length; i++)
		{
			if(arr[i] == ids){
				qty += parseInt($(this).val());
				unit_price = $(this).attr('unit_price')
				idss.push(ids)
			}
		}
	})
	if(qty > po_qty){
    	showError("The related SI Qty can't more than SI Qty")
    	return false;
	}else{
		ids = id.split("_");
		arr = []
		for(i = 0; i<= ids.length; i++){
			if(i>0){
				if(ids[i]!= undefined  && ids[i].length > 0){
					arr.push(ids[i])
				}
			}
		}
		$("input[name='related_"+arr.join("$")+"']").val(idss.join(','));
		$("input[name='with_out_price_"+arr.join("$")+"']").val(unit_price);
		$("td[id='with_out_price_"+arr.join("$")+"']").html(unit_price);
		$("input[name='with_out_amount_"+arr.join("$")+"']").val(Number(unit_price*qty).toFixed(2));
		$("td[id='with_out_amount_"+arr.join("$")+"']").html(Number(unit_price*qty).toFixed(2));
		
		var variance_amount = $("input[name='change_with_out_amount_"+arr.join("$")+"']").val();
		$("input[name='variance_amount_"+arr.join("$")+"']").val(Number(variance_amount - unit_price*qty).toFixed(2));
		$("td[id='variance_amount_"+arr.join("$")+"']").html(Number(variance_amount - unit_price*qty).toFixed(2));
		var variance_unit_price = $("input[name='change_with_out_price_"+arr.join("$")+"']").val();
		$("input[name='variance_price_"+arr.join("$")+"']").val(Number(variance_unit_price - unit_price).toFixed(4));
		showMsg("Save Successfully!");
		parent.dialog("close");
	}
}

var changeLine = function(obj){
	$("textarea[name*='"+obj+"']").each(function(){
		var c, le;
		$(this).keyup(function(){
			c = $(this).val();
			le = c.match(/[^ -~]/g) == null ? c.length : c.length + c.match(/[^ -~]/g).length;
			if(le > 0){
				l = Math.ceil(parseInt(le)/24);
				$(this).attr({rows:l, style:"width: 178px; border:1px solid #456A90; height: "+20*l+"px;"});
			}
		});
		$(this).mouseout(function(){
			$(this).attr({rows:1, style:"width: 178px; height: 20px;"});
		});
		$(this).mouseover(function(){
			c = $(this).val();
			le = c.match(/[^ -~]/g) == null ? c.length : c.length + c.match(/[^ -~]/g).length;
			if(le > 0){
				l = Math.ceil(parseInt(le)/24);
				$(this).attr({rows:l, style:"width: 178px; border:1px solid #456A90; height: "+20*l+"px;"});
			}
		});
	})
}