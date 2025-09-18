from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from datetime import datetime
import os

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

def load_pdf_content(pdf_path: str) -> str:
    """Load and extract text content from PDF file"""
    try:
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found at {pdf_path}")
        
        # Load PDF using PyPDFLoader
        loader = PyPDFLoader(pdf_path)
        documents = loader.load()
        
        # Combine all pages into one text
        full_text = ""
        for doc in documents:
            full_text += doc.page_content + "\n"
        
        return full_text
    
    except Exception as e:
        print(f"Error loading PDF: {str(e)}")
        # Fallback to hardcoded content if PDF loading fails
        return get_fallback_content()

def get_fallback_content() -> str:
    """Fallback content in case PDF loading fails"""
    return """
    HOSPITAL WIDE POLICIES - Community Health Center Harichandanpur, Keonjhar, Odisha
    
    VISITOR'S POLICY:
    Objective: To make sure that our patients get the rest they need and other patients are not disturbed.
    
    Policy:
    1. Visitors must be age of 12 years or above
    2. Siblings will be allowed to visit the maternity units as long as they do not exhibit symptoms of cold or other respiratory infection
    3. Request to visit in compassionate care situation may be approved by the nursing sister
    
    Visiting Hours:
    General Visiting Hours:
    - Before and after the round of doctor
    - Please limit your stay to 15-20 minutes
    - Maximum no. of visitors in the rooms are 02 at a time
    - Children under the age of 12 are not permitted in wards nor may they wait in the waiting area
    - A care giver may interrupt your visit during patients care routine
    - If you are unfit please postpone your visit
    
    For complete hospital policies, please ensure the PDF file is available at utils/hospital.pdf
    """

def setup_vector_store():
    """Setup in-memory vector store with hospital policies from PDF"""
    
    # Define PDF path
    pdf_path = os.path.join("utils/data", "hospital_policies.pdf")
    
    # Load content from PDF
    hospital_policies_content = load_pdf_content(pdf_path)
    
    # Split text into chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    
    texts = text_splitter.split_text(hospital_policies_content)
    
    # Create in-memory vector store
    vector_store = InMemoryVectorStore(embeddings)
    vector_store.add_texts(texts)
    
    return vector_store

# Initialize vector store
try:
    vector_store = setup_vector_store()
    print("Vector store initialized successfully with PDF content")
except Exception as e:
    print(f"Warning: Failed to initialize vector store: {str(e)}")
    vector_store = None

@tool
def search_hospital_policies(query: str) -> str:
    """Search hospital policies and procedures for specific information about patient care, visiting hours, admission procedures, consent policies, confidentiality rules, bed management, transfers, complaints, quality standards, and medicine management."""
    try:
        if vector_store is None:
            return "Error: Hospital policies database is not available. Please ensure the PDF file exists at utils/hospital.pdf"
        
        docs = vector_store.similarity_search(query, k=3)
        if not docs:
            return "No relevant hospital policies found for your query."
        
        context = "\n\n".join([doc.page_content for doc in docs])
        return f"Hospital Policies Information:\n{context}"
    except Exception as e:
        return f"Error searching hospital policies: {str(e)}"

@tool
def get_current_datetime() -> str:
    """Get the current date and time information."""
    return f"Current date and time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

@tool
def get_owner_info() -> str:
    """Get information about the hospital owner Dr. Harshin and hospital leadership details."""
    return """Hospital Owner Information:
    Name: Dr. Harshin
    Position: Owner and Medical Director
    Hospital: Community Health Center Harichandanpur
    Location: Keonjhar, Odisha, India
    
    Dr. Harshin is the owner and medical director of Community Health Center Harichandanpur, 
    overseeing all medical operations, policy implementation, and ensuring quality healthcare 
    delivery at the facility. Under his leadership, the hospital maintains comprehensive 
    policies for patient care, safety, and quality management."""

# List of all tools
TOOLS = [search_hospital_policies, get_current_datetime, get_owner_info]