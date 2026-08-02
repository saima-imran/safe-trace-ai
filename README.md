# SafeTrace-AI

**AI-Assisted Semantic Change-Impact Analysis for Safety Requirements and Verification Evidence**

SafeTrace-AI is a small research-oriented prototype exploring how changes in
software safety requirements affect existing verification evidence.

The project combines deterministic traceability analysis with a local large
language model (LLM) to explain the semantic impact of requirement changes
and provide advisory review suggestions.

## Research Question

> To what extent can a local LLM identify and explain the impact of semantic
> changes in software safety requirements on existing verification evidence
> when combined with deterministic traceability?

## Initial Scope

- Detect changes between requirement versions
- Trace changed requirements to test cases and test results
- Identify verification evidence that may require review
- Use deterministic rules for reproducible evidence checks
- Use a local LLM through Ollama for semantic change-impact explanations
- Keep AI-generated suggestions clearly separated from deterministic findings

## Project Status

🚧 **Planning and early development**

The initial case study uses a small fictional automotive safety example.

## Important Limitation

SafeTrace-AI is a research prototype for exploring AI-assisted Requirements
Engineering and evidence analysis.

It does not assess complete ISO 26262 compliance, determine ASIL levels,
provide safety certification, or replace professional engineering judgement.# safe-trace-ai
AI-assisted semantic change-impact analysis for safety requirements and verification evidence.
