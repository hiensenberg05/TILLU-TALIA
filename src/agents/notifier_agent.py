"""
💬 Notifier Agent - Communicates updates to the user
Sends Slack alerts, weekly digests, and email confirmations
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from composio import Composio

from tools.slack_tool import SlackTool
from tools.gmail_tool import GmailTool

logger = logging.getLogger(__name__)

class NotifierAgent:
    """
    Notifier Agent handles:
    - Sending Slack notifications for new receipts
    - Creating weekly spending summaries
    - Sending email confirmations
    - Alerting about spending anomalies
    """
    
    def __init__(self):
        self.composio = Composio()
        self.slack_tool = SlackTool()
        self.gmail_tool = GmailTool()
        
        self.status = {
            "last_notification": None,
            "notifications_sent": 0,
            "slack_messages": 0,
            "emails_sent": 0,
            "errors": []
        }
    
    async def send_notifications(self, analysis_results: Dict[str, Any], update_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send notifications based on analysis and update results
        """
        logger.info("📢 Sending notifications...")
        
        receipts = analysis_results.get("receipts", [])
        summary = analysis_results.get("summary", {})
        insights = analysis_results.get("insights", [])
        anomalies = analysis_results.get("anomalies", [])
        
        notification_results = {
            "status": "success",
            "notifications_sent": 0,
            "slack_messages": 0,
            "emails_sent": 0,
            "details": []
        }
        
        try:
            # Send Slack notification for new receipts
            if receipts:
                slack_result = await self.send_slack_receipt_notification(receipts, summary)
                if slack_result["status"] == "success":
                    notification_results["slack_messages"] += 1
                    notification_results["details"].append("Slack receipt notification sent")
            
            # Send anomaly alerts
            if anomalies:
                anomaly_result = await self.send_anomaly_alert(anomalies)
                if anomaly_result["status"] == "success":
                    notification_results["slack_messages"] += 1
                    notification_results["details"].append("Slack anomaly alert sent")
            
            # Send weekly summary if it's the right time
            if await self.should_send_weekly_summary():
                weekly_result = await self.send_weekly_summary(analysis_results)
                if weekly_result["status"] == "success":
                    notification_results["slack_messages"] += 1
                    notification_results["emails_sent"] += 1
                    notification_results["details"].append("Weekly summary sent")
            
            # Send email confirmation
            if receipts:
                email_result = await self.send_email_confirmation(receipts, summary)
                if email_result["status"] == "success":
                    notification_results["emails_sent"] += 1
                    notification_results["details"].append("Email confirmation sent")
            
            notification_results["notifications_sent"] = (
                notification_results["slack_messages"] + notification_results["emails_sent"]
            )
            
            self.status["last_notification"] = datetime.now()
            self.status["notifications_sent"] += notification_results["notifications_sent"]
            self.status["slack_messages"] += notification_results["slack_messages"]
            self.status["emails_sent"] += notification_results["emails_sent"]
            
            logger.info(f"✅ Notifications sent: {notification_results['notifications_sent']} total")
            
            return notification_results
            
        except Exception as e:
            logger.error(f"❌ Notification sending failed: {str(e)}")
            self.status["errors"].append(str(e))
            notification_results["status"] = "error"
            notification_results["error"] = str(e)
            return notification_results
    
    async def send_slack_receipt_notification(self, receipts: List[Dict[str, Any]], summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send Slack notification about new receipts processed
        """
        try:
            receipt_count = len(receipts)
            total_amount = summary.get("total_amount", 0)
            
            # Create message
            message = f"""🧾 *New Receipts Processed*
            
📊 *Summary:*
• {receipt_count} receipt{'s' if receipt_count != 1 else ''} processed
• Total amount: ${total_amount:.2f}
• Top categories: {', '.join([cat[0] for cat in summary.get('top_categories', [])[:3]])}

📋 *Recent Receipts:*
"""
            
            # Add recent receipts
            for receipt in receipts[-3:]:  # Show last 3 receipts
                merchant = receipt.get("merchant", "Unknown")
                amount = receipt.get("amount", 0)
                category = receipt.get("category", "Other")
                message += f"• {merchant}: ${amount:.2f} ({category})\n"
            
            message += f"\n✅ All receipts have been categorized and added to your financial dashboard!"
            
            # Send to Slack
            result = await self.slack_tool.send_message(
                channel="#personal-finance",  # Configure your channel
                message=message,
                username="Project Raseed"
            )
            
            return {
                "status": "success",
                "message_sent": True,
                "receipt_count": receipt_count,
                "total_amount": total_amount,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Slack receipt notification failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def send_anomaly_alert(self, anomalies: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Send Slack alert about spending anomalies
        """
        try:
            if not anomalies:
                return {"status": "success", "message": "No anomalies to report"}
            
            message = f"⚠️ *Spending Anomaly Alert*\n\n"
            
            for anomaly in anomalies:
                anomaly_type = anomaly.get("type", "unknown")
                description = anomaly.get("description", "")
                severity = anomaly.get("severity", "medium")
                
                emoji = "🔴" if severity == "high" else "🟡" if severity == "medium" else "🟢"
                message += f"{emoji} {description}\n"
            
            message += "\n💡 Consider reviewing these transactions for accuracy."
            
            # Send to Slack
            result = await self.slack_tool.send_message(
                channel="#personal-finance",
                message=message,
                username="Project Raseed Alert"
            )
            
            return {
                "status": "success",
                "anomalies_reported": len(anomalies),
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Anomaly alert failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def send_weekly_summary(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send weekly spending summary
        """
        try:
            summary = analysis_results.get("summary", {})
            insights = analysis_results.get("insights", [])
            
            # Create comprehensive weekly summary
            message = f"""📊 *Weekly Spending Summary*
*Week of {datetime.now().strftime('%B %d, %Y')}*

💰 *Financial Overview:*
• Total spent: ${summary.get('total_amount', 0):.2f}
• Number of transactions: {summary.get('receipt_count', 0)}
• Average transaction: ${summary.get('statistics', {}).get('average_amount', 0):.2f}

🏷️ *Top Spending Categories:*
"""
            
            for category, amount in summary.get("top_categories", [])[:5]:
                message += f"• {category}: ${amount:.2f}\n"
            
            if insights:
                message += f"\n💡 *Insights & Recommendations:*\n"
                for insight in insights[:3]:
                    message += f"• {insight}\n"
            
            message += f"\n📈 View your complete dashboard in Notion for detailed analysis!"
            
            # Send to Slack
            slack_result = await self.slack_tool.send_message(
                channel="#personal-finance",
                message=message,
                username="Project Raseed Weekly"
            )
            
            # Send email summary
            email_result = await self.send_weekly_email_summary(summary, insights)
            
            return {
                "status": "success",
                "slack_sent": slack_result.get("status") == "success",
                "email_sent": email_result.get("status") == "success",
                "summary_data": summary
            }
            
        except Exception as e:
            logger.error(f"❌ Weekly summary failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def send_weekly_email_summary(self, summary: Dict[str, Any], insights: List[str]) -> Dict[str, Any]:
        """
        Send weekly summary via email
        """
        try:
            subject = f"Weekly Spending Summary - {datetime.now().strftime('%B %d, %Y')}"
            
            body = f"""
            <h2>📊 Weekly Spending Summary</h2>
            <p>Here's your spending overview for the week:</p>
            
            <h3>💰 Financial Overview</h3>
            <ul>
                <li>Total spent: ${summary.get('total_amount', 0):.2f}</li>
                <li>Number of transactions: {summary.get('receipt_count', 0)}</li>
                <li>Average transaction: ${summary.get('statistics', {}).get('average_amount', 0):.2f}</li>
            </ul>
            
            <h3>🏷️ Top Spending Categories</h3>
            <ul>
            """
            
            for category, amount in summary.get("top_categories", [])[:5]:
                body += f"<li>{category}: ${amount:.2f}</li>"
            
            body += "</ul>"
            
            if insights:
                body += "<h3>💡 Insights & Recommendations</h3><ul>"
                for insight in insights[:3]:
                    body += f"<li>{insight}</li>"
                body += "</ul>"
            
            body += """
            <p>View your complete financial dashboard in Notion for detailed analysis.</p>
            <p>Best regards,<br>Project Raseed Team</p>
            """
            
            # Send email
            result = await self.gmail_tool.send_email(
                to="user@example.com",  # Configure your email
                subject=subject,
                body=body,
                is_html=True
            )
            
            return {
                "status": "success",
                "email_sent": True,
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Weekly email summary failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def send_email_confirmation(self, receipts: List[Dict[str, Any]], summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Send email confirmation of processed receipts
        """
        try:
            subject = f"Receipts Processed - {len(receipts)} new transaction{'s' if len(receipts) != 1 else ''}"
            
            body = f"""
            <h2>🧾 Receipts Successfully Processed</h2>
            <p>Your receipts have been processed and added to your financial dashboard.</p>
            
            <h3>📊 Summary</h3>
            <ul>
                <li>Receipts processed: {len(receipts)}</li>
                <li>Total amount: ${summary.get('total_amount', 0):.2f}</li>
                <li>Categories: {len(summary.get('category_totals', {}))}</li>
            </ul>
            
            <h3>📋 Recent Transactions</h3>
            <ul>
            """
            
            for receipt in receipts[-5:]:  # Show last 5 receipts
                merchant = receipt.get("merchant", "Unknown")
                amount = receipt.get("amount", 0)
                category = receipt.get("category", "Other")
                date = receipt.get("date", "")
                body += f"<li>{date}: {merchant} - ${amount:.2f} ({category})</li>"
            
            body += """
            </ul>
            <p>All transactions have been categorized and are now available in your Notion dashboard and Google Sheets.</p>
            <p>Best regards,<br>Project Raseed Team</p>
            """
            
            # Send email
            result = await self.gmail_tool.send_email(
                to="user@example.com",  # Configure your email
                subject=subject,
                body=body,
                is_html=True
            )
            
            return {
                "status": "success",
                "email_sent": True,
                "receipts_confirmed": len(receipts),
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Email confirmation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def should_send_weekly_summary(self) -> bool:
        """
        Check if it's time to send a weekly summary (e.g., every Monday)
        """
        now = datetime.now()
        # Send weekly summary on Mondays at 9 AM
        return now.weekday() == 0 and now.hour >= 9
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent": "NotifierAgent",
            "status": "active" if not self.status["errors"] else "error",
            "last_notification": self.status["last_notification"],
            "notifications_sent": self.status["notifications_sent"],
            "slack_messages": self.status["slack_messages"],
            "emails_sent": self.status["emails_sent"],
            "errors": self.status["errors"]
        }

# Demo function
async def demo_notifications():
    """Demo the notifier agent"""
    notifier = NotifierAgent()
    
    print("💬 Notifier Agent Demo")
    print("=" * 30)
    
    # Sample analysis results
    sample_analysis = {
        "receipts": [
            {
                "merchant": "Whole Foods",
                "amount": 85.50,
                "category": "Groceries",
                "date": "2024-01-15"
            }
        ],
        "summary": {
            "total_amount": 85.50,
            "receipt_count": 1,
            "top_categories": [("Groceries", 85.50)],
            "statistics": {"average_amount": 85.50}
        },
        "insights": [
            "Consider buying generic brands to save money",
            "Track grocery spending to stay within budget"
        ],
        "anomalies": []
    }
    
    sample_update = {
        "updated_databases": ["Google Sheets", "Notion"],
        "status": "success"
    }
    
    results = await notifier.send_notifications(sample_analysis, sample_update)
    
    print(f"Status: {results['status']}")
    print(f"Notifications sent: {results['notifications_sent']}")
    print(f"Slack messages: {results['slack_messages']}")
    print(f"Emails sent: {results['emails_sent']}")
    
    for detail in results.get("details", []):
        print(f"  • {detail}")
    
    return results

if __name__ == "__main__":
    asyncio.run(demo_notifications())
