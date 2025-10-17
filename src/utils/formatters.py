"""
🛠️ Formatters - Utility functions for data formatting and processing
"""

import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

def format_currency(amount: float, currency: str = "USD") -> str:
    """
    Format amount as currency string
    """
    if currency == "USD":
        return f"${amount:.2f}"
    else:
        return f"{amount:.2f} {currency}"

def format_date(date_str: str) -> str:
    """
    Format date string to readable format
    """
    try:
        if isinstance(date_str, str):
            # Try to parse the date
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime("%B %d, %Y")
        return str(date_str)
    except:
        return str(date_str)

def format_receipt_summary(receipt: Dict[str, Any]) -> str:
    """
    Format a receipt into a readable summary string
    """
    merchant = receipt.get("merchant", "Unknown")
    amount = receipt.get("amount", 0)
    category = receipt.get("category", "Other")
    date = receipt.get("date", "")
    
    formatted_date = format_date(date)
    formatted_amount = format_currency(amount)
    
    return f"{formatted_date}: {merchant} - {formatted_amount} ({category})"

def format_category_breakdown(category_totals: Dict[str, float]) -> str:
    """
    Format category totals into readable breakdown
    """
    if not category_totals:
        return "No spending data available"
    
    breakdown = []
    total = sum(category_totals.values())
    
    for category, amount in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (amount / total) * 100 if total > 0 else 0
        formatted_amount = format_currency(amount)
        breakdown.append(f"• {category}: {formatted_amount} ({percentage:.1f}%)")
    
    return "\n".join(breakdown)

def format_insights_list(insights: List[str]) -> str:
    """
    Format insights list into readable format
    """
    if not insights:
        return "No insights available"
    
    formatted_insights = []
    for i, insight in enumerate(insights, 1):
        formatted_insights.append(f"{i}. {insight}")
    
    return "\n".join(formatted_insights)

def sanitize_text(text: str, max_length: int = 1000) -> str:
    """
    Sanitize and truncate text for safe display
    """
    if not text:
        return ""
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length-3] + "..."
    
    return text

def extract_numeric_amount(text: str) -> Optional[float]:
    """
    Extract numeric amount from text string
    """
    # Remove currency symbols and extract number
    amount_match = re.search(r'[\d,]+\.?\d*', text.replace('$', '').replace(',', ''))
    
    if amount_match:
        try:
            return float(amount_match.group())
        except ValueError:
            return None
    
    return None

def validate_receipt_data(receipt: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate and clean receipt data
    """
    validated = receipt.copy()
    
    # Ensure required fields
    if not validated.get("merchant"):
        validated["merchant"] = "Unknown Merchant"
    
    if not validated.get("amount"):
        validated["amount"] = 0.0
    
    if not validated.get("category"):
        validated["category"] = "Other"
    
    if not validated.get("date"):
        validated["date"] = datetime.now().strftime("%Y-%m-%d")
    
    # Sanitize text fields
    validated["merchant"] = sanitize_text(validated["merchant"], 100)
    
    if validated.get("items"):
        validated["items"] = [sanitize_text(item, 50) for item in validated["items"]]
    
    # Ensure amount is numeric
    try:
        validated["amount"] = float(validated["amount"])
    except (ValueError, TypeError):
        validated["amount"] = 0.0
    
    return validated

def create_json_summary(data: Dict[str, Any]) -> str:
    """
    Create a formatted JSON summary of data
    """
    try:
        return json.dumps(data, indent=2, default=str)
    except:
        return str(data)

def format_anomaly_alert(anomaly: Dict[str, Any]) -> str:
    """
    Format anomaly data into readable alert
    """
    anomaly_type = anomaly.get("type", "unknown")
    description = anomaly.get("description", "")
    severity = anomaly.get("severity", "medium")
    
    emoji_map = {
        "high": "🔴",
        "medium": "🟡", 
        "low": "🟢"
    }
    
    emoji = emoji_map.get(severity, "⚪")
    
    return f"{emoji} **{anomaly_type.replace('_', ' ').title()}**: {description}"

def format_workflow_status(status: Dict[str, Any]) -> str:
    """
    Format workflow status into readable summary
    """
    status_text = f"**Status**: {status.get('status', 'unknown').title()}\n"
    
    if status.get('session_id'):
        status_text += f"**Session ID**: {status['session_id']}\n"
    
    if status.get('start_time'):
        status_text += f"**Started**: {format_date(status['start_time'])}\n"
    
    if status.get('summary'):
        summary = status['summary']
        status_text += f"**Receipts**: {summary.get('receipts_processed', 0)}\n"
        status_text += f"**Total**: {format_currency(summary.get('total_amount', 0))}\n"
    
    return status_text.strip()
