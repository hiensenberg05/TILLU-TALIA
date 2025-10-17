"""
🔄 Updater Agent - Syncs structured data to Sheets & Notion
Maintains a real-time financial database
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from composio import Composio

from tools.sheets_tool import SheetsTool
from tools.notion_tool import NotionTool

logger = logging.getLogger(__name__)

class UpdaterAgent:
    """
    Updater Agent handles:
    - Syncing receipt data to Google Sheets
    - Updating Notion dashboards
    - Maintaining data consistency
    - Creating financial summaries
    """
    
    def __init__(self):
        self.composio = Composio()
        self.sheets_tool = SheetsTool()
        self.notion_tool = NotionTool()
        
        self.status = {
            "last_update": None,
            "sheets_updated": False,
            "notion_updated": False,
            "errors": []
        }
    
    async def update_databases(self, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update both Google Sheets and Notion with analyzed receipt data
        """
        logger.info("📊 Updating databases with analyzed receipts...")
        
        receipts = analysis_results.get("receipts", [])
        summary = analysis_results.get("summary", {})
        insights = analysis_results.get("insights", [])
        
        update_results = {
            "status": "success",
            "updated_databases": [],
            "sheets_result": None,
            "notion_result": None,
            "update_time": datetime.now().isoformat()
        }
        
        try:
            # Update Google Sheets
            logger.info("📈 Updating Google Sheets...")
            sheets_result = await self.update_sheets(receipts, summary)
            update_results["sheets_result"] = sheets_result
            
            if sheets_result["status"] == "success":
                update_results["updated_databases"].append("Google Sheets")
                self.status["sheets_updated"] = True
            
            # Update Notion Dashboard
            logger.info("📋 Updating Notion dashboard...")
            notion_result = await self.update_notion(receipts, summary, insights)
            update_results["notion_result"] = notion_result
            
            if notion_result["status"] == "success":
                update_results["updated_databases"].append("Notion")
                self.status["notion_updated"] = True
            
            self.status["last_update"] = datetime.now()
            
            logger.info(f"✅ Database update complete: {len(update_results['updated_databases'])} databases updated")
            
            return update_results
            
        except Exception as e:
            logger.error(f"❌ Database update failed: {str(e)}")
            self.status["errors"].append(str(e))
            update_results["status"] = "error"
            update_results["error"] = str(e)
            return update_results
    
    async def update_sheets(self, receipts: List[Dict[str, Any]], summary: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update Google Sheets with receipt data
        """
        try:
            # Prepare data for sheets
            sheet_data = []
            
            # Add header row if this is the first update
            if not await self.sheets_tool.has_data():
                headers = [
                    "Date", "Merchant", "Amount", "Currency", "Category", 
                    "Items", "Source", "Timestamp", "Insights"
                ]
                sheet_data.append(headers)
            
            # Add receipt data
            for receipt in receipts:
                row = [
                    receipt.get("date", ""),
                    receipt.get("merchant", ""),
                    receipt.get("amount", 0),
                    receipt.get("currency", "USD"),
                    receipt.get("category", "Other"),
                    ", ".join(receipt.get("items", [])),
                    receipt.get("source", ""),
                    receipt.get("timestamp", ""),
                    "; ".join(receipt.get("spending_insights", []))
                ]
                sheet_data.append(row)
            
            # Add summary row
            if summary:
                summary_row = [
                    "SUMMARY",
                    f"Total: ${summary.get('total_amount', 0):.2f}",
                    f"Count: {summary.get('receipt_count', 0)}",
                    f"Categories: {len(summary.get('category_totals', {}))}",
                    "",
                    "",
                    "",
                    "",
                    f"Top: {', '.join([cat[0] for cat in summary.get('top_categories', [])[:3]])}"
                ]
                sheet_data.append(summary_row)
            
            # Update the sheet
            result = await self.sheets_tool.append_data(sheet_data)
            
            return {
                "status": "success",
                "rows_added": len(sheet_data),
                "sheet_id": result.get("sheet_id"),
                "result": result
            }
            
        except Exception as e:
            logger.error(f"❌ Sheets update failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_notion(self, receipts: List[Dict[str, Any]], summary: Dict[str, Any], insights: List[str]) -> Dict[str, Any]:
        """
        Update Notion dashboard with receipt data and insights
        """
        try:
            # Create new database entries for receipts
            notion_pages = []
            
            for receipt in receipts:
                page_data = {
                    "properties": {
                        "Date": {"date": {"start": receipt.get("date", "")}},
                        "Merchant": {"title": [{"text": {"content": receipt.get("merchant", "")}}]},
                        "Amount": {"number": receipt.get("amount", 0)},
                        "Category": {"select": {"name": receipt.get("category", "Other")}},
                        "Source": {"select": {"name": receipt.get("source", "Unknown")}},
                        "Items": {"rich_text": [{"text": {"content": ", ".join(receipt.get("items", []))}}]},
                        "Insights": {"rich_text": [{"text": {"content": "; ".join(receipt.get("spending_insights", []))}}]}
                    }
                }
                
                page_result = await self.notion_tool.create_page(page_data)
                notion_pages.append(page_result)
            
            # Update summary dashboard
            summary_result = await self.update_summary_dashboard(summary, insights)
            
            return {
                "status": "success",
                "pages_created": len(notion_pages),
                "pages": notion_pages,
                "summary_updated": summary_result
            }
            
        except Exception as e:
            logger.error(f"❌ Notion update failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def update_summary_dashboard(self, summary: Dict[str, Any], insights: List[str]) -> Dict[str, Any]:
        """
        Update the summary dashboard in Notion
        """
        try:
            # Create summary page
            summary_content = {
                "properties": {
                    "Title": {"title": [{"text": {"content": f"Spending Summary - {datetime.now().strftime('%Y-%m-%d')}"}}]},
                    "Total Amount": {"number": summary.get("total_amount", 0)},
                    "Receipt Count": {"number": summary.get("receipt_count", 0)},
                    "Date": {"date": {"start": datetime.now().isoformat()}}
                },
                "children": [
                    {
                        "object": "block",
                        "type": "heading_2",
                        "heading_2": {"rich_text": [{"text": {"content": "📊 Spending Overview"}}]}
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": f"Total spent: ${summary.get('total_amount', 0):.2f}"}}]
                        }
                    },
                    {
                        "object": "block",
                        "type": "paragraph",
                        "paragraph": {
                            "rich_text": [{"text": {"content": f"Number of receipts: {summary.get('receipt_count', 0)}"}}]
                        }
                    }
                ]
            }
            
            # Add category breakdown
            if summary.get("category_totals"):
                summary_content["children"].append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"text": {"content": "🏷️ Category Breakdown"}}]}
                })
                
                for category, amount in summary.get("category_totals", {}).items():
                    summary_content["children"].append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": f"{category}: ${amount:.2f}"}}]
                        }
                    })
            
            # Add insights
            if insights:
                summary_content["children"].append({
                    "object": "block",
                    "type": "heading_2",
                    "heading_2": {"rich_text": [{"text": {"content": "💡 Insights & Recommendations"}}]}
                })
                
                for insight in insights:
                    summary_content["children"].append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"text": {"content": insight}}]
                        }
                    })
            
            result = await self.notion_tool.create_page(summary_content)
            
            return {
                "status": "success",
                "page_created": True,
                "page_id": result.get("id")
            }
            
        except Exception as e:
            logger.error(f"❌ Summary dashboard update failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def create_monthly_report(self, month: str, year: int) -> Dict[str, Any]:
        """
        Create a comprehensive monthly spending report
        """
        try:
            # This would typically fetch data from sheets and create a comprehensive report
            logger.info(f"📅 Creating monthly report for {month} {year}")
            
            # For now, return a placeholder
            return {
                "status": "success",
                "report_type": "monthly",
                "month": month,
                "year": year,
                "message": "Monthly report functionality to be implemented"
            }
            
        except Exception as e:
            logger.error(f"❌ Monthly report creation failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent": "UpdaterAgent",
            "status": "active" if not self.status["errors"] else "error",
            "last_update": self.status["last_update"],
            "sheets_updated": self.status["sheets_updated"],
            "notion_updated": self.status["notion_updated"],
            "errors": self.status["errors"]
        }

# Demo function
async def demo_update():
    """Demo the updater agent"""
    updater = UpdaterAgent()
    
    print("🔄 Updater Agent Demo")
    print("=" * 30)
    
    # Sample analysis results
    sample_analysis = {
        "receipts": [
            {
                "merchant": "Whole Foods",
                "amount": 85.50,
                "category": "Groceries",
                "items": ["organic vegetables", "dairy products"],
                "date": "2024-01-15",
                "source": "Gmail",
                "timestamp": datetime.now().isoformat(),
                "spending_insights": ["High-value purchase: $85.50", "Grocery expense - consider meal prep for savings"]
            }
        ],
        "summary": {
            "total_amount": 85.50,
            "receipt_count": 1,
            "category_totals": {"Groceries": 85.50},
            "top_categories": [("Groceries", 85.50)]
        },
        "insights": [
            "Consider buying generic brands to save money",
            "Track grocery spending to stay within budget"
        ]
    }
    
    results = await updater.update_databases(sample_analysis)
    
    print(f"Status: {results['status']}")
    print(f"Databases updated: {', '.join(results['updated_databases'])}")
    
    if results['sheets_result']:
        print(f"Sheets: {results['sheets_result']['status']}")
    
    if results['notion_result']:
        print(f"Notion: {results['notion_result']['status']}")
    
    return results

if __name__ == "__main__":
    asyncio.run(demo_update())
