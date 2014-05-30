# -*- coding: utf-8 -*-
import os, traceback, logging, datetime
import win32com.client
import pythoncom
from win32com.client import Dispatch
from common import *
from vatsystem.util import const
from datetime import date


__all__=["VATExcel", "VATAPExcel", "VATAPDZDExcel", "VATCSTCSTExcel", 
         "VATStockWithOutItem", "VATStockWithItem", "VATInvoiceWithOutCost", 
         "VATInvoiceWithCost", "VATAPDZDMPIExcel", "PIProceedsExcel", "DNProceedsExcel", "PICostExcel", "DNCostExcel"]

class ExcelBasicGenerator:
    def __init__(self, templatePath=None, destinationPath=None, overwritten=True):
        #solve the problem when create the excel at second time ,the exception is occur.
        pythoncom.CoInitialize()

        self.excelObj=Dispatch('Excel.Application')
#        self.excelObj.Visible = False

        if templatePath and os.path.exists(templatePath):
            self.workBook=self.excelObj.Workbooks.open(templatePath)
        else:
            self.workBook=self.excelObj.Workbooks.Add()

        self.destinationPath=destinationPath
        self.overwritten=overwritten

    def inputData(self): pass

    def outputData(self):
        try:
            if not self.destinationPath : pass
            elif os.path.exists(self.destinationPath):
                if self.overwritten:
                    os.remove(self.destinationPath)
                    self.excelObj.ActiveWorkbook.SaveAs(self.destinationPath)
            else:
                self.excelObj.ActiveWorkbook.SaveAs(self.destinationPath)
        except:
            traceback.print_exc()
        finally:
            try:
                self.workBook.Close(SaveChanges=0)
            except:
                traceback.print_exc()

    def clearData(self):
        try:
            if hasattr(self, "workBook"): self.workBook.Close(SaveChanges=0)
        except:
            traceback.print_exc()

class VATExcel(ExcelBasicGenerator):
    def inputData(self, additionInfo=[], header=[], data=[]):
        excelSheet=self.workBook.Sheets(1)
        excelSheet.Name=additionInfo[6]
        _ar_input_data(excelSheet, additionInfo, header, data)

#        excelSheet.Columns("A:AZ").EntireColumn.AutoFit()

def _ar_input_data(excelSheet, additionInfo, header, data):
    
    if not data: data=[("",), ]
    row=len(data)
    col=len(data[0])
    startRow=13
    lastRow=startRow + row
    startCol=1

    excelSheet.Range("cust_code").Value=additionInfo[0] if len(additionInfo)>1 else ''
    excelSheet.Range("cust_name").Value=additionInfo[1]+'('+additionInfo[2]+')' if len(additionInfo)>6 else ''
    excelSheet.Range("cust_tel").Value=additionInfo[3] if len(additionInfo)>6 else ''
    excelSheet.Range("cust_fax").Value=additionInfo[4] if len(additionInfo)>6 else ''
    excelSheet.Range("contact_sales").Value=additionInfo[5] if len(additionInfo)>6 else ''
    excelSheet.Range("title").Value=u'美皇贸易（深圳）有限公司'+additionInfo[7] if len(additionInfo)>6 else ''

    excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.LineStyle=1
    excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.Weight=2
    excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Font.Name="Trebuchet MS"
    excelSheet.Range("A%d:%s%d"%(lastRow+1, number2alphabet(col), lastRow+7)).Font.Name=u"宋体"
    excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Font.Size=12
    excelSheet.Range("A%d:%s%d"%(lastRow+1, number2alphabet(col), lastRow+1)).Font.Size=14
    excelSheet.Range("A%d:%s%d"%(lastRow+2, number2alphabet(col), lastRow+7)).Font.Size=12

    excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value=data

    for row in range(startRow, lastRow):
            excelSheet.Cells(row, alphabet2number('h')).WrapText=False

    for col in ["l", "m", "n", "o", "p", "q"]:
        excelSheet.Cells(lastRow, alphabet2number(col)).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%(col, a), [startRow, lastRow-1]))

    for col in ["k", "l", "m", "n", "o", "p", "q"]:
        for row in range(startRow, lastRow+1):
            excelSheet.Cells(row, alphabet2number(col)).NumberFormatLocal="0.00_ "

    excelSheet.Cells(lastRow+1, alphabet2number('a')).Font.Bold=True
    excelSheet.Cells(lastRow+1, alphabet2number('k')).Font.Bold=True
    excelSheet.Cells(lastRow+1, alphabet2number('k')).HorizontalAlignment=-4108

    for i in range(1, 8): excelSheet.Cells(lastRow+i, alphabet2number('a')).HorizontalAlignment=-4131

    excelSheet.Cells(lastRow, alphabet2number('b')).Value='Total'
    excelSheet.Cells(lastRow+1, alphabet2number('a')).Value=u'核对人签名：'
    excelSheet.Cells(lastRow+1, alphabet2number('k')).Value=u'单位公章：'
    excelSheet.Cells(lastRow+2, alphabet2number('a')).Value=u'日期：'
    excelSheet.Cells(lastRow+3, alphabet2number('a')).Value=u'请在核对后签名盖章并传真到美皇贸易（深圳）有限公司'
    excelSheet.Cells(lastRow+4, alphabet2number('a')).Value=u'如有问题，请联系以下：'
    excelSheet.Cells(lastRow+5, alphabet2number('a')).Value=u'Tel:'+additionInfo[10] if additionInfo[10] else u'Tel:'
    excelSheet.Cells(lastRow+5, alphabet2number('f')).Value=u'Fax:'+additionInfo[11] if additionInfo[11] else u'Fax:'
    excelSheet.Cells(lastRow+6, alphabet2number('a')).Value=u'Email:'+additionInfo[9] if additionInfo[9] else u'Email:'
    excelSheet.Cells(lastRow+7, alphabet2number('a')).Value=u'联系人：'+additionInfo[8] if additionInfo[8] else u'联系人：'
    return lastRow
    
