"""
🔧 Helpers - Utility functions for common operations
"""

import os
import json
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import hashlib

logger = logging.getLogger(__name__)

def load_env_config() -> Dict[str, str]:
    """
    Load configuration from environment variables
    """
    config = {
        "COMPOSIO_API_KEY": os.getenv("COMPOSIO_API_KEY"),
        "GEMINI_API_KEY": os.getenv("GEMINI_API_KEY"),
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
        "USER_ID": os.getenv("USER_ID", "default_user"),
        "SPREADSHEET_ID": os.getenv("SPREADSHEET_ID"),
        "NOTION_DATABASE_ID": os.getenv("NOTION_DATABASE_ID"),
        "SLACK_CHANNEL": os.getenv("SLACK_CHANNEL", "#personal-finance"),
        "EMAIL_ADDRESS": os.getenv("EMAIL_ADDRESS")
    }
    
    # Validate required config
    required_keys = ["COMPOSIO_API_KEY", "GEMINI_API_KEY"]
    missing_keys = [key for key in required_keys if not config[key]]
    
    if missing_keys:
        logger.warning(f"Missing required environment variables: {missing_keys}")
    
    return config

def generate_session_id() -> str:
    """
    Generate unique session ID
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_suffix = hashlib.md5(str(datetime.now().timestamp()).encode()).hexdigest()[:8]
    return f"raseed_{timestamp}_{random_suffix}"

def calculate_date_range(days_back: int = 7) -> tuple:
    """
    Calculate date range for data extraction
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days_back)
    return start_date, end_date

def is_receipt_email(subject: str, body: str) -> bool:
    """
    Check if email is likely a receipt/invoice
    """
    receipt_keywords = [
        "receipt", "invoice", "order confirmation", "payment confirmation",
        "thank you for your purchase", "order summary", "bill", "statement",
        "payment received", "transaction", "purchase"
    ]
    
    text_to_check = f"{subject} {body}".lower()
    
    return any(keyword in text_to_check for keyword in receipt_keywords)

def is_receipt_file(filename: str, mime_type: str = None) -> bool:
    """
    Check if file is likely a receipt/invoice
    """
    # Check filename
    receipt_keywords = ["receipt", "invoice", "bill", "statement", "order"]
    filename_lower = filename.lower()
    
    if any(keyword in filename_lower for keyword in receipt_keywords):
        return True
    
    # Check file extension
    receipt_extensions = [".pdf", ".png", ".jpg", ".jpeg"]
    if any(filename_lower.endswith(ext) for ext in receipt_extensions):
        return True
    
    # Check MIME type
    if mime_type:
        receipt_mime_types = [
            "application/pdf",
            "image/png",
            "image/jpeg",
            "image/jpg"
        ]
        if mime_type in receipt_mime_types:
            return True
    
    return False

def categorize_merchant(merchant: str) -> str:
    """
    Categorize merchant based on common patterns
    """
    merchant_lower = merchant.lower()
    
    # Groceries
    if any(keyword in merchant_lower for keyword in ["grocery", "supermarket", "whole foods", "trader joe", "safeway"]):
        return "Groceries"
    
    # Transportation
    if any(keyword in merchant_lower for keyword in ["uber", "lyft", "taxi", "gas", "fuel", "parking"]):
        return "Transportation"
    
    # Dining
    if any(keyword in merchant_lower for keyword in ["restaurant", "cafe", "coffee", "food delivery", "doordash", "ubereats"]):
        return "Dining"
    
    # Entertainment
    if any(keyword in merchant_lower for keyword in ["movie", "theater", "concert", "netflix", "spotify", "streaming"]):
        return "Entertainment"
    
    # Shopping
    if any(keyword in merchant_lower for keyword in ["amazon", "target", "walmart", "retail", "store"]):
        return "Shopping"
    
    # Utilities
    if any(keyword in merchant_lower for keyword in ["electric", "water", "gas", "internet", "phone", "utility"]):
        return "Utilities"
    
    # Healthcare
    if any(keyword in merchant_lower for keyword in ["pharmacy", "medical", "doctor", "hospital", "health"]):
        return "Healthcare"
    
    return "Other"

