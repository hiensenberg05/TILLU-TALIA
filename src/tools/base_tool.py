"""
🔧 Base Tool - Common authentication and connection handling for all tools
"""

import os
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider

logger = logging.getLogger(__name__)

class BaseTool(ABC):
    """
    Base class for all Composio tools with proper authentication
    """
    
    def __init__(self, toolkit_name: str, auth_config_id: str = None):
        # Initialize Composio with proper authentication
        api_key = os.getenv("COMPOSIO_API_KEY")
        if not api_key:
            raise ValueError("COMPOSIO_API_KEY not found in environment variables")
        
        self.composio = Composio(api_key=api_key, provider=OpenAIAgentsProvider())
        self.toolkit_name = toolkit_name
        self.user_id = os.getenv("USER_ID", "default_user")
        self.auth_config_id = auth_config_id
        self.connected_account = None
        
        # Check connection on initialization
        self._check_connection()
    
    def _check_connection(self):
        """
        Check if the service is properly connected
        """
        try:
            if not self.auth_config_id:
                logger.warning(f"⚠️ {self.toolkit_name} auth_config_id not provided")
                return
            
            # Try to get connected accounts
            connected_accounts = self.composio.connected_accounts.list(user_id=self.user_id)
            
            # Find connection for this toolkit
            for account in connected_accounts:
                if account.auth_config_id == self.auth_config_id:
                    self.connected_account = account
                    logger.info(f"✅ {self.toolkit_name} connected: {account.id}")
                    return
            
            logger.warning(f"⚠️ {self.toolkit_name} not connected. You may need to authenticate.")
            
        except Exception as e:
            logger.error(f"❌ Failed to check {self.toolkit_name} connection: {str(e)}")
    
    async def ensure_connection(self) -> bool:
        """
        Ensure the service is connected, create connection if needed
        """
        if self.connected_account:
            return True
        
        if not self.auth_config_id:
            logger.error(f"❌ {self.toolkit_name} auth_config_id not configured")
            return False
        
        try:
            # Create connection request
            connection_request = self.composio.connected_accounts.link(
                user_id=self.user_id,
                auth_config_id=self.auth_config_id,
            )
            
            if connection_request.redirect_url:
                logger.info(f"🔗 Please visit this URL to connect {self.toolkit_name}: {connection_request.redirect_url}")
                
                # Wait for connection
                self.connected_account = connection_request.wait_for_connection()
                logger.info(f"✅ {self.toolkit_name} connected successfully: {self.connected_account.id}")
                return True
            else:
                logger.error(f"❌ Failed to create {self.toolkit_name} connection request")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect {self.toolkit_name}: {str(e)}")
            return False
    
    async def execute_tool(self, slug: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a tool with proper authentication
        """
        try:
            # Ensure connection
            if not await self.ensure_connection():
                logger.error(f"❌ {self.toolkit_name} not connected")
                return {
                    "status": "error",
                    "error": f"{self.toolkit_name} not connected"
                }
            
            # Execute the tool
            result = self.composio.tools.execute(
                slug=slug,
                arguments=arguments,
                user_id=self.user_id,
                connected_account_id=self.connected_account.id
            )
            
            if result.successful:
                return {
                    "status": "success",
                    "data": result.data
                }
            else:
                logger.error(f"{self.toolkit_name} tool execution failed: {result.error}")
                return {
                    "status": "error",
                    "error": result.error
                }
                
        except Exception as e:
            logger.error(f"❌ {self.toolkit_name} tool execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    @abstractmethod
    async def get_tools(self):
        """
        Get available tools for this toolkit
        """
        pass
