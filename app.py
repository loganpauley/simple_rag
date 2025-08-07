#!/usr/bin/env python3
"""
Flask API for Simple RAG System with Ollama integration
"""

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import os
import json
import tempfile
import shutil
from werkzeug.utils import secure_filename
import requests
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Configuration
UPLOAD_FOLDER = 'temp_uploads'
ALLOWED_EXTENSIONS = {'txt'}
OLLAMA_URL = "http://localhost:11434"  # Default Ollama URL
MODEL_NAME = "llama2"  # Default model

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Global variables for document storage
documents = []
embeddings_model = None
index = None

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def load_documents_from_text(text, filename):
    """Load documents from text content"""
    # Split text into chunks (simple approach)
    chunks = re.split(r'\n\s*\n', text)  # Split on double newlines
    chunks = [chunk.strip() for chunk in chunks if chunk.strip()]
    
    # If chunks are too long, split them further
    max_chunk_size = 1000
    final_chunks = []
    for chunk in chunks:
        if len(chunk) > max_chunk_size:
            # Split on sentences
            sentences = re.split(r'[.!?]+', chunk)
            current_chunk = ""
            for sentence in sentences:
                if len(current_chunk) + len(sentence) < max_chunk_size:
                    current_chunk += sentence + ". "
                else:
                    if current_chunk:
                        final_chunks.append(current_chunk.strip())
                    current_chunk = sentence + ". "
            if current_chunk:
                final_chunks.append(current_chunk.strip())
        else:
            final_chunks.append(chunk)
    
    return [{"content": chunk, "source": filename} for chunk in final_chunks]

def create_embeddings():
    """Create embeddings for all documents"""
    global embeddings_model, index, documents
    
    if not documents:
        return False
    
    # Initialize the embedding model
    if embeddings_model is None:
        embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Create embeddings
    texts = [doc["content"] for doc in documents]
    embeddings = embeddings_model.encode(texts, show_progress_bar=True)
    
    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
    
    # Normalize embeddings for cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings.astype('float32'))
    
    return True

def search_documents(query, top_k=5):
    """Search for relevant documents"""
    global embeddings_model, index, documents
    
    if index is None or not documents:
        return []
    
    # Create query embedding
    query_embedding = embeddings_model.encode([query])
    faiss.normalize_L2(query_embedding)
    
    # Search
    scores, indices = index.search(query_embedding.astype('float32'), top_k)
    
    # Return relevant documents
    results = []
    for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
        if idx < len(documents):
            results.append({
                "content": documents[idx]["content"],
                "source": documents[idx]["source"],
                "score": float(score)
            })
    
    return results

def query_ollama(prompt):
    """Send query to Ollama"""
    try:
        response = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()["response"]
    except Exception as e:
        return f"Error querying Ollama: {str(e)}"

def create_context_prompt(query, relevant_docs):
    """Create a prompt with context for Ollama"""
    if not relevant_docs:
        return f"Question: {query}\n\nAnswer based on your general knowledge:"
    
    context = "\n\n".join([f"Document {i+1} ({doc['source']}): {doc['content']}" 
                          for i, doc in enumerate(relevant_docs)])
    
    prompt = f"""You are a helpful AI assistant. Use the following documents as context to answer the question. If the documents don't contain relevant information, you can use your general knowledge, but prioritize the document context.

Documents:
{context}

Question: {query}

Answer:"""
    
    return prompt

@app.route('/')
def index():
    """Serve the main page"""
    return render_template_string('''
    <!DOCTYPE html>
    <html>
    <head>
        <title>Simple RAG System - Backend</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            .container { max-width: 800px; margin: 0 auto; }
            .status { padding: 10px; margin: 10px 0; border-radius: 5px; }
            .success { background: #d4edda; color: #155724; }
            .error { background: #f8d7da; color: #721c24; }
            .info { background: #d1ecf1; color: #0c5460; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🤖 Simple RAG System - Backend API</h1>
            <p>This is the backend API for the RAG system. The frontend is available at:</p>
            <p><a href="https://loganpauley.github.io/simple_rag/" target="_blank">https://loganpauley.github.io/simple_rag/</a></p>
            
            <h2>API Endpoints:</h2>
            <ul>
                <li><strong>POST /upload</strong> - Upload documents</li>
                <li><strong>POST /query</strong> - Query with context</li>
                <li><strong>GET /status</strong> - Check system status</li>
            </ul>
            
            <div class="status info">
                <strong>Status:</strong> Backend API is running
            </div>
        </div>
    </body>
    </html>
    ''')

@app.route('/upload', methods=['POST'])
def upload_file():
    """Upload and process documents"""
    global documents
    
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            
            # Read file content
            content = file.read().decode('utf-8')
            
            # Process documents
            new_docs = load_documents_from_text(content, filename)
            documents.extend(new_docs)
            
            # Create embeddings
            success = create_embeddings()
            
            return jsonify({
                "message": f"Successfully processed {len(new_docs)} document chunks from {filename}",
                "total_documents": len(documents),
                "embeddings_created": success
            })
        
        return jsonify({"error": "Invalid file type"}), 400
    
    except Exception as e:
        return jsonify({"error": f"Error processing file: {str(e)}"}), 500

@app.route('/query', methods=['POST'])
def query():
    """Query the RAG system"""
    try:
        data = request.get_json()
        if not data or 'question' not in data:
            return jsonify({"error": "No question provided"}), 400
        
        question = data['question']
        
        # Search for relevant documents
        relevant_docs = search_documents(question, top_k=3)
        
        # Create prompt with context
        prompt = create_context_prompt(question, relevant_docs)
        
        # Query Ollama
        response = query_ollama(prompt)
        
        return jsonify({
            "answer": response,
            "context_used": len(relevant_docs),
            "sources": [doc["source"] for doc in relevant_docs]
        })
    
    except Exception as e:
        return jsonify({"error": f"Error processing query: {str(e)}"}), 500

@app.route('/status', methods=['GET'])
def status():
    """Get system status"""
    try:
        # Check Ollama connection
        ollama_status = "unknown"
        try:
            response = requests.get(f"{OLLAMA_URL}/api/tags", timeout=5)
            if response.status_code == 200:
                ollama_status = "connected"
            else:
                ollama_status = "error"
        except:
            ollama_status = "disconnected"
        
        return jsonify({
            "status": "running",
            "documents_loaded": len(documents),
            "embeddings_created": index is not None,
            "ollama_status": ollama_status,
            "ollama_url": OLLAMA_URL,
            "model_name": MODEL_NAME
        })
    
    except Exception as e:
        return jsonify({"error": f"Error getting status: {str(e)}"}), 500

@app.route('/clear', methods=['POST'])
def clear_documents():
    """Clear all loaded documents"""
    global documents, index
    documents = []
    index = None
    return jsonify({"message": "All documents cleared"})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 