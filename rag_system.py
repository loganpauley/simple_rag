import os
import glob
import json
import requests
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SimpleRAG:
    def __init__(self, folder_path: str, model_name: str = "llama2", ollama_url: str = "http://localhost:11434"):
        """
        Initialize the RAG system with Ollama.
        
        Args:
            folder_path: Path to the folder containing .txt files
            model_name: Name of the Ollama model to use (default: llama2)
            ollama_url: URL of the Ollama server (default: localhost:11434)
        """
        self.folder_path = folder_path
        self.documents = []
        self.embeddings = None
        self.index = None
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.model_name = model_name
        self.ollama_url = ollama_url
        
        # Check if Ollama is running
        self.check_ollama_connection()
        
        # Load and index documents
        self.load_documents()
        self.create_index()
    
    def check_ollama_connection(self):
        """Check if Ollama is running and the model is available."""
        try:
            # Check if Ollama server is running
            response = requests.get(f"{self.ollama_url}/api/tags")
            if response.status_code != 200:
                raise Exception("Ollama server is not running")
            
            # Check if the model is available
            models = response.json().get('models', [])
            model_names = [model['name'] for model in models]
            
            if self.model_name not in model_names:
                print(f"Model '{self.model_name}' not found. Available models: {model_names}")
                print(f"Please install the model with: ollama pull {self.model_name}")
                print("Using 'llama2' as fallback...")
                self.model_name = "llama2"
                
                # Try to pull the model if it doesn't exist
                try:
                    pull_response = requests.post(f"{self.ollama_url}/api/pull", 
                                                json={"name": self.model_name})
                    if pull_response.status_code == 200:
                        print(f"Successfully pulled {self.model_name}")
                    else:
                        raise Exception(f"Failed to pull model {self.model_name}")
                except Exception as e:
                    print(f"Error pulling model: {e}")
                    print("Please install Ollama and pull a model manually:")
                    print("1. Install Ollama from https://ollama.ai")
                    print("2. Run: ollama pull llama2")
            
            print(f"Connected to Ollama server at {self.ollama_url}")
            print(f"Using model: {self.model_name}")
            
        except Exception as e:
            print(f"Error connecting to Ollama: {e}")
            print("\nTo use this RAG system:")
            print("1. Install Ollama from https://ollama.ai")
            print("2. Start Ollama")
            print("3. Pull a model: ollama pull llama2")
            print("4. Run this script again")
            raise
    
    def load_documents(self):
        """Load all .txt files from the specified folder."""
        txt_files = glob.glob(os.path.join(self.folder_path, "*.txt"))
        
        if not txt_files:
            print(f"No .txt files found in {self.folder_path}")
            return
        
        for file_path in txt_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        self.documents.append({
                            'content': content,
                            'file': os.path.basename(file_path),
                            'path': file_path
                        })
                        print(f"Loaded: {os.path.basename(file_path)}")
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
        
        print(f"Loaded {len(self.documents)} documents")
    
    def create_index(self):
        """Create FAISS index from document embeddings."""
        if not self.documents:
            print("No documents to index")
            return
        
        # Create embeddings for all documents
        texts = [doc['content'] for doc in self.documents]
        self.embeddings = self.model.encode(texts, show_progress_bar=True)
        
        # Create FAISS index
        dimension = self.embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)  # Inner product for cosine similarity
        self.index.add(self.embeddings.astype('float32'))
        
        print(f"Created index with {len(self.documents)} documents")
    
    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        """
        Search for relevant documents.
        
        Args:
            query: Search query
            top_k: Number of top results to return
            
        Returns:
            List of relevant documents with scores
        """
        if not self.index or not self.documents:
            return []
        
        # Encode query
        query_embedding = self.model.encode([query])
        
        # Search
        scores, indices = self.index.search(query_embedding.astype('float32'), top_k)
        
        results = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):
                results.append({
                    'document': self.documents[idx],
                    'score': float(score),
                    'rank': i + 1
                })
        
        return results
    
    def query_ollama(self, prompt: str) -> str:
        """Query the Ollama model."""
        try:
            response = requests.post(
                f"{self.ollama_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9,
                        "max_tokens": 1000
                    }
                },
                timeout=60
            )
            
            if response.status_code == 200:
                return response.json().get('response', 'No response received')
            else:
                return f"Error: HTTP {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"Error querying Ollama: {str(e)}"
    
    def create_context_prompt(self, query: str, relevant_docs: List[Dict[str, Any]]) -> str:
        """Create a context-aware prompt for the LLM."""
        if not relevant_docs:
            return f"Question: {query}\n\nPlease answer based on your general knowledge."
        
        context_parts = []
        for doc_info in relevant_docs:
            doc = doc_info['document']
            context_parts.append(f"From file '{doc['file']}':\n{doc['content']}\n")
        
        context = "\n".join(context_parts)
        
        prompt = f"""You are a helpful assistant with access to specific documents. Use the following context to answer the question, but you can also use your general knowledge when appropriate.

Context from documents:
{context}

Question: {query}

Please provide a comprehensive answer using the context above when relevant, but feel free to use your general knowledge when the context doesn't fully address the question or when you need to provide additional insights."""

        return prompt
    
    def query(self, question: str, use_context: bool = True, top_k: int = 3) -> str:
        """
        Query the RAG system with a question.
        
        Args:
            question: The question to ask
            use_context: Whether to use document context (set to False to query LLM directly)
            top_k: Number of relevant documents to include in context
            
        Returns:
            LLM's response
        """
        try:
            if use_context:
                # Search for relevant documents
                relevant_docs = self.search(question, top_k)
                
                # Create context-aware prompt
                prompt = self.create_context_prompt(question, relevant_docs)
                
                print(f"Found {len(relevant_docs)} relevant documents")
                for doc_info in relevant_docs:
                    print(f"  - {doc_info['document']['file']} (score: {doc_info['score']:.3f})")
            else:
                # Query LLM directly without context
                prompt = question
                print("Querying LLM directly (no document context)")
            
            # Get response from Ollama
            response = self.query_ollama(prompt)
            return response
            
        except Exception as e:
            return f"Error: {str(e)}"

def main():
    """Interactive command-line interface for the RAG system."""
    print("Simple RAG System (with Ollama)")
    print("=" * 50)
    
    # Get folder path
    folder_path = input("Enter the path to your .txt files folder: ").strip()
    
    if not os.path.exists(folder_path):
        print(f"Error: Folder '{folder_path}' does not exist")
        return
    
    # Get model name (optional)
    model_name = input("Enter Ollama model name (default: llama2): ").strip()
    if not model_name:
        model_name = "llama2"
    
    # Initialize RAG system
    try:
        rag = SimpleRAG(folder_path, model_name=model_name)
    except Exception as e:
        print(f"Error initializing RAG system: {e}")
        return
    
    print(f"\nRAG system ready! Using model: {rag.model_name}")
    print("Type 'quit' to exit, 'direct' to query LLM without context.")
    print("-" * 50)
    
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

if __name__ == "__main__":
    main() 