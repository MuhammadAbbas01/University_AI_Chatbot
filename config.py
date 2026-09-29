"""
Configuration for the University of Malakand AI Assistant.

Model selection (set OLLAMA_MODEL as an environment variable to override):
    - mistral        -> tested on CPU-only machines (default)
    - deepseek-r1:7b -> tested on machines with a GPU

Secrets (SECRET_KEY, ADMIN_PASSWORD) can also be set through environment
variables. The built-in defaults are for local demo use only.
"""

import os
import requests

# ================================================================================
# UNIVERSITY INFORMATION
# ================================================================================
UNIVERSITY_NAME = "University of Malakand"
UNIVERSITY_TAGLINE = "Bridging aspirations & achievements"
UNIVERSITY_LOCATION = "Chakdara, Lower Dir, Khyber Pakhtunkhwa, Pakistan"
UNIVERSITY_WEBSITE = "https://www.uom.edu.pk"
UNIVERSITY_STATS = {
    "students": "6,324",
    "faculty": "305",
    "programs": "68",
    "ranking": "#9 in Pakistan (QS Ranking)",
    "established": "2001"
}

# ================================================================================
# APP SETTINGS
# ================================================================================
APP_NAME = "University of Malakand AI Assistant"
SECRET_KEY = os.environ.get("SECRET_KEY", "uom-ai-2024-ultra-secure-key")
DEBUG_MODE = False

# ================================================================================
# OLLAMA SETTINGS
# ================================================================================
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "mistral")   # "deepseek-r1:7b" for GPU machines
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
OLLAMA_TIMEOUT = 300

# ================================================================================
# RAG SETTINGS
# ================================================================================
PDF_FOLDER = "data/pdfs"
VECTOR_DB_PATH = "vector_db"

# Chunking: large chunks keep complete regulation clauses together
CHUNK_SIZE = 1500
CHUNK_OVERLAP = 300           # overlap so no rule is cut in half

# Retrieval (MMR): fetch a wide candidate pool, keep the best few
TOP_K_RESULTS = 10            # chunks passed to the LLM
FETCH_K = 50                  # candidates considered before MMR selection
LAMBDA_MULT = 0.5             # balance between relevance and diversity

# ================================================================================
# SERVER SETTINGS
# ================================================================================
HOST = "0.0.0.0"
PORT = 5000
MAX_HISTORY = 100
THREADED = True

# ================================================================================
# SECURITY SETTINGS
# ================================================================================
# Demo default only. Set the ADMIN_PASSWORD environment variable for any real deployment.
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "malakand2024")

# ================================================================================
# RESPONSE SETTINGS
# ================================================================================
ENABLE_STREAMING = True
STREAM_DELAY = 0.01
MAX_ANSWER_LENGTH = 3000
TEMPERATURE = 0.0             # deterministic output for factual answers
SHOW_SOURCES = True
RESPONSE_LANGUAGE = "english"

# ================================================================================
# ANALYTICS SETTINGS
# ================================================================================
ENABLE_ANALYTICS = True
ANALYTICS_FILE = "analytics.json"

# ================================================================================
# LOGGING SETTINGS
# ================================================================================
ENABLE_LOGGING = True
LOG_FILE = "logs/system.log"
LOG_LEVEL = "INFO"

# ================================================================================
# UNIVERSITY RESOURCES
# ================================================================================
UNIVERSITY_RESOURCES = {
    "Semester Regulations": "https://www.uom.edu.pk/downloads",
    "Admission Forms": "https://exams.uom.edu.pk/forms.php",
    "Online Admissions": "https://admissions.uom.edu.pk/",
    "Downloads Page": "https://www.uom.edu.pk/downloads",
    "Examination Rules": "https://www.uom.edu.pk/downloads",
    "Fee Structure": "https://www.uom.edu.pk/downloads"
}

# ================================================================================
# AUTO-CREATE FOLDERS
# ================================================================================
os.makedirs(PDF_FOLDER, exist_ok=True)
os.makedirs(VECTOR_DB_PATH, exist_ok=True)
os.makedirs("logs", exist_ok=True)

# ================================================================================
# RAG PROMPT TEMPLATE
# ================================================================================
PROMPT_TEMPLATE = """You are a precise document search system for University of Malakand, Pakistan. Extract EXACT information from official university documents.

🎯 RULES:

1. READ ALL CONTEXT THOROUGHLY
   - Multiple document chunks are provided
   - Read all of them before answering
   - Find the most recent and specific information

2. DOCUMENT PRIORITY:
   First use: Graduate Degree Regulations 2024 (Amended 2025)
   Then use: Semester Regulations 2024 (Amended 7-25)
   Then use: Any 2024/2025 documents
   Last use: Older documents (only if 2024/2025 don't have the answer)

3. BE EXACT:
   - Use EXACT numbers (2 years, 7 days, ONE MONTH, etc.)
   - Use EXACT percentages (50%, 100%, etc.)
   - Quote specific section numbers when available
   - Don't approximate or round

4. IF DOCUMENTS CONFLICT:
   - Always use the NEWEST document
   - State which document you're using

5. ANSWER FORMAT:

**Answer**
[Clear direct answer with exact details]

**Details:**
• [Key point 1]
• [Key point 2]
• [Key point 3]

**Source:** [Document name and section if available]

Context: {context}

Question: {question}

Answer:"""

# ================================================================================
# VALIDATION
# ================================================================================
def validate_config():
    """Check if configuration is correct"""
    errors = []

    # Check Ollama
    try:
        response = requests.get(f"{OLLAMA_HOST}/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get('models', [])
            model_names = [m['name'] for m in models]

            if not any(OLLAMA_MODEL in name for name in model_names):
                errors.append(f"⚠️ Model '{OLLAMA_MODEL}' not found! Run: ollama pull {OLLAMA_MODEL}")
            else:
                print(f"✅ Model '{OLLAMA_MODEL}' is ready!")
        else:
            errors.append("❌ Cannot connect to Ollama")
    except Exception as e:
        errors.append(f"❌ Ollama not running! Error: {e}")
        errors.append("   Start Ollama by running: ollama serve")

    # Check PDFs
    if not os.path.exists(PDF_FOLDER):
        errors.append(f"❌ PDF folder not found: {PDF_FOLDER}")

    pdf_files = []
    if os.path.exists(PDF_FOLDER):
        pdf_files = [f for f in os.listdir(PDF_FOLDER)
                    if f.endswith('.pdf') and not f.startswith('._')]

    if len(pdf_files) == 0:
        errors.append(f"⚠️ No PDF files found in {PDF_FOLDER}")
    else:
        print(f"✅ Found {len(pdf_files)} PDF files")

    return errors

if __name__ == "__main__":
    print("=" * 80)
    print("🔧 VALIDATING CONFIGURATION")
    print("=" * 80)
    print(f"\n🤖 Model: {OLLAMA_MODEL}")
    print(f"📚 PDF Folder: {PDF_FOLDER}")
    print(f"🔍 Retrieval Settings:")
    print(f"   - Chunk Size: {CHUNK_SIZE}")
    print(f"   - Top K Results: {TOP_K_RESULTS}")
    print(f"   - Fetch K Candidates: {FETCH_K}")
    print(f"   - Diversity Lambda: {LAMBDA_MULT}")
    print(f"   - Temperature: {TEMPERATURE}")

    errors = validate_config()

    if errors:
        print("\n⚠️ ISSUES FOUND:")
        for error in errors:
            print(error)
    else:
        print("\n✅ Configuration is valid")
    
    print("=" * 80)