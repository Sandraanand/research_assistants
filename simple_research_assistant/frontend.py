"""
Simplified Streamlit Frontend
Clean and user-friendly interface with PDF support and progress tracking
"""
import streamlit as st
import requests
import time
from config import config

# API URL
API_URL = f"http://localhost:{config.BACKEND_PORT}"

# Page config
st.set_page_config(
    page_title="Research Assistant",
    page_icon="🔬",
    layout="wide"
)

# Initialize session state
if 'results' not in st.session_state:
    st.session_state.results = None
if 'workflow_id' not in st.session_state:
    st.session_state.workflow_id = None


def call_api(endpoint: str, data: dict):
    """Call backend API"""
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


def upload_pdf(endpoint: str, files: dict, data: dict = None):
    """Upload PDF to backend"""
    try:
        response = requests.post(f"{API_URL}{endpoint}", files=files, data=data, timeout=300)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Upload Error: {str(e)}")
        return None


# ==================== Main App ====================

st.title("🔬 Research Assistant")
st.markdown("### AI-Powered Research Tool with GPT-4o")

# Sidebar
with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Select Page",
        ["🏠 Home", "📚 Research", "💡 Explain Concept", "📝 Submit Paper", "🔍 Check Status"]
    )
    
    st.markdown("---")
    st.info("**Powered by:**\n- Autogen 0.4\n- Selector GroupChat\n- Azure OpenAI GPT-4o")


# ==================== Home Page ====================

if page == "🏠 Home":
    st.header("Welcome!")
    
    st.markdown("""
    This research assistant uses **Autogen 0.4 Selector GroupChat** to coordinate multiple AI agents:
    
    ### 🤖 Agents
    
    1. **Literature Agent** - Searches PubMed for papers
    2. **Synthesis Agent** - Summarizes research papers
    3. **Extensions Agent** - Proposes future research directions
    4. **Explainer Agent** - Explains concepts simply
    5. **Advisor Agent** - Checks paper formatting
    
    ### 🚀 Quick Start
    
    1. **Research**: Enter a topic to find and analyze papers
    2. **Explain**: Get simple explanations of complex concepts
    3. **Submit**: Upload PDF paper and submit it
    4. **Track**: Check submission status anytime
    
    All agents are coordinated automatically by Selector GroupChat!
    """)


# ==================== Research Page ====================

elif page == "📚 Research":
    st.header("Research Workflow")
    
    st.info("💡 You can run full workflow OR just search literature independently!")
    
    topic = st.text_input("Research Topic", placeholder="e.g., Machine learning in healthcare")
    max_papers = st.slider("Max Papers", 1, 10, 5)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Full Workflow", type="primary", use_container_width=True):
            if topic:
                # Start workflow
                response = call_api("/api/research/full", {
                    "topic": topic,
                    "max_papers": max_papers
                })
                
                if response and "workflow_id" in response:
                    st.session_state.workflow_id = response["workflow_id"]
                    
                    # Progress tracking
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Poll for progress
                    while True:
                        try:
                            progress_response = requests.get(
                                f"{API_URL}/api/research/progress/{st.session_state.workflow_id}"
                            ).json()
                            
                            status = progress_response.get("status")
                            step = progress_response.get("step", "")
                            progress = progress_response.get("progress", 0)
                            
                            # Update UI
                            progress_bar.progress(progress / 100)
                            
                            # Update status with emoji
                            if "Searching" in step or "papers" in step.lower():
                                status_text.info(f"📚 {step}")
                            elif "synthesis" in step.lower() or "Synthesizing" in step:
                                status_text.info(f"📖 {step}")
                            elif "extension" in step.lower() or "generating" in step.lower():
                                status_text.info(f"🔮 {step}")
                            else:
                                status_text.info(f"⏳ {step}")
                            
                            # Check if completed
                            if status == "completed":
                                st.session_state.results = progress_response.get("results")
                                status_text.success("✅ Research completed!")
                                time.sleep(1)
                                st.rerun()
                                break
                            elif status == "failed":
                                status_text.error(f"❌ {step}")
                                break
                            
                            time.sleep(2)  # Poll every 2 seconds
                        
                        except Exception as e:
                            st.error(f"Error tracking progress: {e}")
                            break
            else:
                st.error("Please enter a research topic")
    
    with col2:
        if st.button("📚 Just Literature", use_container_width=True):
            if topic:
                with st.spinner("Searching PubMed..."):
                    response = call_api("/api/literature/search", {
                        "topic": topic,
                        "max_papers": max_papers
                    })
                    
                    if response:
                        st.session_state.results = {
                            "topic": topic,
                            "literature": response.get("formatted", ""),
                            "synthesis": "Not run (literature only)",
                            "extensions": "Not run (literature only)",
                            "status": "literature_only"
                        }
                        st.success(f"✅ Found {response.get('count', 0)} papers!")
                        st.rerun()
            else:
                st.error("Please enter a research topic")
    
    # Display results
    if st.session_state.results:
        results = st.session_state.results
        
        st.markdown("---")
        
        # Literature
        with st.expander("📚 Literature Search Results", expanded=True):
            st.markdown(results.get("literature", "No results"))
        
        # Only show if full workflow was run
        if results.get("status") != "literature_only":
            # Synthesis
            with st.expander("📖 Paper Summaries", expanded=True):
                st.markdown(results.get("synthesis", "No summaries"))
            
            # Extensions
            with st.expander("🔮 Future Research Extensions", expanded=True):
                st.markdown(results.get("extensions", "No extensions"))


