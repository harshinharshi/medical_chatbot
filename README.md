# Medical Assistant FastAPI 🏥

A FastAPI-based medical assistant for Community Health Center Harichandanpur, Keonjhar, Odisha. This AI-powered assistant helps with hospital policies, procedures, visiting hours, appointment management, and general medical inquiries.

## Features ✨

- **AI-Powered Responses**: Uses LangChain and Groq for intelligent conversations
- **Hospital Policy Search**: Vector-based search through hospital policies PDF
- **Appointment Management**: SQL-based appointment and token booking system
- **Doctor Information**: Query available doctors and their schedules
- **Multi-conversation Support**: Maintains conversation history with thread IDs
- **RESTful API**: Clean and well-documented FastAPI endpoints
- **Real-time Information**: Current date/time and hospital information

## Setup Instructions 🚀

### 1. Prerequisites

- Python 3.8 or higher
- Groq API key (sign up at [Groq Console](https://console.groq.com))

### 2. Installation

```bash
# Clone or download the project
cd your-project-directory

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment Setup

Create a `.env` file in the project root:

```bash
# .env file
GROQ_API_KEY=your_groq_api_key_here

# Optional: LangSmith tracing (for debugging)
LANGSMITH_TRACING="true"
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY=your_langsmith_key_here
LANGSMITH_PROJECT="medical_chatbot"
```

### 4. Setup Database with Dummy Data

**IMPORTANT:** Run this command first to create the appointment database:

```bash
python setup_database.py
```

This creates a `hospital.db` SQLite database with:
- **2 Doctors**: 
  - Dr. Harshin (General Medicine) - Available Monday to Friday
  - Dr. Priya Sharma (Pediatrics) - Available Monday, Wednesday, Friday
- **Sample appointments** with token numbers for testing
- Appointments scheduled for today and upcoming days

You should see output like:
```
✅ Database created successfully!
📊 Database file: hospital.db
👨‍⚕️ Doctors added: 2
📅 Appointments added: 12
```

### 5. Prepare Hospital Policies (Optional)

If you have a hospital policies PDF:

- Create a folder: `utils/data/`
- Place your PDF file as: `utils/data/hospital_policies.pdf`

If no PDF is available, the system will use fallback content.

### 6. Run the Application

```bash
# Start the FastAPI server
python main.py

# Or use uvicorn directly
uvicorn main:app --reload
```

The API will be available at: http://localhost:8000

### 7. Run LangGraph Studio (Optional)

You can visualize and interact with the LangGraph agent using LangGraph Studio.

First, ensure you have provided all required API keys in the `.env` file.

Then, from the project root directory, run the following command:

```bash
langgraph dev
```

## API Endpoints 📡

### 1. Root Information

```bash
GET /
```

Returns basic API information and available endpoints.

### 2. Health Check

```bash
GET /health
```

Check if the service is running properly.

### 3. Hospital Information

```bash
GET /info
```

Get details about the hospital and available services.

### 4. Chat with Assistant

```bash
POST /chat
Content-Type: application/json

{
    "message": "What are the visiting hours?",
    "thread_id": "optional-thread-id"
}
```

### 5. Interactive Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Usage Examples 💡

### Python Requests

```python
import requests

# Chat with the assistant about appointments
response = requests.post(
    "http://localhost:8000/chat",
    json={
        "message": "What is the token booked for Dr. Harshin?",
        "thread_id": "user-123"
    }
)

result = response.json()
print(result["response"])
```


## Project Structure 📁

```
project/
├── main.py                      # FastAPI application
├── agent.py                     # LangGraph agent setup
├── setup_database.py            # Database setup with dummy data
├── test_sql_agent.py            # Test script for SQL agent
├── requirements.txt             # Dependencies
├── .env                         # Environment variables
├── .gitignore                   # Git ignore rules
├── hospital.db                  # SQLite database (created by setup)
├── utils/
│   ├── __init__.py             # Package initialization
│   ├── llm.py                  # Groq LLM configuration
│   ├── nodes.py                # Agent nodes
│   ├── state.py                # State management
│   ├── tools.py                # Agent tools (including SQL tools)
│   └── data/                   # Data folder
│       └── hospital_policies.pdf
└── README.md                    # This file
```

## Available Tools 🛠️

The assistant has access to these tools:

### Original Tools:
1. **search_hospital_policies**: Search through hospital policies and procedures
2. **get_current_datetime**: Get current date and time
3. **get_owner_info**: Information about Dr. Harshin and hospital leadership

### New SQL Agent Tools:
4. **get_doctor_appointments**: Get all appointments for a specific doctor
5. **get_todays_appointments**: Get today's appointment schedule
6. **get_available_doctors**: List all doctors at the hospital

## Appointment System Queries 🗓️

### Example Questions About Appointments:

**Doctor Appointments:**
- "What is the token booked for Dr. Harshin?"
- "Show me all appointments for Dr. Harshin"
- "What tokens are booked for Dr. Priya Sharma?"
- "Tell me Dr. Harshin's appointments"

**Today's Appointments:**
- "What tokens are booked for Dr. Harshin today?"
- "Show me today's appointments"
- "What is today's appointment schedule?"
- "Today's tokens for Dr. Priya"

**Doctor Information:**
- "Which doctors are available?"
- "Who are the doctors at the hospital?"
- "Show me the list of doctors"
- "What is Dr. Harshin's specialization?"

**Patient Details:**
The system can provide:
- Token numbers for each appointment
- Patient names who have booked tokens
- Appointment dates and times
- Appointment status (Scheduled/Completed)
- Doctor specializations

**Combined Queries:**
- "What are the visiting hours and Dr. Harshin's tokens for today?"
- "Who is the hospital owner and what appointments does Dr. Priya have?"

## Example Conversations 🤔

### Example 1: Check Tokens for a Doctor
```
You: What is the token booked for Dr. Harshin?