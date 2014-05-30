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
        <td class="head">${pt(i.create_time)}</td>
        <td>${i.create_by}</td>
        <td>${i.action_type}</td>
        <td nowrap='nowrap' style="table-layout:fixed">${i.remark} </td>
      </tr>
      % endfor 
    </tbody>
  </table>
</div>