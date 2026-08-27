# 🏗️ PaperMate Architecture

## High-Level

`	ext
AI / Client
    │
    ▼
Research API
    │
    ├── Search ───────→ SearXNG
    │
    ├── Retrieval
    │
    ├── Evidence
    │
    ├── Claims
    │
    ├── Validation
    │
    └── Citations
    │
    ▼
Structured Research Result
`

## Research Chain

`	ext
Question → Search → Retrieval → Evidence → Claims → Validation → Citations → Answer
`

## Infrastructure

`	ext
Windows Host
│
├── Ollama :11434
│   └── qwen2.5:3b
│
└── Docker
    └── SearXNG :8080
`

## Memory

Memory is intentionally separated from the research pipeline so that persistent context can evolve independently.

`	ext
User Context ─────┐
Research Context ─┼──→ Memory
System Context ───┘
`

## Design Goals

1. Local-first
2. Evidence-first
3. Provider-independent
4. Traceable
5. Replaceable
6. Measurable

## Architectural Decision

The final architecture remains open while Vane and PaperMate are compared on the same hardware.
