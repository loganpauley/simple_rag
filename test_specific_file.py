#!/usr/bin/env python3
"""
Test script for the RAG system with a specific .txt file.
"""

import os
import shutil
from rag_system import SimpleRAG

def main():
    # Your specific file path
    source_file = r"C:\Users\el pe\Downloads\2-sumilab-full-export.txt"
    
    # Create a temporary folder for the file
    temp_folder = os.path.join(os.getcwd(), "temp_docs")
    if not os.path.exists(temp_folder):
        os.makedirs(temp_folder)
    
    # Copy the file to our working directory
    dest_file = os.path.join(temp_folder, "2-sumilab-full-export.txt")
    try:
        shutil.copy2(source_file, dest_file)
        print(f"✓ Copied file to: {dest_file}")
    except Exception as e:
        print(f"Error copying file: {e}")
        return
    
    try:
        # Initialize the RAG system
        print("Initializing RAG system...")
        rag = SimpleRAG(temp_folder, model_name="llama2")
        
        print("\n" + "="*60)
        print("RAG SYSTEM READY!")
        print("="*60)
        print("You can now ask questions about your document.")
        print("Type 'quit' to exit, 'direct' to query LLM without context.")
        print("-" * 60)
        
        while True:
            question = input("\nYour question: ").strip()
            
            if question.lower() == 'quit':
                break
            elif question.lower() == 'direct':
                question = input("Direct question to LLM: ").strip()
                if question.lower() == 'quit':
                    break
                response = rag.query(question, use_context=False)
            else:
                response = rag.query(question, use_context=True)
            
            print(f"\nAnswer: {response}")
    
    except Exception as e:
        print(f"Error: {e}")
        print("\nMake sure you have:")
        print("1. Installed Ollama from https://ollama.ai")
        print("2. Started the Ollama service")
        print("3. Pulled a model: ollama pull llama2")
    
    finally:
        # Clean up temporary folder
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)
            print(f"\nCleaned up temporary folder: {temp_folder}")

if __name__ == "__main__":
    main() 