# ⚡ PaperMate

> **Local-first, evidence-grounded research infrastructure.**

![Status](https://img.shields.io/badge/status-DEVELOPING-orange)
![Inference](https://img.shields.io/badge/inference-Ollama-black)
![Search](https://img.shields.io/badge/search-SearXNG-purple)
![Architecture](https://img.shields.io/badge/architecture-local--first-blue)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue)

---

## 🧠 What is PaperMate?

PaperMate is an experimental research intelligence backend designed to turn
web search into **structured, traceable and evidence-grounded research**.

Instead of treating search results as the final answer, PaperMate separates
research into explicit stages:

```text
┌──────────────────────────────────────────────────────────┐
│                      USER QUESTION                       │
└──────────────────────────┬───────────────────────────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     SEARCH      │
                  │     SearXNG     │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    EVIDENCE     │
                  │   Extraction    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  LOCAL MODEL    │
                  │     Ollama      │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │     CLAIMS      │
                  │   Generation    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │   VALIDATION    │
                  │ Claims ↔ Source │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │    CITATIONS    │
                  │   Provenance    │
                  └────────┬────────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │ STRUCTURED ANSWER│
                  └─────────────────┘