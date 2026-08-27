# ðŸ“Š PaperMate Benchmarks

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