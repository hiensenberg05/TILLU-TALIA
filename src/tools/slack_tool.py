"""
💬 Slack Tool - Handles Slack integration for notifications
"""

import asyncio
import logging
import os
from typing import Dict, Any, List, Optional

from .base_tool import BaseTool

logger = logging.getLogger(__name__)

class SlackTool(BaseTool):
    """
    Slack Tool handles:
    - Sending messages to Slack channels
    - Creating rich notifications
    - Managing Slack workspace communication
    - Proper authentication with Composio
    """
    
    def __init__(self):
        # Initialize with Slack auth config
        auth_config_id = os.getenv("SLACK_AUTH_CONFIG_ID", "ac_slack_config")
        super().__init__("Slack", auth_config_id)
        self.default_channel = os.getenv("SLACK_CHANNEL", "#personal-finance")
        
    async def get_tools(self):
        """Get Slack tools"""
        return self.composio.tools.get(user_id=self.user_id, toolkits=["SLACK"])
    
    async def send_message(self, channel: str, message: str, username: str = "Project Raseed") -> Dict[str, Any]:
        """
        Send message to Slack channel
        """
        try:
            result = await self.execute_tool(
                slug="SLACK_SEND_MESSAGE",
                arguments={
                    "channel": channel,
                    "text": message,
                    "username": username,
                    "icon_emoji": ":receipt:"
                }
            )
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "message_id": result["data"].get("ts"),
                    "channel": channel,
                    "result": result["data"]
                }
            else:
                logger.error(f"Slack send message failed: {result['error']}")
                return {
                    "status": "error",
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"❌ Slack send message failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def send_rich_message(self, channel: str, blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send rich message with blocks to Slack
        """
        try:
            result = await self.execute_tool(
                slug="SLACK_SEND_BLOCKS",
                arguments={
                    "channel": channel,
                    "blocks": blocks,
                    "username": "Project Raseed",
                    "icon_emoji": ":chart_with_upwards_trend:"
                }
            )
            
            if result["status"] == "success":
                return {
                    "status": "success",
                    "message_id": result["data"].get("ts"),
                    "channel": channel,
                    "result": result["data"]
                }
            else:
                logger.error(f"Slack send blocks failed: {result['error']}")
                return {
                    "status": "error",
                    "error": result["error"]
                }
                
        except Exception as e:
            logger.error(f"❌ Slack send blocks failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def create_receipt_notification_blocks(self, receipts: List[Dict[str, Any]], summary: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create rich Slack blocks for receipt notification
        """
        blocks = [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "🧾 New Receipts Processed"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Receipts:* {len(receipts)}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Total:* ${summary.get('total_amount', 0):.2f}"
                    }
                ]
            }
        ]
        
        # Add recent receipts
        if receipts:
            receipt_text = ""
            for receipt in receipts[-3:]:  # Show last 3
                merchant = receipt.get("merchant", "Unknown")
                amount = receipt.get("amount", 0)
                category = receipt.get("category", "Other")
                receipt_text += f"• {merchant}: ${amount:.2f} ({category})\n"
            
            blocks.append({
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Recent Receipts:*\n{receipt_text}"
                }
            })
        
        # Add action button
        blocks.append({
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "View Dashboard"
                    },
                    "url": "https://notion.so/your-dashboard",  # Configure your dashboard URL
                    "style": "primary"
                }
            ]
        })
        
        return blocks
    
    async def send_receipt_notification(self, receipts: List[Dict[str, Any]], summary: Dict[str, Any], channel: str = "#personal-finance") -> Dict[str, Any]:
        """
        Send formatted receipt notification to Slack
        """
        try:
            blocks = await self.create_receipt_notification_blocks(receipts, summary)
            return await self.send_rich_message(channel, blocks)
            
        except Exception as e:
            logger.error(f"❌ Slack receipt notification failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
