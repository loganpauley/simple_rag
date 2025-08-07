#!/usr/bin/env python3
"""
Setup script for the Simple RAG system.
This script helps you install dependencies and set up Ollama.
"""

import subprocess
import sys
import os
import requests
import time

def run_command(command, description):
    """Run a command and handle errors."""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        print(f"Command output: {e.stdout}")
        print(f"Error output: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible."""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 7):
        print("✗ Python 3.7 or higher is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True

def install_python_dependencies():
    """Install Python dependencies."""
    return run_command("pip install -r requirements.txt", "Installing Python dependencies")

def check_ollama_installation():
    """Check if Ollama is installed and running."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✓ Ollama is running")
            return True
        else:
            print("✗ Ollama is not responding properly")
            return False
    except requests.exceptions.RequestException:
        print("✗ Ollama is not running or not installed")
        return False

def install_ollama():
    """Provide instructions for installing Ollama."""
    print("\n" + "="*50)
    print("OLLAMA INSTALLATION REQUIRED")
    print("="*50)
    print("Ollama is not installed or not running.")
    print("\nTo install Ollama:")
    print("1. Visit https://ollama.ai")
    print("2. Download and install Ollama for your operating system")
    print("3. Start Ollama")
    print("4. Run this setup script again")
    print("\nAfter installation, you can pull a model with:")
    print("ollama pull llama2")
    return False

def pull_default_model():
    """Pull the default Llama2 model."""
    print("\nPulling Llama2 model (this may take a few minutes)...")
    return run_command("ollama pull llama2", "Pulling Llama2 model")

def test_rag_system():
    """Test the RAG system with sample documents."""
    print("\n" + "="*50)
    print("TESTING RAG SYSTEM")
    print("="*50)
    
    # Check if documents folder exists
    documents_path = os.path.join(os.getcwd(), "documents")
    if not os.path.exists(documents_path):
        print("✗ Documents folder not found")
        return False
    
    # Check if there are .txt files
    txt_files = [f for f in os.listdir(documents_path) if f.endswith('.txt')]
    if not txt_files:
        print("✗ No .txt files found in documents folder")
        return False
    
    print(f"✓ Found {len(txt_files)} .txt files")
    
    # Try to import and test the RAG system
    try:
        from rag_system import SimpleRAG
        print("✓ RAG system imports successfully")
        
        # Test with a simple query
        rag = SimpleRAG(documents_path, model_name="llama2")
        print("✓ RAG system initialized successfully")
        
        # Test search functionality
        results = rag.search("test", top_k=1)
        print(f"✓ Search functionality working ({len(results)} results)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing RAG system: {e}")
        return False

def main():
    """Main setup function."""
    print("Simple RAG System Setup")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install Python dependencies
    if not install_python_dependencies():
        print("\nFailed to install Python dependencies. Please check your pip installation.")
        return
    
    # Check Ollama
    if not check_ollama_installation():
        install_ollama()
        return
    
    # Pull default model
    if not pull_default_model():
        print("\nFailed to pull Llama2 model. You can try manually:")
        print("ollama pull llama2")
        return
    
    # Test the system
    if test_rag_system():
        print("\n" + "="*50)
        print("SETUP COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("You can now run the RAG system with:")
        print("python rag_system.py")
        print("\nOr test it with:")
        print("python example_usage.py")
    else:
        print("\nSetup completed with some issues. Please check the errors above.")

if __name__ == "__main__":
    main() 