# âš¡ PaperMate

> **Local-first research intelligence infrastructure for evidence-grounded AI.**

[![Status](https://img.shields.io/badge/status-DEVELOPING-orange?style=for-the-badge)](STATUS.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black?style=for-the-badge)](https://ollama.com/)
[![SearXNG](https://img.shields.io/badge/Search-SearXNG-purple?style=for-the-badge)](https://docs.searxng.org/)

PaperMate is an experimental **research backend** built around a simple idea:

> **Research should be traceable, not merely generated.**

Instead of treating web search as a prompt for an unconstrained answer, PaperMate separates research into explicit stages and preserves the relationships between **sources, evidence, claims, citations, and provenance**.

---

## ðŸ“Œ At a Glance

| Metric | Verified value |
|---|---:|
| Research API | `POST /research` |
| Successful research test | **HTTP 200** |
| Sources in verified run | **3** |
| Evidence records | **3** |
| Claims | **1** |
| Citations | **2** |
| References | **2** |
| Citation validation | **PASSED** |
| Local Ollama models observed | **7** |
| Direct `qwen2.5:3b` baseline | **1.16 s** |
| Search backend | SearXNG |
| Inference backend | Ollama |

> The numbers above are development measurements, not production benchmarks.

---

## ðŸ§¬ Research Pipeline

![PaperMate research pipeline](docs/assets/pipeline.svg)

The core flow is:

```text
Question
   â†“
Search
   â†“
Retrieval
   â†“
Evidence
   â†“
Claims
   â†“
Validation
   â†“
Citations
   â†“
Structured answer
```

### Evidence chain

```text
SOURCE
  â†“
EVIDENCE
  â†“
CLAIM
  â†“
CITATION
  â†“
ANSWER
```

This structure is the central architectural idea behind PaperMate. The answer is not the only artifact produced by research; the intermediate provenance is part of the output.

---

## ðŸ” What PaperMate Currently Provides

### Research

PaperMate can perform a research request against retrieved web material and return a structured research object.

### Evidence

Evidence is kept as a first-class object with an association to the source that produced it.

### Claims

Claims are represented separately from the final answer and retain the evidence IDs used to support them.

### Citation validation

The research pipeline validates the relationship between generated claims and retrieved evidence before returning a successful research result.

### Provenance

Research responses retain execution metadata describing the pipeline and model run used to produce the result.

### Local inference

Ollama is used as the local inference layer, keeping the core research path compatible with a local-first deployment.

### Memory

The repository also contains an experimental memory layer centered around MemPalace. This part of the system is still under development.

---

## âš™ï¸ Current Stack

| Layer | Current implementation |
|---|---|
| Research API | Python backend |
| Search | SearXNG |
| LLM inference | Ollama |
| Tested LLM | `qwen2.5:3b` |
| Embedding candidate | `bge-m3:latest` |
| Memory | MemPalace prototype |
| Storage | Local project/storage layers |
| Tests | Python test suite |

### Local endpoints

```text
Ollama   â†’ http://127.0.0.1:11434
SearXNG  â†’ local Docker service / port 8080
Research â†’ POST /research
```

---

## ðŸ§ª Verified Research Run

The following request has been exercised successfully:

> **What are randomized controlled trials used for?**

The verified output contained:

- **3** sources
- **3** evidence records
- **1** claim
- **2** citations
- **2** references
- citation validation: **passed**

The reported execution pipeline was:

```text
searxng
   â†“
evidence
   â†“
ollama
   â†“
claim_validation
   â†“
citation_rendering
```

This is the current end-to-end proof that the main research path works as intended.

---

## âš¡ Local Model Baseline

A direct HTTP request to Ollama using `qwen2.5:3b` was measured at approximately:

# **1.16 seconds**

That measurement is intentionally labelled as a **raw inference baseline**.

It does **not** represent full research latency. A real research operation also includes source discovery, retrieval, evidence processing, validation, and response generation.

![Benchmark overview](docs/assets/benchmark.svg)

---

## ðŸ§  Model Inventory

The local Ollama installation observed during development contained **7 models**:

| # | Model | Role observed |
|---:|---|---|
| 1 | `qwen2.5:3b` | General local LLM / verified research model |
| 2 | `sage-browser-vl:latest` | Local multimodal model |
| 3 | `qwen3-vl:2b` | Local multimodal model |
| 4 | `bge-m3:latest` | Embedding candidate |
| 5 | `gemma3:1b-it-qat` | General local model |
| 6 | `qwen3:1.7b` | Lightweight local model |
| 7 | `llama3.2:latest` | General local model |

Model selection remains an implementation decision rather than a permanent commitment.

---

## ðŸ§± System Architecture

PaperMate is split into several logical boundaries:

```text
                        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                        â”‚   Application    â”‚
                        â”‚  Vane / Clients  â”‚
                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                 â”‚
                                 â–¼
                        â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                        â”‚   Intelligence   â”‚
                        â”‚     Gateway      â”‚
                        â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                                 â”‚
              â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
              â”‚                  â”‚                  â”‚
              â–¼                  â–¼                  â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚  Research  â”‚     â”‚   Memory   â”‚     â”‚ Providers  â”‚
       â”‚  Pipeline  â”‚     â”‚ MemPalace  â”‚     â”‚   Ollama   â”‚
       â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜     â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜
             â”‚                                      â”‚
             â–¼                                      â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”                       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚  SearXNG   â”‚                       â”‚ Local LLMs â”‚
       â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜                       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
             â”‚
             â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚  Evidence  â”‚
       â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜
             â”‚
             â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚   Claims   â”‚
       â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜
             â”‚
             â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚ Validation â”‚
       â””â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”˜
             â”‚
             â–¼
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â”‚ Citations  â”‚
       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

Each layer is intended to be replaceable without forcing the entire system to change with it.

---

## ðŸ”Œ API Contract

### `POST /research`

Example request:

```json
{
  "question": "What are randomized controlled trials used for?",
  "max_sources": 3,
  "require_citations": true
}
```

The response contains structured fields for:

```text
answer
sources[]
evidence[]
claims[]
citations[]
references[]
model_runs[]
provenance
```

See [API.md](API.md) for the detailed contract.

---

## ðŸ›¡ï¸ Why the Evidence Layer Exists

A conventional research assistant can collapse the entire process into:

```text
Search â†’ Prompt â†’ Answer
```

PaperMate instead aims for:

```text
Search
  â†“
Retrieved material
  â†“
Evidence extraction
  â†“
Claim construction
  â†“
Claim/evidence validation
  â†“
Citation rendering
  â†“
Answer
```

That extra structure makes the research process inspectable and gives downstream applications more than just a string of generated text.

---

## ðŸ§  Memory Layer

PaperMate includes an experimental memory subsystem using MemPalace-related components.

Current work includes:

- memory contracts
- storage
- retrieval experiments
- gateway integration
- memory probing

Memory is deliberately separated from the research pipeline so that persistent context can evolve independently of search and synthesis.

---

## ðŸ³ Vane Evaluation

Vane integration is currently **experimental**.

A previous attempt to deeply modify Vane's native research path introduced unnecessary configuration and performance complexity, so that work was rolled back.

The current plan is intentionally open-ended:

```text
Official Vane Docker
          â†“
     Local Ollama
          â†“
      Benchmark
          â†“
 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”
 â”‚                 â”‚
 â–¼                 â–¼
Vane           PaperMate
 â”‚                 â”‚
 â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”˜
          â–¼
   System comparison
```

Possible long-term outcomes include:

- Vane alone
- PaperMate alone
- Vane + PaperMate
- a hybrid research architecture
- independent systems

No outcome is assumed in advance.

See [docs/VANE_INTEGRATION.md](docs/VANE_INTEGRATION.md).

---

## ðŸ“ˆ What Will Be Measured Next

The next benchmark set will compare complete systems on the same hardware.

| Metric | Direction |
|---|---|
| Answer quality | Higher is better |
| Research depth | Higher is better |
| Evidence grounding | Higher is better |
| Citation accuracy | Higher is better |
| Time to first token | Lower is better |
| Total latency | Lower is better |
| Search latency | Lower is better |
| Model latency | Lower is better |
| CPU usage | Lower is better |
| RAM usage | Lower is better |
| GPU usage | Lower is better |
| VRAM usage | Lower is better |
| Failure rate | Lower is better |

No future performance number will be presented as a measured benchmark until it has actually been tested.

---

## ðŸ“ Repository Layout

```text
PaperMate/
â”‚
â”œâ”€â”€ backend/          API and backend services
â”œâ”€â”€ intelligence/     Intelligence contracts and providers
â”œâ”€â”€ memory/           Memory contracts and MemPalace
â”œâ”€â”€ research/         Research/search logic
â”œâ”€â”€ infra/            Infrastructure configuration
â”œâ”€â”€ tests/            Automated tests
â”œâ”€â”€ docs/             Engineering documentation
â”‚   â””â”€â”€ assets/       README diagrams
â”œâ”€â”€ data/             Local runtime data (ignored)
â”‚
â”œâ”€â”€ README.md
â”œâ”€â”€ STATUS.md
â”œâ”€â”€ ROADMAP.md
â”œâ”€â”€ ARCHITECTURE.md
â””â”€â”€ BENCHMARKS.md
```

---

## ðŸš§ Development Status

### **ðŸŸ  DEVELOPING**

PaperMate is an active engineering project rather than a finished product.

The project is currently focused on:

1. Research quality
2. Evidence and citation reliability
3. Memory evaluation
4. Local deployment
5. Reproducible benchmarking
6. Comparison against official Vane deployment

The architecture may change as experiments produce new evidence.

---

## ðŸ—ºï¸ Documentation

- [Project status](STATUS.md)
- [Roadmap](ROADMAP.md)
- [Architecture](ARCHITECTURE.md)
- [API](API.md)
- [Benchmarks](BENCHMARKS.md)
- [Vane integration](docs/VANE_INTEGRATION.md)
- [Sage lessons](docs/SAGE_LESSONS.md)

---

## ðŸŽ¯ Engineering Principle

> **Measure first. Integrate only when the evidence justifies the complexity.**