var time;
var layout;

$(function() {
    initMenu();
});

var initMenu = function(){
    $(".menu-tab li:not(.highlight)").each(function(){
        var orginImg = $(this).css("background-image");
        var replaceImg = "url(/images/images/main_05.jpg)"
        $(this).hover( 
            function(){$(this).css("background-image",replaceImg);},
            function(){$(this).css("background-image",orginImg);}
        );
    });
    $("#function-menu a img").each(function(){
        var orginImg = $(this).attr("src");
        var replaceImg = orginImg.replace("_g.jpg",".jpg");
        $(this).hover(
            function(){$(this).attr("src",replaceImg);},
            function(){$(this).attr("src",orginImg);} 
        );
    });
}

var initTr = function(){
	$(".gridTable tbody tr").each(function(){
		$(this).unbind();
		$(this).hover(
			function(){$(this).css("background-color","#edf6ff")},
			function(){$(this).removeAttr("style")}
		);
		$(this).dblclick(function(){
			if($(this).children(".head").children("input").attr("checked")){
				$(this).children(".head").children("input").removeAttr("checked");resetBtn();
			}
			else{
				$(this).children(".head").children("input").attr("checked","checked");resetBtn();
			}
		});	
	});
}

var initTr2 = function(){
	$("input[name='select_id']").click(function(){
		var parentObj = $(this).parent("td").parent("tr")
		if($(this).attr("checked")){
			parentObj.css("background-color","#A5B5CC")
		}
		else{
			parentObj.removeAttr("style")
		}
	})

	$(".gridTable tbody tr").each(function(){
		$(this).unbind("dblclick");
		$(this).dblclick(function(){
			if($(this).children(".head").children("input").attr("checked")){
				$(this).children(".head").children("input").removeAttr("checked");
				$(this).removeAttr("style")
			}
			else{
				$(this).children(".head").children("input").attr("checked","checked");
				$(this).css("background-color","#A5B5CC")
			}
		});	

	});
}

var initTotal = function(){
	$(".check_numbers").each(function(){
		var linkAge = $(this)
		$(this).focus(function(){ 
			time = window.setInterval(function(){
				substring(linkAge);
			},100);
		});	
		$(this).blur(function(){
			window.clearInterval(time);
			substring($(this));
		});
	})
}

var initSumQty = function(){
	$("input[redirct]").each(function(){
		var linkAge = $(this)
		$(this).focus(function(){ 
			time = window.setInterval(function(){
				sumQty(linkAge);
			},100);
		});	
		$(this).blur(function(){
			window.clearInterval(time);
			sumQty($(this));
		});
	})
}

function sumQty(obj){
	var sumqty = 0;
	var ids = obj.attr("ids");
	$("input[redirct=qty_"+ids+"]").each(function(){
		if($(this).val().length > 0){
			sumqty += parseInt($(this).val())
		}
	})
	var objs = $("input[name='"+obj.attr("redirct")+"']")
	objs.val(sumqty);
	Statement(objs);
	if(objs[0]) changeVal(objs);
}

var initChangeVal = function(){
	$("#tabs :text").each(function(){
		var obj = $(this)
		$(this).focus(function(){
			time = window.setInterval(function(){
				changeVal(obj);
			},150);
		});
		$(this).blur(function(){
			window.clearInterval(time);
			changeVal($(this));
		});
		
	})
}

var initPayment = function(){
	var total_amounts = {};
	$(".payment").each(function(){
		var amount = 0;
		var mHead_id = $(this).attr("Head_id");
		var invoice = $(this).attr("invoice");
		var parentCate = $(this).attr("cate");
		$("input[invoice='"+invoice+"'][cate='"+parentCate+"'][Head_id='"+mHead_id+"']").each(function(){
			var objVal  = $(this).val();
			if(isNaN(Number(objVal)) == false){
				amount += Number(objVal)
			} 
		})
		if(parentCate == 'charge'){
			var chargeVal = $("*[invoice='"+invoice+"'][thead_id='"+$(this).attr('thead_id')+"'][cate='other_charge']") 
			if(chargeVal.attr('type') == 'text'){
				chargeVal = chargeVal.val()
			}else{
				chargeVal = chargeVal.html()
			}
			if(isNaN(Number(chargeVal)) == false){
				amount += Number(chargeVal)
			}
		}
		if(parentCate == 'item_amount' || parentCate == 'charge'){
			if(total_amounts[""+invoice+"_"+mHead_id+""]){
				total_amounts[""+invoice+"_"+mHead_id+""] = total_amounts[""+invoice+"_"+mHead_id+""] + amount
			}else{
				total_amounts[""+invoice+"_"+mHead_id+""] = amount
			}
		}
		$(this).html(amount.toFixed(2));
	})
	$.each(total_amounts, function(i){
		m = i.split("_");
		$("td[id='order_amount_without_tax_"+m[0]+"'][head_id='"+m[1]+"']").html(total_amounts[i]);
	})
}

