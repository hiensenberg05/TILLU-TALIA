"""
🧾 Extractor Agent - Fetches and extracts raw receipt data
Connects to Gmail/Drive → uses Gemini Vision for OCR
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import base64
import io

from composio import Composio
from openai import OpenAI
import google.generativeai as genai

from tools.gmail_tool import GmailTool
from tools.drive_tool import DriveTool

logger = logging.getLogger(__name__)

class ExtractorAgent:
    """
    Extractor Agent handles:
    - Fetching receipts from Gmail and Google Drive
    - Using Gemini Vision for OCR extraction
    - Converting images/PDFs to structured JSON data
    """
    
    def __init__(self):
        self.composio = Composio()
        self.gmail_tool = GmailTool()
        self.drive_tool = DriveTool()
        
        # Initialize Gemini Vision
        genai.configure(api_key="YOUR_GEMINI_API_KEY")  # Set in .env
        self.vision_model = genai.GenerativeModel('gemini-1.5-flash')
        
        self.status = {"last_extraction": None, "receipts_found": 0, "errors": []}
    
    async def extract_all_receipts(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Extract receipts from both Gmail and Google Drive
        """
        logger.info("🔍 Starting receipt extraction from all sources...")
        
        all_receipts = []
        extraction_sources = []
        
        try:
            # Extract from Gmail
            logger.info("📧 Extracting receipts from Gmail...")
            gmail_receipts = await self.extract_from_gmail(days_back)
            all_receipts.extend(gmail_receipts["receipts"])
            extraction_sources.append({"source": "Gmail", "count": len(gmail_receipts["receipts"])})
            
            # Extract from Google Drive
            logger.info("📁 Extracting receipts from Google Drive...")
            drive_receipts = await self.extract_from_drive(days_back)
            all_receipts.extend(drive_receipts["receipts"])
            extraction_sources.append({"source": "Google Drive", "count": len(drive_receipts["receipts"])})
            
            self.status["last_extraction"] = datetime.now()
            self.status["receipts_found"] = len(all_receipts)
            
            logger.info(f"✅ Extraction complete: {len(all_receipts)} receipts found")
            
            return {
                "status": "success",
                "receipts": all_receipts,
                "sources": extraction_sources,
                "total_count": len(all_receipts),
                "extraction_time": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Extraction failed: {str(e)}")
            self.status["errors"].append(str(e))
            return {
                "status": "error",
                "error": str(e),
                "receipts": [],
                "sources": []
            }
    
    async def extract_from_gmail(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Extract receipts from Gmail emails and attachments
        """
        try:
            # Search for receipt-related emails
            search_queries = [
                "receipt subject:receipt OR subject:invoice OR subject:order confirmation",
                "attachment:pdf OR attachment:png OR attachment:jpg",
                "from:amazon.com OR from:paypal.com OR from:stripe.com"
            ]
            
            emails = await self.gmail_tool.search_emails(
                query=" OR ".join(search_queries),
                days_back=days_back
            )
            
            receipts = []
            for email in emails:
                # Extract receipt data from email content
                receipt_data = await self.extract_receipt_from_email(email)
                if receipt_data:
                    receipt_data["source"] = "Gmail"
                    receipt_data["email_id"] = email.get("id")
                    receipts.append(receipt_data)
                
                # Process attachments
                if email.get("attachments"):
                    for attachment in email["attachments"]:
                        attachment_receipt = await self.extract_receipt_from_attachment(attachment)
                        if attachment_receipt:
                            attachment_receipt["source"] = "Gmail Attachment"
                            attachment_receipt["email_id"] = email.get("id")
                            receipts.append(attachment_receipt)
            
            return {
                "status": "success",
                "receipts": receipts,
                "source": "Gmail",
                "emails_processed": len(emails)
            }
            
        except Exception as e:
            logger.error(f"❌ Gmail extraction failed: {str(e)}")
            return {"status": "error", "error": str(e), "receipts": []}
    
    async def extract_from_drive(self, days_back: int = 7) -> Dict[str, Any]:
        """
        Extract receipts from Google Drive files
        """
        try:
            # Search for receipt files in Drive
            files = await self.drive_tool.search_files(
                query="receipt OR invoice OR bill",
                file_types=["pdf", "png", "jpg", "jpeg"],
                days_back=days_back
            )
            
            receipts = []
            for file_info in files:
                receipt_data = await self.extract_receipt_from_file(file_info)
                if receipt_data:
                    receipt_data["source"] = "Google Drive"
                    receipt_data["file_id"] = file_info.get("id")
                    receipts.append(receipt_data)
            
            return {
                "status": "success",
                "receipts": receipts,
                "source": "Google Drive",
                "files_processed": len(files)
            }
            
        except Exception as e:
            logger.error(f"❌ Drive extraction failed: {str(e)}")
            return {"status": "error", "error": str(e), "receipts": []}
    
    async def extract_receipt_from_email(self, email: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract receipt data from email content using Gemini
        """
        try:
            email_content = email.get("body", "")
            subject = email.get("subject", "")
            
            # Use Gemini to extract structured data from email text
            prompt = f"""
            Extract receipt/purchase information from this email:
            
            Subject: {subject}
            Body: {email_content[:2000]}  # Limit to avoid token limits
            
            Return JSON with:
            - merchant: string
            - date: string (YYYY-MM-DD format)
            - amount: number
            - currency: string
            - items: array of strings
            - category: string (Groceries, Utilities, Entertainment, etc.)
            - confidence: number (0-1)
            
            If no receipt data found, return null.
            """
            
            response = self.vision_model.generate_content(prompt)
            
            # Parse the response
            try:
                receipt_data = json.loads(response.text)
                if receipt_data and receipt_data.get("confidence", 0) > 0.7:
                    return receipt_data
            except json.JSONDecodeError:
                pass
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Email extraction failed: {str(e)}")
            return None
    
    async def extract_receipt_from_attachment(self, attachment: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract receipt data from email attachment using Gemini Vision
        """
        try:
            # Download attachment content
            attachment_data = await self.gmail_tool.download_attachment(attachment["id"])
            
            # Convert to base64 for Gemini Vision
            if attachment_data:
                image_data = base64.b64encode(attachment_data).decode()
                
                # Use Gemini Vision to extract receipt data
                prompt = """
                Analyze this receipt/invoice image and extract:
                - merchant: business name
                - date: purchase date
                - amount: total amount paid
                - currency: currency code
                - items: list of purchased items
                - category: expense category
                - confidence: extraction confidence (0-1)
                
                Return as JSON. If not a receipt, return null.
                """
                
                response = self.vision_model.generate_content([
                    prompt,
                    {"mime_type": attachment.get("mimeType", "image/jpeg"), "data": image_data}
                ])
                
                try:
                    receipt_data = json.loads(response.text)
                    if receipt_data and receipt_data.get("confidence", 0) > 0.7:
                        return receipt_data
                except json.JSONDecodeError:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"❌ Attachment extraction failed: {str(e)}")
            return None
    
    async def extract_receipt_from_file(self, file_info: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract receipt data from Google Drive file using Gemini Vision
        """
        try:
            # Download file content
            file_data = await self.drive_tool.download_file(file_info["id"])
            
            if file_data:
                image_data = base64.b64encode(file_data).decode()
                
                # Use Gemini Vision for extraction
                prompt = """
                Analyze this receipt/invoice image and extract:
                - merchant: business name
                - date: purchase date (YYYY-MM-DD)
                - amount: total amount paid
                - currency: currency code
                - items: list of purchased items
                - category: expense category (Groceries, Utilities, Entertainment, etc.)
                - confidence: extraction confidence (0-1)
                
                Return as JSON. If not a receipt, return null.
                """
                
                response = self.vision_model.generate_content([
                    prompt,
                    {"mime_type": file_info.get("mimeType", "image/jpeg"), "data": image_data}
                ])
                
                try:
                    receipt_data = json.loads(response.text)
                    if receipt_data and receipt_data.get("confidence", 0) > 0.7:
                        return receipt_data
                except json.JSONDecodeError:
                    pass
            
            return None
            
        except Exception as e:
            logger.error(f"❌ File extraction failed: {str(e)}")
            return None
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent": "ExtractorAgent",
            "status": "active" if not self.status["errors"] else "error",
            "last_extraction": self.status["last_extraction"],
            "receipts_found": self.status["receipts_found"],
            "errors": self.status["errors"]
        }

# Demo function
async def demo_extraction():
    """Demo the extractor agent"""
    extractor = ExtractorAgent()
    
    print("🧾 Extractor Agent Demo")
    print("=" * 30)
    
    results = await extractor.extract_all_receipts()
    
    print(f"Status: {results['status']}")
    print(f"Receipts found: {results['total_count']}")
    
    for source in results.get("sources", []):
        print(f"  • {source['source']}: {source['count']} receipts")
    
    return results

if __name__ == "__main__":
    asyncio.run(demo_extraction())