# ==================== Explain Concept Page ====================

elif page == "💡 Explain Concept":
    st.header("Concept Explainer")
    
    concept = st.text_input("Concept to Explain", placeholder="e.g., Neural Networks")
    context = st.text_area("Optional Context", placeholder="Add context from your research...")
    
    if st.button("💡 Explain", type="primary"):
        if concept:
            with st.spinner("Generating explanation..."):
                result = call_api("/api/explain", {
                    "concept": concept,
                    "context": context if context else None
                })
                
                if result:
                    st.markdown("### Explanation")
                    st.info(result.get("explanation", ""))
        else:
            st.error("Please enter a concept")


# ==================== Submit Paper Page ====================

elif page == "📝 Submit Paper":
    st.header("Paper Submission")
    
    tab1, tab2 = st.tabs(["Check Formatting", "Submit Paper"])
    
    with tab1:
        st.subheader("Check Paper Formatting (PDF)")
        
        st.info("📄 Upload your research paper as a PDF file")
        
        uploaded_file = st.file_uploader(
            "Upload PDF Paper",
            type=['pdf'],
            help="Upload your research paper in PDF format"
        )
        
        title_override = st.text_input(
            "Paper Title (optional)",
            placeholder="Leave empty to extract from PDF metadata"
        )
        
        if st.button("📝 Check Formatting"):
            if uploaded_file:
                with st.spinner("Extracting text and checking formatting..."):
                    files = {"pdf_file": uploaded_file.getvalue()}
                    data = {"title": title_override} if title_override else {}
                    
                    result = upload_pdf("/api/check-paper-pdf", files, data)
                    
                    if result:
                        st.markdown("### Feedback")
                        st.info(result.get("feedback", ""))
            else:
                st.error("Please upload a PDF file")
    
    with tab2:
        st.subheader("Submit Paper (PDF)")
        
        st.info("📤 Upload your PDF paper and submit to professor")
        
        pdf_file = st.file_uploader(
            "Upload PDF Paper",
            type=['pdf'],
            key="submit_pdf",
            help="Upload your research paper in PDF format"
        )
        
        title = st.text_input("Paper Title", key="submit_title")
        authors = st.text_input(
            "Authors (comma-separated)", 
            placeholder="Dr. Smith, Dr. Jones",
            key="submit_authors"
        )
        professor_email = st.text_input(
            "Professor Email", 
            placeholder="professor@university.edu",
            key="submit_email"
        )
        
        if st.button("📤 Submit Paper", type="primary"):
            if all([pdf_file, title, authors, professor_email]):
                with st.spinner("Extracting PDF and submitting paper..."):
                    files = {"pdf_file": pdf_file.getvalue()}
                    data = {
                        "title": title,
                        "authors": authors,
                        "professor_email": professor_email
                    }
                    
                    result = upload_pdf("/api/submit-paper-pdf", files, data)
                    
                    if result:
                        st.success(f"✅ {result.get('message')}")
                        st.info(f"**Submission ID:** `{result.get('submission_id')}`\n\nSave this ID to check status later!")
                        
                        # Show formatting feedback
                        if result.get('formatting_feedback'):
                            with st.expander("📋 Formatting Feedback"):
                                st.info(result['formatting_feedback'].get('feedback', ''))
            else:
                st.error("Please fill all fields and upload a PDF")


# ==================== Check Status Page ====================

elif page == "🔍 Check Status":
    st.header("Check Submission Status")
    
    submission_id = st.text_input("Submission ID", placeholder="SUB-XXXXXXXX")
    
    if st.button("🔍 Check Status"):
        if submission_id:
            try:
                response = requests.get(f"{API_URL}/api/submission/{submission_id}")
                response.raise_for_status()
                result = response.json()
                
                st.markdown("### Submission Details")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Status", result.get("status", "unknown").upper())
                    st.write(f"**Title:** {result.get('title')}")
                
                with col2:
                    st.write(f"**Submitted:** {result.get('submitted_at')}")
                
                if result.get("feedback"):
                    st.markdown("### Feedback")
                    st.info(result.get("feedback"))
                
            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 404:
                    st.error("❌ Submission not found")
                else:
                    st.error(f"Error: {str(e)}")
            except Exception as e:
                st.error(f"Error: {str(e)}")
        else:
            st.error("Please enter a submission ID")
