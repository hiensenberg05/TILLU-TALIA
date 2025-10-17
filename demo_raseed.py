"""
💳 Project Raseed - Demo Script
AI-Powered Receipt & Spending Companion

This demo showcases the complete 4-agent workflow:
1. Extractor Agent - Fetches receipts from Gmail/Drive
2. Analyzer Agent - Categorizes and analyzes expenses  
3. Updater Agent - Syncs data to Sheets & Notion
4. Notifier Agent - Sends notifications and summaries
"""

import asyncio
import logging
from datetime import datetime

from src.main_orchestrator import MainOrchestrator
from src.utils.helpers import load_env_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def demo_complete_workflow():
    """
    Demo the complete Project Raseed workflow
    """
    print("💳 PROJECT RASEED - AI-POWERED RECEIPT & SPENDING COMPANION")
    print("=" * 70)
    print()
    
    # Load configuration
    config = load_env_config()
    
    # Check if required API keys are configured
    if not config.get("COMPOSIO_API_KEY"):
        print("❌ COMPOSIO_API_KEY not found in environment variables")
        print("📋 Please set up your .env file with the required API keys")
        return
    
    if not config.get("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("📋 Please set up your .env file with the required API keys")
        return
    
    print("✅ Configuration loaded successfully")
    print()
    
    # Initialize the main orchestrator
    orchestrator = MainOrchestrator()
    
    try:
        print("🚀 Starting Project Raseed Workflow...")
        print("=" * 50)
        
        # Start the complete workflow
        results = await orchestrator.start_workflow()
        
        print()
        print("📊 WORKFLOW RESULTS")
        print("=" * 30)
        print(f"Status: {results['status']}")
        print(f"Session ID: {results['session_id']}")
        print(f"Start Time: {results.get('start_time', 'N/A')}")
        print(f"End Time: {results.get('end_time', 'N/A')}")
        
        if results['status'] == 'success' and 'summary' in results:
            summary = results['summary']
            print()
            print("💰 FINANCIAL SUMMARY")
            print("-" * 20)
            print(f"Receipts processed: {summary.get('receipts_processed', 0)}")
            print(f"Categories found: {summary.get('categories_found', 0)}")
            print(f"Total amount: ${summary.get('total_amount', 0):.2f}")
            print(f"Databases updated: {', '.join(summary.get('databases_updated', []))}")
            print(f"Notifications sent: {summary.get('notifications_sent', 0)}")
        
        elif results['status'] == 'no_receipts':
            print()
            print("ℹ️ No new receipts found to process")
            print("💡 Try adding some receipts to your Gmail or Google Drive")
        
        else:
            print()
            print(f"❌ Workflow failed: {results.get('message', 'Unknown error')}")
        
        # Show detailed results if available
        if results.get('extraction_results'):
            extraction = results['extraction_results']
            print()
            print("📥 EXTRACTION RESULTS")
            print("-" * 20)
            print(f"Sources processed: {len(extraction.get('sources', []))}")
            for source in extraction.get('sources', []):
                print(f"  • {source['source']}: {source['count']} receipts")
        
        if results.get('analysis_results'):
            analysis = results['analysis_results']
            print()
            print("🧠 ANALYSIS RESULTS")
            print("-" * 20)
            print(f"Insights generated: {len(analysis.get('insights', []))}")
            print(f"Anomalies detected: {len(analysis.get('anomalies', []))}")
            
            if analysis.get('insights'):
                print()
                print("💡 Key Insights:")
                for insight in analysis['insights'][:3]:
                    print(f"  • {insight}")
        
        if results.get('notification_results'):
            notification = results['notification_results']
            print()
            print("📢 NOTIFICATION RESULTS")
            print("-" * 20)
            print(f"Slack messages: {notification.get('slack_messages', 0)}")
            print(f"Emails sent: {notification.get('emails_sent', 0)}")
        
        print()
        print("✅ Demo completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Demo failed: {str(e)}")
        print(f"❌ Demo failed: {str(e)}")

async def demo_individual_agents():
    """
    Demo individual agents separately
    """
    print()
    print("🔧 INDIVIDUAL AGENT DEMOS")
    print("=" * 30)
    
    from src.agents.extractor_agent import ExtractorAgent
    from src.agents.analyzer_agent import AnalyzerAgent
    from src.agents.updater_agent import UpdaterAgent
    from src.agents.notifier_agent import NotifierAgent
    
    # Demo Extractor Agent
    print()
    print("🧾 Testing Extractor Agent...")
    extractor = ExtractorAgent()
    extraction_results = await extractor.extract_all_receipts(days_back=1)
    print(f"  Status: {extraction_results['status']}")
    print(f"  Receipts found: {extraction_results.get('total_count', 0)}")
    
    # Demo Analyzer Agent with sample data
    print()
    print("📊 Testing Analyzer Agent...")
    analyzer = AnalyzerAgent()
    sample_receipts = [
        {
            "merchant": "Whole Foods",
            "amount": 85.50,
            "category": "Groceries",
            "items": ["organic vegetables", "dairy products"],
            "date": "2024-01-15"
        }
    ]
    analysis_results = await analyzer.analyze_receipts(sample_receipts)
    print(f"  Status: {analysis_results['status']}")
    print(f"  Receipts analyzed: {len(analysis_results.get('receipts', []))}")
    
    # Demo Updater Agent
    print()
    print("🔄 Testing Updater Agent...")
    updater = UpdaterAgent()
    update_results = await updater.update_databases(analysis_results)
    print(f"  Status: {update_results['status']}")
    print(f"  Databases updated: {len(update_results.get('updated_databases', []))}")
    
    # Demo Notifier Agent
    print()
    print("💬 Testing Notifier Agent...")
    notifier = NotifierAgent()
    notification_results = await notifier.send_notifications(analysis_results, update_results)
    print(f"  Status: {notification_results['status']}")
    print(f"  Notifications sent: {notification_results.get('notifications_sent', 0)}")

async def main():
    """
    Main demo function
    """
    print("🎯 Project Raseed Demo Options:")
    print("1. Complete Workflow Demo")
    print("2. Individual Agent Demos")
    print("3. Both")
    
    choice = input("\nEnter your choice (1-3): ").strip()
    
    if choice in ["1", "3"]:
        await demo_complete_workflow()
    
    if choice in ["2", "3"]:
        await demo_individual_agents()
    
    if choice not in ["1", "2", "3"]:
        print("Invalid choice. Running complete workflow demo...")
        await demo_complete_workflow()

if __name__ == "__main__":
    print("🚀 Starting Project Raseed Demo...")
    asyncio.run(main())
