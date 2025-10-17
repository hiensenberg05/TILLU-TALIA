"""
💳 Project Raseed - Main Orchestrator
Controls the 4-agent workflow for receipt extraction and analysis
"""

import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from agents.extractor_agent import ExtractorAgent
from agents.analyzer_agent import AnalyzerAgent
from agents.updater_agent import UpdaterAgent
from agents.notifier_agent import NotifierAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MainOrchestrator:
    """
    Main orchestrator that coordinates the 4-agent workflow:
    1. Extractor Agent - Fetches and extracts receipt data
    2. Analyzer Agent - Categorizes and analyzes expenses
    3. Updater Agent - Syncs data to Sheets & Notion
    4. Notifier Agent - Sends notifications and summaries
    """
    
    def __init__(self):
        self.extractor = ExtractorAgent()
        self.analyzer = AnalyzerAgent()
        self.updater = UpdaterAgent()
        self.notifier = NotifierAgent()
        
        # Workflow state tracking
        self.workflow_state = {
            "session_id": None,
            "start_time": None,
            "processed_receipts": 0,
            "errors": []
        }
    
    async def start_workflow(self, session_id: str = None) -> Dict[str, Any]:
        """
        Start the complete Project Raseed workflow
        """
        if not session_id:
            session_id = f"raseed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        self.workflow_state["session_id"] = session_id
        self.workflow_state["start_time"] = datetime.now()
        
        logger.info(f"🚀 Starting Project Raseed workflow: {session_id}")
        
        try:
            # Step 1: Extract receipts from Gmail and Drive
            logger.info("📥 Step 1: Extracting receipts...")
            extraction_results = await self.extractor.extract_all_receipts()
            
            if not extraction_results["receipts"]:
                logger.info("ℹ️ No new receipts found")
                return self._create_workflow_result("no_receipts", "No new receipts to process")
            
            # Step 2: Analyze extracted receipts
            logger.info("🧠 Step 2: Analyzing receipts...")
            analysis_results = await self.analyzer.analyze_receipts(extraction_results["receipts"])
            
            # Step 3: Update Sheets and Notion
            logger.info("📊 Step 3: Updating databases...")
            update_results = await self.updater.update_databases(analysis_results)
            
            # Step 4: Send notifications
            logger.info("📢 Step 4: Sending notifications...")
            notification_results = await self.notifier.send_notifications(analysis_results, update_results)
            
            # Compile final results
            workflow_results = self._compile_workflow_results(
                extraction_results, analysis_results, update_results, notification_results
            )
            
            logger.info(f"✅ Workflow completed successfully: {session_id}")
            return workflow_results
            
        except Exception as e:
            logger.error(f"❌ Workflow failed: {str(e)}")
            self.workflow_state["errors"].append(str(e))
            return self._create_workflow_result("error", str(e))
    
    async def process_single_receipt(self, receipt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single receipt through the complete pipeline
        """
        session_id = f"single_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        try:
            # Analyze the receipt
            analysis = await self.analyzer.analyze_receipts([receipt_data])
            
            # Update databases
            update_results = await self.updater.update_databases(analysis)
            
            # Send notification
            notification_results = await self.notifier.send_notifications(analysis, update_results)
            
            return {
                "status": "success",
                "session_id": session_id,
                "analysis": analysis,
                "update_results": update_results,
                "notification_results": notification_results
            }
            
        except Exception as e:
            logger.error(f"❌ Single receipt processing failed: {str(e)}")
            return {"status": "error", "error": str(e)}
    
    def _compile_workflow_results(self, extraction: Dict, analysis: Dict, update: Dict, notification: Dict) -> Dict[str, Any]:
        """Compile all workflow results into a comprehensive summary"""
        
        return {
            "status": "success",
            "session_id": self.workflow_state["session_id"],
            "start_time": self.workflow_state["start_time"].isoformat(),
            "end_time": datetime.now().isoformat(),
            "summary": {
                "receipts_processed": len(extraction.get("receipts", [])),
                "categories_found": len(set([r.get("category", "Unknown") for r in analysis.get("receipts", [])])),
                "total_amount": sum([r.get("amount", 0) for r in analysis.get("receipts", [])]),
                "databases_updated": update.get("updated_databases", []),
                "notifications_sent": notification.get("notifications_sent", 0)
            },
            "extraction_results": extraction,
            "analysis_results": analysis,
            "update_results": update,
            "notification_results": notification,
            "errors": self.workflow_state["errors"]
        }
    
    def _create_workflow_result(self, status: str, message: str) -> Dict[str, Any]:
        """Create a simple workflow result"""
        return {
            "status": status,
            "session_id": self.workflow_state["session_id"],
            "message": message,
            "start_time": self.workflow_state["start_time"].isoformat() if self.workflow_state["start_time"] else None,
            "end_time": datetime.now().isoformat()
        }
    
    async def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        return {
            "workflow_state": self.workflow_state,
            "agents_status": {
                "extractor": await self.extractor.get_status(),
                "analyzer": await self.analyzer.get_status(),
                "updater": await self.updater.get_status(),
                "notifier": await self.notifier.get_status()
            }
        }

# Demo function
async def demo_workflow():
    """Demo the complete Project Raseed workflow"""
    orchestrator = MainOrchestrator()
    
    print("💳 Project Raseed - AI-Powered Receipt & Spending Companion")
    print("=" * 60)
    
    # Start the workflow
    results = await orchestrator.start_workflow()
    
    print(f"\n📊 Workflow Results:")
    print(f"Status: {results['status']}")
    print(f"Session ID: {results['session_id']}")
    
    if results['status'] == 'success':
        summary = results['summary']
        print(f"\n✅ Summary:")
        print(f"  • Receipts processed: {summary['receipts_processed']}")
        print(f"  • Categories found: {summary['categories_found']}")
        print(f"  • Total amount: ${summary['total_amount']:.2f}")
        print(f"  • Databases updated: {', '.join(summary['databases_updated'])}")
        print(f"  • Notifications sent: {summary['notifications_sent']}")
    
    return results

if __name__ == "__main__":
    # Run the demo workflow
    asyncio.run(demo_workflow())
