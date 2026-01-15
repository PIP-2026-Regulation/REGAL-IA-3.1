# 🇪🇺 EU AI Act Compliance Advisor (React Version)

Interactive compliance assessment tool for the EU AI Act, powered by Llama 3.1 and RAG (Retrieval-Augmented Generation).

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Ollama](https://img.shields.io/badge/Ollama-llama3.1-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110-teal)
![React](https://img.shields.io/badge/React-18.2-cyan)
![Vite](https://img.shields.io/badge/Vite-5.1-purple)

## 📋 Features

- **Risk Classification**: Automatically classifies AI systems (Prohibited, High-Risk, Limited, Minimal)
- **RAG-based Analysis**: Uses the official EU AI Act PDF for accurate references
- **Interactive Interview**: Structured Q&A to gather compliance information
- **Detailed Reports**: Generates comprehensive compliance assessments with article citations
- **Modern React UI**: Responsive, user-friendly interface with real-time updates
- **Session Management**: Support for multiple concurrent assessments
- **RESTful API**: FastAPI backend with OpenAPI documentation

## 🏗️ Project Structure

```
eu-ai-act-advisor/
├── api.py                    # FastAPI backend server
├── app.py                    # Legacy Gradio interface (optional)
├── src/
│   ├── __init__.py
│   ├── document_processor.py # PDF chunking & embeddings
│   ├── llm_client.py        # Ollama API client
│   └── legal_advisor.py     # Main business logic
├── frontend/
│   ├── src/
│   │   ├── App.jsx          # Main React component
│   │   ├── App.css          # Styling
│   │   ├── main.jsx         # React entry point
│   │   └── index.css        # Global styles
│   ├── index.html
│   ├── package.json
│   └── vite.config.js
├── requirements.txt
├── .env
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ and npm
- [Ollama](https://ollama.com/) installed and running
- EU AI Act PDF document

### Backend Setup

```bash
# Navigate to project root
cd eu-ai-act-chatbot

# Create virtual environment (if not exists)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install Python dependencies
pip install -r requirements.txt

# Ensure .env file is configured
# See Configuration section below
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install
```

### Setup Ollama

```bash
# Install Ollama (if not already installed)
# Windows: Download from https://ollama.com/download
# Mac: brew install ollama
# Linux: curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server (in a separate terminal)
ollama serve

# Pull the model (in another terminal)
ollama pull llama3.1:8b
```

### Download Required Documents

The EU AI Act PDF should already be in the project root as `OJ_L_202401689_EN_TXT.pdf`.

### Run the Application

**Terminal 1 - Backend API:**
```bash
# From project root
python api.py
# API will run on http://localhost:8000
# API docs available at http://localhost:8000/docs
```

**Terminal 2 - Frontend Dev Server:**
```bash
# From frontend directory
cd frontend
npm run dev
# Frontend will run on http://localhost:5173
```

Open http://localhost:5173 in your browser.

## ⚙️ Configuration

Edit `.env` file in the project root:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
AI_ACT_PDF_PATH=OJ_L_202401689_EN_TXT.pdf
QUESTIONS_JSON_PATH=Questions_Reference.json
PORT=8000
```

## 🔌 API Endpoints

The FastAPI backend provides the following endpoints:

- `GET /` - API information
- `GET /health` - Health check
- `POST /session/new` - Create new assessment session
- `POST /session/{session_id}/reset` - Reset a session
- `DELETE /session/{session_id}` - Delete a session
- `POST /chat` - Send message and get response

Full API documentation: http://localhost:8000/docs

## 📸 Features Showcase

### Modern Chat Interface
- Clean, responsive design with EU color scheme
- Real-time typing indicators
- Markdown support for rich formatting
- Progress tracking
- Session management

### Smart Session Handling
- Multiple concurrent assessments
- Session persistence
- Easy reset functionality

### Enhanced UX
- Smooth animations
- Keyboard shortcuts (Enter to send, Shift+Enter for new line)
- Auto-scroll to latest message
- Loading states and error handling

## 🛠️ Development

### Backend Development

```bash
# Run with auto-reload
uvicorn api:app --reload --port 8000

# Run tests (if available)
pytest
```

### Frontend Development

```bash
# Development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

## 🏭 Production Build

### Backend

```bash
# Install production dependencies
pip install -r requirements.txt

# Run with Gunicorn (Linux/Mac)
gunicorn api:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Or with Uvicorn directly
uvicorn api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Frontend

```bash
cd frontend
npm run build
# Built files will be in frontend/dist/

# Serve with a static server
npx serve -s dist -p 5173
```

## 🔄 Migration from Gradio

The legacy Gradio interface (`app.py`) is still available for backward compatibility:

```bash
python app.py
```

However, the React version offers:
- Better performance and scalability
- Modern UI/UX
- Session management
- API-first architecture
- Easier customization and extension

## 🌐 Deployment Options

### Option 1: Traditional Hosting
- Backend: Deploy FastAPI to services like Heroku, Railway, or DigitalOcean
- Frontend: Deploy to Vercel, Netlify, or Cloudflare Pages

### Option 2: Docker
```dockerfile
# Example Dockerfile for backend
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Option 3: All-in-One
Serve the built React app from FastAPI:
```python
from fastapi.staticfiles import StaticFiles
app.mount("/", StaticFiles(directory="frontend/dist", html=True), name="frontend")
```

## 🔧 Troubleshooting

### Backend Issues

**Port already in use:**
```bash
# Change port in .env or run with different port
PORT=8001 python api.py
```

**Ollama connection error:**
- Ensure Ollama is running: `ollama serve`
- Check URL in .env matches Ollama server
- Verify model is pulled: `ollama list`

### Frontend Issues

**API connection error:**
- Verify backend is running on port 8000
- Check proxy configuration in `vite.config.js`
- Clear browser cache

**Build errors:**
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📊 Architecture

```
┌─────────────┐      HTTP      ┌──────────────┐
│   React     │ ◄────────────► │   FastAPI    │
│  Frontend   │    REST API    │   Backend    │
└─────────────┘                └──────────────┘
                                       │
                                       ├─► LegalAdvisor
                                       ├─► DocumentProcessor
                                       ├─► EmbeddingService
                                       └─► OllamaClient
                                              │
                                              ▼
                                       ┌──────────────┐
                                       │    Ollama    │
                                       │  (Llama 3.1) │
                                       └──────────────┘
```

## 📄 License

MIT License

## ⚠️ Disclaimer

This tool provides **preliminary guidance only**. It is not a substitute for professional legal advice. Always consult qualified legal counsel for official EU AI Act compliance assessments.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
- Open an issue on GitHub
- Check the API documentation at `/docs`
- Review the configuration in `.env`
