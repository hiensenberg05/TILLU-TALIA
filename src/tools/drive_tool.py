"""
📁 Drive Tool - Handles Google Drive integration for receipt files
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class DriveTool(BaseTool):
    """
    Drive Tool handles:
    - Searching for receipt files in Google Drive
    - Downloading file content
    - Managing file metadata
    - Proper authentication with Composio
    """
    
    def __init__(self):
        # Initialize with Google Drive auth config
        auth_config_id = os.getenv("GOOGLE_DRIVE_AUTH_CONFIG_ID", "ac_google_drive_config")
        super().__init__("Google Drive", auth_config_id)
        
    async def get_tools(self):
        """Get Google Drive tools"""
        return self.composio.tools.get(user_id=self.user_id, toolkits=["GOOGLE_DRIVE"])
    
    async def search_files(self, query: str, file_types: List[str] = None, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Search for files in Google Drive
        """
        try:
            # Build search query
            search_query = f"name contains '{query}'"
            
            if file_types:
                file_type_filter = " or ".join([f"mimeType contains '{ft}'" for ft in file_types])
                search_query += f" and ({file_type_filter})"
            
            # Add date filter
            date_filter = f"modifiedTime > '{datetime.now() - timedelta(days=days_back)}'"
            search_query += f" and {date_filter}"
            
            result = await self.execute_tool(
                slug="GOOGLE_DRIVE_SEARCH_FILES",
                arguments={
                    "query": search_query,
                    "max_results": 50
                }
            )
            
            if result["status"] == "success":
                files = result["data"] if isinstance(result["data"], list) else [result["data"]]
                logger.info(f"✅ Found {len(files)} files in Google Drive")
                return files
            else:
                logger.error(f"Google Drive search failed: {result['error']}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Google Drive search failed: {str(e)}")
            return []
    
    async def download_file(self, file_id: str) -> Optional[bytes]:
        """
        Download file content from Google Drive
        """
        try:
            result = await self.execute_tool(
                slug="GOOGLE_DRIVE_DOWNLOAD_FILE",
                arguments={
                    "file_id": file_id
                }
            )
            
            if result["status"] == "success":
                # Handle different data formats
                data = result["data"]
                if isinstance(data, str):
                    return data.encode()
                return data
            else:
                logger.error(f"Google Drive download failed: {result['error']}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Google Drive download failed: {str(e)}")
            return None
    
    async def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get file metadata from Google Drive
        """
        try:
            result = await self.execute_tool(
                slug="GOOGLE_DRIVE_GET_FILE_METADATA",
                arguments={
                    "file_id": file_id
                }
            )
            
            if result["status"] == "success":
                return result["data"]
            else:
                logger.error(f"Google Drive get metadata failed: {result['error']}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Google Drive get metadata failed: {str(e)}")
            return {}
