<%namespace name="tw" module="tw.core.mako_util"/>

<div style="clear:both"></div>
<div class="log-six-sub-title">PO Item Detail Info</div>
<%def name="showGroup(l)">
    <div class="case-list-one">
    	%for field in l:
    		<ul>
    			<li class="label"><label ${tw.attrs([('id', '%s.label' % field.id),('for', field.id)])} class="fieldlabel">${tw.content(field.label_text)}</label></li>
    			% if value_for(field):
    			<li>${value_for(field)}</li>
    			% else:
    			<li>&nbsp;</li>
    			% endif
    		</ul>
    	%endfor
    </div>
</%def>


<%
	gs = [[],[]]
	for index,field in enumerate(fields): gs[index%2].append(field)
%>

%for g in gs:
	${showGroup(g)}
%endfor

