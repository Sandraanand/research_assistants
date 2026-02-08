# Simple Research Assistant - Updated

A clean, simplified multi-agent research assistant using **Autogen 0.4** with **Selector GroupChat** and **Azure OpenAI GPT-4o**.

## ✨ New Features

### 1. PDF Upload Support
- ✅ Upload research papers as PDF files
- ✅ Automatic text extraction from PDFs
- ✅ PDF metadata extraction (title, author, pages)
- ✅ No more copy-paste - just upload!

### 2. Real-Time Progress Tracking
- ✅ Live progress bar during research workflow
- ✅ Step-by-step status updates
- ✅ Visual indicators for each phase:
  - 📚 Searching for papers (20%)
  - 📖 Papers retrieved, starting synthesis (50%)
  - 🔮 Synthesis complete, generating research extensions (75%)
  - ✅ Research workflow completed (100%)

### 3. Background Processing
- ✅ Research runs in background
- ✅ Non-blocking UI
- ✅ Progress polling every 2 seconds

## 🏗️ Architecture

```
User Request
     ↓
Selector GroupChat (Autogen 0.4)
     ↓
Automatically selects appropriate agent:
     ├── Literature Agent (PubMed search)
     ├── Synthesis Agent (Summarization)
     ├── Extensions Agent (Future research)
     ├── Explainer Agent (Simple explanations)
     └── Advisor Agent (Paper checking)
```

## 📁 Project Structure

```
simple_research_assistant/
├── config.py              # Configuration (Azure OpenAI)
├── database.py            # SQLAlchemy models
├── orchestrator.py        # Selector GroupChat + Agents
├── backend.py             # FastAPI server with PDF support
├── frontend.py            # Streamlit UI with progress tracking
├── pubmed_utils.py        # PubMed search
├── pdf_utils.py           # NEW: PDF text extraction
├── requirements.txt       # Dependencies
├── .env.example           # Environment template
└── README.md              # This file
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` with your Azure OpenAI credentials:

```env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=gpt-4o
```

### 3. Start Backend

```bash
python backend.py
```

Backend runs on: `http://localhost:8000`

### 4. Start Frontend

In a new terminal:

```bash
streamlit run frontend.py
```

Frontend opens at: `http://localhost:8501`

## 🎯 Usage

### Research Workflow (With Progress Tracking)

1. Navigate to "📚 Research" page
2. Enter a research topic
3. Select max papers (1-10)
4. Click "🚀 Start Research"
5. Watch real-time progress:
   - **20%**: 📚 Searching for papers
   - **50%**: 📖 Papers retrieved, starting synthesis
   - **75%**: 🔮 Synthesis complete, generating research extensions
   - **100%**: ✅ Research workflow completed

**Progress Updates:**
```
⏳ Initializing workflow
📚 Searching for papers
📖 Papers retrieved, starting synthesis
🔮 Synthesis complete, generating research extensions
✅ Research workflow completed
```

### Submit Papers (PDF Upload)

**Check Formatting:**
1. Go to "📝 Submit Paper"
2. Click "Check Formatting" tab
3. Upload PDF file
4. Optionally override title
5. Click "📝 Check Formatting"
6. Review feedback

**Submit Paper:**
1. Click "Submit Paper" tab
2. Upload PDF file
3. Enter title
4. Enter authors (comma-separated)
5. Enter professor email
6. Click "📤 Submit Paper"
7. Save your submission ID

**Benefits:**
- ✅ No copy-paste needed
- ✅ Automatic text extraction
- ✅ Preserves formatting information
- ✅ Works with any PDF

### Explain Concepts

1. Go to "💡 Explain Concept"
2. Enter a concept (e.g., "Neural Networks")
3. Optionally add context
4. Get simple explanation with examples

### Check Status

1. Go to "🔍 Check Status"
2. Enter your submission ID
3. View current status and feedback

## 🔧 API Endpoints

### New Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/research` | POST | Start research (returns workflow_id) |
| `/api/research/progress/{id}` | GET | Check workflow progress |
| `/api/check-paper-pdf` | POST | Check PDF formatting |
| `/api/submit-paper-pdf` | POST | Submit PDF paper |

### Existing Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/explain` | POST | Explain a concept |
| `/api/check-paper` | POST | Check text formatting |
| `/api/submission/{id}` | GET | Check submission status |

