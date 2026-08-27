# ðŸ”— Vane Integration Notes

## Status

**ðŸŸ¡ EXPERIMENTAL**

PaperMate has been evaluated as a possible research backend for Vane.

A deeper integration was attempted and subsequently rolled back after it introduced unwanted configuration and performance complexity into the Vane installation.

## Current Approach

The next experiment is to run Vane through its intended Docker deployment and connect it to the same local Ollama infrastructure used by PaperMate.

```text
Official Vane Docker
        â”‚
        â–¼
     Ollama
        â”‚
        â–¼
   Same hardware
        â”‚
        â–¼
  Same test questions
        â”‚
   â”Œâ”€â”€â”€â”€â”´â”€â”€â”€â”€â”
   â–¼         â–¼
 Vane    PaperMate
   â”‚         â”‚
   â””â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”˜
        â–¼
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