var initStatement = function(){
	$("input[statement]").each(function(){
		var linkAge = $(this)
		$(this).focus(function(){ 
			time = window.setInterval(function(){
				Statement(linkAge);
			},100);
		});	
		$(this).blur(function(){
			window.clearInterval(time);
			Statement($(this));
		});
	})
}

var Statement = function(obj){
	var ids = obj.attr("ids");
	var qty = $("input[name='qty_"+ids+"']").val();
	var unit = $("input[name='unit_"+ids+"']").val();
	if(unit == null || unit == undefined || unit == "" || unit=="&nbsp;" ||unit.length == 0){
		unit = $("input[name='price_"+ids+"']").val();
	}
	var tax_rate = $("input[name='tax_rate_"+ids+"']").val();
	var rmb_unit = Number(unit/(1+parseFloat(tax_rate))).toFixed(3);
	if(tax_rate == null || tax_rate == "" || tax_rate=="&nbsp;" ||tax_rate.length == 0){
		tax_rate = parseInt($("input[name='tax_"+ids+"']").val())/100;
		rmb_unit = Number(unit*(1+parseFloat(tax_rate))).toFixed(3);
	}
	var rmb_amount = Number(rmb_unit * qty).toFixed(3);
	var rmb_amount_p = Number(unit * qty).toFixed(2);
	var rmb_tax = Number(rmb_amount_p - rmb_amount).toFixed(3);
	
	$("#rmb_unit_"+ids+"").html(rmb_unit);
	$("#rmb_amount_"+ids+"").html(rmb_amount);
	$("#rmb_tax_"+ids+"").html(rmb_tax);
	$("#rmb_amount_p_"+ids+"").html(rmb_amount_p);
	
	$("input[name='rmb_unit_"+ids+"']").val(rmb_unit);
	$("input[name='rmb_amount_"+ids+"']").val(rmb_amount);
	$("input[name='rmb_tax_"+ids+"']").val(rmb_tax);
	$("input[name='rmb_amount_p_"+ids+"']").val(rmb_amount_p);
	
	$("input[name='item_amount_"+ids+"']").val(rmb_amount_p);
	$("input[name='order_amount_"+ids+"']").val(rmb_amount);
	
	$("#item_amount_"+ids+"").html(rmb_amount_p);
	$("#item_base_amount_"+ids+"").html(rmb_amount_p);
	$("input[name='item_amount_"+ids+"']").val(rmb_amount_p);
	$("input[name='item_base_amount_"+ids+"']").val(rmb_amount_p);
	initPayment();
}

var initGetAll = function(id){
	var quantity_total = 0
	var total_amount_total = 0
	var total_amount_without_tax_total = 0
	var tax_total = 0
	var total_amount_total_amount_total = 0
	var freights = 0
	var item_totals = 0
	var total_vat_total_amounts = 0
	$(id+" .quantity").each(function(){
		if(isNaN(Number($(this).html()))==false){
			quantity_total += Number($(this).html());
		}
	})
	$(id+" .total_amount").each(function(){
		if(isNaN(Number($(this).html()))==false){
			total_amount_total += Number($(this).html());
		}
	})
	$(id+" .total_amount_without_tax").each(function(){
		if(isNaN(Number($(this).html()))==false){
			total_amount_without_tax_total += Number($(this).html());
		}
	})
	$(id+" .tax").each(function(){
		if(isNaN(Number($(this).html()))==false){
			tax_total += Number($(this).html());
		}
	})
	$(id+" .total_amount_total_amount").each(function(){
		if(isNaN(Number($(this).html()))==false){
			total_amount_total_amount_total += Number($(this).html());
		}
	})
	$(id+" .freights").each(function(){
		if(isNaN(Number($(this).html()))==false){
			freights += Number($(this).html());
		}
	})
	$(id+" .item_total").each(function(){
		if(isNaN(Number($(this).html()))==false){
			item_totals += Number($(this).html());
		}
	})
	$(id+" .total_vat_total_amount").each(function(){
		if(isNaN(Number($(this).html()))==false){
			total_vat_total_amounts += Number($(this).html());
		}
	})
	$(id+" .total_amount_all").html(total_amount_total.toFixed(2))
	$(id+" .total_amount_without_tax_all").html(total_amount_without_tax_total.toFixed(2))
	$(id+" .tax_all").html(tax_total.toFixed(2))
	$(id+" .total_amount_total_amount_all").html(total_amount_total_amount_total.toFixed(2))
	$(id+" .quantity_all").html(quantity_total)
	$(id+" .freights_all").html(freights.toFixed(2))
	$(id+" .item_total_all").html(item_totals.toFixed(2))
	$(id+" .total_vat_total_amount_all").html(total_vat_total_amounts.toFixed(2))
}

