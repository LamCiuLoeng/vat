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
        		var type = 'display_name'
        	}
            if(type=='item_code'){
        		var type = 'item_no'
        	}
        	$(this).autocomplete("/cost/autocomplete",{
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
<%def name="header()"> 
<div class='submenu' id="function-menu">
    <ul>
        <li class='li-start'></li>
        <li class='li-center'> <a href="/cost/index"><img src="/images/images/VAT-ERP_g.jpg"></a></li>
        <li class='li-end'></li>
    </ul> 
</div>
</%def>
<div class="ui-layout-west">
    <div class="none"><img src="../images/busy.gif" /></div>
    <div id="accordion" class="search none">
        <h3><a>Search MSI/MSO</a></h3>
        <div>
            <form action="/cost" method="get" id="_form0">
            	<a onclick="viewAll('/cost?type=${const.SEARCH_TYPE_MSIMSO}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')"  href="javascript:void(0)">Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_MSIMSO}" />
                %if kw.get('type','')==const.SEARCH_TYPE_MSIMSO:
                	${thead_search_form(value=kw)|n}
                %else:
                	${thead_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(0)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(0)"/>
            </form>
        </div>
        <h3><a>Search MCN</a></h3>
        <div>
            <form action="/cost" method="get" id="_form1">
                <a href="javascript:void(0)" onclick="viewAll('/cost?type=${const.SEARCH_TYPE_MCN}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')" >Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_MCN}" />
                %if kw.get('type','')==const.SEARCH_TYPE_MCN:
                	${chead_search_form(value=kw)|n}
                %else:
                	${chead_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(1)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(1)"/>
            </form>
        </div>
        <h3><a>Search CST</a></h3>
        <div>
            <form action="/cost" method="get" id="_form2">
                <a href="javascript:void(0)" onclick="viewAll('/cost?type=${const.SEARCH_TYPE_CST}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')" >Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_CST}" />
                %if kw.get('type','')==const.SEARCH_TYPE_CST:
                	${ohead_search_form(value=kw)|n}
                %else:
                	${ohead_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(2)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(2)"/>
            </form>
        </div>
        <h3><a>Search CCN</a></h3>
        <div>
            <form action="/cost" method="get" id="_form3">
                <a href="javascript:void(0)" onclick="viewAll('/cost?type=${const.SEARCH_TYPE_CCN}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')" >Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_CCN}" />
                %if kw.get('type','')==const.SEARCH_TYPE_CCN:
                	${nhead_search_form(value=kw)|n}
                %else:
                	${nhead_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(3)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(3)"/>
            </form>
        </div>
        <h3><a>Search PI</a></h3>
        <div>
            <form action="/cost" method="get" id="_form4">
                <a href="javascript:void(0)" onclick="viewAll('/cost?type=${const.SEARCH_TYPE_PI}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')" >Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_PI}" />
                %if kw.get('type','')==const.SEARCH_TYPE_PI:
                	${po_search_form(value=kw)|n}
                %else:
                	${po_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(4)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(4)"/>
            </form>
        </div>
       <h3><a>Search Charge</a></h3>
        <div>
            <form action="/cost" method="get" id="_form5">
                <a href="javascript:void(0)" onclick="viewAll('/cost?type=${const.SEARCH_TYPE_CHARGE}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')" >Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_CHARGE}" />
                %if kw.get('type','')==const.SEARCH_TYPE_CHARGE:
                	${charge_search_form(value=kw)|n}
                %else:
                	${charge_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(5)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(5)"/>
            </form>
        </div>
       	<h3><a>Search Variance</a></h3>
        <div>
            <form action="/cost" method="get" id="_form6">
                <a href="javascript:void(0)" onclick="viewAll('/cost?type=${const.SEARCH_TYPE_VARIANCE}&date_from=${last_month()[0]}&date_to=${last_month()[1]}')" >Last Month</a><br/>
                <input type="hidden" name="type" value="${const.SEARCH_TYPE_VARIANCE}" />
                %if kw.get('type','')==const.SEARCH_TYPE_VARIANCE:
                	${variance_search_form(value=kw)|n}
                %else:
                	${variance_search_form()|n}
                %endif
                <br/>
                <input type="button" class="btn" value="Search" onclick="toSearch(6)"/>
                <input type="button" class="btn" value="Reset" onclick="toReset(6)"/>
            </form>
        </div>
    </div>
</div>
<div class="ui-layout-center ui-layout-pane ui-layout-pane-center" style="position: absolute; margin: 0px; left: 166px; right: 0px; top: 144px; bottom: 0px; height: 243px; width: 1272px; z-index: 1; visibility: visible; display: block;">
    <div id="tabs" class="ui-tabs ui-widget ui-widget-content ui-corner-all" >
        %if kw.get('type','')==const.SEARCH_TYPE_MSIMSO:
        <%include file="vatsystem.templates.ar.list_thead"/>
        %elif kw.get('type','')==const.SEARCH_TYPE_MCN:
        <%include file="vatsystem.templates.ar.list_chead"/>
        %endif
    </div>
</div>
