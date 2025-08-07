# Simple RAG System (with Ollama)

A simple Retrieval-Augmented Generation (RAG) system that allows you to query local LLMs with context from your local .txt files. **No API keys required!**

## Features

- Loads all .txt files from a specified folder
- Creates semantic embeddings using Sentence Transformers
- Uses FAISS for fast similarity search
- Provides context-aware responses from local LLMs via Ollama
- Option to query LLM directly without context
- Interactive command-line interface
- **Completely free** - no API costs!

## Setup

1. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Ollama:**
   - Download and install Ollama from [https://ollama.ai](https://ollama.ai)
   - Start the Ollama service
   - Pull a model (e.g., llama2):
     ```bash
     ollama pull llama2
     ```

3. **Prepare your documents:**
   - Create a folder with your .txt files
   - Each .txt file will be loaded and indexed

## Usage

### Command Line Interface

Run the interactive interface:
```bash
python rag_system.py
```

The system will:
1. Ask for the path to your .txt files folder
2. Ask for the Ollama model name (default: llama2)
3. Load and index all .txt files
4. Start an interactive session where you can ask questions

### Commands

- **Regular questions**: The system will search your documents and provide context-aware answers
- **Type `direct`**: Query the LLM directly without using your document context
- **Type `quit`**: Exit the program

### Programmatic Usage

You can also use the RAG system in your own Python code:

```python
from rag_system import SimpleRAG

# Initialize the RAG system
rag = SimpleRAG(
    folder_path="path/to/your/txt/files",
    model_name="llama2"  # or any other Ollama model
)

# Query with context
response = rag.query("What is the main topic discussed in the documents?")

# Query without context (direct to LLM)
response = rag.query("What is the capital of France?", use_context=False)

# Search for relevant documents
relevant_docs = rag.search("machine learning", top_k=5)
```

## Available Models

You can use any model available in Ollama. Popular options include:

- `llama2` - Meta's Llama 2 (default)
- `llama2:7b` - Smaller, faster version
- `llama2:13b` - Larger, more capable version
- `mistral` - Mistral AI's model
- `codellama` - Code-focused model
- `phi` - Microsoft's Phi model

To see all available models:
```bash
ollama list
```

To pull a new model:
```bash
ollama pull model_name
```

## How It Works

1. **Document Loading**: All .txt files in the specified folder are loaded
2. **Embedding Creation**: Each document is converted to a vector using Sentence Transformers
3. **Indexing**: FAISS creates a searchable index from the embeddings
4. **Query Processing**: When you ask a question:
   - The question is converted to a vector
   - Similar documents are found using semantic search
   - Relevant document content is included in the prompt to the local LLM
   - The LLM provides a response using both your documents and its general knowledge

## Requirements

- Python 3.7+
- Ollama installed and running
- Internet connection (only for initial model download)

## Dependencies

- `sentence-transformers`: For creating document embeddings
- `faiss-cpu`: For fast similarity search
- `python-dotenv`: For environment variable management
- `numpy`: For numerical operations
- `requests`: For communicating with Ollama

## Advantages of Using Ollama

- **Free**: No API costs or usage limits
- **Private**: All processing happens locally on your machine
- **Fast**: No network latency for API calls
- **Flexible**: Choose from many different models
- **Offline**: Works without internet after model download

## Tips

- **Model Selection**: Larger models (13B+) are more capable but slower. Smaller models (7B) are faster but may be less accurate
- **Document Quality**: The quality of your .txt files will directly impact the relevance of responses
- **File Size**: Very large files may be split into chunks for better performance
- **Memory Usage**: Larger models require more RAM. Make sure you have enough memory for your chosen model

## Troubleshooting

- **Ollama not running**: Make sure Ollama is installed and the service is started
- **Model not found**: Pull the model with `ollama pull model_name`
- **No documents found**: Make sure your folder path is correct and contains .txt files
- **Import errors**: Make sure all dependencies are installed with `pip install -r requirements.txt`
- **Memory issues**: Try a smaller model or close other applications

## Quick Start

1. Install Ollama: https://ollama.ai
2. Pull a model: `ollama pull llama2`
3. Install Python dependencies: `pip install -r requirements.txt`
4. Run the system: `python rag_system.py`
5. Enter your documents folder path when prompted
6. Start asking questions! 