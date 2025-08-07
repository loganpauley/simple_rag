#!/usr/bin/env python3
"""
Local development script for the RAG backend
"""

import os
import sys
import subprocess
import time
import requests

def check_ollama():
    """Check if Ollama is running"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running")
            return True
        else:
            print("❌ Ollama is not responding properly")
            return False
    except:
        print("❌ Ollama is not running. Please start Ollama first:")
        print("   ollama serve")
        return False

def install_dependencies():
    """Install Python dependencies"""
    print("📦 Installing dependencies...")
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def run_backend():
    """Run the Flask backend"""
    print("🚀 Starting RAG backend...")
    print("   Backend will be available at: http://localhost:5000")
    print("   Press Ctrl+C to stop")
    
    try:
        subprocess.run([sys.executable, "app.py"])
    except KeyboardInterrupt:
        print("\n🛑 Backend stopped")

def main():
    print("🤖 Simple RAG System - Backend Setup")
    print("=" * 50)
    
    # Check Ollama
    if not check_ollama():
        return
    
    # Install dependencies
    if not install_dependencies():
        return
    
    # Run backend
    run_backend()

if __name__ == "__main__":
    main() 