package com.report;

import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.util.HashMap;
import java.util.Iterator;
import java.util.LinkedList;
import java.util.List;
import java.util.Map;

import org.apache.poi.hssf.usermodel.HSSFFont;
import org.apache.poi.openxml4j.exceptions.InvalidFormatException;
import org.apache.poi.ss.usermodel.Cell;
import org.apache.poi.ss.usermodel.CellStyle;
import org.apache.poi.ss.usermodel.Font;
import org.apache.poi.ss.usermodel.IndexedColors;
import org.apache.poi.ss.usermodel.Row;
import org.apache.poi.ss.usermodel.Sheet;
import org.apache.poi.ss.usermodel.Workbook;
import org.apache.poi.ss.usermodel.WorkbookFactory;
import org.apache.poi.ss.util.CellRangeAddress;


import py4j.GatewayServer;



public class Index {
	
	@SuppressWarnings("unchecked")
	public void report(String im, String ou, List<List<Object>> header, HashMap<String, HashMap<String, String>> style) throws InvalidFormatException, IOException{
		InputStream inp = new FileInputStream(im);
	    Workbook wb = WorkbookFactory.create(inp);
	    Sheet sheet = wb.getSheetAt(0);
	    createStyle(style, sheet, wb);
	    Iterator<?> header_iter = ((List<?>) header).iterator();
	    while (header_iter.hasNext()) {
	    	Integer x = null;
	    	Integer y = null;
	    	Object header_value = null;
			List<Object> header_item = (List<Object>) header_iter.next();
			if(header_item.size() == 2){
				String path = (String) header_item.get(0);
				System.out.println(path);
				CellRangeAddress position = CellRangeAddress.valueOf(path);
				x = position.getFirstRow();
				y = position.getFirstColumn();
				header_value = (Object) header_item.get(1);
			}else{
				x = (Integer) header_item.get(0);
	    		y = (Integer) header_item.get(1);
	    		header_value = (Object) header_item.get(2);
			}
	    	if(header_value == null || x == null || y == null) continue;
	    	Row row = sheet.getRow(x);
	    	if(row == null)
	    		row = sheet.createRow(x);
	    	String header_type = header_value.getClass().getName();
    		Cell cell = row.getCell(y);
    		if(cell == null)
    			cell = row.createCell(y);
	    	if(header_type == "java.lang.String"){
	    		cell.setCellValue((String) header_value);
	    	}
	    	else if(header_type == "java.lang.Integer"){
	    		cell.setCellValue((Integer) header_value);
	    	}
	    	else if(header_type == "java.lang.Double"){
	    		cell.setCellValue((Double) header_value);
	    	}	
	    	else if(header_type == "java.util.LinkedList"){
	    		Integer column_x = x;
	    		Iterator<?> header_column = ((List<List<String>>) header_value).iterator();
	    		while (header_column.hasNext()) {
	    			Iterator<?> header_column_list = ((List<String>) header_column.next()).iterator();
	    	    	Row row_column = sheet.getRow(column_x);
	    	    	if(row_column == null)
	    	    		row_column = sheet.createRow(column_x);
	    	    	Integer i = 0;
	    	    	while (header_column_list.hasNext()) {
	    	    		Cell row_row = row_column.getCell(i);
	    	    		if(row_row == null)
	    	    			row_row = row_column.createCell(i);
	    	    		Object column_value = header_column_list.next();
	    	    		if(column_value != null){
	    	    			setCell(row_row, column_value);
	    	    		}
	    	    		i = i + 1;
					}
	    	    	column_x = column_x + 1;
				}
	    	}
			
		}
	    FileOutputStream fileOut = new FileOutputStream(ou);
	    wb.write(fileOut);
	    fileOut.close();
	    inp.close();
	}
	
	public void setCell(Cell cell, Object cell_value){
		String type = cell_value.getClass().getName();
		if(type == "java.lang.Integer"){
			cell.setCellValue((Integer) cell_value);
		}else if(type == "java.lang.Double"){
			cell.setCellValue((Double) cell_value);
		}else if(type == "java.lang.String"){
			cell.setCellValue((String) cell_value);
		}
	}
	
