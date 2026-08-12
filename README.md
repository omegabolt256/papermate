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
🎯 Usage
text
  PROJECTS

  [N] New Project
  [D] Delete Project
  [Q] Quit
Open a project and you'll see:

text
  [1] Search & Add Papers
  [2] My Papers (view, open PDFs, cite)
  [3] Chat with AI
  [4] Zotero Sync
  [B] Back
Search Papers
Type any topic: leukemia liposomes
Results from 4 sources. Add all with da or pick specific with d 3.

My Papers
O — Open PDF in your viewer

B — Open in browser (for paywalled papers)

C — Copy citation (saved to citations.txt)

Z — Save to Zotero

DL — Download all PDFs

Chat with AI
Ask anything about your papers. AI cites them as [PAPER 1], [PAPER 2]. If your papers don't have the answer, it says so.

Zotero Sync
1 — Import your Zotero library into the project

2 — Push all project papers to Zotero

🔑 Zotero Setup (Optional)
Go to zotero.org/settings/keys

Click "Create new private key"

Check: Allow library access, Allow notes access, Allow write access

Click Save Key

Copy the key and your User ID

Edit config/settings.py:

python
ZOTERO_API_KEY = "your-key-here"
ZOTERO_USER_ID = "your-user-id"
✅ Audit
Run the test suite:

bash
python audit.py
Current: 100% pass — 10/10 components functional

🛠️ Tech Stack
Python 3.10+

Ollama + Llama 3.2

PyMuPDF (PDF processing)

SQLite (storage)

Unpaywall API (free open access finder)

Zotero API (reference sync)

📁 Project Structure
text
papermate/
├── app/
│   ├── search/          # Search adapters (4 sources)
│   ├── papers/          # Downloader, Unpaywall, manager
│   ├── projects/        # Project management
│   ├── chats/           # Chat system
│   ├── models/          # Ollama provider
│   ├── database/        # SQLite models
│   └── integrations/
│       └── zotero/      # Zotero client + sync
├── config/
│   └── settings.py      # Configuration
├── run.py               # Main program
├── audit.py             # Test suite
├── requirements.txt
└── README.md
📝 License
MIT — Free to use, modify, and share.

⭐ Support
Star this repo if you find it useful!

Built with ❤️ for researchers.
