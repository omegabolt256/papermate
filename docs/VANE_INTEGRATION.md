# 🔗 Vane Integration Notes

**Status: EXPERIMENTAL**

PaperMate was experimentally connected to Vane as a research backend. The experiment was rolled back after unnecessary configuration and performance complexity was introduced.

## Current Evaluation

`	ext
Official Vane Docker
        ↓
    Local Ollama
        ↓
     Benchmark
        ↓
 Compare against PaperMate
`

## Possible Outcomes

- Vane only
- PaperMate only
- Vane + PaperMate
- Hybrid
- Independent projects

## Docker Networking

When Ollama runs on the Windows host and Vane runs in Docker, the host is normally reached as:

http://host.docker.internal:11434

## Decision Criteria

- Answer quality
- Research depth
- Evidence grounding
- Citation accuracy
- Total latency
- Resource usage
- Reliability
- Complexity

No final integration decision has been made.