var initToogle = function(){
	$(".other_charge_tab").each(function(){
		$(this).toggle(
				function(){
					$(this).next(".other_charge_content").show()
				},
				function(){ 
					$(this).next(".other_charge_content").hide()
				}
		)
	})
}

var intiParsePrice = function(){
	$(".unit_price_detail").each(function(){
		var num = new Number($(this).html());
		$(this).html(num.toFixed(6));
	})
}

var initTips = function(){
	$("td").tipsy({gravity: 'sw'})
}

var initDetail = function(obj){
	$(".so_head_"+obj).each(function(){
		var detailClass = $(this).attr("pre_detail");
		if($(detailClass).length == 0){
			$(this).hide();
		}
	})
	
}

var initScroll = function(){
	$("#scroll").width($("#theadObj").width());
	$("#theadObj").children("th").each(function(index){
		var scrollObj   = $("#scrollObj").children("th").eq(index)
		var theadWdith  = $(this).width();
		var scrollWdith = scrollObj.width();

		scrollObj.width(theadWdith)
		
	})
	var warpOffset  = $(".ui-layout-center").offset();
	var boxOffset   = $("#scroll").offset();
	var boxPosition = $("#scroll").position();
	$(".ui-layout-center").scroll( function() { 
		var boxPositionTop = Math.abs(boxPosition.top);
		var checkShow = boxPositionTop - $(".ui-layout-center").scrollTop();
		if(checkShow<0){
			if(!$("#tabs-0").hasClass("ui-tabs-hide")){
				$("#scroll").css("top",$(".ui-layout-center").scrollTop()).show();
			}
		}else{
			$("#scroll").hide();
		}
	});
}

var initType  = function(){
	var url = document.location.href;
	if (url.search("\/ar\/")>-1){
		return 1;
	}
	if (url.search("\/ap\/")>-1){
		return 2;
	}
	if (url.search("\/cost\/")>-1){
		return 3;
	}
	if (url.search("\/report\/")>-1){
		return 4;
	}
}

var resetLink = function(){
    $('.toggle2').parent().next().hide();
    $(".toggle_down").unbind("click")
    $('.toggle_down').click(function(){toggleIcon($(this))})
    $(".toggle_right").unbind("click")
    $('.toggle_right').click(function(){toggleIcon($(this))})
    $(".btn").unbind("hover")
    $('.btn').hover(
        function () {$(this).addClass("btnhov");},
        function () {$(this).removeClass("btnhov");}
    );
    $(".toggle_max").unbind("click")
    $('.toggle_max').click(function(){toggleScreen($(this))})
    $(".toggle_min").unbind("click")
    $('.toggle_min').click(function(){toggleScreen($(this))})
    $(".numeric").numeric();
    $('.west').tipsy({gravity: 'w'});
    //$("tbody>tr:odd").addClass("odd");
    //$("tbody>tr:even").addClass("even");
    //$("tbody>tr").mouseover(function(){$(this).addClass("hover");}).mouseout(function(){$(this).removeClass("hover");});
    initDate();
    resetBtn();
}

var historyGo = function(){history.forward(1);}
var historyBack = function(){history.back(-1);}
var resetForm = function(){$('form')[0].reset();}
var toggleScreen = function(obj){
    if($(obj).attr('class')=='toggle_min'){
        layout.open('north');
        layout.open('west');
    }else if($(obj).attr('class')=='toggle_max'){
        layout.close('north');
        layout.close('west');
    }
}

