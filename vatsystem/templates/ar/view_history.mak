<%
    from vatsystem.util.mako_filter import b,pd,pi,pf,pt,pq
%>
<div class="gridInDiv">
  <table cellspacing="0" cellpadding="0" border="0" class="gridTable">
    <thead class="cl3">
      <tr>
        <th>Time</th>
        <th>User</th>
        <th>Action Type</th>
        <th>Description </th>
      </tr>
    </thead>
    <tbody>
      % for i in historys:
      <tr>
        <td class="head" width='150'>${pt(i.create_time)}</td>
        <td width='100'>${i.create_by}</td>
        <td width='120'>${i.action_type}</td>
        <td>
        	<textarea style="width:100%;overflow-y:visible;border:none;text-indent:20px;color:#222222"  readonly disabled="disabled">${i.remark}</textarea>
        	
        </td>
      </tr>
      % endfor 
    </tbody>
  </table>
</div>