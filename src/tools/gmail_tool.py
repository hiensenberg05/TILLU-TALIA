"""
📧 Gmail Tool - Handles Gmail integration for receipt extraction
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import base64

from composio import Composio
from composio_openai_agents import OpenAIAgentsProvider

logger = logging.getLogger(__name__)

class GmailTool:
    """
    Gmail Tool handles:
    - Searching for receipt-related emails
    - Extracting email content and attachments
    - Sending email notifications
    - Proper authentication with Composio
    """
    
    def __init__(self):
        # Initialize Composio with proper authentication
        api_key = os.getenv("COMPOSIO_API_KEY")
        if not api_key:
            raise ValueError("COMPOSIO_API_KEY not found in environment variables")
        
        self.composio = Composio(api_key=api_key, provider=OpenAIAgentsProvider())
        
        # Use the user ID from environment or default
        self.user_id = os.getenv("USER_ID", "default_user")
        
        # Your Gmail auth config ID (from your setup)
        self.auth_config_id = os.getenv("GMAIL_AUTH_CONFIG_ID", "ac_yW1QCETwbgI7")
        
        # Check if we have a connected account
        self.connected_account = None
        self._check_connection()
    
    def _check_connection(self):
        """
        Check if Gmail is properly connected
        """
        try:
            # Try to get connected accounts
            connected_accounts = self.composio.connected_accounts.list(user_id=self.user_id)
            
            # Find Gmail connection
            for account in connected_accounts:
                if account.auth_config_id == self.auth_config_id:
                    self.connected_account = account
                    logger.info(f"✅ Gmail connected: {account.id}")
                    return
            
            logger.warning("⚠️ Gmail not connected. You may need to authenticate.")
            
        except Exception as e:
            logger.error(f"❌ Failed to check Gmail connection: {str(e)}")
    
    async def ensure_connection(self) -> bool:
        """
        Ensure Gmail is connected, create connection if needed
        """
        if self.connected_account:
            return True
        
        try:
            # Create connection request
            connection_request = self.composio.connected_accounts.link(
                user_id=self.user_id,
                auth_config_id=self.auth_config_id,
            )
            
            if connection_request.redirect_url:
                logger.info(f"🔗 Please visit this URL to connect Gmail: {connection_request.redirect_url}")
                
                # Wait for connection
                self.connected_account = connection_request.wait_for_connection()
                logger.info(f"✅ Gmail connected successfully: {self.connected_account.id}")
                return True
            else:
                logger.error("❌ Failed to create Gmail connection request")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to connect Gmail: {str(e)}")
            return False
        
    async def search_emails(self, query: str, days_back: int = 7) -> List[Dict[str, Any]]:
        """
        Search for emails matching the query
        """
        try:
            # Ensure Gmail is connected
            if not await self.ensure_connection():
                logger.error("❌ Gmail not connected")
                return []
            
            # Use Composio to search Gmail with proper authentication
            tools = self.composio.tools.get(user_id=self.user_id, toolkits=["GMAIL"])
            
            # Create search query with date filter
            date_filter = f"newer_than:{days_back}d"
            full_query = f"{query} {date_filter}"
            
            # Execute search using Composio with connected account
            result = self.composio.tools.execute(
                slug="GMAIL_SEARCH_EMAILS",
                arguments={
                    "query": full_query,
                    "max_results": 50
                },
                user_id=self.user_id,
                connected_account_id=self.connected_account.id
            )
            
            if result.successful:
                emails = result.data if isinstance(result.data, list) else [result.data]
                logger.info(f"✅ Found {len(emails)} emails")
                return emails
            else:
                logger.error(f"Gmail search failed: {result.error}")
                return []
                
        except Exception as e:
            logger.error(f"❌ Gmail search failed: {str(e)}")
            return []
    
    async def get_email_content(self, email_id: str) -> Dict[str, Any]:
        """
        Get full email content including attachments
        """
        try:
            # Ensure Gmail is connected
            if not await self.ensure_connection():
                logger.error("❌ Gmail not connected")
                return {}
            
            result = self.composio.tools.execute(
                slug="GMAIL_GET_EMAIL",
                arguments={
                    "email_id": email_id,
                    "include_attachments": True
                },
                user_id=self.user_id,
                connected_account_id=self.connected_account.id
            )
            
            if result.successful:
                return result.data
            else:
                logger.error(f"Gmail get email failed: {result.error}")
                return {}
                
        except Exception as e:
            logger.error(f"❌ Gmail get email failed: {str(e)}")
            return {}
    
    async def download_attachment(self, attachment_id: str) -> Optional[bytes]:
        """
        Download email attachment
        """
        try:
            # Ensure Gmail is connected
            if not await self.ensure_connection():
                logger.error("❌ Gmail not connected")
                return None
            
            result = self.composio.tools.execute(
                slug="GMAIL_DOWNLOAD_ATTACHMENT",
                arguments={
                    "attachment_id": attachment_id
                },
                user_id=self.user_id,
                connected_account_id=self.connected_account.id
            )
            
            if result.successful:
                # Handle base64 encoded data
                if isinstance(result.data, str):
                    return base64.b64decode(result.data)
                return result.data
            else:
                logger.error(f"Gmail attachment download failed: {result.error}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Gmail attachment download failed: {str(e)}")
            return None
    
    async def send_email(self, to: str, subject: str, body: str, is_html: bool = False) -> Dict[str, Any]:
        """
        Send email notification
        """
        try:
            # Ensure Gmail is connected
            if not await self.ensure_connection():
                logger.error("❌ Gmail not connected")
                return {
                    "status": "error",
                    "error": "Gmail not connected"
                }
            
            result = self.composio.tools.execute(
                slug="GMAIL_SEND_EMAIL",
                arguments={
                    "to": to,
                    "subject": subject,
                    "body": body,
                    "is_html": is_html
                },
                user_id=self.user_id,
                connected_account_id=self.connected_account.id
            )
            
            if result.successful:
                return {
                    "status": "success",
                    "message_id": result.data.get("id"),
                    "result": result.data
                }
            else:
                logger.error(f"Gmail send email failed: {result.error}")
                return {
                    "status": "error",
                    "error": result.error
                }
                
        except Exception as e:
            logger.error(f"❌ Gmail send email failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