def calculate_spending_stats(receipts: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Calculate spending statistics from receipts
    """
    if not receipts:
        return {}
    
    amounts = [r.get("amount", 0) for r in receipts]
    
    stats = {
        "total_amount": sum(amounts),
        "receipt_count": len(receipts),
        "average_amount": sum(amounts) / len(amounts),
        "max_amount": max(amounts),
        "min_amount": min(amounts),
        "category_totals": {}
    }
    
    # Calculate category totals
    for receipt in receipts:
        category = receipt.get("category", "Other")
        amount = receipt.get("amount", 0)
        stats["category_totals"][category] = stats["category_totals"].get(category, 0) + amount
    
    return stats

def detect_spending_anomalies(receipts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect potential spending anomalies
    """
    anomalies = []
    
    if len(receipts) < 3:
        return anomalies
    
    amounts = [r.get("amount", 0) for r in receipts]
    avg_amount = sum(amounts) / len(amounts)
    
    # High-value anomaly
    threshold = avg_amount * 2
    for receipt in receipts:
        if receipt.get("amount", 0) > threshold:
            anomalies.append({
                "type": "high_value",
                "description": f"Unusually high expense: ${receipt['amount']:.2f}",
                "receipt": receipt,
                "severity": "high"
            })
    
    # Frequent merchant anomaly
    merchant_counts = {}
    for receipt in receipts:
        merchant = receipt.get("merchant", "")
        merchant_counts[merchant] = merchant_counts.get(merchant, 0) + 1
    
    for merchant, count in merchant_counts.items():
        if count >= 3:
            anomalies.append({
                "type": "frequent_merchant",
                "description": f"Frequent spending at {merchant}: {count} transactions",
                "merchant": merchant,
                "count": count,
                "severity": "medium"
            })
    
    return anomalies

async def retry_operation(operation, max_retries: int = 3, delay: float = 1.0):
    """
    Retry an async operation with exponential backoff
    """
    for attempt in range(max_retries):
        try:
            return await operation()
        except Exception as e:
            if attempt == max_retries - 1:
                raise e
            
            logger.warning(f"Operation failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
            await asyncio.sleep(delay * (2 ** attempt))
    
    return None

def create_receipt_hash(receipt: Dict[str, Any]) -> str:
    """
    Create hash for receipt to detect duplicates
    """
    # Use merchant, amount, and date to create hash
    hash_string = f"{receipt.get('merchant', '')}{receipt.get('amount', 0)}{receipt.get('date', '')}"
    return hashlib.md5(hash_string.encode()).hexdigest()

def filter_duplicate_receipts(receipts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate receipts based on hash
    """
    seen_hashes = set()
    unique_receipts = []
    
    for receipt in receipts:
        receipt_hash = create_receipt_hash(receipt)
        if receipt_hash not in seen_hashes:
            seen_hashes.add(receipt_hash)
            unique_receipts.append(receipt)
    
    return unique_receipts

def format_error_message(error: Exception, context: str = "") -> str:
    """
    Format error message with context
    """
    error_msg = str(error)
    if context:
        return f"{context}: {error_msg}"
    return error_msg

def validate_api_response(response: Any, expected_fields: List[str] = None) -> bool:
    """
    Validate API response structure
    """
    if not response:
        return False
    
    if isinstance(response, dict):
        if expected_fields:
            return all(field in response for field in expected_fields)
        return True
    
    return False

def create_backup_filename(prefix: str = "backup") -> str:
    """
    Create backup filename with timestamp
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{timestamp}.json"

def save_backup(data: Dict[str, Any], filename: str) -> bool:
    """
    Save data backup to file
    """
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        return True
    except Exception as e:
        logger.error(f"Failed to save backup: {str(e)}")
        return False

def load_backup(filename: str) -> Optional[Dict[str, Any]]:
    """
    Load data backup from file
    """
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load backup: {str(e)}")
        return None