class APExcel(ExcelBasicGenerator):
    
    def outputData(self, additionInfo=[], header=[], data=[]):
        if const.IMP_TYPE == 1:
            keys = {"A":"dn_no", "B":"po_no", "C":"desc_zh", "D":"item_code", 
                    "E":"qty", "F":"unit_price", "G":"tax_rate", "H":"rmb_unit", "I":"rmb_amount",
                    "J":"rmb_tax", "K":"rmb_amount_p"}
            keys1 = {"A":"dn_no", "B":"po_no", "C":"desc_zh", "D":"item_code", 
                    "E":"qty", "F":"ex", "G":"unit_price", "H":"tax_rate", "I":"rmb_unit",
                    "J":"rmb_amount", "K":"rmb_tax","L":"rmb_amount_p"}
            keys2 = {"A":"dn_no", "B":"po_no", "C":"desc_zh", "D":"item_code", 
                    "E":"qty", "F":"ex", "G":"unit_price", "H":"exchange_rate", "I":"tax_rate",
                    "J":"rmb_unit", "K":"rmb_amount","L":"rmb_tax", "M":"rmb_amount_p"}
        else:
                keys = {"A":"invoice_no", "B":"department", "C":"issue_date", "D":"supplier_code", 
                "E":"supplier_name", "F":"supplier_short_name", "G":"remark", "H":"currency", "I":"posted_status",
                "J":"invoice_amount", "K":"invoice_base_amount", "L":"po_no", "M":"grn_no", "N":"corporate_customer", 
                "O":"private_brand", "P":"private_brand_sub_line", "Q":"packaging_category", "R":"packaging_type", "V":"merchandise",
                "W":"internal_item_code", "X":"item_code", "Y":"item_description", "Z":"qty", "AA":"unit", "AB":"unit_price",
                "AC":"item_amount", "AD":"item_base_amount","AE":"pi_line_no","AF":"tax_rate" ,"AG":"billing_month", "AH":"kingdee_date", "AI":"reconciliation_lot", "AJ":"payment_date"
                }
                keys1 = {"A":"number", "B":"stock_adjustment_no", "C":"po_no", "D":"note_type", 
                "E":"other_ref", "F":"note_remark", "G":"issue_date", "H":"department", "I":"supplier_code",
                "J":"supplier_name", "K":"sales_contact",
                "L":"currency", "M":"note_amount", "N":"note_base_amount", 
                "O":"corporate_customer", "P":"private_brand", "Q":"private_brand_sub_line", "R":"packaging_category", "S":"packaging_type", "V":"material",
                "W":"merchandise", "X":"internal_item_code", "Y":"item_code", "Z":"item_description", "AA":"order_qty", "AB":"unit",
                "AC":"unit_price", "AD":"amount", "AE":"base_amount", "AF":"sn_line_no", "AG":"tax_rate", "AH":"billing_month", "AI":"kingdee_date", "AJ":"reconciliation_lot", "AK":"payment_date"
            }
        data, pi_list, dn_list = {}, [], []
        for sheet in range(1, 3):
            try:
                excelSheet= self.workBook.Sheets(sheet)
                xldata = excelSheet.UsedRange.Value
            except:
                continue
            if not xldata:continue
            cellsLength = len(xldata)
            num = 0
            startCol = 1
            for i in range(startCol, cellsLength):
                firstCellValue = excelSheet.Cells(i, "A").Value
                if const.IMP_TYPE == 1:
                    if isinstance(firstCellValue,(str,unicode)) and (u'\u5355\u53f7' in firstCellValue or 'D/N No' in firstCellValue): 
                        startCol = i
                        #break
                else:
                    if isinstance(firstCellValue,(str,unicode)) and ("Number" in firstCellValue or "Invoice Number" in firstCellValue):
                        startCol = i
                        if isinstance(firstCellValue,(str,unicode)) and "Invoice Number" in firstCellValue:
                            type = 1
                        else:
                            type = 2
                        #break
                if not firstCellValue:
                    num += 1
                if num == 5:
                   cellsLength = i
                   break
            cellsLength = cellsLength + 2
            for a in range(startCol, cellsLength):
                subdata, birgedata = {}, {}
                rangesKey = keys2.keys() if const.IMP_TYPE == 1 else keys1.keys()
                for col in rangesKey:
                    cellValue = excelSheet.Cells(a, col).Value
                    firstCellValue = excelSheet.Cells(a, "A").Value
                    if isinstance(firstCellValue,(str,unicode)) and (u'\u5355\u53f7' in firstCellValue or 'D/N No' in firstCellValue or "Number" in firstCellValue or "Invoice Number" in firstCellValue): continue
                    if cellValue: 
                        subdata.update({col:cellValue.strip() if isinstance(cellValue,(str,unicode)) else cellValue})
                if len(subdata)>7:
                    if const.IMP_TYPE == 1:
                        if subdata.get('L') and subdata.get('M'):keys = keys2
                        if subdata.get('L') and not subdata.get('M'):keys = keys1
                    else:
                        if type == 2: keys = keys1
                    for a, b in keys.iteritems(): 
                        birgedata.update({b:subdata.get(a)})
                    if const.IMP_TYPE == 2 and type == 2:
                        dn_list.append(birgedata)
                    else:pi_list.append(birgedata)
        data.update({"pi_list":pi_list,'dn_list':dn_list})
        return data
        
