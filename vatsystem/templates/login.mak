<%!
	from tg.flash import get_flash,get_status
	from vatsystem.util import const
%>
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
<html>
<head>
    <meta content="text/html; charset=utf-8" http-equiv="content-type">
    <title>r-pac - Login</title>
    <link type="images/x-icon" rel="shortcut icon" href="/images/favicon.ico" />
	<link type="text/css" rel="stylesheet" href="/css/screen.css" />
	<script type="text/javascript" src="/js/jquery-1.4.2.min.js"></script>
    <script type="text/javascript" language="JavaScript">
        //
        $(document).ready(function(){
            if ($.browser.msie) {
                $("#contenulogin").append("<div style='margin-top:30px;'>*You are using IE,it's recommended to upgrade your browser to <a href='http://download.cdn.mozilla.net/pub/mozilla.org/firefox/releases/19.0.2/win32/en-US/Firefox%20Setup%2019.0.2.exe'>Firefox</a> or higher to get the better view.</div>");
            }
        });
        //
    </script>
%if get_flash():
    <script language="JavaScript" type="text/javascript">
        //<![CDATA[
        $(document).ready(function(){
            %if get_status() == "ok":
                showMsg("${get_flash()|n}");
            %elif get_status() == "warn":
                showError("${get_flash()|n}");
            %endif
        });
        //]]>
    </script> 
%endif
</head>
<body onload="document.getElementById('login_name').focus()">
    <div id="contenulogin">
        <div id="logo-login"></div>
        <div id="boxlogin">
            <form action="${tg.url('/login_handler', came_from = came_from.encode('utf-8'), __logins = login_counter.encode('utf-8'))}" method="POST">
                <fieldset>
                    <legend>r-pac authentication</legend>
                    <p><label for="company">Company :  </label><select name='company' style='width:150px'>
                    												<option value='${const.COMPANY_CODE_SZ}'>美皇貿易(深圳)有限公司 </option>
                    												<option value='${const.COMPANY_CODE_SH}'>r-pac Packaging(SZ) </option>
                    												<option value='${const.COMPANY_CODE_EU}'>r-pac Packaging(Europe)</option>
                    											</select></p>
                    <p><label for="login_name">Login :  </label><input style="width:150px" type="text" name="login" id="login_name"></p>
                    <p><label for="login_password">Password : </label><input style="width:150px" type="password" name="password" id="login_password"></p>
                    <p style="text-align:center"><input type="submit" value="Login" class="submit"></p>

                </fieldset>
            </form>
        </div>
    </div>
</body>
</html>