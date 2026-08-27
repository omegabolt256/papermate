$ErrorActionPreference = 'Stop'

$root = (Get-Location).Path
$docs = Join-Path $root 'docs'
$assets = Join-Path $docs 'assets'
New-Item -ItemType Directory -Force $assets | Out-Null

$readme = @'
# ⚡ PaperMate

> **Local-first research intelligence infrastructure for evidence-grounded AI.**

[![Status](https://img.shields.io/badge/status-DEVELOPING-orange?style=for-the-badge)](STATUS.md)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-black?style=for-the-badge)](https://ollama.com/)
[![SearXNG](https://img.shields.io/badge/Search-SearXNG-purple?style=for-the-badge)](https://docs.searxng.org/)

PaperMate is an experimental **research backend** built around a simple idea:

> **Research should be traceable, not merely generated.**

Instead of treating web search as a prompt for an unconstrained answer, PaperMate separates research into explicit stages and preserves the relationships between **sources, evidence, claims, citations, and provenance**.

---

## 📌 At a Glance

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

## 🧬 Research Pipeline

![PaperMate research pipeline](docs/assets/pipeline.svg)

The core flow is:

```text
Question
   ↓
Search
   ↓
Retrieval
   ↓
Evidence
   ↓
Claims
   ↓
Validation
   ↓
Citations
   ↓
Structured answer
```

### Evidence chain

```text
SOURCE
  ↓
EVIDENCE
  ↓
CLAIM
  ↓
CITATION
  ↓
ANSWER
```

This structure is the central architectural idea behind PaperMate. The answer is not the only artifact produced by research; the intermediate provenance is part of the output.

---

## 🔍 What PaperMate Currently Provides

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

## ⚙️ Current Stack

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
Ollama   → http://127.0.0.1:11434
SearXNG  → local Docker service / port 8080
Research → POST /research
```

---

## 🧪 Verified Research Run

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
   ↓
evidence
   ↓
ollama
   ↓
claim_validation
   ↓
citation_rendering
```

This is the current end-to-end proof that the main research path works as intended.

---

## ⚡ Local Model Baseline

A direct HTTP request to Ollama using `qwen2.5:3b` was measured at approximately:

# **1.16 seconds**

That measurement is intentionally labelled as a **raw inference baseline**.

It does **not** represent full research latency. A real research operation also includes source discovery, retrieval, evidence processing, validation, and response generation.

![Benchmark overview](docs/assets/benchmark.svg)

---

## 🧠 Model Inventory

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

## 🧱 System Architecture

PaperMate is split into several logical boundaries:

```text
                        ┌──────────────────┐
                        │   Application    │
                        │  Vane / Clients  │
                        └────────┬─────────┘
                                 │
                                 ▼
                        ┌──────────────────┐
                        │   Intelligence   │
                        │     Gateway      │
                        └────────┬─────────┘
                                 │
              ┌──────────────────┼──────────────────┐
              │                  │                  │
              ▼                  ▼                  ▼
       ┌────────────┐     ┌────────────┐     ┌────────────┐
       │  Research  │     │   Memory   │     │ Providers  │
       │  Pipeline  │     │ MemPalace  │     │   Ollama   │
       └─────┬──────┘     └────────────┘     └─────┬──────┘
             │                                      │
             ▼                                      ▼
       ┌────────────┐                       ┌────────────┐
       │  SearXNG   │                       │ Local LLMs │
       └─────┬──────┘                       └────────────┘
             │
             ▼
       ┌────────────┐
       │  Evidence  │
       └─────┬──────┘
             │
             ▼
       ┌────────────┐
       │   Claims   │
       └─────┬──────┘
             │
             ▼
       ┌────────────┐
       │ Validation │
       └─────┬──────┘
             │
             ▼
       ┌────────────┐
       │ Citations  │
       └────────────┘
```

Each layer is intended to be replaceable without forcing the entire system to change with it.

---

## 🔌 API Contract

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

## 🛡️ Why the Evidence Layer Exists

A conventional research assistant can collapse the entire process into:

```text
Search → Prompt → Answer
```

PaperMate instead aims for:

```text
Search
  ↓
Retrieved material
  ↓
Evidence extraction
  ↓
Claim construction
  ↓
Claim/evidence validation
  ↓
Citation rendering
  ↓
Answer
```

That extra structure makes the research process inspectable and gives downstream applications more than just a string of generated text.

---

## 🧠 Memory Layer

PaperMate includes an experimental memory subsystem using MemPalace-related components.

Current work includes:

- memory contracts
- storage
- retrieval experiments
- gateway integration
- memory probing

Memory is deliberately separated from the research pipeline so that persistent context can evolve independently of search and synthesis.

---

## 🐳 Vane Evaluation

Vane integration is currently **experimental**.

A previous attempt to deeply modify Vane's native research path introduced unnecessary configuration and performance complexity, so that work was rolled back.

The current plan is intentionally open-ended:

```text
Official Vane Docker
          ↓
     Local Ollama
          ↓
      Benchmark
          ↓
 ┌────────┴────────┐
 │                 │
 ▼                 ▼
Vane           PaperMate
 │                 │
 └────────┬────────┘
          ▼
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

## 📈 What Will Be Measured Next

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

## 📁 Repository Layout

```text
PaperMate/
│
├── backend/          API and backend services
├── intelligence/     Intelligence contracts and providers
├── memory/           Memory contracts and MemPalace
├── research/         Research/search logic
├── infra/            Infrastructure configuration
├── tests/            Automated tests
├── docs/             Engineering documentation
│   └── assets/       README diagrams
├── data/             Local runtime data (ignored)
│
├── README.md
├── STATUS.md
├── ROADMAP.md
├── ARCHITECTURE.md
└── BENCHMARKS.md
```

---

## 🚧 Development Status

### **🟠 DEVELOPING**

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

## 🗺️ Documentation

- [Project status](STATUS.md)
- [Roadmap](ROADMAP.md)
- [Architecture](ARCHITECTURE.md)
- [API](API.md)
- [Benchmarks](BENCHMARKS.md)
- [Vane integration](docs/VANE_INTEGRATION.md)
- [Sage lessons](docs/SAGE_LESSONS.md)

---

## 🎯 Engineering Principle

> **Measure first. Integrate only when the evidence justifies the complexity.**
'@

$status = @'
# 📍 PaperMate Status

## Current State

**🟠 DEVELOPING**

PaperMate is an active experimental research-intelligence project. Core research functionality has been verified locally; several subsystems remain under development.

## Verified

| Area | State |
|---|---|
| Research API | ✅ Verified |
| SearXNG retrieval | ✅ Verified |
| Ollama inference | ✅ Verified |
| Evidence representation | ✅ Verified |
| Claim representation | ✅ Verified |
| Citation rendering | ✅ Verified |
| Citation validation | ✅ Verified |
| Provenance | ✅ Verified |
| Automated research tests | ✅ Verified |
| Memory layer | 🟡 Experimental |
| Vane integration | 🟡 Experimental |
| Production deployment | ⚪ Not ready |

## Verified Numbers

- **3** sources in the verified research run
- **3** evidence records
- **1** claim
- **2** citations
- **2** references
- **7** Ollama models observed locally
- **1.16 s** direct `qwen2.5:3b` inference baseline
- citation validation: **passed**

## Current Focus

1. Research quality
2. Evidence grounding
3. Citation reliability
4. Memory evaluation
5. Local deployment
6. Full-system benchmarking
7. Vane comparison

## Important Boundary

The `1.16 s` figure is a direct model-inference measurement. It is not a full research latency benchmark.

## Decision State

No permanent architecture has been selected. The next architectural decision will be based on measured performance and research quality rather than framework preference.
'@

$roadmap = @'
# 🧭 PaperMate Roadmap

**Status: DEVELOPING**

The roadmap is intentionally open-ended. Items describe development direction, not promises about the final architecture.

## ✅ Foundation

- [x] Backend structure
- [x] Research request/response models
- [x] Search integration
- [x] Retrieval layer
- [x] Evidence layer
- [x] Claim model
- [x] Citation renderer
- [x] Citation validation
- [x] Provenance
- [x] Ollama provider
- [x] Initial automated tests

## 🟡 Developing

- [ ] Memory quality evaluation
- [ ] Source ranking
- [ ] Evidence quality scoring
- [ ] Claim validation improvements
- [ ] Research caching
- [ ] Gateway hardening
- [ ] Failure recovery
- [ ] Configuration validation
- [ ] Reproducible benchmark runner

## 🔬 Evaluation

- [ ] Official Vane Docker deployment
- [ ] Vane + Ollama baseline
- [ ] PaperMate + Ollama baseline
- [ ] Same-question benchmark set
- [ ] Quality comparison
- [ ] Citation/evidence comparison
- [ ] Latency comparison
- [ ] Resource comparison

## 🧭 Possible Directions

```text
                 ┌───────────────┐
                 │   Evaluation  │
                 └───────┬───────┘
                         │
       ┌─────────────────┼─────────────────┐
       ▼                 ▼                 ▼
    Vane only       PaperMate only      Hybrid
       │                 │                 │
       └─────────────────┴─────────────────┘
                         │
                         ▼
                  Final architecture
```

Other possibilities include deeper integration or keeping both systems independent.

## 📏 Success Criteria

The project should improve against measurable system-level criteria:

- answer quality
- evidence grounding
- citation accuracy
- research depth
- latency
- resource usage
- reliability
- maintainability

The simplest system that satisfies the requirements should win.
'@

$architecture = @'
# 🏗️ PaperMate Architecture

## High-Level Model

```text
                         APPLICATIONS
                              │
                              ▼
                    ┌──────────────────┐
                    │ Intelligence     │
                    │ Gateway          │
                    └────────┬─────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
          ▼                  ▼                  ▼
      Research             Memory            Providers
      Pipeline            MemPalace           Ollama
          │                                     │
          ▼                                     ▼
       SearXNG                              Local Models
          │
          ▼
       Evidence
          │
          ▼
        Claims
          │
          ▼
      Validation
          │
          ▼
      Citations
          │
          ▼
       Answer
```

## Research Flow

```text
Question → Search → Retrieval → Evidence → Claims → Validation → Citations → Answer
```

## Data Relationships

```text
Source
  │
  └── Evidence
        │
        └── Claim
              │
              └── Citation
```

The relationships are explicit so downstream clients can inspect how a claim relates to supporting material.

## Local Infrastructure

```text
Windows Host
│
├── Ollama :11434
│   └── qwen2.5:3b
│
└── Docker
    └── SearXNG :8080
```

## Design Principles

### Local-first

Prefer locally controlled search, inference, memory and storage where practical.

### Evidence-first

Retrieved evidence is represented before final synthesis.

### Provider independence

Research logic should not depend permanently on one model provider.

### Traceability

Claims should remain connected to supporting evidence and sources.

### Replaceability

Search, inference, memory and clients should be replaceable boundaries.

### Measurability

Architecture decisions should be supported by reproducible tests.

## Vane Boundary

PaperMate is currently evaluating Vane rather than assuming Vane must depend on PaperMate.

Possible architectures include:

```text
Vane → PaperMate
Vane ↔ PaperMate
Vane and PaperMate independently
PaperMate standalone
```

The final boundary will depend on benchmark results.
'@

$bench = @'
# 📊 PaperMate Benchmarks

## Verified Measurements

| Metric | Value | Type |
|---|---:|---|
| Direct Ollama inference | **1.16 s** | Measured |
| Ollama models observed | **7** | Observed inventory |
| Verified research HTTP status | **200** | Measured |
| Sources in verified research run | **3** | Measured |
| Evidence records | **3** | Measured |
| Claims | **1** | Measured |
| Citations | **2** | Measured |
| References | **2** | Measured |
| Citation validation | **PASSED** | Measured |

## Direct Model Baseline

```text
Model:       qwen2.5:3b
Endpoint:    127.0.0.1:11434
Mode:        non-streaming HTTP
Latency:     1.16 s
```

## Important Distinction

Raw model latency is only one part of a research request.

```text
Search
  +
Retrieval
  +
Evidence processing
  +
Model inference
  +
Claim validation
  +
Citation rendering
  =
Total research latency
```

## Planned Benchmark Set

| Metric | Vane | PaperMate |
|---|---|---|
| Time to first token | Pending | Pending |
| Total latency | Pending | Pending |
| Search latency | Pending | Pending |
| Model latency | Pending | Pending |
| Search calls | Pending | Pending |
| Model calls | Pending | Pending |
| Answer quality | Pending | Pending |
| Evidence grounding | Pending | Pending |
| Citation accuracy | Pending | Pending |
| CPU usage | Pending | Pending |
| RAM usage | Pending | Pending |
| GPU usage | Pending | Pending |
| VRAM usage | Pending | Pending |
| Failure rate | Pending | Pending |

## Benchmark Policy

Only numbers backed by an actual test are labelled as measured. Estimates, targets and future values remain explicitly marked as such.
'@

$vane = @'
# 🔗 Vane Integration Notes

## Status

**🟡 EXPERIMENTAL**

PaperMate has been evaluated as a possible research backend for Vane.

A deeper integration was attempted and subsequently rolled back after it introduced unwanted configuration and performance complexity into the Vane installation.

## Current Approach

The next experiment is to run Vane through its intended Docker deployment and connect it to the same local Ollama infrastructure used by PaperMate.

```text
Official Vane Docker
        │
        ▼
     Ollama
        │
        ▼
   Same hardware
        │
        ▼
  Same test questions
        │
   ┌────┴────┐
   ▼         ▼
 Vane    PaperMate
   │         │
   └────┬────┘
        ▼
   Comparison
```

## Docker Networking

When Ollama runs on the Windows host and Vane runs inside Docker, the container should normally access the host service through:

```text
http://host.docker.internal:11434
```

rather than `127.0.0.1` from inside the container.

## Evaluation Criteria

1. Answer quality
2. Research depth
3. Evidence grounding
4. Citation reliability
5. Time to first token
6. Total latency
7. Search latency
8. CPU/RAM usage
9. GPU/VRAM usage
10. Reliability
11. Configuration complexity

## Possible Outcomes

- Vane only
- PaperMate only
- Vane + PaperMate
- Hybrid
- Independent projects

No outcome is predetermined.
'@

$pipelineSvg = @'
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="620" viewBox="0 0 1200 620">
  <defs>
    <linearGradient id="bg" x1="0" x2="1" y1="0" y2="1">
      <stop offset="0" stop-color="#0f172a"/>
      <stop offset="1" stop-color="#111827"/>
    </linearGradient>
    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
      <feDropShadow dx="0" dy="8" stdDeviation="10" flood-opacity="0.22"/>
    </filter>
  </defs>
  <rect width="1200" height="620" rx="28" fill="url(#bg)"/>
  <text x="70" y="72" font-family="Segoe UI, Arial" font-size="34" font-weight="700" fill="#f8fafc">PaperMate Research Pipeline</text>
  <text x="70" y="108" font-family="Segoe UI, Arial" font-size="17" fill="#94a3b8">Search → evidence → claims → validation → citations</text>
  <g filter="url(#shadow)" font-family="Segoe UI, Arial" text-anchor="middle">
    <rect x="55" y="190" width="140" height="86" rx="16" fill="#1e293b" stroke="#38bdf8"/>
    <text x="125" y="226" font-size="19" font-weight="700" fill="#e2e8f0">Question</text>
    <text x="125" y="252" font-size="14" fill="#94a3b8">input</text>

    <rect x="225" y="190" width="140" height="86" rx="16" fill="#1e293b" stroke="#a78bfa"/>
    <text x="295" y="226" font-size="19" font-weight="700" fill="#e2e8f0">Search</text>
    <text x="295" y="252" font-size="14" fill="#94a3b8">SearXNG</text>

    <rect x="395" y="190" width="140" height="86" rx="16" fill="#1e293b" stroke="#34d399"/>
    <text x="465" y="226" font-size="19" font-weight="700" fill="#e2e8f0">Evidence</text>
    <text x="465" y="252" font-size="14" fill="#94a3b8">retrieval</text>

    <rect x="565" y="190" width="140" height="86" rx="16" fill="#1e293b" stroke="#fbbf24"/>
    <text x="635" y="226" font-size="19" font-weight="700" fill="#e2e8f0">Claims</text>
    <text x="635" y="252" font-size="14" fill="#94a3b8">reasoning</text>

    <rect x="735" y="190" width="140" height="86" rx="16" fill="#1e293b" stroke="#fb7185"/>
    <text x="805" y="226" font-size="19" font-weight="700" fill="#e2e8f0">Validate</text>
    <text x="805" y="252" font-size="14" fill="#94a3b8">provenance</text>

    <rect x="905" y="190" width="140" height="86" rx="16" fill="#1e293b" stroke="#60a5fa"/>
    <text x="975" y="226" font-size="19" font-weight="700" fill="#e2e8f0">Citations</text>
    <text x="975" y="252" font-size="14" fill="#94a3b8">references</text>
  </g>
  <g stroke="#64748b" stroke-width="3" fill="none">
    <path d="M195 233 H220"/><path d="M365 233 H390"/><path d="M535 233 H560"/><path d="M705 233 H730"/><path d="M875 233 H900"/>
  </g>
  <g font-family="Segoe UI, Arial" text-anchor="middle">
    <rect x="170" y="380" width="860" height="150" rx="20" fill="#0b1220" stroke="#334155"/>
    <text x="600" y="425" font-size="22" font-weight="700" fill="#f8fafc">Verified development path</text>
    <text x="600" y="458" font-size="18" fill="#cbd5e1">3 sources • 3 evidence records • 1 claim • 2 citations</text>
    <text x="600" y="490" font-size="18" fill="#cbd5e1">HTTP 200 • citation validation: PASSED • qwen2.5:3b</text>
  </g>
</svg>
'@

$benchmarkSvg = @'
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="640" viewBox="0 0 1200 640">
  <rect width="1200" height="640" rx="28" fill="#0f172a"/>
  <text x="70" y="72" font-family="Segoe UI, Arial" font-size="34" font-weight="700" fill="#f8fafc">Verified PaperMate Numbers</text>
  <text x="70" y="108" font-family="Segoe UI, Arial" font-size="17" fill="#94a3b8">Development measurements collected during local testing</text>
  <g font-family="Segoe UI, Arial">
    <text x="90" y="175" font-size="18" font-weight="700" fill="#e2e8f0">Direct Ollama inference</text>
    <line x1="90" y1="210" x2="1110" y2="210" stroke="#334155" stroke-width="2"/>
    <text x="90" y="255" font-size="30" font-weight="700" fill="#38bdf8">1.16 s</text>
    <text x="245" y="255" font-size="17" fill="#94a3b8">qwen2.5:3b • direct HTTP • non-streaming</text>

    <text x="90" y="330" font-size="18" font-weight="700" fill="#e2e8f0">Verified research output</text>
    <g transform="translate(90,360)">
      <g fill="#1e293b" stroke="#334155">
        <rect x="0" y="0" width="180" height="90" rx="14"/><rect x="200" y="0" width="180" height="90" rx="14"/>
        <rect x="400" y="0" width="180" height="90" rx="14"/><rect x="600" y="0" width="180" height="90" rx="14"/><rect x="800" y="0" width="180" height="90" rx="14"/>
      </g>
      <g text-anchor="middle">
        <text x="90" y="38" font-size="30" font-weight="700" fill="#f8fafc">3</text><text x="90" y="65" font-size="14" fill="#94a3b8">sources</text>
        <text x="290" y="38" font-size="30" font-weight="700" fill="#f8fafc">3</text><text x="290" y="65" font-size="14" fill="#94a3b8">evidence</text>
        <text x="490" y="38" font-size="30" font-weight="700" fill="#f8fafc">1</text><text x="490" y="65" font-size="14" fill="#94a3b8">claim</text>
        <text x="690" y="38" font-size="30" font-weight="700" fill="#f8fafc">2</text><text x="690" y="65" font-size="14" fill="#94a3b8">citations</text>
        <text x="890" y="38" font-size="24" font-weight="700" fill="#34d399">PASSED</text><text x="890" y="65" font-size="14" fill="#94a3b8">validation</text>
      </g>
    </g>

    <text x="90" y="520" font-size="18" font-weight="700" fill="#e2e8f0">Model inventory</text>
    <text x="90" y="556" font-size="31" font-weight="700" fill="#a78bfa">7</text>
    <text x="140" y="556" font-size="17" fill="#94a3b8">local Ollama models observed</text>
    <text x="90" y="595" font-size="14" fill="#64748b">Full research latency is not yet formally benchmarked.</text>
  </g>
</svg>
'@

[System.IO.File]::WriteAllText((Join-Path $root 'README.md'), $readme, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $root 'STATUS.md'), $status, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $root 'ROADMAP.md'), $roadmap, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $root 'ARCHITECTURE.md'), $architecture, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $root 'BENCHMARKS.md'), $bench, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $docs 'VANE_INTEGRATION.md'), $vane, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $assets 'pipeline.svg'), $pipelineSvg, [System.Text.UTF8Encoding]::new($false))
[System.IO.File]::WriteAllText((Join-Path $assets 'benchmark.svg'), $benchmarkSvg, [System.Text.UTF8Encoding]::new($false))

Write-Host "PaperMate documentation rebuilt." -ForegroundColor Green
Write-Host "Updated: README.md STATUS.md ROADMAP.md ARCHITECTURE.md BENCHMARKS.md docs/VANE_INTEGRATION.md" -ForegroundColor Cyan
Write-Host "Added: docs/assets/pipeline.svg docs/assets/benchmark.svg" -ForegroundColor Cyan
