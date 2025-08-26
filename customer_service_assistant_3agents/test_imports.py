#!/usr/bin/env python3

# Test all the imports from the notebook
try:
    import os
    print("✓ os imported successfully")
    
    import time
    print("✓ time imported successfully")
    
    from dotenv import load_dotenv
    print("✓ dotenv imported successfully")
    
    import openai
    print("✓ openai imported successfully")
    
    import uuid
    print("✓ uuid imported successfully")
    
    from docx import Document
    print("✓ docx imported successfully")
    
    from openai import OpenAI
    print("✓ OpenAI imported successfully")
    
    import chromadb
    print("✓ chromadb imported successfully")
    
    from chromadb.config import Settings
    print("✓ chromadb.config.Settings imported successfully")
    
    print("\n🎉 All imports successful! The notebook should run without import errors.")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Unexpected error: {e}") 