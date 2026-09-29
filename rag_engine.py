"""
RAG engine for the University of Malakand AI Assistant.

Loads the university PDFs, builds a FAISS vector index, retrieves relevant
chunks with MMR, and generates cited answers through a local Ollama model.
"""

import os
import glob
import re
from typing import List, Dict
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.llms import Ollama
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import config

class UniversityRAG:
    """
    Retrieval-augmented QA over the university's official PDF documents.

    1. Loads every PDF in the configured folder
    2. Splits pages into overlapping chunks and indexes them in FAISS
    3. Retrieves diverse chunks with MMR
    4. Generates a formatted answer with the local LLM
    5. Returns source citations (file, page, snippet)
    """
    
    def __init__(self):
        """Connect to the LLM and load the embedding model"""
        print("=" * 80)
        print("🚀 INITIALIZING RAG SYSTEM")
        print("=" * 80)
        print(f"🤖 Model: {config.OLLAMA_MODEL}")
        print(f"📚 PDF Folder: {config.PDF_FOLDER}")
        print(f"🔍 Chunk Size: {config.CHUNK_SIZE} chars")
        print(f"🎯 Top K Results: {config.TOP_K_RESULTS}")
        print(f"🎲 Diversity Lambda: {config.LAMBDA_MULT}")
        
        # Initialize LLM
        print("\n🔧 Connecting to LLM...")
        self.llm = Ollama(
            model=config.OLLAMA_MODEL,
            base_url=config.OLLAMA_HOST,
            temperature=config.TEMPERATURE,
            top_k=40,              # Consider top 40 tokens
            top_p=0.9,             # Nucleus sampling
            num_predict=2500,      # Allow long detailed answers
            repeat_penalty=1.2,    # Avoid repetition
            num_ctx=4096          # Large context window
        )
        print("✅ LLM connected!")
        
        # Initialize embeddings
        print("\n🔧 Loading embedding model...")
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={'device': 'cpu'},
            encode_kwargs={
                'normalize_embeddings': True,
                'batch_size': 32
            }
        )
        print("✅ Embeddings loaded!")
        
        self.vector_db = None
        self.qa_chain = None
        
        print("\n" + "=" * 80)
        print("✅ SYSTEM INITIALIZED!")
        print("=" * 80)
    
    def load_pdfs(self) -> List:
        """
        Load all PDFs from the configured folder.
        
        Each page keeps metadata (file name, path, doc id) for source citations.
        """
        print("\n" + "=" * 80)
        print("📚 LOADING ALL UNIVERSITY PDFs")
        print("=" * 80)
        
        pdf_files = glob.glob(os.path.join(config.PDF_FOLDER, "*.pdf"))
        pdf_files = [f for f in pdf_files if not os.path.basename(f).startswith('._')]
        
        if not pdf_files:
            print("❌ ERROR: No PDFs found!")
            return []
        
        print(f"\n✅ Found {len(pdf_files)} PDF files")
        print("📄 Loading each file...\n")
        
        all_documents = []
        successfully_loaded = 0
        
        for i, pdf_path in enumerate(pdf_files, 1):
            try:
                filename = os.path.basename(pdf_path)
                print(f"   [{i}/{len(pdf_files)}] Loading: {filename[:60]}...")
                
                loader = PyPDFLoader(pdf_path)
                documents = loader.load()
                
                # Add rich metadata
                for doc in documents:
                    doc.metadata['source_file'] = filename
                    doc.metadata['source_path'] = pdf_path
                    doc.metadata['doc_id'] = i
                
                all_documents.extend(documents)
                successfully_loaded += 1
                
            except Exception as e:
                print(f"   ⚠️ Warning: Could not load {filename}: {str(e)}")
                continue
        
        print("\n" + "=" * 80)
        print(f"✅ SUCCESSFULLY LOADED {successfully_loaded}/{len(pdf_files)} PDFs")
        print(f"📄 Total Pages: {len(all_documents)}")
        print("=" * 80)
        
        return all_documents
    
    def create_vector_db(self):
        """
        Create the FAISS vector database.
        
        Splits documents into overlapping chunks and indexes them with FAISS.
        """
        print("\n" + "=" * 80)
        print("🔨 CREATING VECTOR DATABASE")
        print("=" * 80)
        
        documents = self.load_pdfs()
        
        if not documents:
            print("❌ Cannot create database: No documents loaded!")
            return False
        
        # Chunking
        print("\n✂️ Splitting documents into chunks...")
        print(f"   Chunk size: {config.CHUNK_SIZE} characters")
        print(f"   Overlap: {config.CHUNK_OVERLAP} characters")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=config.CHUNK_SIZE,
            chunk_overlap=config.CHUNK_OVERLAP,
            separators=[
                "\n\n\n",
                "\n\n",
                "\n",
                ". ",
                ".",
                " ",
                ""
            ],
            length_function=len,
            keep_separator=True
        )
        
        chunks = text_splitter.split_documents(documents)
        
        print(f"\n✅ Created {len(chunks)} searchable chunks")
        print(f"   Average chunk size: {sum(len(c.page_content) for c in chunks) // len(chunks)} chars")
        
        # Create FAISS vector database
        print("\n💾 Building FAISS search index...")
        print("   Indexing chunks for similarity search")
        
        try:
            self.vector_db = FAISS.from_documents(
                documents=chunks,
                embedding=self.embeddings
            )
            
            # Save to disk
            self.vector_db.save_local(config.VECTOR_DB_PATH)
            
            print(f"\n✅ DATABASE CREATED SUCCESSFULLY!")
            print(f"   Saved to: {config.VECTOR_DB_PATH}")
            print(f"   Indexed {len(chunks)} chunks")
            print("\n" + "=" * 80)
            
            return True
            
        except Exception as e:
            print(f"\n❌ ERROR creating database: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def load_vector_db(self):
        """Load existing database from disk"""
        print("\n🔄 Loading existing database...")
        try:
            self.vector_db = FAISS.load_local(
                config.VECTOR_DB_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            print("✅ Database loaded successfully!")
            return True
        except Exception as e:
            print(f"⚠️ Could not load database: {e}")
            return False
    
    def setup_qa_chain(self):
        """
        Set up the retrieval QA chain.
        
        Builds the prompt template and the MMR retriever.
        """
        
        db_file = os.path.join(config.VECTOR_DB_PATH, "index.faiss")
        
        if not os.path.exists(db_file):
            print("\n⚠️ Database not found. Creating new one...")
            if not self.create_vector_db():
                return False
        else:
            if not self.load_vector_db():
                print("⚠️ Could not load existing database. Creating new one...")
                if not self.create_vector_db():
                    return False
        
        # Prompt template
        PROMPT = PromptTemplate(
            template=config.PROMPT_TEMPLATE,
            input_variables=["context", "question"]
        )
        
        print("\n🔧 Setting up question-answer chain...")
        
        # Retrieval with MMR
        retriever = self.vector_db.as_retriever(
            search_type="mmr",  # Maximum Marginal Relevance for diversity
            search_kwargs={
                "k": config.TOP_K_RESULTS,      # chunks passed to the LLM
                "fetch_k": config.FETCH_K,      # candidate pool size
                "lambda_mult": config.LAMBDA_MULT  # Balance relevance vs diversity
            }
        )
        
        # Create QA chain
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            chain_type_kwargs={"prompt": PROMPT},
            return_source_documents=True
        )
        
        print("✅ Question-Answer system ready!")
        print(f"   Retrieves {config.TOP_K_RESULTS} most relevant chunks")
        print(f"   From pool of {config.FETCH_K} candidates")
        print(f"   Using MMR for diverse sources")
        print(f"   Powered by {config.OLLAMA_MODEL}")
        
        return True
    
    def format_answer(self, raw_answer: str) -> str:
        """
        Post-process the raw LLM answer.
        
        Normalises spacing, headings, bullets and numbered lists.
        """
        
        if not raw_answer or len(raw_answer.strip()) < 10:
            return raw_answer
        
        answer = raw_answer.strip()
        
        # Clean up extra spaces
        answer = re.sub(r' +', ' ', answer)
        
        # Ensure blank lines before headings
        answer = re.sub(r'([^\n])\n(\*\*[^*]+\*\*)', r'\1\n\n\2', answer)
        
        # Ensure blank lines after headings
        answer = re.sub(r'(\*\*[^*]+\*\*)\n([^\n])', r'\1\n\n\2', answer)
        
        # Clean up bullet points
        answer = answer.replace('- ', '• ')
        answer = re.sub(r'\n•', '\n• ', answer)
        
        # Clean up numbered lists
        answer = re.sub(r'\n(\d+\.)', r'\n\1 ', answer)
        
        # Remove excessive blank lines
        while '\n\n\n' in answer:
            answer = answer.replace('\n\n\n', '\n\n')
        
        answer = answer.strip() + '\n'
        
        return answer
    
    def get_answer(self, question: str) -> Dict:
        """
        Answer a question from the indexed documents.

        Returns a dict with the formatted answer, source citations and a
        confidence label based on how many different PDFs were retrieved.
        """
        
        if not self.qa_chain:
            print("❌ QA system not initialized!")
            return {
                "answer": "System is initializing. Please wait a moment and try again.",
                "sources": [],
                "confidence": "low"
            }
        
        try:
            print("\n" + "=" * 80)
            print(f"🔍 PROCESSING QUESTION")
            print("=" * 80)
            print(f"Question: {question[:100]}...")
            print(f"\n📚 Retrieving the {config.TOP_K_RESULTS} most relevant chunks from {config.FETCH_K} candidates...")
            
            # Query the system
            result = self.qa_chain({"query": question})
            raw_answer = result.get("result", "").strip()
            
            if not raw_answer:
                print("⚠️ No answer generated!")
                return {
                    "answer": "I apologize, but I couldn't find specific information about this in the university documents. Please try rephrasing your question or contact the relevant department directly.",
                    "sources": [],
                    "confidence": "low"
                }
            
            # Format the answer
            print("🎨 Formatting answer with proper structure...")
            formatted_answer = self.format_answer(raw_answer)
            
            # Extract sources
            print("📄 Extracting sources from different PDFs...")
            sources = []
            source_files = set()
            
            if "source_documents" in result:
                for doc in result["source_documents"]:
                    source_file = doc.metadata.get('source_file', 'Unknown')
                    if source_file == 'Unknown':
                        source_file = os.path.basename(doc.metadata.get('source', 'Unknown'))
                    
                    page = doc.metadata.get('page', 'Unknown')
                    
                    # Get preview snippet
                    snippet = doc.page_content[:200].strip()
                    snippet = snippet.replace('\n', ' ')
                    snippet = re.sub(r'\s+', ' ', snippet)
                    
                    if source_file not in source_files or len(sources) < 8:
                        sources.append({
                            "file": source_file,
                            "page": page,
                            "snippet": snippet + "..."
                        })
                        source_files.add(source_file)
            
            # Limit to top 8 sources
            sources = sources[:8]
            num_pdfs = len(source_files)
            
            print("\n✅ ANSWER GENERATED!")
            print(f"   Sources: {num_pdfs} different PDF{'s' if num_pdfs != 1 else ''}")
            print(f"   Length: {len(formatted_answer)} characters")
            print(f"   Confidence: {'HIGH' if num_pdfs >= 4 else 'MEDIUM' if num_pdfs >= 2 else 'LOW'}")
            print("=" * 80)
            
            return {
                "answer": formatted_answer,
                "sources": sources,
                "confidence": "high" if num_pdfs >= 4 else "medium" if num_pdfs >= 2 else "low",
                "num_pdfs_searched": num_pdfs
            }
            
        except Exception as e:
            print(f"\n❌ ERROR generating answer: {e}")
            import traceback
            traceback.print_exc()
            
            return {
                "answer": "I apologize, but I encountered an error while processing your question. Please try again or contact support if the problem persists.",
                "sources": [],
                "confidence": "error"
            }
    
    def reload_database(self):
        """Reload database when new PDFs are added"""
        print("\n" + "=" * 80)
        print("🔄 RELOADING DATABASE")
        print("=" * 80)
        
        success = self.create_vector_db() and self.setup_qa_chain()
        
        if success:
            print("\n✅ DATABASE RELOADED SUCCESSFULLY!")
        else:
            print("\n❌ DATABASE RELOAD FAILED!")
        
        print("=" * 80)
        return success


# ============================================================================
# GLOBAL INSTANCE (Singleton)
# ============================================================================

rag_system = None

def initialize_rag():
    """Initialize the global RAG system"""
    global rag_system
    
    try:
        print("\n\n")
        print("=" * 80)
        print("🎓 UNIVERSITY OF MALAKAND AI ASSISTANT")
        print("   RAG SYSTEM")
        print("=" * 80)
        
        rag_system = UniversityRAG()
        success = rag_system.setup_qa_chain()
        
        if success:
            print("\n\n")
            print("=" * 80)
            print("🎉 SUCCESS! SYSTEM IS READY")
            print("=" * 80)
            print("✅ All PDFs loaded and indexed")
            print(f"✅ {config.OLLAMA_MODEL} model connected")
            print("✅ Vector database ready")
            print("✅ Question-Answer system active")
            print("✅ Answer formatting enabled")
            print("✅ Multi-source citation ready")
            print("=" * 80)
            print("\n\n")
        else:
            print("\n❌ INITIALIZATION FAILED!")
        
        return success
        
    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def get_rag_system():
    """Get the global RAG system instance"""
    return rag_system


# ============================================================================
# TESTING
# ============================================================================

if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("🧪 TESTING RAG ENGINE")
    print("=" * 80)
    
    if initialize_rag():
        print("\n✅ Initialization successful! Testing...\n")
        
        test_question = "What are the examination regulations?"
        print(f"Question: {test_question}")
        print("-" * 80)
        
        result = rag_system.get_answer(test_question)
        
        print("\n📝 ANSWER:")
        print(result["answer"])
        
        print("\n📚 SOURCES:")
        for i, source in enumerate(result["sources"], 1):
            print(f"   {i}. {source['file']} (Page {source['page']})")
        
        print("\n" + "=" * 80)
        print("✅ TEST COMPLETE!")
        print("=" * 80)
    else:
        print("\n❌ Initialization failed!")