#!/usr/bin/env python3

import os
import time
from dotenv import load_dotenv
import openai
import uuid
from docx import Document
from openai import OpenAI
import chromadb
from chromadb.config import Settings

# Load API Key
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
llm = OpenAI(api_key=openai_api_key)

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

    for chunk in chunks:
        response = llm.embeddings.create(input=[chunk], model="text-embedding-ada-002")
        embedding = response.data[0].embedding

        collection.add(documents=[chunk], embeddings=[embedding], ids=[str(uuid.uuid4())])

    return collection

# Agent1: Query Embedding Agent
def embed_query(query, llm):
    response = llm.embeddings.create(input=[query], model="text-embedding-ada-002")
    return response.data[0].embedding

# Agent2: Vector Search Agent
def retrieve_documents(embedding, collection, k=3):
    results = collection.query(query_embeddings=[embedding], n_results=k)
    docs = results.get("documents", [[]])[0]
    return "\n---\n".join(docs) if docs else ""

# Agent3: Responder Agent
def generate_response(context, user_input, llm):
    messages = [
        {"role": "system", "content": "You are an expert assistant. Use the context below to answer questions clearly and politely."},
        {"role": "user", "content": f"Context:\n{context}"},
        {"role": "user", "content": user_input}
    ]
    response = llm.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.3
    )
    return response.choices[0].message.content.strip()

# Controller Function
def run_three_agent_rag_system(doc_path):
    print("Loading knowledge base from document...")
    chunks = load_docx_chunks(doc_path)
    collection = build_knowledge_base(chunks)
    print("Customer service assistant (Three-Agent RAG system) ready! Ask product-related questions.")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Customer assistant: Thank you! Have a great day!")
            break

        # Step 1: Generate embedding for query
        embedding = embed_query(user_input, llm)

        # Step 2: Search for relevant documents
        context = retrieve_documents(embedding, collection)

        # Step 3: Generate a response using context
        response = generate_response(context, user_input, llm)
        print(f"Customer assistant: {response}")

if __name__ == "__main__":
    doc_path = "/Users/bessy/codework_c/CSTU/agenticAI/customer_service_assistant_3agents/apple_product_prices_2025.docx"
    run_three_agent_rag_system(doc_path) 