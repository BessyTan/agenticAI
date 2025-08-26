import os
import time
import uuid
from docx import Document
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

# Load local embedding model
print("Loading local embedding model...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
print("Embedding model loaded successfully!")

# Step1: Load and parse word document
# Agent1: Document Loader
def load_docx_chunks(doc_path):
    doc = Document(doc_path)
    chunks = []
    current_category = ""

    for para in doc.paragraphs:
        if para.style.name.startswith("Heading"):
            current_category = para.text.strip()
        elif para.text.strip():
            full_text = f"{current_category}: {para.text.strip()}" if current_category else para.text.strip()
            chunks.append(full_text)
    return chunks

# Step2: Create/Open ChromaDB and store embeddings
def build_knowledge_base(chunks, collection_name="chat_memory6"):
    client = chromadb.PersistentClient(
        path = "/Users/bessy/codework_c/CSTU/agenticAI/customer_service_assistant_3agents",
        settings = Settings(anonymized_telemetry=False))
    collection = client.get_or_create_collection(name=collection_name)

    print(f"Creating embeddings for {len(chunks)} chunks...")
    for i, chunk in enumerate(chunks):
        # Use local embedding model instead of OpenAI
        embedding = embedding_model.encode(chunk).tolist()
        collection.add(documents=[chunk], embeddings=[embedding], ids=[str(uuid.uuid4())])
        
        if (i + 1) % 5 == 0:
            print(f"Processed {i + 1}/{len(chunks)} chunks...")

    print("Knowledge base built successfully!")
    return collection

# Agent1: Query Embedding Agent
def embed_query(query):
    # Use local embedding model instead of OpenAI
    return embedding_model.encode(query).tolist()

# Agent2: Vector Search Agent (Single Agent)
def retrieve_documents(embedding, collection, k=3):
    results = collection.query(query_embeddings=[embedding], n_results=k)
    docs = results.get("documents", [[]])[0]
    return "\n---\n".join(docs) if docs else ""

# Agent3: Responder Agent (Simplified - no OpenAI needed)
def generate_response(context, user_input):
    if not context:
        return "I don't have enough information to answer that question. Please try asking about Apple products, pricing, or specifications."
    
    # Simple rule-based response system
    context_lower = context.lower()
    user_input_lower = user_input.lower()
    
    if "price" in user_input_lower or "cost" in user_input_lower:
        if "iphone" in context_lower:
            return f"Based on the information I have: {context[:200]}... For specific pricing details, please refer to the context above."
        elif "mac" in context_lower:
            return f"Based on the information I have: {context[:200]}... For specific pricing details, please refer to the context above."
        else:
            return f"Here's what I found about pricing: {context[:300]}..."
    
    elif "spec" in user_input_lower or "feature" in user_input_lower:
        return f"Here are the specifications and features I found: {context[:300]}..."
    
    elif "apple" in user_input_lower:
        return f"Here's what I know about Apple products: {context[:300]}..."
    
    else:
        return f"Based on the available information: {context[:300]}... Is there something specific about Apple products you'd like to know?"

# Controller Function
def run_three_agent_rag_system(doc_path):
    print("Loading knowledge base from document...")
    chunks = load_docx_chunks(doc_path)
    print(f"Loaded {len(chunks)} chunks from document")
    
    collection = build_knowledge_base(chunks)
    print("Customer service assistant (Three-Agent RAG system) ready! Ask product-related questions.")
    print("Type 'exit', 'quit', or 'bye' to end the session.")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Customer assistant: Thank you! Have a great day!")
            break

        # Step 1: Generate embedding for query
        print("Processing your question...")
        embedding = embed_query(user_input)

        # Step 2: Search for relevant documents (Single Agent)
        context = retrieve_documents(embedding, collection)

        # Step 3: Generate a response using context
        response = generate_response(context, user_input)
        print(f"Customer assistant: {response}")

if __name__ == "__main__":
    doc_path = "/Users/bessy/codework_c/CSTU/agenticAI/customer_service_assistant_3agents/apple_product_prices_2025.docx"
    
    if not os.path.exists(doc_path):
        print(f"Error: Document not found at {doc_path}")
        exit(1)
    
    print("Starting 3-Agent RAG Customer Service System (Local Embeddings)...")
    print("Agent 1: Document Loader")
    print("Agent 2: Vector Search Agent (Single Agent)")
    print("Agent 3: Responder Agent")
    run_three_agent_rag_system(doc_path) 