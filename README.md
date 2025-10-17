# 💳 Project Raseed — AI-Powered Receipt & Spending Companion

> Transform your scattered receipts into actionable financial insights with AI-powered automation

[![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)](https://fastapi.tiangolo.com/)
[![Composio](https://img.shields.io/badge/Composio-000000?style=for-the-badge&logo=composio)](https://composio.dev/)
[![Gemini](https://img.shields.io/badge/Gemini-4285F4?style=for-the-badge&logo=google)](https://ai.google.dev/)
[![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)

## 🎯 Overview

Project Raseed is an AI-driven personal finance companion that automates receipt collection, extraction, categorization, and analysis across multiple platforms. It uses **Gemini AI (Vision + Text)** for intelligent data extraction and **Composio Tool Router** to integrate seamlessly with Gmail, Google Drive, Sheets, Slack, and Notion.

**The result** — effortless expense tracking, automated insights, and real-time spending summaries delivered directly to your favorite workspace.

## 🧩 Problem

Modern users face an invisible chaos of receipts:
- 📧 Digital invoices buried in Gmail
- 📁 Scanned bills scattered in Google Drive  
- 📊 Manual expense logging in Sheets
- 🚫 No unified view of where their money actually goes

**💥 The outcome**: missed budgets, untracked spending, and zero actionable insights.

## 💡 Solution

Project Raseed transforms this fragmented process into an **autonomous agentic workflow** that:

1. 🧾 **Extracts** receipts from Gmail and Drive using Gemini Vision
2. 🧠 **Analyzes** expenses using Gemini Text for categorization
3. 📊 **Updates** live dashboards in Notion and Sheets  
4. 💬 **Notifies** users on Slack with personalized summaries

Everything happens automatically, with no manual entry or app-hopping.

## 🧠 Agentic Architecture

Project Raseed follows a **4-Agent modular workflow**, making the system scalable, explainable, and maintainable.

| Agent | Role | Core Functions |
|-------|------|----------------|
| 🧾 **Extractor Agent** | Fetches and extracts raw receipt data | Connects Gmail/Drive → uses Gemini Vision for OCR |
| 📊 **Analyzer Agent** | Performs expense reasoning and pattern detection | Categorizes expenses, finds anomalies, summarizes insights |
| 🔄 **Updater Agent** | Syncs structured data to Sheets & Notion | Maintains a real-time financial database |
| 💬 **Notifier Agent** | Communicates updates to the user | Sends Slack alerts, weekly digests, and email confirmations |

Each agent runs independently but communicates through a **Main Orchestrator**, which controls workflow and data handoff.

## 🧱 System Workflow

```
📥 Gmail / Google Drive (receipts, invoices)
        ↓
🧾 Extractor Agent → Gemini Vision → structured JSON (merchant, date, total)
        ↓
📊 Analyzer Agent → Gemini Text → categorize, detect anomalies, summarize
        ↓
🔄 Updater Agent → Google Sheets / Notion → update dashboards
        ↓
💬 Notifier Agent → Slack / Gmail → send summaries and alerts
```

## ⚙️ Tooling & Tech Stack

| Component | Tool / API | Purpose |
|-----------|------------|---------|
| **LLM Reasoning** | Gemini Text API | Categorization, trend detection, reasoning |
| **Image / OCR** | Gemini Vision API | Extracts data from images & PDFs |
| **App Integration** | Composio Tool Router | Connects Gmail, Drive, Sheets, Notion, Slack |
| **Data Store** | Google Sheets | Central transaction database |
| **Dashboard** | Notion API | Expense visualization & insights |
| **Notifications** | Slack / Gmail (via Composio) | Alerts and summaries |
| **Language** | Python | Core implementation |
| **API Framework** | FastAPI | REST API with automatic docs |

## 🏗️ Project Structure

```
project-raseed/
├── src/
│   ├── main_orchestrator.py          # Controls agent communication
│   ├── agents/
│   │   ├── extractor_agent.py        # Fetch + extract receipts
│   │   ├── analyzer_agent.py         # Categorize + analyze
│   │   ├── updater_agent.py          # Update Notion & Sheets
│   │   └── notifier_agent.py         # Send Slack/Gmail notifications
│   ├── tools/
│   │   ├── gmail_tool.py
│   │   ├── drive_tool.py
│   │   ├── sheets_tool.py
│   │   ├── slack_tool.py
│   │   └── notion_tool.py
│   └── utils/
│       ├── formatters.py
│       └── helpers.py
├── main.py                           # FastAPI application
├── demo_raseed.py                    # Demo script
├── requirements.txt                  # Python dependencies
├── env_example.txt                   # Environment variables template
└── README.md                         # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Setup

```bash
# Copy the example environment file
cp env_example.txt .env

# Edit .env with your actual values
```

### 3. Required Environment Variables

```env
# Core API Keys
COMPOSIO_API_KEY=your_composio_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here

# User Configuration
USER_ID=your_email@example.com
EMAIL_ADDRESS=your_email@example.com

# Google Services
SPREADSHEET_ID=your_google_sheets_id_here
NOTION_DATABASE_ID=your_notion_database_id_here

# Slack Configuration
SLACK_CHANNEL=#personal-finance
```

### 4. Start the Application

```bash
# Start FastAPI server
python main.py

# Or run the demo
python demo_raseed.py
```

The API will be available at `http://localhost:8000`

## 📚 API Endpoints

### Core Workflow
- `POST /workflow/start` - Start complete receipt processing workflow
- `GET /workflow/status` - Get current workflow status
- `POST /receipt/process` - Process a single receipt

### System Management
- `GET /` - API information
- `GET /health` - Detailed health status
- `GET /agents/status` - Get status of all agents
- `GET /config` - Get current configuration

### Demo & Testing
- `GET /demo` - Run demo workflow
- `GET /docs` - Interactive API documentation

## 🔧 Essential Composio Tools Setup

### Required Tools in Your Composio Account:

1. **📧 Gmail Integration**
   - Enable Gmail toolkit
   - Connect your Gmail account
   - Grant permissions for reading emails and attachments

2. **📁 Google Drive Integration**
   - Enable Google Drive toolkit
   - Connect your Google Drive
   - Grant permissions for reading files

3. **📊 Google Sheets Integration**
   - Enable Google Sheets toolkit
   - Connect your Google Sheets
   - Grant permissions for reading/writing data

4. **💬 Slack Integration**
   - Enable Slack toolkit
   - Connect your Slack workspace
   - Configure bot permissions for sending messages

5. **📋 Notion Integration**
   - Enable Notion toolkit
   - Connect your Notion workspace
   - Grant permissions for creating/updating pages

### Authentication Configurations:
- Set up OAuth2 for Gmail, Drive, Sheets
- Configure Slack app credentials
- Set up Notion integration
- Test all connections before deployment

## 🔌 API Usage Examples

### Start Complete Workflow
```bash
curl -X POST "http://localhost:8000/workflow/start" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "demo_session_001",
    "days_back": 7
  }'
```

### Process Single Receipt
```bash
curl -X POST "http://localhost:8000/receipt/process" \
  -H "Content-Type: application/json" \
  -d '{
    "receipt": {
      "merchant": "Whole Foods",
      "amount": 85.50,
      "currency": "USD",
      "category": "Groceries",
      "items": ["organic vegetables", "dairy products"],
      "date": "2024-01-15",
      "source": "Manual"
    }
  }'
```

### Get Workflow Status
```bash
curl -X GET "http://localhost:8000/workflow/status"
```

### Run Demo
```bash
curl -X GET "http://localhost:8000/demo"
```

## 🧩 Demo Script

Run the complete demo to see all agents in action:

```bash
python demo_raseed.py
```

The demo will:
1. ✅ Initialize all agents
2. 🧾 Extract receipts from Gmail/Drive
3. 📊 Analyze and categorize expenses
4. 📈 Update Sheets and Notion
5. 💬 Send notifications via Slack

## 🚀 Deployment

### Local Development
```bash
python main.py
```

### Production with Uvicorn
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔍 Monitoring & Debugging

- **Health Check**: `GET /health`
- **API Documentation**: `http://localhost:8000/docs`
- **Interactive Docs**: `http://localhost:8000/redoc`
- **Agent Status**: `GET /agents/status`
- **Logs**: Check console output for detailed logging

## 🛡️ Security & Privacy

- 🔐 Keep your API keys secure and never commit them
- 🔒 Use environment variables for sensitive data
- 🛡️ Implement proper authentication for production
- 🔄 Regularly rotate API keys
- 📊 Monitor API usage and costs
- 🔒 All data processing happens locally/privately

## 🌍 Impact

✅ **Converts** unstructured receipts into structured, usable insights  
✅ **Automates** personal finance tracking with zero manual effort  
✅ **Combines** AI reasoning with familiar productivity tools for accessibility  
✅ **Scales** to business expense management and sustainability tracking  

## 🎯 Key Features

- **🧠 AI-Powered Extraction**: Uses Gemini Vision for OCR from images and PDFs
- **📊 Smart Categorization**: Automatically categorizes expenses using Gemini Text
- **🔄 Real-time Sync**: Updates Sheets and Notion dashboards automatically
- **💬 Intelligent Notifications**: Sends contextual alerts via Slack and email
- **🚨 Anomaly Detection**: Identifies unusual spending patterns
- **📈 Spending Insights**: Generates actionable financial recommendations
- **🔌 Multi-Platform**: Integrates with Gmail, Drive, Sheets, Slack, Notion
- **⚡ FastAPI Backend**: Modern REST API with automatic documentation

## 📖 Documentation

- **📚 FastAPI Docs**: Available at `/docs` when running
- **🔧 Composio Docs**: [docs.composio.dev](https://docs.composio.dev)
- **🤖 Gemini AI Docs**: [ai.google.dev](https://ai.google.dev)
- **📋 Notion API**: [developers.notion.com](https://developers.notion.com)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Composio** for seamless app integrations
- **Google Gemini** for powerful AI capabilities
- **FastAPI** for the excellent web framework
- **OpenAI** for additional AI capabilities

---

**💳 Project Raseed** - Transforming receipts into insights, one AI agent at a time 🚀

*No manual tracking, no data loss — just instant clarity on where your money goes.*
