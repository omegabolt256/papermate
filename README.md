# 📄 PaperMate

AI-powered research assistant for medical and academic research.

## Features

- 🔍 **Multi-source search** — PubMed, Semantic Scholar, arXiv
- 📥 **One-click downloads** — Get PDFs instantly
- 💬 **Smart chat** — AI answers from your papers + searches internet if needed
- 📚 **Zotero sync** — Auto-import your Zotero library
- 📂 **Watch folder** — Drop PDFs to auto-import
- ✅ **Systematic review** — Screen, synthesize, PRISMA tracking
- 📊 **Evidence extraction** — Structured data from papers
- 📝 **Export** — BibTeX, CSV, RIS, reports
- 🔒 **100% local** — Uses Ollama, nothing leaves your machine

## Quick Start

```bash
# Install Ollama
# https://ollama.com
ollama pull llama3.2

# Clone and run
git clone https://github.com/omegabolt256/papermate.git
cd papermate
pip install -r requirements.txt
python run.py

Usage

[N] New Project
[1] Search & Add Papers
[2] My Papers
[3] Chat with Project (AI + Internet)
[4] Deep Research
[5] Export & Reports
[6] Zotero Sync
[7] Systematic Review
[S] Saved Searches
[W] Watch Folder

Tech Stack
Python 3.10+

Ollama + Llama 3.2 (local AI)

PyMuPDF (PDF processing)

SQLite (storage)

Zotero API (reference sync)

License
MIT

