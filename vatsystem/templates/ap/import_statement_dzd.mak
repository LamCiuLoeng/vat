<%
from vatsystem.util import const
%>
<form name="form1" enctype="multipart/form-data" method="post" action="/ap/import_statement_dzd?id=${ids}">
      
     <label>
       <input type="file" name="attachment"> <input type="submit" value="OK" name="ok">
    </label>
    <p>
    <input type="radio" name="type" id='type1' value="${const.IMPORT_STATEMENT_YES}" checked> <label for='type1'>Import and Save DB</label> 
    <br />
	<input type="radio" name="type" id='type2' value="${const.IMPORT_STATEMENT_NO}"> <label for='type2'>Import and not Save DB, We will save it later</label> 
	</p>
 </form>