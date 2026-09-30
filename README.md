# REALITYX

**VERIFY WHAT’S REAL.**

Reality verification infrastructure for detecting authentic, manipulated, synthetic, and uncertain digital content using multimodal forensics, provenance, biological signals, and evidence fusion.

## Vision

REALITYX is designed as a model-agnostic, privacy-first verification infrastructure for images, video, audio, documents, CCTV, screenshots, payment-related documents, and future digital media.

## Verification principle

REALITYX does not claim that any single signal can prove truth with certainty. It combines independent evidence and reports:

- 🟢 Likely Real / Likely Authentic
- 🟠 Uncertain
- 🔴 Likely Fake / Likely Manipulated

Every result includes evidence and signal status.

## Architecture

- Next.js — web interface
- Python + FastAPI — verification API
- OpenCV / ML — forensic analysis
- Rust + cryptography / C2PA boundary — provenance and integrity
- PostgreSQL — minimal metadata, results, hashes, and audit data

## Security principles

- Zero-trust file ingestion
- Magic-byte and parser validation
- Strict upload and decoded-pixel limits
- Decompression-bomb protection
- Isolated analysis workers
- Least privilege
- Idempotent verification requests
- Rate limiting and abuse protection
- Structured JSON logging
- Deterministic dependencies and reproducible builds
- Minimal retention of user originals

## Biological signal engine

The biological verification layer analyzes measurable visual and temporal signals such as rPPG/pulse-related patterns, micro-motion, eye activity, skin and nail-bed variation, and cross-region consistency.

These signals are treated as forensic evidence, not medical diagnosis or absolute proof of biological state.

## Development

Engineering workflow:

**Architecture → Security → Code → Tests → Integration → Performance → Final Verification**

Make it work. Make it right. Make it fast.

## Status

Early foundation phase — Biological Verification MVP is the first implementation milestone.