class VATAPExcel(ExcelBasicGenerator):
    def inputData(self, additionInfo=[], header=[], data=[]):
        excelSheet=self.workBook.Sheets(1)
        excelSheet.Name=additionInfo[1]
        
        if not data: data=[("",), ]

        row=len(data)
        col=len(data[0])
        startRow=12
        lastRow=startRow+row
        startCol=1

        excelSheet.Range("supplier_name").Value=additionInfo[0] if len(additionInfo)>1 else ''
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).WrapText=False
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.LineStyle=1
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.Weight=2
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Font.Name="Trebuchet MS"
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Font.Size=12

        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value=data
        for col in ["e", "h", "j"]:
            excelSheet.Cells(lastRow, alphabet2number(col)).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%(col, a), [startRow, lastRow-1]))

        excelSheet.Cells(lastRow, alphabet2number("k")).Value="=sum(H%d,J%d)"%(lastRow, lastRow)

class VATAPDZDExcel(ExcelBasicGenerator):
    
    def inputData(self, additionInfo=[], header=[], data=[]):
        excelSheet=self.workBook.Sheets(1)
        excelSheet.Name=additionInfo[1]

        if not data: data=[("",), ]

        row=len(data)
        col=len(data[0])
        startRow=6
        lastRow=startRow+row
        startCol=1

        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.LineStyle=1
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.Weight=2
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Font.Name="Trebuchet MS"
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Font.Size=11

        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value=data
        if col == 11:
            excelSheet.Cells(lastRow, alphabet2number("H")).Value= additionInfo[2]
            excelSheet.Cells(lastRow, alphabet2number("J")).Value= additionInfo[3]
        else:
            excelSheet.Cells(lastRow, alphabet2number("I")).Value= additionInfo[2]
            excelSheet.Cells(lastRow, alphabet2number("K")).Value= additionInfo[3]
        excelSheet.Cells(lastRow, alphabet2number("G")).Value= u'合计'