var disableBtn = function(obj, bool){
    if(!(obj instanceof Array)) obj = [obj]
    for(var i=0;i<obj.length;i++){
        var jq = $(obj[i]);
        if(bool){jq.attr('disabled', true);jq.addClass("btndisable");}
        else{jq.attr('disabled', false);jq.removeClass("btndisable");}
    }
}

var initDate = function(){
    var dateFormat = 'yy-mm-dd';
    var dateFormat2 = 'yy.mm.dd'
    $('.datePicker').datepicker({
        dateFormat: dateFormat,
		changeYear: true,
        changeMonth: true,
        showOn: 'button',
        buttonImage: '../images/calendar.gif',
        buttonImageOnly: true,
        beforeShow: function(input,inst) {"option","hide"}
    });
    $('.datePickerNoImg').datepicker({
        dateFormat: dateFormat,
        changeMonth: true,
        changeYear: true
    });
    $('.datePickerNoImg2').datepicker({
        dateFormat: dateFormat2,
        changeMonth: true,
        changeYear: true
    });
}

var toggleIcon = function(obj){
    if($(obj).attr('class')=='toggle_down'){
        $(obj).parent().next().slideUp("fast");
        $(obj).attr('class', 'toggle_right')
    }else{
        $(obj).parent().next().slideDown("fast");
        $(obj).attr('class', 'toggle_down')
    }
}

var resetBtn = function(){}
var selectAll = function(obj){
    $("tbody").each(function(){
        if(!$(this).attr("class"))
            if($(obj).attr("checked")){
                 $(this).find(".cboxClass").attr("checked","checked");
            }else{
                 $(this).find(".cboxClass").removeAttr("checked");
            }
        	resetBtn();
    }) 
}

var selectAllDetail = function(obj,selectBox){$(obj).attr("checked") ? $("."+selectBox+"[type='checkbox']").attr("checked","checked") :  $("."+selectBox+"[type='checkbox']").removeAttr("checked");resetBtn();}
var selectOne = function(){resetBtn();}
var getCboxArr = function(){
    var str = []
    $(".cboxClass").each(function(i, obj){
        var jq=$(obj)
        if(jq.attr('checked'))
            str.push(jq.val())
    })
    return str
}
var getCboxArr2 = function(obj){
    var str = []
    $(obj).find(".cboxClass").each(function(i, obj){
        var jq=$(obj)
        if(jq.attr('checked'))
            str.push(jq.val())
    })
    return str
}
var getCboxStr = function(){return getCboxArr().join(',')}
var validateCbox = function(){
    if(getCboxArr().length==0){
        showError('Please select at least one checkbox!');return false;
    }else return true;
}

var showError = function(msg){
    //if(msg instanceof Array) msg=msg.join('<br/>');
    //$.modaldialog.error(msg);
    $.prompt(msg,{opacity: 0.6,prefix:'cleanred',top:'40%',left:'35%', zIndex:1011});
}

function no_related_si(e,v,m,f){
	if(e){
		query = head_query;
		t_head_id = head_id;
		type = head_type;
		$.get("/ar/relation_si",{relation:query,t_head_id:t_head_id,type:type, head_type:'no_check'}, function(data){
			if(data.status == 0){
				showMsg("Save Success!");
			}
		},'json');
	}
}

var showErrorQuestion = function(msg){
    //if(msg instanceof Array) msg=msg.join('<br/>');
    //$.modaldialog.error(msg);
    $.prompt(msg,{callback: no_related_si, buttons: {Yes: true, No:false, Cancel:false}, opacity: 0.6,prefix:'cleanred',top:'40%',left:'35%'});
}
 

var showMsg = function(msg){
    //if(msg instanceof Array) msg=msg.join('<br/>');
    //$.growlUI('Success','  ');
    //$.modaldialog.success(msg);
    //$.prompt(msg,{opacity: 0.6,prefix:'cleanblue'});
    $.prompt(msg,{opacity: 0.6,prefix:'cleanblue',top:'40%',left:'35%',useiframe:true, zIndex:1052});
}

var showMsgBool = function(msg){
    //if(msg instanceof Array) msg=msg.join('<br/>');
    //$.growlUI('Success','  ');
    //$.modaldialog.success(msg);
    //$.prompt(msg,{opacity: 0.6,prefix:'cleanblue'});
	$.prompt(msg,{opacity: 0.6,prefix:'cleanblue',top:'40%',left:'35%',useiframe:true,buttons: { Ok: true, Cancel: false }});
}

