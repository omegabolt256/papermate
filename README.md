# ⚡ PaperMate

> Local-first, evidence-grounded research intelligence infrastructure.

![Status](https://img.shields.io/badge/status-DEVELOPING-orange) ![Python](https://img.shields.io/badge/Python-3.10%2B-blue) ![Ollama](https://img.shields.io/badge/LLM-Ollama-black) ![SearXNG](https://img.shields.io/badge/Search-SearXNG-purple)

## 🧠 Overview

PaperMate is an experimental local-first research backend that turns search results into structured, traceable research.

`	ext
Question → Search → Evidence → Claims → Validation → Citations → Answer
`

## 📊 Verified Numbers

| Metric | Result |
|---|---:|
| Research HTTP status | **200** |
| Sources in verified run | **3** |
| Evidence records | **3** |
| Claims | **1** |
| Citations | **2** |
| References | **2** |
| Local Ollama models | **7** |
| Direct qwen2.5:3b latency | **1.16 s** |
| Citation validation | **PASSED** |

## 🏗️ Architecture

`	ext
                    ┌───────────────┐
                    │   AI / Client  │
                    └───────┬───────┘
                            │
                            ▼
                    ┌───────────────┐
                    │   PaperMate   │
                    │   Research API│
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │    SearXNG    │
                    │    Search     │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │    Evidence   │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │     Ollama    │
                    │ qwen2.5:3b    │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ Claims +       │
                    │ Validation     │
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │ Citations +    │
                    │ Provenance     │
                    └───────────────┘
`

## 🔬 Research Model

`	ext
SOURCE
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
CITATION
  ↓
ANSWER
`

The purpose is to keep factual output traceable to retrieved evidence.

## ⚙️ Current Stack

| Component | Configuration |
|---|---|
| Search | SearXNG |
| Search port | 8080 |
| Inference | Ollama |
| LLM | qwen2.5:3b |
| Ollama port | 11434 |
| Embedding candidate | ge-m3:latest |
| Default max sources | 10 |
| Citations | Required |

## 🧪 Verified Research Run

Question:

> What are randomized controlled trials used for?

The complete research pipeline returned structured sources, evidence, claims, citations, references, model metadata and provenance with citation validation passing.

## ⚡ Performance

Direct Ollama inference was measured at approximately **1.16 seconds** for a short fixed response using qwen2.5:3b.

This is a raw model measurement, not complete research latency.

## 🧠 Memory

PaperMate contains an experimental memory layer based around MemPalace. Memory contracts, storage and probing are under active development.

## 🐳 Vane Evaluation

Vane integration remains exploratory. An initial integration experiment was rolled back after introducing unnecessary configuration and performance complexity.

The current approach is open-ended:

`	ext
Official Vane Docker
        ↓
   Local Ollama
        ↓
    Benchmark
        ↓
Compare with PaperMate
`

Possible outcomes include Vane alone, PaperMate alone, a hybrid, deeper integration, or keeping both systems independent.

## 🗺️ Development

**DEVELOPING**

Current focus:

- Research quality
- Memory evaluation
- Performance benchmarking
- Local deployment
- Source and citation quality
- Vane comparison

## 📁 Repository

`	ext
PaperMate/
├── backend/
├── intelligence/
├── memory/
├── research/
├── infra/
├── tests/
├── docs/
├── README.md
├── STATUS.md
└── ROADMAP.md
`

## 🎯 Principle

> **Measure first. Integrate only when the evidence justifies the complexity.**
