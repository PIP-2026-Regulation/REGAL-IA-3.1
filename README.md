# 🇪🇺 EU AI Act Compliance Advisor

Interactive compliance assessment tool for the EU AI Act, powered by Llama 3.1 and RAG (Retrieval-Augmented Generation).

![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Ollama](https://img.shields.io/badge/Ollama-llama3.1-green)
![Gradio](https://img.shields.io/badge/Gradio-4.31-orange)

## 📋 Features

- **Risk Classification**: Automatically classifies AI systems (Prohibited, High-Risk, Limited, Minimal)
- **RAG-based Analysis**: Uses the official EU AI Act PDF for accurate references
- **Interactive Interview**: Structured Q&A to gather compliance information
- **Detailed Reports**: Generates comprehensive compliance assessments with article citations
- **Web Interface**: User-friendly Gradio chat interface

## 🏗️ Project Structure

```
eu-ai-act-advisor/
├── app.py                    # Gradio web interface
├── src/
│   ├── __init__.py
│   ├── document_processor.py # PDF chunking & embeddings
│   ├── llm_client.py        # Ollama API client
│   └── legal_advisor.py     # Main business logic
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/) installed and running
- EU AI Act PDF document

### Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/eu-ai-act-advisor.git
cd eu-ai-act-advisor

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env
```

### Setup Ollama

```bash
# Install Ollama (if not already installed)
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama server
ollama serve

# Pull the model (in another terminal)
ollama pull llama3.1:8b
```

### Download Required Documents

```bash
# Download EU AI Act PDF
curl -o OJ_L_202401689_EN_TXT.pdf "https://eur-lex.europa.eu/legal-content/EN/TXT/PDF/?uri=OJ:L_202401689"
```

### Run the Application

```bash
python app.py
```

Open http://localhost:7860 in your browser.

## 📸 Screenshot

```
┌─────────────────────────────────────────────────────────────┐
│  🇪🇺 EU AI Act Compliance Advisor                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  🤖 Please describe your AI system in detail...             │
│                                                             │
│  👤 We're building a chatbot that uses GPT-4 to answer      │
│     customer support questions about our products.          │
│                                                             │
│  🤖 [Q1/15] What types of personal data does your           │
│     system process from customer interactions?              │
│                                                             │
│  ...                                                        │
│                                                             │
│  📊 FINAL COMPLIANCE ASSESSMENT                             │
│  Risk Level: LIMITED RISK                                   │
│  Applicable: Article 52 (Transparency)                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## ⚙️ Configuration

Edit `.env` file:

```env
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
AI_ACT_PDF_PATH=OJ_L_202401689_EN_TXT.pdf
PORT=7860
```

## 🔧 Git Commands

```bash
# Initialize repository
git init
git add .
git commit -m "Initial commit: EU AI Act Compliance Advisor"

# Push to GitHub
git remote add origin https://github.com/YOUR_USERNAME/eu-ai-act-advisor.git
git branch -M main
git push -u origin main
```

## 📄 License

MIT License

## ⚠️ Disclaimer

This tool provides **preliminary guidance only**. It is not a substitute for professional legal advice. Always consult qualified legal counsel for official EU AI Act compliance assessments.
