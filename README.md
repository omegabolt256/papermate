# 📄 PaperMate

AI-powered research assistant for searching, downloading, reading, and chatting with academic papers.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Audit](https://img.shields.io/badge/Audit-100%25-brightgreen.svg)

## ✨ Features

- 🔍 **4 Search Sources** — PubMed, Europe PMC, OpenAlex, arXiv
- 📥 **Smart Downloads** — Unpaywall + arXiv + PMC open access PDFs
- 💬 **AI Chat** — Ask questions about your papers (Ollama, local)
- 📚 **Zotero Sync** — Auto-save downloads to Zotero, import your library
- 📝 **Citations** — Copy citations, save to file
- 📁 **Projects** — Organize research by topic
- 🔒 **100% Local** — No API keys required, nothing leaves your machine

## 📋 Requirements

| Software | Version | Download |
|----------|---------|----------|
| Python | 3.10+ | [python.org](https://python.org) |
| Ollama | Latest | [ollama.com](https://ollama.com) |
| Zotero (optional) | Account | [zotero.org](https://zotero.org) |

## 🚀 Installation

### Step 1: Install Python
1. Go to [python.org](https://python.org)
2. Download Python 3.10 or newer
3. During install, **check** "Add Python to PATH"
4. Click Install

### Step 2: Install Ollama
1. Go to [ollama.com](https://ollama.com)
2. Download and install
3. Open terminal and pull the AI model:
```bash
ollama pull llama3.2
Step 3: Clone PaperMate
bash
git clone https://github.com/omegabolt256/papermate.git
cd papermate
Step 4: Install Dependencies
bash
pip install -r requirements.txt
Step 5: Run
bash
python run.py