class VATAPDZDMPIExcel(ExcelBasicGenerator):
    def inputData(self, additionInfo=[], header=[], data=[]):
        excelSheet=self.workBook.Sheets(1)
        #excelSheet.Name=additionInfo[1]
        
        if not data: data=[("",), ]

        row=len(data)
        col=len(data[0])
        startRow=11
        lastRow=startRow+row
        startCol=1

        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).WrapText=False
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.LineStyle=1
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.Weight=2
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Font.Name="Trebuchet MS"
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Font.Size=12
        
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value=data
        '''
        for col in ["e", "h", "j"]:
            excelSheet.Cells(lastRow, alphabet2number(col)).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%(col, a), [startRow, lastRow-1]))

        excelSheet.Cells(lastRow, alphabet2number("k")).Value="=sum(H%d,J%d)"%(lastRow, lastRow)
        '''
        
class VATCSTCSTExcel(ExcelBasicGenerator):
    
    def inputData(self, additionInfo=[], header=[], data=[]):
        excelSheet=self.workBook.Sheets(1)
        excelSheet.Name=additionInfo[6]
        ar_lastRow = _ar_input_data(excelSheet, additionInfo, header, data[0])
        excelSheet.Cells(ar_lastRow, alphabet2number("G")).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%("G", a), [13, ar_lastRow-1]))
        
        
        lastRow = ar_lastRow + 9
        ap_line = lastRow
        cst_keys = {
              'A':'SO#', 'B':'PO#', 'C':'Supplier Short Name', 
              'D':u'VAT号码', 'E':'designation', 'F':'Set Item', 'G':'PO Qty', 
              'H':u'币别', 'I':u'汇率', 'J':u'未税单价', 'K':u'未税金额', 'L':'remark'
        }
        for k, v in cst_keys.iteritems():
            excelSheet.Cells(lastRow + 1, alphabet2number(k)).Borders.LineStyle=1
            excelSheet.Cells(lastRow + 1, alphabet2number(k)).Value = v
        
        row=len(data[1])
        if len(data[1])>0:
            col=len(data[1][0])
            startRow = lastRow + 2
            lastRow=startRow+row
            excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.LineStyle=1
            excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow)).Borders.Weight=2
            excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value=data[1]
            excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Font.Size=10
            excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Font.Name=u"宋体"
            
            for i in range(startRow, lastRow): 
                excelSheet.Cells(i, alphabet2number('H')).HorizontalAlignment=-4108
                excelSheet.Cells(i, alphabet2number('I')).HorizontalAlignment=-4108
                excelSheet.Cells(i, alphabet2number('K')).HorizontalAlignment=-4108
                
            
            excelSheet.Cells(lastRow, alphabet2number('B')).Value="Total"
            excelSheet.Cells(lastRow, alphabet2number('G')).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%('G', a), [startRow, lastRow-1]))
            excelSheet.Cells(lastRow, alphabet2number('K')).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%('K', a), [startRow, lastRow-1]))
            excelSheet.Cells(lastRow, alphabet2number('K')).HorizontalAlignment=-4108
    
    
