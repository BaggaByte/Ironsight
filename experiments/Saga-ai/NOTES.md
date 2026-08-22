# Legacy Experimental Code

This directory contains experimental systems built before SentinelAI was consolidated into a single unified platform. 

## Contents
1. **Aegis AI**: An exploratory AI code-security reviewer (SAST + LLM patches). It used `ollama` and `chromadb` for a RAG-based remediation planner. Its concepts (like the Analyzer -> Critic pattern) were ported directly into Sentinel's core scanning engine.
2. **Mini-Mythos (Nexus)**: An exploratory autonomous infra pentesting framework. Its frontend and GRC reporting concepts were absorbed into Sentinel.

These are preserved here for portfolio value and historical reference, but they are **not** part of the active, production Sentinel stack.
