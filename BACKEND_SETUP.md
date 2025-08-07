# 🤖 Simple RAG System - Backend Setup

This guide will help you set up the backend API that connects your web interface to Ollama for real RAG functionality.

## 🎯 What This Does

The backend provides:
- **Document Processing**: Upload and chunk .txt files
- **Semantic Search**: Find relevant document sections using embeddings
- **Ollama Integration**: Send queries with context to your local LLM
- **REST API**: Connect your GitHub Pages frontend to the backend

## 🚀 Quick Start (Local Development)

### 1. Prerequisites

- Python 3.8+ installed
- Ollama installed and running locally
- Llama2 model pulled: `ollama pull llama2`

### 2. Start Ollama

```bash
# Start Ollama service
ollama serve

# In another terminal, pull the model
ollama pull llama2
```

### 3. Run the Backend

```bash
# Install dependencies and start backend
py run_backend.py
```

The backend will be available at: `http://localhost:5000`

### 4. Test the API

```bash
# Check status
curl http://localhost:5000/status

# Upload a document
curl -X POST -F "file=@documents/2-sumilab-full-export.txt" http://localhost:5000/upload

# Query the system
curl -X POST -H "Content-Type: application/json" \
  -d '{"question":"What is Sumilab?"}' \
  http://localhost:5000/query
```

## 🌐 Deploy to Production

### Option 1: Render (Recommended)

1. **Fork this repository** to your GitHub account

2. **Sign up for Render** at [render.com](https://render.com)

3. **Create a new Web Service**:
   - Connect your GitHub repository
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `gunicorn app:app`
   - Choose Python 3.9

4. **Configure Environment Variables**:
   - `OLLAMA_URL`: Your Ollama server URL (if using remote Ollama)
   - `MODEL_NAME`: The model to use (default: llama2)

5. **Update Frontend URL**:
   - Edit `docs/index.html`
   - Replace `BACKEND_URL` with your Render URL

### Option 2: Railway

1. **Sign up for Railway** at [railway.app](https://railway.app)

2. **Deploy from GitHub**:
   - Connect your repository
   - Railway will auto-detect Python and deploy

3. **Set environment variables** as needed

### Option 3: Heroku

1. **Create a `Procfile`**:
   ```
   web: gunicorn app:app
   ```

2. **Deploy to Heroku**:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

## 🔧 Configuration

### Environment Variables

You can configure the backend using environment variables:

```bash
# Ollama configuration
OLLAMA_URL=http://localhost:11434  # Default
MODEL_NAME=llama2                  # Default

# Flask configuration
FLASK_ENV=production
FLASK_DEBUG=0
```

### Using Remote Ollama

If you want to use a remote Ollama server:

1. **Set up Ollama on a VPS** or use a cloud service
2. **Update `OLLAMA_URL`** in your deployment
3. **Ensure the Ollama server is accessible** from your backend

## 📡 API Endpoints

### `GET /`
- **Description**: API status page
- **Response**: HTML page with API information

### `POST /upload`
- **Description**: Upload and process documents
- **Body**: Form data with `file` field
- **Response**: JSON with processing results

### `POST /query`
- **Description**: Query the RAG system
- **Body**: JSON with `question` field
- **Response**: JSON with `answer` and metadata

### `GET /status`
- **Description**: Get system status
- **Response**: JSON with system information

### `POST /clear`
- **Description**: Clear all loaded documents
- **Response**: JSON confirmation

## 🔍 How It Works

1. **Document Upload**: Files are chunked into smaller pieces for better search
2. **Embedding Creation**: Each chunk gets converted to a vector using Sentence Transformers
3. **Vector Search**: When you ask a question, it finds the most relevant document chunks
4. **Context Building**: Relevant chunks are combined into a prompt
5. **LLM Query**: The prompt is sent to Ollama with your question
6. **Response**: Ollama generates an answer based on the context

## 🛠️ Troubleshooting

### Common Issues

**Ollama Connection Failed**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if needed
ollama serve
```

**Model Not Found**
```bash
# Pull the required model
ollama pull llama2
```

**Dependencies Installation Failed**
```bash
# Try upgrading pip
py -m pip install --upgrade pip

# Install dependencies manually
py -m pip install flask flask-cors sentence-transformers faiss-cpu
```

**CORS Issues**
- The backend includes CORS headers for cross-origin requests
- If you still have issues, check your browser's developer console

### Debug Mode

To run in debug mode:

```bash
# Set environment variable
set FLASK_DEBUG=1

# Run the app
py app.py
```

## 🔒 Security Considerations

- **File Upload**: Only .txt files are allowed
- **CORS**: Configured for cross-origin requests from your GitHub Pages
- **Input Validation**: All inputs are validated and sanitized
- **Error Handling**: Comprehensive error handling prevents crashes

## 📈 Performance Tips

- **Document Chunking**: Documents are automatically chunked for optimal search
- **Embedding Caching**: Embeddings are created once and reused
- **Connection Pooling**: HTTP connections are reused for Ollama queries
- **Memory Management**: Large documents are processed in chunks

## 🎉 Next Steps

1. **Deploy the backend** to a cloud service
2. **Update your frontend** with the backend URL
3. **Test the full system** with your documents
4. **Customize the prompts** for better responses
5. **Add more features** like document management

Your RAG system will now provide real AI-powered responses based on your uploaded documents! 🚀 