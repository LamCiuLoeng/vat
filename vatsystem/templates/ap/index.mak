<%inherit file="vatsystem.templates.layout"/>
<%
	from vatsystem.util import const
	from vatsystem.util.mako_filter import b, last_month
%>
<%def name="extTitle()">r-pac - VAT System</%def>
<%def name="extCSS()">
<link rel="stylesheet" href="/css/ar.css" />
</%def> 
<%def name="extJavaScript()">  
<script type="text/javascript" src="/js/vat_ar.js"></script>
<script type="text/javascript">
    $(function() {
    	changeHeadFont();
        var accordion = $("#accordion");
        var index = $.cookie("accordion");
        var active = index == null ? 0 : accordion.find("h3:eq(" + index + ")");
        accordion.accordion({
            header: "h3",
            event: "click hoverintent",
            active: active,
            change: function(event, ui) {
                var index = $(this).find("h3").index ( ui.newHeader[0] );
                $.cookie("accordion", index, {path: "/"});
                $("#tabs").empty();
            },
            autoHeight: false
        });
        accordion.show()
        layout = $('body').layout({
            resizable:false,
            useStateCookie: true
        }) 

        layout.sizePane("north", 138);
        layout.sizePane("west", 170);  
        resetLink();
        
        $(".ajaxSearchField").each(function(){
        	var type = $(this).attr("name")
        	var formID = $(this).parent("form").attr("id")
        	if(type=='create_by_id'){
        		type = 'display_name'
        	}
        	if(formID=='_form0'){
        		if(type=='customer_code'){
        			type = 'customer'
        		}
        	}
        	$(this).autocomplete("/ap/autocomplete",{
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
	            	if((formID == "_form2" || formID == "_form3" || formID == "_form4") && type=="item_code")type = "item_no"
	            	if(formID == "_form0" && type == "supplier")type="supplier_code"
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
<%def name="header()"> 
<div class='submenu' id="function-menu">
    <ul>
        <li class='li-start'></li>
        <li class='li-center'> <a href="/ap/index"><img src="/images/images/VAT-ERP_g.jpg"></a></li>
        <li class='li-center'> <a href="/ap/import_statement"><img src="/images/images/Import-Excel_g.jpg"></a></li>
        <li class='li-end'></li>
    </ul> 
</div>
</%def>
<div class="ui-layout-west">
    <div class="none"><img src="../images/busy.gif" /></div>
    <div id="accordion" class="search none">
    	<h3><a>Search DZD</a></h3>
        <div>
            <form action="/ap" method="get" id="_form0">
            	<a onclick="viewAll('/ap?type=${const.SEARCH_TYPE_EXCEL}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')"  href="javascript:void(0)">Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_EXCEL}" />
                %if kw.get('type','')==const.SEARCH_TYPE_EXCEL:
                ${excel_search_form(value=kw)|n}
                %else:
                ${excel_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(0)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(0)"/>
            </form>
        </div>
        <h3 style='display:none'><a>Search PI</a></h3>
        <div  style='display:none'>
            <form action="/ap" method="get" id="_form1">
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_PI}" />
                %if kw.get('type','')==const.SEARCH_TYPE_PI:
                ${pi_search_form(value=kw)|n}
                %else:
                ${pi_search_form()|n} 
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(1)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(1)"/>
            </form>
        </div>
        <h3><a>Search MPI</a></h3>
        <div>
            <form action="/ap" method="get" id="_form2">
            	<a onclick="viewAll('/ap?type=${const.SEARCH_TYPE_PSIPSO}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')"  href="javascript:void(0)">Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_PSIPSO}" />
                %if kw.get('type','')==const.SEARCH_TYPE_MSIMSO:
                ${phead_search_form(value=kw)|n}
                %else:
                ${phead_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(2)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(2)"/>
            </form>
        </div>
        <h3><a>Search MSN</a></h3>
        <div>
            <form action="/ap" method="get" id="_form3">
                <a href="javascript:void(0)" onclick="viewAll('/ap?type=${const.SEARCH_TYPE_MCN}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')" >Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_MSN}" />
                %if kw.get('type','')==const.SEARCH_TYPE_MSN:
                ${shead_search_form(value=kw)|n}
                %else:
                ${shead_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(3)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(3)"/>
            </form>
        </div>
        <h3 style='display:none'><a>Search MF</a></h3>
        <div style='display:none'>
            <form action="/ap" method="get" id="_form4">
                <a href="javascript:void(0)" onclick="viewAll('/ap?type=${const.SEARCH_TYPE_MF}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')" >Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_MF}" />
                %if kw.get('type','')==const.SEARCH_TYPE_MF:
                ${mhead_search_form(value=kw)|n}
                %else:
                ${mhead_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(4)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(4)"/>
            </form>
        </div>
    </div>
</div>
<div class="ui-layout-center ui-layout-pane ui-layout-pane-center" style="position: absolute; margin: 0px; left: 166px; right: 0px; top: 144px; bottom: 0px; height: 243px; width: 1272px; z-index: 1; visibility: visible; display: block;">
    <div id="tabs" class="ui-tabs ui-widget ui-widget-content ui-corner-all" >
        %if kw.get('type','')==const.SEARCH_TYPE_SI:
        <%include file="vatsystem.templates.ar.list_si"/>
        %elif kw.get('type','')==const.SEARCH_TYPE_SO:
        <%include file="vatsystem.templates.ar.list_so"/>
        %elif kw.get('type','')==const.SEARCH_TYPE_MSIMSO:
        <%include file="vatsystem.templates.ar.list_thead"/>
        %elif kw.get('type','')==const.SEARCH_TYPE_MCN:
        <%include file="vatsystem.templates.ar.list_chead"/>
        %endif
    </div>
</div>