	@SuppressWarnings("unchecked")
	public void createStyle(HashMap<String, HashMap<String, String>> style, Sheet mSheet, Workbook mWorkbook){
		Iterator<?> style_iter = style.entrySet().iterator();
		while (style_iter.hasNext()) {
	        Map.Entry style_entry = (Map.Entry) style_iter.next();
	        String key = (String) style_entry.getKey();
	        HashMap<String, String> val = (HashMap<String, String>)  style_entry.getValue();
	        if(key.equals("sheet")){
		        Iterator<?> attr_iter = val.entrySet().iterator();
		        while (attr_iter.hasNext()) {
		        	Map.Entry attr_entry = (Map.Entry) attr_iter.next();
		        	Integer attr_key = (Integer) attr_entry.getKey();
		        	String attr_val = (String) attr_entry.getValue();
		        	mWorkbook.setSheetName(attr_key, attr_val);
		        }
	        	continue;
	        }
	        CellRangeAddress position = CellRangeAddress.valueOf(key);
	        for (int i = position.getFirstRow(); i < position.getLastRow() + 1; i++) {
				for (int j = position.getFirstColumn(); j < position.getLastColumn() + 1; j++) {
					Row row = mSheet.getRow(i);
					if(row == null)
						row = mSheet.createRow(i);
					Cell cell = row.getCell(j);
					if(cell == null)
						cell = row.createCell(j);
		        	CellStyle cellStyle = mWorkbook.createCellStyle();
			        Iterator<?> attr_iter = val.entrySet().iterator();
			        while (attr_iter.hasNext()) {
			        	Map.Entry attr_entry = (Map.Entry) attr_iter.next();
			        	String attr_key = (String) attr_entry.getKey();
			        	String attr_val = (String) attr_entry.getValue();
			        	if(attr_val == null) 
			        		continue;
			        	if(attr_key.equals("border")){
			        		cellStyle.setBorderBottom(CellStyle.BORDER_THIN);
			        		cellStyle.setBorderLeft(CellStyle.BORDER_THIN);
			        		cellStyle.setBorderRight(CellStyle.BORDER_THIN);
			        		cellStyle.setBorderTop(CellStyle.BORDER_THIN);
			        	}
			        	if(attr_key.equals("borderColor")){
			        		cellStyle.setBottomBorderColor(IndexedColors.BLACK.getIndex());
			        		cellStyle.setLeftBorderColor(IndexedColors.BLACK.getIndex());
			        		cellStyle.setRightBorderColor(IndexedColors.BLACK.getIndex());
			        		cellStyle.setTopBorderColor(IndexedColors.BLACK.getIndex());
			        	}
			        	if(attr_key.equals("excute")){
			        		cell.setCellFormula(attr_val);
			        	}
			        	if(attr_key.equals("align")){
			        		if(attr_val.equals("right")){
			        			cellStyle.setAlignment(CellStyle.ALIGN_RIGHT);
			        		}else if(attr_val.equals("left")){
			        			cellStyle.setAlignment(CellStyle.ALIGN_LEFT);
			        		}else if(attr_val.equals("top")){
			        			cellStyle.setVerticalAlignment(CellStyle.VERTICAL_TOP);
			        		}else if(attr_val.equals("bottom")){
			        			cellStyle.setVerticalAlignment(CellStyle.VERTICAL_BOTTOM);
			        		}else if(attr_val.equals("center")){
			        			cellStyle.setAlignment(CellStyle.ALIGN_CENTER);
			        		}
			        	}
			           Font font = null;
				       if(attr_key.equals("fontSize")){
				    	   		short fontSize = Short.parseShort(attr_val);
				    	   		if(font == null)
				    	   			font = mWorkbook.createFont();
				        		font.setFontHeightInPoints(fontSize);
				        	    row.setHeightInPoints(fontSize + 4);
				           }
			        	if(attr_key.equals("fontBold")){
			        		if(font == null)
			        			font = mWorkbook.createFont();
			        		font.setBoldweight(HSSFFont.BOLDWEIGHT_BOLD);
			        	}
			           if(attr_key.equals("fontColor")){
			        	    if(font == null)
			        	    	font = mWorkbook.createFont();
			        	    font.setColor(IndexedColors.BLACK.getIndex());
			           }
			          if(font != null){
			        	  cellStyle.setFont(font);
			          }
			          if(attr_key.equals("merged")){
			        	  	mSheet.addMergedRegion(position);
			          }
					}
			        cell.setCellStyle(cellStyle);
				}
			}
	        
		}
	}
	
	
	public List<Object> create_list(){
		return new LinkedList<Object>(); 
	}

	public HashMap<String, Object> create_hashmap(){
		return new HashMap<String, Object>();
	}
	
	public static void main(String[] args) {
		Index mIndex = new Index();
		GatewayServer gatewayServer = new GatewayServer(mIndex);
	    gatewayServer.start();
	    System.out.println("Gateway Server Started");
	}	
}