var showMsgBoolForSI = function(msg){
    //if(msg instanceof Array) msg=msg.join('<br/>');
    //$.growlUI('Success','  ');
    //$.modaldialog.success(msg);
    //$.prompt(msg,{opacity: 0.6,prefix:'cleanblue'});
	$.prompt(msg,{opacity: 0.6,prefix:'cleanblue',top:'40%',left:'35%',useiframe:true,buttons: { Ok: true, Cancel: false }, callback: ifOKReturnTrue});
}

var closeMsg = function(){
    //if(msg instanceof Array) msg=msg.join('<br/>');
    //$.growlUI('Success','  ');
    //$.modaldialog.success(msg);
    //$.prompt(msg,{opacity: 0.6,prefix:'cleanblue'});
    $.prompt.close();
}

var closeAll = function(){$('.toggle').hide()}
var openAll = function(){$('.toggle').show()}
var toggleOne = function(id){$('#'+id).toggle()}
var viewThead = function(id){$('#tr2_'+id).toggle();}
var showWaiting = function(){$.blockUI({baseZ:1013, message: '<img src="../images/busy.gif" /> loading...',css:{width:'150px',padding:'5px 0',fontSize:'16px',fontWeight:'400'}})}
var closeBlock = function(){$.unblockUI()};
var checkTime  = function(str){
	var r = str.match(/^(\d{1,4})(-|\/)(\d{1,2})\2(\d{1,2})$/);  
	if(r==null)return   false;   var   d   =   new   Date(r[1],   r[3]-1,   r[4]);  
	return(d.getFullYear()==r[1]&&(d.getMonth()+1)==r[3]&&d.getDate()==r[4]);
} 

var substring = function(subCheck) {
	var val = subCheck.val(); 
	subCheck.parent("td").prev(".available_qty").html(val);
}

