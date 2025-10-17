"""
📋 Notion Tool - Handles Notion integration for dashboard management
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional

from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class NotionTool(BaseTool):
    """
    Notion Tool handles:
    - Creating pages in Notion databases
    - Updating dashboard content
    - Managing financial data visualization
    - Proper authentication with Composio
    """
    
    def __init__(self):
        # Initialize with Notion auth config
        auth_config_id = os.getenv("NOTION_AUTH_CONFIG_ID", "ac_notion_config")
        super().__init__("Notion", auth_config_id)
        self.database_id = os.getenv("NOTION_DATABASE_ID", "YOUR_NOTION_DATABASE_ID")
        
    async def get_tools(self):
        """Get Notion tools"""
        return self.composio.tools.get(user_id=self.user_id, toolkits=["NOTION"])
    
    async def create_page(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new page in Notion database
        """
        try:
            result = await self.execute_tool(
                slug="NOTION_CREATE_PAGE",
                arguments={
                    "database_id": self.database_id,
                    "properties": page_data.get("properties", {}),
                    "children": page_data.get("children", [])
                }
            )
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "page_id": result["data"].get("id"),
                    "result": result["data"]
                }
            else:
                logger.error(f"Notion create page failed: {result['error']}")
                return {
                    "status": "error",
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"❌ Notion create page failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_page(self, page_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing Notion page
        """
        try:
            tools = self.composio.tools.get(user_id=self.user_id, toolkits=["NOTION"])
            
            result = self.composio.tools.execute(
                slug="NOTION_UPDATE_PAGE",
                arguments={
                    "page_id": page_id,
                    "properties": properties
                },
                user_id=self.user_id
            )
            
            if result.successful:
                return {
                    "status": "success",
                    "page_id": page_id,
                    "result": result.data
                }
            else:
                logger.error(f"Notion update page failed: {result.error}")
                return {
                    "status": "error",
                    "error": result.error
                }
                
        except Exception as e:
            logger.error(f"❌ Notion update page failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def query_database(self, filter_conditions: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Query Notion database for existing data
        """
        try:
            tools = self.composio.tools.get(user_id=self.user_id, toolkits=["NOTION"])
            
            arguments = {
                "database_id": self.database_id
            }
            
            if filter_conditions:
                arguments["filter"] = filter_conditions
            
            result = self.composio.tools.execute(
                slug="NOTION_QUERY_DATABASE",
                arguments=arguments,
                user_id=self.user_id
            )
            
            if result.successful:
                return {
                    "status": "success",
                    "pages": result.data.get("results", []),
                    "result": result.data
                }
            else:
                logger.error(f"Notion query database failed: {result.error}")
                return {
                    "status": "error",
                    "error": result.error
                }
                
        except Exception as e:
            logger.error(f"❌ Notion query database failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
