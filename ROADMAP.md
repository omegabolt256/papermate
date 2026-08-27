# ðŸ§­ PaperMate Roadmap

**Status: DEVELOPING**

The roadmap is intentionally open-ended. Items describe development direction, not promises about the final architecture.

## âœ… Foundation

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

## ðŸŸ¡ Developing

- [ ] Memory quality evaluation
- [ ] Source ranking
- [ ] Evidence quality scoring
- [ ] Claim validation improvements
- [ ] Research caching
- [ ] Gateway hardening
- [ ] Failure recovery
- [ ] Configuration validation
- [ ] Reproducible benchmark runner

## ðŸ”¬ Evaluation

- [ ] Official Vane Docker deployment
- [ ] Vane + Ollama baseline
- [ ] PaperMate + Ollama baseline
- [ ] Same-question benchmark set
- [ ] Quality comparison
- [ ] Citation/evidence comparison
- [ ] Latency comparison
- [ ] Resource comparison

## ðŸ§­ Possible Directions

```text
                 â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
                 â”‚   Evaluation  â”‚
                 â””â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚
       â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
       â–¼                 â–¼                 â–¼
    Vane only       PaperMate only      Hybrid
       â”‚                 â”‚                 â”‚
       â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚
                         â–¼
                  Final architecture
```

Other possibilities include deeper integration or keeping both systems independent.

## ðŸ“ Success Criteria

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