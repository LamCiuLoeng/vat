<%!
	from tg import session
	from tg.flash import get_flash,get_status
	from repoze.what.predicates import not_anonymous,in_group
%>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>${self.extTitle()}</title>
<link type="images/x-icon" rel="shortcut icon" href="/images/favicon.ico" />
<link type="text/css" rel="stylesheet" href="/css/theme/jquery-ui-1.8.5.custom.css" />
<link type="text/css" rel="stylesheet" href="/css/jquery.autocomplete.css" />
<link type="text/css" rel="stylesheet" href="/css/impromt.css" />
<link type="text/css" rel="stylesheet" href="/css/tipsy.css" />
<link type="text/css" rel="stylesheet" href="/css/screen.css" />
<link type="text/css" rel="stylesheet" href="/Plugins/fancybox/jquery.fancybox-1.3.4.css" />
${self.extCSS()}
<script type="text/javascript" src="/js/jquery-1.4.2.min.js"></script>
<script type="text/javascript" src="/js/jquery-ui-1.7.3.custom.min.js"></script>
<script type="text/javascript" src="/js/numeric.js"></script>
<script type="text/javascript" src="/js/jquery.autocomplete.pack.js"></script>
<script type="text/javascript" src="/js/jquery-impromptu.3.1.min.js"></script>
<script type="text/javascript" src="/js/jquery.blockUI.js"></script>
<script type="text/javascript" src="/js/jquery.layout-latest.js"></script>
<script type="text/javascript" src="/js/jquery.cookie.js"></script>
<script type="text/javascript" src="/js/jquery.tipsy.js"></script>
<script type="text/javascript" src="/Plugins/fancybox/jquery.fancybox-1.3.4.js"></script>
<script type="text/javascript" src="/js/jquery.form.js"></script>
<script type="text/javascript" src="/js/common.js"></script>
%if get_flash():
<script language="JavaScript" type="text/javascript">
    $(document).ready(function(){
	    %if get_status() == "ok":
	        showMsg("${get_flash()|n}");
	    %elif get_status() == "warn":
	        showError("${get_flash()|n}");
	    %endif
    });
    
</script>
%endif 
${self.extJavaScript()}
</head>
<style type="text/css">
<!--
	*{margin:0;padding:0}
	body{height:100%;}
	.blockBox{background:#000;position:absolute;left:0;top:0;height:100%;width:100%;filter:alpha(opacity=50);opacity:0.5;-moz-opacity:0.5;z-index:1000;curso;cursor:wait}
	.message{width:150px;color:#000;border:3px solid #aaa;padding:5px 0;text-align:center;background-color:#fff;position:relative;left:45%;top:45%;z-index:1001;cursor:wait}
-->
</style>

<script type="text/javascript">
	function load(){
		document.write("<div class='blockUI' style='display: none;'></div><div class='blockUI blockBox blockOverlay'></div><div class='message blockUI blockMsg blockPage' style='font-size:16px; font-weight:400;'><img src='/images/busy.gif' border='0'/>Loading</div>")
	}
</script>
<body style="height:100%">
<script>
load();
</script>
    <div class="ui-layout-north">
        <div>
            <table width="100%" border="0" cellspacing="0" cellpadding="0">
              <tr>
                <td width="200" valign="middle"><img src="/images/${session['company_code']}.jpg" width="737" height="72" /></td>
                <td valign="middle" bgcolor="#EDF6FF">
                    <div id="pageLogin"><span class="welcome">Welcome :</span> ${request.identity["user"]} | <a href="/">Home</a> | <a href="/logout_handler">Logout</a></div>
                </td>
              </tr>
            </table>
        </div>
        <div class="menu-tab">
            <ul>
                <li class="${'highlight' if tab_focus=='main' else ''}"><a href="/index">Main</a></li>
                <li class="${'highlight' if tab_focus=='report' else ''}"><a href="/report">Report</a></li>
                <li class="${'highlight' if tab_focus=='master' else ''}"><a href="/master">Master</a></li>
                %if in_group("Admin"):
                <li class="${'highlight' if tab_focus=='access' else ''}"><a href="/access">Access</a></li>
                %endif
            </ul>
            <div class="r box5" id="change-head-font">
                ERP Data:<span class="cl5">&nbsp;&nbsp;&nbsp;&nbsp;</span>
                MSI/MSO Data:<span class="cl3">&nbsp;&nbsp;&nbsp;&nbsp;</span>
                MCN Data:<span class="cl4">&nbsp;&nbsp;&nbsp;&nbsp;</span>
            </div>
        </div>
        <div class="clear"></div>
        ${self.header()}
    </div>
    ${self.body()}
    <hr class="space">
    <div id="footer"><span style="margin-right:40px">Copyright r-pac International Corp.</span></div>
<script type="text/javascript">
	closeBlock();
</script>
</body>
</html>
<%def name="extTitle()">r-pac</%def>
<%def name="extCSS()"></%def>
<%def name="extJavaScript()"></%def>
<%def name="header()"></%def>