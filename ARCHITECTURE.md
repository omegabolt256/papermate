# ðŸ—ï¸ PaperMate Architecture

## High-Level Model

```text
                         APPLICATIONS
                              â”‚
                              â–¼
                    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                    â”‚ Intelligence     â”‚
                    â”‚ Gateway          â”‚
                    â””â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                             â”‚
          â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
          â”‚                  â”‚                  â”‚
          â–¼                  â–¼                  â–¼
      Research             Memory            Providers
      Pipeline            MemPalace           Ollama
          â”‚                                     â”‚
          â–¼                                     â–¼
       SearXNG                              Local Models
          â”‚
          â–¼
       Evidence
          â”‚
          â–¼
        Claims
          â”‚
          â–¼
      Validation
          â”‚
          â–¼
      Citations
          â”‚
          â–¼
       Answer
```

## Research Flow

```text
Question â†’ Search â†’ Retrieval â†’ Evidence â†’ Claims â†’ Validation â†’ Citations â†’ Answer
```

## Data Relationships

```text
Source
  â”‚
  â””â”€â”€ Evidence
        â”‚
        â””â”€â”€ Claim
              â”‚
              â””â”€â”€ Citation
```

The relationships are explicit so downstream clients can inspect how a claim relates to supporting material.

## Local Infrastructure

```text
Windows Host
â”‚
â”œâ”€â”€ Ollama :11434
â”‚   â””â”€â”€ qwen2.5:3b
â”‚
â””â”€â”€ Docker
    â””â”€â”€ SearXNG :8080
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
Vane â†’ PaperMate
Vane â†” PaperMate
Vane and PaperMate independently
PaperMate standalone
```

The final boundary will depend on benchmark results.