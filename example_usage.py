#!/usr/bin/env python3
"""
Example usage of the Simple RAG system with Ollama.
This script demonstrates how to use the RAG system programmatically.
"""

import os
from rag_system import SimpleRAG

def main():
    # Example folder path - change this to your actual folder
    folder_path = "C:/Users/el pe/rag_project/documents"
    
    # Create the documents folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        print(f"Created documents folder: {folder_path}")
        print("Please add some .txt files to this folder and run the script again.")
        return
    
    # Check if there are any .txt files
    txt_files = [f for f in os.listdir(folder_path) if f.endswith('.txt')]
    if not txt_files:
        print(f"No .txt files found in {folder_path}")
        print("Please add some .txt files to this folder and run the script again.")
        return
    
    print(f"Found {len(txt_files)} .txt files in {folder_path}")
    
    try:
        # Initialize the RAG system with Ollama
        print("Initializing RAG system with Ollama...")
        rag = SimpleRAG(folder_path, model_name="llama2")
        
        # Example queries
        queries = [
            "What are the main topics discussed in the documents?",
            "Can you summarize the key points from the documents?",
            "What is the capital of France?",  # This will use general knowledge
        ]
        
        print("\n" + "="*50)
        print("EXAMPLE QUERIES")
        print("="*50)
        
        for i, query in enumerate(queries, 1):
            print(f"\nQuery {i}: {query}")
            print("-" * 30)
            
            # Query with context
            response = rag.query(query, use_context=True)
            print(f"Response: {response}")
            
            print("\n" + "="*50)
        
        # Example of searching for relevant documents
        print("\nSEARCH EXAMPLE")
        print("="*50)
        search_query = "important information"
        relevant_docs = rag.search(search_query, top_k=3)
        
        print(f"\nSearch results for '{search_query}':")
        for doc_info in relevant_docs:
            doc = doc_info['document']
            print(f"  - {doc['file']} (score: {doc_info['score']:.3f})")
            print(f"    Content preview: {doc['content'][:100]}...")
        
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Installed Ollama from https://ollama.ai")
        print("2. Started the Ollama service")
        print("3. Pulled a model: ollama pull llama2")

if __name__ == "__main__":
    main() 