class VATStockWithOutItem(ExcelBasicGenerator):
    
    def inputData(self, additionInfo=[], header=[], data=[]):
        excelSheet=self.workBook.Sheets(1)
        excelSheet.Name=  u'库存商品明细账'
        if not data: data=[("",), ]
        row=len(data)
        col=9
        startRow=8
        lastRow=startRow+row
        startCol=1
        
        excelSheet.Cells(3, alphabet2number('B')).Value=additionInfo[0]
        excelSheet.Cells(3, alphabet2number('D')).Value=additionInfo[1]
        excelSheet.Cells(7, alphabet2number('H')).Value=additionInfo[2]
        excelSheet.Cells(7, alphabet2number('I')).Value=additionInfo[3]
        excelSheet.Range("H%d:%s%d"%(7, number2alphabet(col), 7)).Borders.LineStyle=1
        
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow+2)).Borders.LineStyle=1
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value=data
        
        for r in range(row):
            excelSheet.Cells(startRow + r, alphabet2number('B')).HorizontalAlignment=-4131
        
        excelSheet.Cells(lastRow+1, alphabet2number('C')).Value=u'本月累计'
        excelSheet.Cells(lastRow+2, alphabet2number('C')).Value=u'本年累计'
        
        excelSheet.Cells(lastRow+1, alphabet2number('E')).Value= additionInfo[8]
        excelSheet.Cells(lastRow+1, alphabet2number('G')).Value= additionInfo[9]
        excelSheet.Cells(lastRow+1, alphabet2number('H')).Value= additionInfo[10]
        excelSheet.Cells(lastRow+1, alphabet2number('I')).Value= additionInfo[11]
        
        excelSheet.Cells(lastRow+2, alphabet2number('E')).Value= additionInfo[4]
        excelSheet.Cells(lastRow+2, alphabet2number('G')).Value= additionInfo[5]
        excelSheet.Cells(lastRow+2, alphabet2number('H')).Value= additionInfo[6]
        excelSheet.Cells(lastRow+2, alphabet2number('I')).Value= additionInfo[7]
    

class VATStockWithItem(ExcelBasicGenerator):
    
    def inputData(self, additionInfo=[], header=[], data=[]):
        
        name = "_".join([additionInfo[0], u'库存商品明细账'])
        excelSheet=self.workBook.Sheets(1)
        excelSheet.Name= u'库存商品明细账'

        if not data: data=[("",), ]

        row=len(data)
        col=8
        startRow=8
        lastRow=startRow+row
        startCol=1
        
        excelSheet.Cells(1, alphabet2number('A')).Value=name
        excelSheet.Cells(3, alphabet2number('B')).Value=additionInfo[1]
        excelSheet.Cells(3, alphabet2number('D')).Value=additionInfo[2]
        excelSheet.Cells(7, alphabet2number('A')).Value= u'期初余额'
        excelSheet.Cells(7, alphabet2number('G')).Value=additionInfo[3]
        excelSheet.Cells(7, alphabet2number('H')).Value=additionInfo[4]
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow+2)).Borders.LineStyle=1
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value = data
        excelSheet.Cells(lastRow+1, alphabet2number('B')).Value=u'本月累计'
        excelSheet.Cells(lastRow+2, alphabet2number('B')).Value=u'本年累计'
        
        
        excelSheet.Cells(lastRow+1, alphabet2number('D')).Value= additionInfo[9]
        excelSheet.Cells(lastRow+1, alphabet2number('F')).Value= additionInfo[10]
        excelSheet.Cells(lastRow+1, alphabet2number('G')).Value= additionInfo[11]
        excelSheet.Cells(lastRow+1, alphabet2number('H')).Value= additionInfo[12]
        
        excelSheet.Cells(lastRow+2, alphabet2number('D')).Value= additionInfo[5]
        excelSheet.Cells(lastRow+2, alphabet2number('F')).Value= additionInfo[6]
        excelSheet.Cells(lastRow+2, alphabet2number('G')).Value= additionInfo[7]
        excelSheet.Cells(lastRow+2, alphabet2number('H')).Value= additionInfo[8]
 
class VATInvoiceWithOutCost(ExcelBasicGenerator):
    
    def inputData(self, additionInfo=[], header=[], data=[]):
        excelSheet=self.workBook.Sheets(1)
        excelSheet.Name=additionInfo[0]
        
        if not data: data=[("",), ]
        row=len(data)
        col=14
        startRow=6
        lastRow=startRow+row
        startCol=1
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value=data
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow+2)).Borders.LineStyle=1
        excelSheet.Cells(lastRow+1, alphabet2number('A')).Value=u'Total'
        excelSheet.Cells(lastRow+1, alphabet2number('E')).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%('E', a), [startRow, lastRow-1]))
        #excelSheet.Cells(lastRow+1, alphabet2number('F')).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%('F', a), [startRow, lastRow-1]))
        excelSheet.Cells(lastRow+1, alphabet2number('G')).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%('G', a), [startRow, lastRow-1]))

 