var changeVal = function(obj){
	var total_amount =  null;
	var unit_price =  null;
	var total_amount_without_tax =  null;
	var tax =  null;
	var total_amount_total_amount =  null;
	var total_vat_total_amount = null;
	var tax_rate = 1.17;
	var val = obj.val();
	var cate = obj.attr('cate');
	if(val.length == 0 && obj.hasClass("tax")){
		obj.val("0")
		obj.attr("tax_rate", "0")
	}
	if(obj.attr("tax_rate")>=0){
		if(obj.hasClass("tax")){
			if(val.length == 0){
				$("input[tax_rate][ids="+obj.attr("ids")+"]").attr("tax_rate",0);
			}else{
				$("input[tax_rate][ids="+obj.attr("ids")+"]").attr("tax_rate",val/100);
			}
		}
		if(obj.hasClass("price")){
			$("input[unit_price][ids="+obj.attr("ids")+"]").attr("unit_price",obj.val());
		}
	}
	var id  = obj.attr("name")+"_"+obj.attr("cate"); 
	var ids = obj.attr("ids")+"_"+obj.attr("cate");
	var tr  = obj.attr("cate")+"_"+obj.attr("ids");
	var ava_qty = $("tr[name='"+tr+"']").children(".available_qty").html()
	var unit_price = new Number($("input[name='price_"+obj.attr('ids')+"'][cate='detail']").val());
	if(ava_qty && Number(val) > Number(ava_qty) && obj.hasClass("qty")){
		obj.css("color","red");
	}
	else{
		obj.css("color","#222222");
	}
	if(id.search("price")>-1){
		if(obj.attr("tax_rate")){
			$("#unit_price_tax_"+ids).html(obj.attr("unit_price"))
		}else{
			$("#unit_price_tax_"+ids).html(val)
		}
	}
	else{
		$("#"+id).html(val);
		if(obj.attr('forid')){
			$("#"+obj.attr('forid')).html(val);
		}
		if(id.search("desc")<0){
			if(val==0 && id.search("qty")>=0 ){
				$("#"+tr).hide();
			}
			else{
				$("#"+tr).show();
			}
		}
	}
	total_vat_total_amount = $("input[name='vat_total_"+obj.attr("ids")+"'][cate='"+obj.attr("cate")+"']").val()
	total_total_amount = $("input[name='total_"+obj.attr("ids")+"'][cate='"+obj.attr("cate")+"']").val()
	other_charge_amount = $("input[name='"+obj.attr("ids")+"'][cate='"+obj.attr("cate")+"']").val()
	if(obj.attr("tax_rate")>=0){
		if (obj.attr("include_tax") == 0){
			$("#unit_price_tax_"+ids).html((obj.attr("unit_price")/ (parseFloat(obj.attr("tax_rate"))+1)).toFixed(6))
			total_amount = $("#qty_"+ids).html() * unit_price
			total_amount_without_tax = $("#unit_price_tax_"+ids).html()*$("#qty_"+ids).html()
			tax = total_amount - total_amount_without_tax 
			total_amount_total_amount = total_amount
		}
		else
		{	
			unit_price = unit_price * (parseFloat(obj.attr("tax_rate"))+1)
			total_amount = $("#qty_"+ids).html() * unit_price
			total_amount_without_tax = $("#unit_price_tax_"+ids).html()*$("#qty_"+ids).html()
			tax = total_amount - total_amount_without_tax 
			total_amount_total_amount = total_amount
		}
	}
	else{
		total_amount = $("#qty_"+ids).html()*$("#unit_price_"+ids).html()
		unit_price = $("#unit_price_tax_"+ids).html()* tax_rate
		total_amount_without_tax = unit_price/tax_rate*$("#qty_"+ids).html()
		tax = unit_price*$("#qty_"+ids).html()-unit_price/tax_rate*$("#qty_"+ids).html()
		total_amount_total_amount = unit_price*$("#qty_"+ids).html()
	}
	if(cate == 'charge' || cate == 'other_charge'){
		total_amount = val * (parseFloat(tax_rate));
		total_amount_without_tax = parseFloat(val);
		tax = val*(parseFloat('0.17'))
		total_amount_total_amount = val * (parseFloat(tax_rate));
		$("#total_amount_"+ids).html(total_amount.toFixed(2));
		$("#total_amount_without_tax_"+ids).html(total_amount_without_tax.toFixed(2));
		$("#tax_"+ids).html(tax.toFixed(2));
		$("#total_amount_total_amount_"+ids).html(total_amount_total_amount.toFixed(2));
	}else{
		$("#total_amount_"+ids).html(total_amount.toFixed(2));
		$("#unit_price_"+ids).html(unit_price.toFixed(6));
		$("#total_amount_without_tax_"+ids).html(total_amount_without_tax.toFixed(2));
		$("#tax_"+ids).html(tax.toFixed(2));
		$("#total_amount_total_amount_"+ids).html(total_amount_total_amount.toFixed(2));
		$("#total_vat_total_amount_"+ids).html(total_vat_total_amount);
		$("#total_total_amount_"+ids).html(total_total_amount);
	}
	initGetAll("#"+$(".ui-tabs-selected").children("a").html());
	initPayment();
}

var initPOTotal = function(id){
	$(".charge_po_total_"+id).each(function(){
		var linkAge = $(this)
		$(this).focus(function(){ 
			time = window.setInterval(function(){
				changeChargePOQty(linkAge);
			},100);
		});	
		$(this).blur(function(){
			window.clearInterval(time);
			changeChargePOQty($(this));
		});
	})
}

var changeChargePOQty = function(obj){
	var po_obj = $("input[name='po_total_"+obj.attr('attr_id')+"']");
	var pi_obj = $("input[name='total_"+obj.attr('attr_id')+"']");
	var po_total = po_obj.val();
	var pi_total = pi_obj.val();
	if(parseFloat(po_total) < parseFloat(pi_total)){
		obj.parent('td').css('background', '#ff0000');
		pi_obj.parent('td').css('background', '#ff0000');
	}else{
		obj.parent('td').removeAttr('style');
		pi_obj.parent('td').removeAttr('style');
	}
}

var dialog;
var OpenDialog = function(url, id, tt){
	showWaiting();
    $(id).remove();
    dialog = $(id);
    if ($(id).length == 0) {
        dialog = $("<div id='"+id+"' style='display:hidden'></div>").appendTo('body');
    }
    dialog.dialog({modal: true, 
    	open: function (){$(this).load(url);},
    	minHeight: 360, 
    	width: '60%', 
    	title: tt
    	}); 
	closeBlock();
}

var closeDialog = function(id){
	dialog.dialog('destroy');
	return true;
}