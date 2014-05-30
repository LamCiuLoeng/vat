<%inherit file="vatsystem.templates.master"/>
<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b
%>
<%def name="extTitle()">r-pac - VAT System</%def>

<%def name="extCSS()">
<link rel="stylesheet" href="/css/ar.css" />
<link type="text/css" rel="stylesheet" href="/css/theme/jquery-ui-1.8.5.custom.css" />
<link type="text/css" rel="stylesheet" href="/css/jquery.autocomplete.css" />
<style type="text/css">
*{font-size:12px}
</style>
</%def>
<%def name="extJavaScript()">
 <script type="text/javascript" src="/js/jquery.autocomplete.pack.js"></script>
<script type="text/javascript" src="/js/vat_ar.js"></script>
<script type="text/javascript">
 	$(document).ready(function(){
 		initDate();
        $("#tabs").tabs();
          $(".ajaxSearchField").each(function(){
        	var type = $(this).attr("name")
        	var formID = '_form2'
        	if(type == 'customer_code' || type == 'customer')type='cust_code'
        	$(this).autocomplete("/ar/autocomplete",{
			    delay:10,
	            max:5,
	            minChars:1,
	            matchSubset:1,
	            matchContains:1,
	            cacheLength:10,
	            matchContains: true,   
	            scrollHeight: 250, 
	            width:250,
	            dataType:'json',
	            extraParams:{form:formID,type:type},
	            parse: function(data) {
	                var array = new Array();
	                for(var i=0;i<data.users.length;i++)
	                {
	                	array[array.length] = { data:data.users[i].rows, value:data.users[i].rows[type], result:data.users[i].rows[type]};
	                }
	                return array;
		        },
				highlight: function(value, term) {
						return value;
					}, 
		        formatItem: function(row) {
		                return row[type];
		        }
	
			    })
        	})
 	})
</script>
</%def>
<div class='submenu' id="function-menu">
    <ul>
        <li class='li-start'></li>
        <li class='li-center'><a href="/report/index"><img src="/images/images/VAT-ERP_g.jpg"></a></li> 
        <li class='li-end'></li>
    </ul>
</div>
<div class="nav-tree">VAT System&nbsp;&nbsp;&gt;&nbsp;&nbsp;Report</div>
<div class="case-960-all" style="width:90%;padding:10px">
    <div id="tabs">
        <ul>
            <li><a href="#tabs-1">库存商品明细账(不分Item)</a></li>
            <li><a href="#tabs-2">库存商品明细账(分Item)</a></li>
            <li><a href="#tabs-3">已收票未做成本</a></li>
            <li><a href="#tabs-4">已做成本未收票</a></li>
            <li><a href="#tabs-5">差异报表</a></li>
            <li><a href="#tabs-6">AR汇总报表</a></li>
        </ul>
        	<div id="tabs-1">
        	 <form action="/report/stock_without_item" method="get" id="_form0" style="padding:10px">
 					${stock_withOut_item_search_form()|n} 
 					<br />
 					<input type="button" class="btn" value="Export"  onclick="checkDate(0)">
 			  </form>
            </div>
            <div id="tabs-2">
            <form action="/report/stock_with_item" method="get" id="_form1" style="padding:10px">
 					${stock_with_Item_search_form()|n} 
 					<br />
 					<input type="button" class="btn" value="Export" onclick="checkDate(1)">
 			</form>
            </div>
            <div id="tabs-3">
            <form action="/report/invoice_without_cost" method="get" id="_form2" style="padding:10px">
 					
 					<br />
 					<input type="submit" class="btn" value="Export">
 			</form>
            </div>
            <div id="tabs-4">
            <form action="/report/invoice_with_cost" method="get" id="_form3" style="padding:10px">
 				
 					<br /> 
 					<input type="submit"  class="btn" value="Export" >
 			</form>
            </div>
            <div id="tabs-5">
            <form action="/report/export_variance" method="get" id="_form4" style="padding:10px">
 				
 					<br /> 
 					<input type="submit"  class="btn" value="Export" >
 			</form>
            </div>
            <div id="tabs-6">
            <form action="/report/export_ar_one" method="post" id="_form5" style="padding:10px">
 					${msi_list_one_form()|n}
 					<br />
 					<input type="button"  class="btn" value="Reset" onclick="$('form#_form5').find('input, select').val('')"><br /><br />
 					<input type="button"  class="btn" value="Export" onclick="$('#_form5').submit()">
 			</form>
            </div>
      
    </div>
</div>
<hr class="space">