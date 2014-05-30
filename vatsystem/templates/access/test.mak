<%inherit file="vatsystem.templates.master"/>

<%def name="extTitle()">r-pac - Financial</%def>

<%def name="extCSS()">
	<link rel="stylesheet" href="/css/jquery.autocomplete.css" type="text/css" />
	<link rel="stylesheet" href="/css/flora.datepicker.css" type="text/css" />
</%def>

<%def name="extJavaScript()">
	<script type="text/javascript" src="/js/jquery.columnfilters.js" language="javascript"></script>
	<script type="text/javascript" src="/js/jquery-impromptu.2.8.min.js" language="javascript"></script>
	<script type="text/javascript" src="/js/jquery.bgiframe.pack.js" language="javascript"></script>
	<script type="text/javascript" src="/js/jquery.autocomplete.pack.js" language="javascript"></script>
	<script type="text/javascript" src="/js/ui.datepicker.js" language="javascript"></script>

	<script language="JavaScript" type="text/javascript">
    //<![CDATA[
          function c(){
          	var aa = {
          		state0 : {
          			html    : 'hello,CL!',
          			buttons : { Cancel: false, Next: true },
          			submit  : function(v,m,f){
          				if(!v){ return true; }
          				else{
          					$.prompt.goToState('state1');
          					return false;
          				}
          			}
          		},
          		state1 : {
          			html    : '<img src="/images/jdtlogo.png"/><br /><img src="/images/jdt.gif"/>',
          			buttons : { Back: -1, Exit: 0 },
          			submit  : function(v,m,f){
		                  if(v==0){ $.prompt.close() }
		                  else if(v=-1){
		                        $.prompt.goToState('state0');
		                 		 return false;
		                 }
		            }
          		}
          	};

          	$.prompt(aa,{opacity: 0.6,prefix:'cleanblue',show:'slideDown'});

          }
    //]]>
   </script>

</%def>


<div class="nav-tree">Financial&nbsp;&nbsp;&gt;&nbsp;&nbsp;SO Search</div>

<p>Test</p>

<input type="button" onclick="c()" value="test"/>