class VATInvoiceWithCost(ExcelBasicGenerator):
    
    def inputData(self, additionInfo=[], header=[], data=[]):
        excelSheet=self.workBook.Sheets(1)
        excelSheet.Name=additionInfo[0]

        if not data: data=[("",), ]

        row=len(data)
        col = 10
        startRow=6
        lastRow=startRow+row
        startCol=1
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow-1)).Value=data
        excelSheet.Range("A%d:%s%d"%(startRow, number2alphabet(col), lastRow+2)).Borders.LineStyle=1
        excelSheet.Cells(lastRow+1, alphabet2number('A')).Value=u'Total'
        excelSheet.Cells(lastRow+1, alphabet2number('E')).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%('E', a), [startRow, lastRow-1]))
        #excelSheet.Cells(lastRow+1, alphabet2number('F')).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%('F', a), [startRow, lastRow-1]))
        excelSheet.Cells(lastRow+1, alphabet2number('G')).Value="=sum(%s)"%":".join(map(lambda a:"%s%d"%('G', a), [startRow, lastRow-1]))

   
   
class PIProceedsExcel(ExcelBasicGenerator):
    
    def outputData(self, additionInfo=[], header=[], data=[]):
        keys = {
               'a':'company_code', 
               'b':'pi_no', 
               'c':'department', 
               'd':'issue_date', 
               'e':'supplier_code', 
               'f':'supplier_name',       
               'g':'supplier_short_name', 
               'h':'remark', 
               'i':'currency', 
               'g':'posted_status', 
               'k':'invoice_amount',      
               'l':'invoice_base_amount', 
               'm':'po_no',  
               'n':'grn_no',  
               'o':'program', 
               'p':'brand', 
               'q':'brand_sub_line', 
               'r':'category', 
               's':'sub_cat_1', 
               't':'sub_cat_2', 
               'u':'sub_cat_3', 
               'v':'material', 
               'w':'merchandise', 
               'x':'internal_item_code', 
               'y':'item_code', 
               'z':'item_description', 
               'aa':'qty', 
               'ab':'unit',  
               'ac':'unit_price', 
               'ad':'item_amount', 
               'ae':'item_base_amount', 
               'af':'kingdee_date', 
               'ag':'date'
               }
        excelSheet= self.workBook.Sheets(1)
        xldata = excelSheet.UsedRange.Value
        cellsLength = len(xldata) + 1
        startCol = 2
        result = []
        for a in range(startCol, cellsLength):
            subdata = {}
            for col, name in keys.iteritems():
                cellValue = excelSheet.Cells(a, col).Value
                if name == 'issue_date' and cellValue:
                    cellValue = date.fromtimestamp(int(cellValue))
                subdata.update({name:cellValue.strip() if isinstance(cellValue,(str,unicode)) else cellValue})
            if len(subdata) > 5:
                print "~"*30, subdata
                result.append(subdata)
        return result

class DNProceedsExcel(ExcelBasicGenerator):
    
    def outputData(self, additionInfo=[], header=[], data=[]):
        keys = {
                'a':'company_code', 
                'b':'number', 
                'c':'stock_adjustment_no',  
                'd':'po_no',  
                'e':'note_type', 
                'f':'other_ref',
                'g':'note_remark', 
                'h':'issue_date', 
                'i':'department',              
                'g':'supplier_code',  
                'k':'supplier_name', 
                'l':'sales_contact', 
                'm':'currency', 
                'n':'note_amount',  
                'o':'note_base_amount',        
                'p':'corporate_customer',  
                'q':'private_brand', 
                'r':'private_brand_sub_line', 
                's':'packaging_category', 
                't':'packaging_type',           
                'u':'sub_cat_2', 
                'v':'sub_cat_3', 
                'w':'material' , 
                'x':'merchandise', 
                'y':'internal_item_code', 
                'z':'item_code', 
                'aa':'item_description', 
                'ab':'order_qty', 
                'ac':'unit',              
                'ad':'unit_price', 
                'ae':'amount',
                'af':'base_amount', 
                'ag':'sn_line_no', 
                'ah':'kingdee_date',
                'ai':'date'
               }
        excelSheet= self.workBook.Sheets(1)
        xldata = excelSheet.UsedRange.Value
        cellsLength = len(xldata) + 1
        startCol = 2
        data = []
        for a in range(startCol, cellsLength):
            subdata = {}
            for col, name in keys.iteritems():
                cellValue = excelSheet.Cells(a, col).Value
                if name == 'issue_date' and cellValue:
                    cellValue = date.fromtimestamp(int(cellValue))
                subdata.update({name:cellValue.strip() if isinstance(cellValue,(str,unicode)) else cellValue})
            if len(subdata) > 5:
                print "~"*30, subdata
                data.append(subdata)
        return data

