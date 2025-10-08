from langchain_core.tools import tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.utilities import SQLDatabase
from datetime import datetime
import os

# Initialize embeddings
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# =============================================================================
# SQL DATABASE SETUP
# =============================================================================

def setup_sql_database():
    """
    Setup connection to SQLite database for appointment management.
    
    This function connects to the hospital.db SQLite database that contains:
    - doctors table: Information about available doctors
    - appointments table: Patient appointments with token numbers
    
    Returns:
        SQLDatabase: Connected database object or None if connection fails
    """
    try:
        # Check if database file exists
        db_path = "hospital.db"
        if not os.path.exists(db_path):
            print(f"⚠️  Warning: Database file '{db_path}' not found.")
            print("   Please run 'python setup_database.py' to create the database first.")
            return None
        
        # Connect to the SQLite database
        db = SQLDatabase.from_uri(f"sqlite:///{db_path}")
        
        # Print database info for debugging
        print(f"✅ SQL Database connected: {db.dialect}")
        print(f"📋 Available tables: {db.get_usable_table_names()}")
        
        return db
    
    except Exception as e:
        print(f"❌ Error connecting to SQL database: {str(e)}")
        return None

# Initialize SQL database connection
sql_db = setup_sql_database()

# =============================================================================
# PDF VECTOR STORE SETUP (Existing functionality)
# =============================================================================

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
    print("✅ Vector store initialized successfully with PDF content")
except Exception as e:
    print(f"⚠️  Warning: Failed to initialize vector store: {str(e)}")
    vector_store = None

# =============================================================================
# TOOL DEFINITIONS
# =============================================================================

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
    """Get information about the hospital owner Dr. Hari and hospital leadership details."""
    return """Hospital Owner Information:
    Name: Dr. Hari
    Position: Owner and Medical Director
    Hospital: Community Health Center Harichandanpur
    Location: Keonjhar, Odisha, India
    
    Dr. Hari is the owner and medical director of Community Health Center Harichandanpur, 
    overseeing all medical operations, policy implementation, and ensuring quality healthcare 
    delivery at the facility. Under his leadership, the hospital maintains comprehensive 
    policies for patient care, safety, and quality management."""

# =============================================================================
# NEW SQL AGENT TOOLS
# =============================================================================

@tool
def get_doctor_appointments(doctor_name: str) -> str:
    """
    Get all appointment tokens for a specific doctor.
    
    This tool queries the hospital database to find all scheduled appointments
    for a given doctor. It returns information about token numbers, patient names,
    appointment dates, and times.
    
    Args:
        doctor_name: Name of the doctor (e.g., "Dr. Harshin", "Dr. Priya Sharma")
    
    Returns:
        Formatted string with appointment details or error message
    
    Examples:
        - "What are the appointments for Dr. Harshin?"
        - "Show me Dr. Priya Sharma's tokens"
        - "What tokens are booked for Dr. Harshin today?"
    """
    try:
        # Check if database is available
        if sql_db is None:
            return "❌ Error: Appointment database is not available. Please contact the administrator."
        
        # Clean up doctor name (handle partial names)
        doctor_name = doctor_name.strip()
        
        # SQL query to get appointments for the doctor
        # Using LIKE to match partial names (e.g., "Harshin" will match "Dr. Harshin")
        query = f"""
        SELECT 
            d.doctor_name,
            d.specialization,
            a.token_number,
            a.patient_name,
            a.appointment_date,
            a.appointment_time,
            a.status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.doctor_id
        WHERE d.doctor_name LIKE '%{doctor_name}%'
        ORDER BY a.appointment_date, a.token_number
        """
        
        # Execute the query
        result = sql_db.run(query)
        
        # Check if any appointments were found
        if not result or result.strip() == "":
            return f"No appointments found for doctor: {doctor_name}. Please check the doctor's name and try again."
        
        # Format the result for better readability
        formatted_result = f"📋 Appointments for {doctor_name}:\n\n{result}"
        
        return formatted_result
    
    except Exception as e:
        return f"❌ Error retrieving appointments: {str(e)}\nPlease try again or contact support."

@tool
def get_todays_appointments(doctor_name: str = "") -> str:
    """
    Get today's appointment tokens for a specific doctor or all doctors.
    
    This tool shows all appointments scheduled for today. If a doctor name is provided,
    it shows only that doctor's appointments. Otherwise, it shows all appointments for today.
    
    Args:
        doctor_name: (Optional) Name of the doctor. Leave empty to see all appointments.
    
    Returns:
        Formatted string with today's appointment details
    
    Examples:
        - "What are today's appointments?"
        - "Show me Dr. Harshin's appointments for today"
        - "Today's tokens for all doctors"
    """
    try:
        # Check if database is available
        if sql_db is None:
            return "❌ Error: Appointment database is not available. Please contact the administrator."
        
        # Get today's date
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Build query based on whether doctor name is provided
        if doctor_name and doctor_name.strip():
            query = f"""
            SELECT 
                d.doctor_name,
                a.token_number,
                a.patient_name,
                a.appointment_time,
                a.status
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date = '{today}'
            AND d.doctor_name LIKE '%{doctor_name.strip()}%'
            ORDER BY a.token_number
            """
            title = f"📅 Today's Appointments for {doctor_name} ({today}):\n\n"
        else:
            query = f"""
            SELECT 
                d.doctor_name,
                a.token_number,
                a.patient_name,
                a.appointment_time,
                a.status
            FROM appointments a
            JOIN doctors d ON a.doctor_id = d.doctor_id
            WHERE a.appointment_date = '{today}'
            ORDER BY d.doctor_name, a.token_number
            """
            title = f"📅 Today's Appointments for All Doctors ({today}):\n\n"
        
        # Execute the query
        result = sql_db.run(query)
        
        # Check if any appointments were found
        if not result or result.strip() == "":
            return f"No appointments scheduled for today ({today})."
        
        # Format and return the result
        formatted_result = title + result
        
        return formatted_result
    
    except Exception as e:
        return f"❌ Error retrieving today's appointments: {str(e)}\nPlease try again or contact support."

@tool
def get_available_doctors() -> str:
    """
    Get a list of all available doctors at the hospital.
    
    This tool returns information about all doctors including their names,
    specializations, and available days.
    
    Returns:
        Formatted string with doctor information
    
    Examples:
        - "Which doctors are available?"
        - "Show me the list of doctors"
        - "Who are the doctors at the hospital?"
    """
    try:
        # Check if database is available
        if sql_db is None:
            return "❌ Error: Appointment database is not available. Please contact the administrator."
        
        # SQL query to get all doctors
        query = """
        SELECT 
            doctor_name,
            specialization,
            available_days
        FROM doctors
        ORDER BY doctor_name
        """
        
        # Execute the query
        result = sql_db.run(query)
        
        # Check if any doctors were found
        if not result or result.strip() == "":
            return "No doctor information available."
        
        # Format the result
        formatted_result = f"👨‍⚕️ Available Doctors at Community Health Center:\n\n{result}"
        
        return formatted_result
    
    except Exception as e:
        return f"❌ Error retrieving doctor information: {str(e)}\nPlease try again or contact support."

# =============================================================================
# TOOLS LIST - Updated to include SQL agent tools
# =============================================================================

# List of all tools available to the agent
TOOLS = [
    search_hospital_policies,  # Original tool for hospital policies
    get_current_datetime,      # Original tool for date/time
    get_owner_info,           # Original tool for owner info
    get_doctor_appointments,  # NEW: Get appointments for a specific doctor
    get_todays_appointments,  # NEW: Get today's appointments
    get_available_doctors     # NEW: Get list of all doctors
]