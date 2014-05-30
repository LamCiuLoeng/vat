<%inherit file="vatsystem.templates.master"/>

<%!
	from tg.flash import get_flash,get_status
	from repoze.what.predicates import not_anonymous,in_group,has_permission,has_any_permission
%>

<%def name="extTitle()">r-pac - Master</%def>

<div class="main-div">
	<div id="main-content">
		<div class="block">
			<a href="/user/index"><img src="/images/user.jpg" width="55" height="55" alt="" /></a>
			<p><a href="/user/index">User</a></p>
			<div class="block-content">The module is the master of the "VAT System" .</div>
		</div>
	</div>
</div>
