"""
📊 Analyzer Agent - Performs expense reasoning and pattern detection
Categorizes expenses, finds anomalies, summarizes insights
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import statistics

import google.generativeai as genai

logger = logging.getLogger(__name__)

class AnalyzerAgent:
    """
    Analyzer Agent handles:
    - Categorizing expenses using Gemini Text
    - Detecting spending patterns and anomalies
    - Generating insights and recommendations
    - Creating spending summaries
    """
    
    def __init__(self):
        # Initialize Gemini Text
        genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Set in .env
        self.text_model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Predefined expense categories
        self.categories = {
            "Groceries": ["grocery", "supermarket", "food", "grocery store", "market"],
            "Utilities": ["electricity", "water", "gas", "internet", "phone", "utility"],
            "Entertainment": ["movie", "theater", "concert", "streaming", "game", "entertainment"],
            "Transportation": ["gas", "fuel", "uber", "lyft", "taxi", "parking", "transport"],
            "Dining": ["restaurant", "cafe", "coffee", "food delivery", "dining"],
            "Healthcare": ["pharmacy", "medical", "doctor", "hospital", "health"],
            "Shopping": ["retail", "store", "clothing", "electronics", "shopping"],
            "Travel": ["hotel", "flight", "travel", "vacation", "booking"],
            "Bills": ["bill", "payment", "subscription", "service"],
            "Other": []  # Default category
        }
        
        self.status = {"last_analysis": None, "receipts_analyzed": 0, "errors": []}
    
    async def analyze_receipts(self, receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze a list of receipts for categorization, patterns, and insights
        """
        logger.info(f"🧠 Analyzing {len(receipts)} receipts...")
        
        if not receipts:
            return {
                "status": "success",
                "receipts": [],
                "summary": {},
                "insights": [],
                "anomalies": []
            }
        
        try:
            analyzed_receipts = []
            
            # Analyze each receipt
            for receipt in receipts:
                analyzed_receipt = await self.analyze_single_receipt(receipt)
                analyzed_receipts.append(analyzed_receipt)
            
            # Generate summary and insights
            summary = await self.generate_summary(analyzed_receipts)
            insights = await self.generate_insights(analyzed_receipts)
            anomalies = await self.detect_anomalies(analyzed_receipts)
            
            self.status["last_analysis"] = datetime.now()
            self.status["receipts_analyzed"] = len(analyzed_receipts)
            
            logger.info(f"✅ Analysis complete: {len(analyzed_receipts)} receipts analyzed")
            
            return {
                "status": "success",
                "receipts": analyzed_receipts,
                "summary": summary,
                "insights": insights,
                "anomalies": anomalies,
                "analysis_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Analysis failed: {str(e)}")
            self.status["errors"].append(str(e))
            return {
                "status": "error",
                "error": str(e),
                "receipts": receipts,
                "summary": {},
                "insights": [],
                "anomalies": []
            }
    
    async def analyze_single_receipt(self, receipt: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a single receipt for categorization and additional insights
        """
        try:
            # Enhance the receipt with better categorization
            enhanced_receipt = receipt.copy()
            
            # Improve category using Gemini
            if not receipt.get("category") or receipt.get("category") == "Other":
                enhanced_receipt["category"] = await self.categorize_receipt(receipt)
            
            # Add spending insights
            enhanced_receipt["spending_insights"] = await self.generate_receipt_insights(receipt)
            
            # Add timestamp if missing
            if not enhanced_receipt.get("timestamp"):
                enhanced_receipt["timestamp"] = datetime.now().isoformat()
            
            return enhanced_receipt
            
        except Exception as e:
            logger.error(f"❌ Single receipt analysis failed: {str(e)}")
            return receipt
    
    async def categorize_receipt(self, receipt: Dict[str, Any]) -> str:
        """
        Use Gemini to categorize a receipt based on merchant and items
        """
        try:
            merchant = receipt.get("merchant", "")
            items = receipt.get("items", [])
            
            prompt = f"""
            Categorize this expense into one of these categories:
            {list(self.categories.keys())}
            
            Merchant: {merchant}
            Items: {', '.join(items) if items else 'Not specified'}
            
            Return only the category name. Choose the most appropriate one.
            """
            
            response = self.text_model.generate_content(prompt)
            category = response.text.strip()
            
            # Validate category
            if category in self.categories:
                return category
            else:
                return "Other"
                
        except Exception as e:
            logger.error(f"❌ Categorization failed: {str(e)}")
            return "Other"
    
    async def generate_receipt_insights(self, receipt: Dict[str, Any]) -> List[str]:
        """
        Generate insights for a single receipt
        """
        insights = []
        
        try:
            amount = receipt.get("amount", 0)
            category = receipt.get("category", "Other")
            merchant = receipt.get("merchant", "")
            
            # Amount-based insights
            if amount > 100:
                insights.append(f"High-value purchase: ${amount:.2f}")
            elif amount < 10:
                insights.append(f"Small purchase: ${amount:.2f}")
            
            # Category-based insights
            if category == "Dining":
                insights.append("Dining expense - consider meal prep for savings")
            elif category == "Transportation":
                insights.append("Transportation cost - track for monthly budget")
            elif category == "Entertainment":
                insights.append("Entertainment expense - ensure it fits budget")
            
            # Merchant-based insights
            if "amazon" in merchant.lower():
                insights.append("Amazon purchase - check for subscription savings")
            elif "uber" in merchant.lower() or "lyft" in merchant.lower():
                insights.append("Ride-share expense - consider public transport")
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Insight generation failed: {str(e)}")
            return []
    
    async def generate_summary(self, receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive spending summary
        """
        try:
            if not receipts:
                return {}
            
            # Calculate totals by category
            category_totals = {}
            total_amount = 0
            
            for receipt in receipts:
                category = receipt.get("category", "Other")
                amount = receipt.get("amount", 0)
                
                category_totals[category] = category_totals.get(category, 0) + amount
                total_amount += amount
            
            # Find top categories
            top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)[:5]
            
            # Calculate statistics
            amounts = [r.get("amount", 0) for r in receipts]
            avg_amount = statistics.mean(amounts) if amounts else 0
            max_amount = max(amounts) if amounts else 0
            min_amount = min(amounts) if amounts else 0
            
            return {
                "total_amount": total_amount,
                "receipt_count": len(receipts),
                "category_totals": category_totals,
                "top_categories": top_categories,
                "statistics": {
                    "average_amount": avg_amount,
                    "max_amount": max_amount,
                    "min_amount": min_amount
                },
                "date_range": {
                    "start": min([r.get("date", "") for r in receipts if r.get("date")]),
                    "end": max([r.get("date", "") for r in receipts if r.get("date")])
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Summary generation failed: {str(e)}")
            return {}
    
    async def generate_insights(self, receipts: List[Dict[str, Any]]) -> List[str]:
        """
        Generate actionable insights using Gemini
        """
        try:
            if not receipts:
                return []
            
            # Prepare data for analysis
            summary = await self.generate_summary(receipts)
            
            prompt = f"""
            Analyze this spending data and provide 3-5 actionable insights:
            
            Total spent: ${summary.get('total_amount', 0):.2f}
            Number of transactions: {summary.get('receipt_count', 0)}
            Top categories: {summary.get('top_categories', [])}
            Average transaction: ${summary.get('statistics', {}).get('average_amount', 0):.2f}
            
            Provide insights about:
            1. Spending patterns
            2. Potential savings opportunities
            3. Budget recommendations
            4. Spending trends
            
            Return as a list of concise, actionable insights.
            """
            
            response = self.text_model.generate_content(prompt)
            
            # Parse insights
            insights_text = response.text.strip()
            insights = [insight.strip() for insight in insights_text.split('\n') if insight.strip()]
            
            return insights[:5]  # Limit to 5 insights
            
        except Exception as e:
            logger.error(f"❌ Insight generation failed: {str(e)}")
            return []
    
    async def detect_anomalies(self, receipts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Detect unusual spending patterns or anomalies
        """
        anomalies = []
        
        try:
            if len(receipts) < 3:  # Need at least 3 receipts for comparison
                return anomalies
            
            # Calculate statistics
            amounts = [r.get("amount", 0) for r in receipts]
            avg_amount = statistics.mean(amounts)
            std_dev = statistics.stdev(amounts) if len(amounts) > 1 else 0
            
            # Detect high-value anomalies
            threshold = avg_amount + (2 * std_dev)
            for receipt in receipts:
                amount = receipt.get("amount", 0)
                if amount > threshold:
                    anomalies.append({
                        "type": "high_value",
                        "description": f"Unusually high expense: ${amount:.2f} (avg: ${avg_amount:.2f})",
                        "receipt": receipt,
                        "severity": "high" if amount > avg_amount + (3 * std_dev) else "medium"
                    })
            
            # Detect frequent same-merchant spending
            merchant_counts = {}
            for receipt in receipts:
                merchant = receipt.get("merchant", "")
                merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1
            
            for merchant, count in merchant_counts.items():
                if count >= 3:  # 3 or more transactions at same merchant
                    total_spent = sum([r.get("amount", 0) for r in receipts if r.get("merchant") == merchant])
                    anomalies.append({
                        "type": "frequent_merchant",
                        "description": f"Frequent spending at {merchant}: {count} transactions, ${total_spent:.2f} total",
                        "merchant": merchant,
                        "count": count,
                        "total_spent": total_spent,
                        "severity": "medium"
                    })
            
            return anomalies
            
        except Exception as e:
            logger.error(f"❌ Anomaly detection failed: {str(e)}")
            return []
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent": "AnalyzerAgent",
            "status": "active" if not self.status["errors"] else "error",
            "last_analysis": self.status["last_analysis"],
            "receipts_analyzed": self.status["receipts_analyzed"],
            "categories_available": len(self.categories),
            "errors": self.status["errors"]
        }

# Demo function
async def demo_analysis():
    """Demo the analyzer agent"""
    analyzer = AnalyzerAgent()
    
    print("📊 Analyzer Agent Demo")
    print("=" * 30)
    
    # Sample receipts for demo
    sample_receipts = [
        {
            "merchant": "Whole Foods",
            "amount": 85.50,
            "category": "Groceries",
            "items": ["organic vegetables", "dairy products"],
            "date": "2024-01-15"
        },
        {
            "merchant": "Uber",
            "amount": 12.75,
            "category": "Transportation",
            "items": ["ride to downtown"],
            "date": "2024-01-15"
        }
    ]
    
    results = await analyzer.analyze_receipts(sample_receipts)
    
    print(f"Status: {results['status']}")
    print(f"Receipts analyzed: {len(results['receipts'])}")
    
    if results['summary']:
        print(f"Total amount: ${results['summary']['total_amount']:.2f}")
        print(f"Top categories: {results['summary']['top_categories']}")
    
    print(f"Insights: {len(results['insights'])}")
    for insight in results['insights'][:3]:
        print(f"  • {insight}")
    
    return results

if __name__ == "__main__":
    asyncio.run(demo_analysis())
