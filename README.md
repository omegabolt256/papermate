@"

\# PaperMate



> Local-first, evidence-grounded research infrastructure.



!\[Status](https://img.shields.io/badge/status-DEVELOPING-orange)

!\[Inference](https://img.shields.io/badge/inference-Ollama-black)

!\[Search](https://img.shields.io/badge/search-SearXNG-purple)

!\[Architecture](https://img.shields.io/badge/architecture-local--first-blue)



\## Overview



PaperMate is a research backend designed to turn search results into structured, traceable research.



The core pipeline is:



&#x20;   Question

&#x20;       ↓

&#x20;   Search

&#x20;       ↓

&#x20;   Evidence

&#x20;       ↓

&#x20;   Local inference

&#x20;       ↓

&#x20;   Claims

&#x20;       ↓

&#x20;   Validation

&#x20;       ↓

&#x20;   Citations

&#x20;       ↓

&#x20;   Structured answer



The project is currently \*\*DEVELOPING\*\*.



\## Current Capabilities



| Capability | Status |

|---|---|

| SearXNG search | Working |

| Local Ollama inference | Working |

| Evidence extraction | Working |

| Claim generation | Working |

| Claim/evidence mapping | Working |

| Citation generation | Working |

| Citation validation | Working |

| Provenance metadata | Working |

| Vane integration | Experimental |

| Production readiness | Not yet |



\## Verified Configuration



| Parameter | Value |

|---|---|

| LLM provider | Ollama |

| Model | `qwen2.5:3b` |

| Ollama endpoint | `127.0.0.1:11434` |

| Search engine | SearXNG |

| SearXNG port | `8080` |

| Default max sources | `10` |

| Citation requirement | `true` |



\## Verified Research Run



Question:



`What are randomized controlled trials used for?`



Observed result:



| Metric | Result |

|---|---:|

| HTTP status | `200` |

| Sources | `3` |

| Evidence records | `3` |

| Claims | `1` |

| Citations | `2` |

| References | `2` |

| Model | `qwen2.5:3b` |

| Provider | Ollama |

| Citation validation | `passed` |



\## Raw Ollama Benchmark



A direct local inference test using `qwen2.5:3b` completed in approximately:



\*\*1.16 seconds\*\*



This is a raw inference measurement, not full research latency.



\## Architecture



```text

&#x20;                   USER QUESTION

&#x20;                         |

&#x20;                         v

&#x20;                 +---------------+

&#x20;                 | PaperMate API |

&#x20;                 | POST /research|

&#x20;                 +-------+-------+

&#x20;                         |

&#x20;                         v

&#x20;                 +---------------+

&#x20;                 |    SearXNG    |

&#x20;                 | Source Search |

&#x20;                 +-------+-------+

&#x20;                         |

&#x20;                         v

&#x20;                 +---------------+

&#x20;                 |   Evidence    |

&#x20;                 |    Layer      |

&#x20;                 +-------+-------+

&#x20;                         |

&#x20;                         v

&#x20;                 +---------------+

&#x20;                 |    Ollama     |

&#x20;                 | Local LLM     |

&#x20;                 +-------+-------+

&#x20;                         |

&#x20;                         v

&#x20;                 +---------------+

&#x20;                 |     Claims    |

&#x20;                 |  Validation   |

&#x20;                 +-------+-------+

&#x20;                         |

&#x20;                         v

&#x20;                 +---------------+

&#x20;                 |   Citations   |

&#x20;                 |  Provenance   |

&#x20;                 +-------+-------+

&#x20;                         |

&#x20;                         v

&#x20;                 STRUCTURED RESULT

