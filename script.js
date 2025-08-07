// Global variables
let uploadedFiles = [];
let chatHistory = [];

// DOM elements
const fileInput = document.getElementById('fileInput');
const uploadSection = document.getElementById('uploadSection');
const fileInfo = document.getElementById('fileInfo');
const status = document.getElementById('status');
const chatMessages = document.getElementById('chatMessages');
const questionInput = document.getElementById('questionInput');
const sendBtn = document.getElementById('sendBtn');

// Event listeners
fileInput.addEventListener('change', handleFileSelect);
uploadSection.addEventListener('dragover', handleDragOver);
uploadSection.addEventListener('dragleave', handleDragLeave);
uploadSection.addEventListener('drop', handleDrop);
sendBtn.addEventListener('click', sendMessage);
questionInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

// File handling functions
function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    processFiles(files);
}

function handleDragOver(event) {
    event.preventDefault();
    uploadSection.classList.add('dragover');
}

function handleDragLeave(event) {
    event.preventDefault();
    uploadSection.classList.remove('dragover');
}

function handleDrop(event) {
    event.preventDefault();
    uploadSection.classList.remove('dragover');
    const files = Array.from(event.dataTransfer.files);
    processFiles(files);
}

function processFiles(files) {
    const txtFiles = files.filter(file => file.name.toLowerCase().endsWith('.txt'));
    
    if (txtFiles.length === 0) {
        showStatus('Please select .txt files only.', 'error');
        return;
    }

    uploadedFiles = txtFiles;
    updateFileInfo();
    enableChat();
    showStatus(`Successfully loaded ${txtFiles.length} file(s)!`, 'success');
    
    // Add system message
    addMessage('assistant', `📚 I've loaded ${txtFiles.length} document(s). You can now ask questions about them!`);
}

function updateFileInfo() {
    if (uploadedFiles.length === 0) {
        fileInfo.style.display = 'none';
        return;
    }

    const fileList = uploadedFiles.map(file => 
        `<div>📄 ${file.name} (${formatFileSize(file.size)})</div>`
    ).join('');

    fileInfo.innerHTML = `
        <strong>Loaded Files:</strong><br>
        ${fileList}
    `;
    fileInfo.style.display = 'block';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function enableChat() {
    questionInput.disabled = false;
    sendBtn.disabled = false;
    questionInput.focus();
}

function disableChat() {
    questionInput.disabled = true;
    sendBtn.disabled = true;
}

// Chat functions
function sendMessage() {
    const question = questionInput.value.trim();
    if (!question || uploadedFiles.length === 0) return;

    // Add user message
    addMessage('user', question);
    questionInput.value = '';

    // Add loading message
    const loadingId = addMessage('loading', '🤔 Thinking...');

    // Simulate AI response (in a real implementation, this would call your RAG system)
    setTimeout(() => {
        // Remove loading message
        removeMessage(loadingId);
        
        // Generate response based on uploaded files
        const response = generateResponse(question);
        addMessage('assistant', response);
    }, 1500 + Math.random() * 2000); // Random delay to simulate processing
}

function generateResponse(question) {
    // This is a simplified response generator
    // In a real implementation, this would use your RAG system
    
    const responses = [
        `Based on the uploaded documents, I can help you with information about "${question}". The documents contain relevant context that I can analyze.`,
        
        `I've analyzed your question: "${question}". From the uploaded files, I can provide insights and answer your query with context from the documents.`,
        
        `Regarding "${question}", I can search through the uploaded documents to find relevant information and provide you with a comprehensive answer.`,
        
        `I understand you're asking about "${question}". Let me search through the uploaded documents to find the most relevant information for you.`
    ];
    
    // Add some context about the files
    const fileNames = uploadedFiles.map(f => f.name).join(', ');
    const baseResponse = responses[Math.floor(Math.random() * responses.length)];
    
    return `${baseResponse}\n\n📁 Documents analyzed: ${fileNames}`;
}

function addMessage(type, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${type}`;
    messageDiv.textContent = content;
    
    const messageId = Date.now() + Math.random();
    messageDiv.id = `msg-${messageId}`;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    
    // Store in chat history
    chatHistory.push({ type, content, id: messageId });
    
    return messageId;
}

function removeMessage(messageId) {
    const messageElement = document.getElementById(`msg-${messageId}`);
    if (messageElement) {
        messageElement.remove();
    }
}

function showStatus(message, type) {
    status.textContent = message;
    status.className = `status ${type}`;
    status.style.display = 'block';
    
    setTimeout(() => {
        status.style.display = 'none';
    }, 5000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Check if we're on GitHub Pages
    if (window.location.hostname.includes('github.io')) {
        addMessage('assistant', '🌐 Welcome to the Simple RAG System on GitHub Pages! Upload your .txt files to get started.');
    }
}); 