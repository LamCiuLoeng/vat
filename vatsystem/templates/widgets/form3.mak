<%namespace name="tw" module="tw.core.mako_util"/>
% if hidden_fields:
    % for field in hidden_fields:
        ${field.display(value_for(field), **args_for(field))}
    % endfor
% endif

<%def name="showGroup(l)">
    %for field in l:
        %if field.label_text=='Date From':
            <label>${tw.content('Create Date')}</label><br/>
            <span class="alt1">(YYYY-MM-DD)</span><br/>
            ${field.display(value_for(field), **args_for(field))}<br/>
            To<br/>
            <span class="alt1">(YYYY-MM-DD)</span><br/>
        %elif field.label_text=='Date To':
            ${field.display(value_for(field), **args_for(field))}<br/>
        %else:
            <label>${tw.content(field.label_text)}</label><br/>${field.display(value_for(field), **args_for(field))}<br/>
        %endif
    %endfor
</%def>


<%
	gs = [[],[]]
	for index,field in enumerate(fields): gs[index%1].append(field)
%>

%for g in gs:
	${showGroup(g)}
%endfor