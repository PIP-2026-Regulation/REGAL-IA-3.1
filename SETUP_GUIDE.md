# Quick Setup Guide - EU AI Act Compliance Advisor (React)

## 🚀 First Time Setup

### Step 1: Install Prerequisites

1. **Python 3.10+**
   - Download from https://www.python.org/downloads/
   - Verify: `python --version`

2. **Node.js 18+**
   - Download from https://nodejs.org/
   - Verify: `node --version` and `npm --version`

3. **Ollama**
   - Windows: Download from https://ollama.com/download
   - Mac: `brew install ollama`
   - Linux: `curl -fsSL https://ollama.com/install.sh | sh`
   - Verify: `ollama --version`

### Step 2: Setup Ollama

```bash
# Start Ollama server (keep this terminal open)
ollama serve

# In a new terminal, pull the model
ollama pull llama3.1:8b
```

### Step 3: Setup Backend

```bash
# Navigate to project directory
cd eu-ai-act-chatbot

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Verify .env file exists and is configured
# Should contain:
# OLLAMA_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.1:8b
# AI_ACT_PDF_PATH=OJ_L_202401689_EN_TXT.pdf
# QUESTIONS_JSON_PATH=Questions_Reference.json
# PORT=8000
```

### Step 4: Setup Frontend

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install
```

## ▶️ Running the Application

### Option 1: Using Startup Scripts (Recommended)

**Windows:**
```bash
start.bat
```

**Mac/Linux:**
```bash
chmod +x start.sh
./start.sh
```

### Option 2: Manual Start

**Terminal 1 - Backend:**
```bash
# From project root, with venv activated
python api.py
```

**Terminal 2 - Frontend:**
```bash
# From frontend directory
npm run dev
```

### Option 3: Individual Components

**Just Backend API:**
```bash
python api.py
# Access API docs at http://localhost:8000/docs
```

**Just Frontend (with backend running):**
```bash
cd frontend
npm run dev
# Access UI at http://localhost:5173
```

**Legacy Gradio Interface:**
```bash
python app.py
# Access at http://localhost:7860
```

## 🌐 Access Points

Once running, you can access:

- **Main Application (React UI)**: http://localhost:5173
- **API Documentation**: http://localhost:8000/docs
- **API Health Check**: http://localhost:8000/health
- **Backend Root**: http://localhost:8000

## ✅ Verify Installation

### Check Backend

```bash
# Should return health status
curl http://localhost:8000/health
```

### Check Frontend

Open http://localhost:5173 in your browser. You should see the EU AI Act Compliance Advisor interface.

### Check Ollama

```bash
# List installed models
ollama list

# Should show llama3.1:8b
```

## 🔧 Common Issues

### Backend won't start

**Issue**: `ModuleNotFoundError`
- **Solution**: Ensure virtual environment is activated and dependencies are installed
  ```bash
  pip install -r requirements.txt
  ```

**Issue**: `Connection to Ollama failed`
- **Solution**: Ensure Ollama is running
  ```bash
  ollama serve
  ```

**Issue**: `Port 8000 already in use`
- **Solution**: Change port in `.env` file or kill process using port 8000

### Frontend won't start

**Issue**: `npm: command not found`
- **Solution**: Install Node.js from https://nodejs.org/

**Issue**: `Module not found`
- **Solution**: Install dependencies
  ```bash
  cd frontend
  npm install
  ```

**Issue**: `Cannot connect to API`
- **Solution**: Ensure backend is running on port 8000

### Ollama issues

**Issue**: Model not found
- **Solution**: Pull the model
  ```bash
  ollama pull llama3.1:8b
  ```

**Issue**: Slow responses
- **Solution**: The model is computationally intensive. Consider:
  - Using a smaller model (llama3.1:7b)
  - Running on a machine with better specs
  - Adjusting temperature and max_tokens in the code

## 📝 Environment Variables

Edit `.env` file to configure:

```env
# Ollama Configuration
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Document Paths
AI_ACT_PDF_PATH=OJ_L_202401689_EN_TXT.pdf
QUESTIONS_JSON_PATH=Questions_Reference.json

# Server Configuration
PORT=8000
```

## 🔄 Updates and Maintenance

### Update Python Dependencies

```bash
pip install -r requirements.txt --upgrade
```

### Update Node Dependencies

```bash
cd frontend
npm update
```

### Update Ollama Model

```bash
ollama pull llama3.1:8b
```

## 📚 Next Steps

1. Read the full documentation in `README_REACT.md`
2. Explore the API at http://localhost:8000/docs
3. Try the chatbot at http://localhost:5173
4. Customize the UI in `frontend/src/App.jsx` and `frontend/src/App.css`
5. Extend the API in `api.py`

## 💡 Tips

- Keep Ollama running in a separate terminal
- Use the `/health` endpoint to verify backend is running
- Check browser console (F12) for frontend errors
- Check terminal output for backend errors
- Use `reset` command in chat to start a new assessment
- Session IDs are automatically managed - no need to track them manually

## 🆘 Getting Help

If you encounter issues:

1. Check this guide's Common Issues section
2. Review the terminal output for error messages
3. Check the browser console for frontend errors
4. Verify all prerequisites are installed
5. Ensure all services (Ollama, backend, frontend) are running
6. Check the API documentation at `/docs`

## 🎯 Quick Test

To verify everything works:

1. Start Ollama: `ollama serve`
2. Start backend: `python api.py`
3. Start frontend: `cd frontend && npm run dev`
4. Open http://localhost:5173
5. Type a test message: "I want to build a chatbot"
6. You should receive a response asking for more details

Success! You're ready to use the EU AI Act Compliance Advisor.