class PICostExcel(ExcelBasicGenerator):
    
    def outputData(self, additionInfo=[], header=[], data=[]):
        
        keys = {
                'a':'company_code', 
                'b':'invoice_number', 
                'c':'department', 
                'd':'issue_date', 
                'e':'supplier_short_name', 
                'f':'remark',              
                'g':'currency', 
                'h':'posted_status', 
                'i':'invoice_amount', 
                'j':'invoice_base_amount', 
                'k':'po_no',                 
                'l':'grn_no', 
                'm':'program', 
                'n':'brand', 
                'o':'private_brand_sub_line',
                'p':'category', 
                'q':'sub_cat_1', 
                'r':'sub_cat_2', 
                's':'sub_cat_3', 
                't':'material', 
                'u':'merchandise',           
                'v':'internal_item_code',  
                'w':'item_code', 
                'x':'item_description', 
                'y':'qty', 
                'z':'unit', 
                'aa':'unit_price', 
                'ab':'item_amount',           
                'ac':'item_base_amount',  
                'ad':'so_no', 
                'ae':'cust_code', 
                'af':'billing_month', 
                'ag':'a_single_date',
                'ah':'date'
               }
        excelSheet= self.workBook.Sheets(1)
        xldata = excelSheet.UsedRange.Value
        cellsLength = len(xldata) + 1
        startCol = 2
        data = []
        for a in range(startCol, cellsLength):
            subdata = {}
            for col, name in keys.iteritems():
                cellValue = excelSheet.Cells(a, col).Value
                if name == 'issue_date' and cellValue:
                    cellValue = date.fromtimestamp(int(cellValue))
                subdata.update({name:cellValue.strip() if isinstance(cellValue,(str,unicode)) else cellValue})
            if len(subdata) > 5:
                print "~"*30, subdata
                data.append(subdata)
        return data
    

class DNCostExcel(ExcelBasicGenerator):
    
    def outputData(self, additionInfo=[], header=[], data=[]):
        keys = {
                'a':'company_code', 
                'c':'stock_adjustment_no', 
                'd':'po_no', 
                'e':'note_type', 
                'f':'other_ref', 
                'g':'note_remark', 
                'h':'issue_date', 
                'i':'department', 
                'j':'supplier_code',             
                'k':'supplier_name', 
                'l':'sales_contact', 
                'm':'currency', 
                'n':'note_amount', 
                'o':'note_base_amount', 
                'p':'corporate_customer',  
                'q':'private_brand', 
                'r':'private_brand_sub_line',  
                's':'packaging_category', 
                't':'packaging_type', 
                'u':'sub_cat_2',                 
                'v':'sub_cat_3', 
                'w':'material', 
                'x':'merchandise', 
                'y':'internal_item_code',  
                'z':'item_code',  
                'aa':'item_description', 
                'ab':'order_qty',  
                'ac':'unit',  
                'ad':'unit_price', 
                'ae':'amount', 
                'af':'base_amount', 
                'ag':'cost', 
                'ah':'so_no', 
                'ai':'cust_code',
                'aj':'date' 
               }
        excelSheet= self.workBook.Sheets(1)
        xldata = excelSheet.UsedRange.Value
        cellsLength = len(xldata) + 1
        startCol = 2
        data = []
        for a in range(startCol, cellsLength):
            subdata = {}
            for col, name in keys.iteritems():
                cellValue = excelSheet.Cells(a, col).Value
                if name == 'issue_date' and cellValue:
                    cellValue = date.fromtimestamp(int(cellValue))
                subdata.update({name:cellValue.strip() if isinstance(cellValue,(str,unicode)) else cellValue})
            if len(subdata) > 5:
                print "~"*30, subdata
                data.append(subdata)
        return data