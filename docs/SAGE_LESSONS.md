# PaperMate v2 — Sage Concept Extraction

## Confirmed Sage Concepts

### WorkloadRoute

Sage defines a workload route as:

- provider
- model

### InferenceRouter

Sage exposes:

- chat(message, provider, model, system)
- chat_messages(messages, provider, model, system)

Both return generated text.

### Provider Failure

Sage raises runtime errors for failed HTTP requests or malformed responses.

This is useful for PaperMate fallback semantics.

## PaperMate v2 Interpretations

These are new PaperMate design decisions inspired by Sage, not direct Sage implementations.

### IntelligenceRequest

Planned fields:

- task_type
- prompt/messages
- context requirements
- structured-output requirement
- privacy policy
- execution profile

### Provider Resolution

The PaperMate resolver will select a provider based on:

- task requirements
- workspace privacy policy
- provider availability
- model capabilities
- execution profile

### Local Worker

The local model will be a separate service boundary.

PaperMate will not import Sage.

## Architectural Rule

Sage and PaperMate remain independent projects.

Sage provides experimental findings and architectural inspiration.

PaperMate v2 implements those concepts independently.
