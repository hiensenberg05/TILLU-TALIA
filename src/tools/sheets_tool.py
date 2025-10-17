"""
📊 Sheets Tool - Handles Google Sheets integration for data storage
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional

from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class SheetsTool(BaseTool):
    """
    Sheets Tool handles:
    - Appending data to Google Sheets
    - Creating new sheets
    - Managing spreadsheet data
    - Proper authentication with Composio
    """
    
    def __init__(self):
        # Initialize with Google Sheets auth config
        auth_config_id = os.getenv("GOOGLE_SHEETS_AUTH_CONFIG_ID", "ac_google_sheets_config")
        super().__init__("Google Sheets", auth_config_id)
        self.spreadsheet_id = os.getenv("SPREADSHEET_ID", "YOUR_SPREADSHEET_ID")
        
    async def get_tools(self):
        """Get Google Sheets tools"""
        return self.composio.tools.get(user_id=self.user_id, toolkits=["GOOGLE_SHEETS"])
    
    async def append_data(self, data: List[List[Any]], sheet_name: str = "Receipts") -> Dict[str, Any]:
        """
        Append data to Google Sheets
        """
        try:
            result = await self.execute_tool(
                slug="GOOGLE_SHEETS_APPEND_DATA",
                arguments={
                    "spreadsheet_id": self.spreadsheet_id,
                    "sheet_name": sheet_name,
                    "data": data
                }
            )
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "rows_added": len(data),
                    "sheet_id": self.spreadsheet_id,
                    "result": result["data"]
                }
            else:
                logger.error(f"Google Sheets append failed: {result['error']}")
                return {
                    "status": "error",
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"❌ Google Sheets append failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def has_data(self, sheet_name: str = "Receipts") -> bool:
        """
        Check if sheet has existing data
        """
        try:
            result = await self.execute_tool(
                slug="GOOGLE_SHEETS_GET_DATA",
                arguments={
                    "spreadsheet_id": self.spreadsheet_id,
                    "sheet_name": sheet_name,
                    "range": "A1:Z1"  # Check first row
                }
            )
            
            if result["status"] == "success":
                data = result["data"]
                return len(data) > 0 and any(cell for cell in data[0] if cell)
            else:
                logger.error(f"Google Sheets get data failed: {result['error']}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Google Sheets has_data check failed: {str(e)}")
            return False
    
    async def create_sheet(self, sheet_name: str) -> Dict[str, Any]:
        """
        Create a new sheet in the spreadsheet
        """
        try:
            result = await self.execute_tool(
                slug="GOOGLE_SHEETS_CREATE_SHEET",
                arguments={
                    "spreadsheet_id": self.spreadsheet_id,
                    "sheet_name": sheet_name
                }
            )
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "sheet_name": sheet_name,
                    "result": result["data"]
                }
            else:
                logger.error(f"Google Sheets create sheet failed: {result['error']}")
                return {
                    "status": "error",
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"❌ Google Sheets create sheet failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