## 📊 Progress Tracking Flow

```
User clicks "Start Research"
        ↓
Backend creates workflow_id
        ↓
Returns workflow_id to frontend
        ↓
Frontend starts polling progress
        ↓
Backend updates progress:
  - 20%: Searching for papers
  - 50%: Papers retrieved
  - 75%: Synthesis complete
  - 100%: Workflow complete
        ↓
Frontend displays results
```

## 🎓 Example Usage

### Python API Example - Research with Progress

```python
import requests
import time

# Start research
response = requests.post("http://localhost:8000/api/research", json={
    "topic": "deep learning in healthcare",
    "max_papers": 5
})

workflow_id = response.json()["workflow_id"]

# Poll for progress
while True:
    progress = requests.get(
        f"http://localhost:8000/api/research/progress/{workflow_id}"
    ).json()
    
    print(f"{progress['step']} - {progress['progress']}%")
    
    if progress["status"] == "completed":
        results = progress["results"]
        break
    
    time.sleep(2)
```

### Python API Example - PDF Upload

```python
import requests

# Check PDF formatting
with open("paper.pdf", "rb") as f:
    files = {"pdf_file": f}
    data = {"title": "My Research Paper"}
    
    response = requests.post(
        "http://localhost:8000/api/check-paper-pdf",
        files=files,
        data=data
    )
    
    print(response.json()["feedback"])

# Submit PDF paper
with open("paper.pdf", "rb") as f:
    files = {"pdf_file": f}
    data = {
        "title": "My Research Paper",
        "authors": "Dr. Smith, Dr. Jones",
        "professor_email": "prof@university.edu"
    }
    
    response = requests.post(
        "http://localhost:8000/api/submit-paper-pdf",
        files=files,
        data=data
    )
    
    print(f"Submission ID: {response.json()['submission_id']}")
```

## 🔄 What's New

### Changes from Previous Version

1. **PDF Support**
   - Added `pdf_utils.py` for text extraction
   - New endpoints: `/api/check-paper-pdf`, `/api/submit-paper-pdf`
   - Frontend file upload component
   - Automatic PDF metadata extraction

2. **Progress Tracking**
   - Background workflow execution
   - Progress polling endpoint
   - Real-time UI updates
   - Visual progress indicators

3. **Better User Experience**
   - No more long waits without feedback
   - Step-by-step progress visibility
   - PDF upload instead of copy-paste
   - Non-blocking UI

## 🐛 Troubleshooting

### PDF Extraction Issues

**Error: "Could not extract text from PDF"**

Solutions:
1. Ensure PDF contains text (not scanned images)
2. Try converting scanned PDF to text first
3. Check PDF is not password-protected
4. Verify PDF is not corrupted

### Progress Not Updating

**Issue: Progress stuck at 0%**

Solutions:
1. Check backend is running
2. Verify Azure OpenAI credentials
3. Check backend logs for errors
4. Ensure workflow_id is valid

### Slow Research Workflow

**Issue: Takes too long**

Solutions:
1. Reduce max_papers (use 3-5 instead of 10)
2. Use more specific research topics
3. Check Azure OpenAI rate limits
4. Verify internet connection for PubMed

## 📝 Requirements

- Python 3.9+
- Azure OpenAI account with GPT-4o deployment
- Internet connection (for PubMed search)
- PDF files with extractable text (not scanned images)

## 🎯 Key Features

1. **Autogen 0.4** with Selector GroupChat
2. **PDF Upload** - No copy-paste needed
3. **Real-Time Progress** - See what's happening
4. **Background Processing** - Non-blocking UI
5. **Simple Code** - Easy to understand
6. **Full Functionality** - All features work

## 📚 Documentation

- **API Documentation**: `http://localhost:8000/docs`
- **Progress Tracking**: See workflow status in real-time
- **PDF Upload**: Automatic text extraction from PDFs

## 🙏 Acknowledgments

- Microsoft Autogen team for the framework
- Azure OpenAI for GPT-4o
- Streamlit for the UI framework
- pdfplumber and PyPDF2 for PDF processing

---

**Simple. Clean. Powerful.**

Built with Autogen 0.4 Selector GroupChat + Azure OpenAI GPT-4o

**New**: PDF Upload + Real-Time Progress Tracking! 🎉
