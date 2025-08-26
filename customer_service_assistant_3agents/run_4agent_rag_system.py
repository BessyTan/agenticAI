#!/usr/bin/env python3

import os
import time
import uuid
from docx import Document
import chromadb
from chromadb.config import Settings

print("🚀 Starting 4-Agent RAG System...")
print("Installing required packages if needed...")

try:
    from sentence_transformers import SentenceTransformer
    print("✓ sentence-transformers already installed")
except ImportError:
    print("Installing sentence-transformers...")
    import subprocess
    subprocess.check_call(["pip", "install", "sentence-transformers"])
    from sentence_transformers import SentenceTransformer
    print("✓ sentence-transformers installed successfully")

# Load local embedding model
print("Loading local embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("✓ Embedding model loaded successfully!")
print(f"Model: {embedding_model.get_sentence_embedding_dimension()} dimensions")

# Agent 1: Document Loader Agent
def load_docx_chunks(doc_path):
    """Load and parse Word document into chunks with category information"""
    print(f"Loading document: {doc_path}")
    doc = Document(doc_path)
    chunks = []
    current_category = ""

    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            current_category = para.text.strip()
        elif para.text.strip():
            full_text = f"{current_category}: {para.text.strip()}" if current_category else para.text.strip()
            chunks.append(full_text)
    
    print(f"✓ Loaded {len(chunks)} text chunks from document")
    return chunks

# Agent 1: Query Embedding Agent
def embed_query(query):
    """Generate embeddings for user queries using local model"""
    return embedding_model.encode(query).tolist()

# Build Knowledge Base with ChromaDB
def build_knowledge_base(chunks, collection_name="chat_memory_4agents"):
    """Create and populate ChromaDB collection with document embeddings"""
    print(f"Building knowledge base with collection: {collection_name}")
    
    client = chromadb.PersistentClient(
        path = "/Users/bessy/codework_c/CSTU/agenticAI/customer_service_assistant_3agents",
        settings = Settings(anonymized_telemetry=False))
    
    # Get or create collection
    try:
        collection = client.get_collection(name=collection_name)
        print(f"✓ Using existing collection: {collection_name}")
    except:
        collection = client.create_collection(name=collection_name)
        print(f"✓ Created new collection: {collection_name}")
    
    # Check if collection already has documents
    count = collection.count()
    if count > 0:
        print(f"✓ Collection already contains {count} documents")
        return collection
    
    print(f"Creating embeddings for {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        # Use local embedding model
        embedding = embedding_model.encode(chunk).tolist()
        collection.add(documents=[chunk], embeddings=[embedding], ids=[str(uuid.uuid4())])
        
        if (i + 1) % 5 == 0:
            print(f"  Processed {i + 1}/{len(chunks)} chunks...")

    print("✓ Knowledge base built successfully!")
    return collection

# Agent 2a: Query Processing Agent
def process_query(query):
    """Process and enhance user queries for better retrieval"""
    print(f"\n🔍 Processing query: '{query}'")
    
    # Clean and normalize the query
    processed_query = query.strip().lower()
    
    # Extract key terms for better search
    key_terms = []
    if "price" in processed_query or "cost" in processed_query:
        key_terms.append("pricing")
    if "iphone" in processed_query:
        key_terms.append("iphone")
    if "mac" in processed_query:
        key_terms.append("mac")
    if "watch" in processed_query:
        key_terms.append("watch")
    if "ipad" in processed_query:
        key_terms.append("ipad")
    if "airpods" in processed_query:
        key_terms.append("airpods")
    
    # Create enhanced query
    enhanced_query = query
    if key_terms:
        enhanced_query = f"{query} {' '.join(key_terms)}"
    
    print(f"✓ Query enhanced: '{query}' → '{enhanced_query}'")
    return enhanced_query

# Agent 2b: Document Retrieval Agent
def retrieve_documents(embedding, collection, k=3):
    """Retrieve relevant documents based on query embedding"""
    print(f"🔍 Searching for {k} most relevant documents...")
    
    try:
        # Perform vector similarity search
        results = collection.query(query_embeddings=[embedding], n_results=k)
        docs = results.get("documents", [[]])[0]
        
        # Process and rank results
        if docs:
            print(f"✓ Found {len(docs)} relevant documents")
            # Join documents with separators for better readability
            formatted_docs = "\n---\n".join(docs)
            return formatted_docs
        else:
            print("⚠ No relevant documents found")
            return ""
            
    except Exception as e:
        print(f"❌ Error retrieving documents: {e}")
        return ""

# Agent 3: Response Generation Agent
def generate_response(context, user_input):
    """Generate human-like responses based on retrieved context"""
    print(f"\n🤖 Generating response for: '{user_input}'")
    
    if not context:
        return "I'm sorry, I couldn't find relevant information to answer your question. Could you please rephrase or ask about a different Apple product?"
    
    # Create a comprehensive response based on context
    response_parts = []
    
    # Extract key information from context
    context_lines = context.split("\n---\n")
    
    for line in context_lines:
        if line.strip():
            # Clean up the line and add to response
            clean_line = line.strip()
            if clean_line and len(clean_line) > 10:  # Only add substantial content
                response_parts.append(clean_line)
    
    if response_parts:
        # Combine the most relevant information
        response = "\n\n".join(response_parts[:2])  # Limit to top 2 most relevant pieces
        
        # Add a helpful conclusion
        response += "\n\nThis information should help answer your question about Apple products. Is there anything specific you'd like to know more about?"
        
        return response
    else:
        return "I found some information but it wasn't specific enough to answer your question. Could you please ask about a specific Apple product or feature?"

# Controller Function - Orchestrates all 4 agents
def run_four_agent_rag_system(doc_path):
    """Main function that coordinates all 4 agents"""
    print("🚀 Starting 4-Agent RAG System...")
    print("=" * 50)
    
    # Agent 1: Load documents and prepare embeddings
    print("\n📚 Agent 1: Document Loader & Embedding Agent")
    chunks = load_docx_chunks(doc_path)
    
    # Build knowledge base
    print("\n🗄️ Building Knowledge Base...")
    collection = build_knowledge_base(chunks)
    
    print("\n✅ Customer service assistant (4-Agent RAG system) ready!")
    print("Ask product-related questions about Apple products.")
    print("Type 'exit', 'quit', or 'bye' to end the session.")
    print("=" * 50)

    while True:
        try:
            user_input = input("\n👤 You: ").strip()
            
            if user_input.lower() in ["exit", "quit", "bye"]:
                print("\n🤖 Customer Assistant: Thank you! Have a great day! 👋")
                break

            if not user_input:
                print("Please enter a question about Apple products.")
                continue

            # Agent 2a: Process and enhance the query
            enhanced_query = process_query(user_input)
            
            # Agent 1: Generate embedding for enhanced query
            embedding = embed_query(enhanced_query)

            # Agent 2b: Search for relevant documents
            context = retrieve_documents(embedding, collection)

            # Agent 3: Generate response using context
            response = generate_response(context, user_input)
            
            print(f"\n🤖 Customer Assistant: {response}")
            
        except KeyboardInterrupt:
            print("\n\n🤖 Customer Assistant: Session interrupted. Goodbye! 👋")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            print("Please try asking your question again.")

if __name__ == "__main__":
    # Set the document path
    doc_path = "/Users/bessy/codework_c/CSTU/agenticAI/customer_service_assistant_3agents/apple_product_prices_2025.docx"
    print(f"📄 Document path: {doc_path}")
    print(f"📁 File exists: {os.path.exists(doc_path)}")
    
    # Run the 4-Agent RAG System
    print("\n🚀 Launching 4-Agent RAG System...")
    run_four_agent_rag_system(doc_path) 