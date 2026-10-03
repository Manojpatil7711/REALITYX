# REALITYX

**VERIFY WHAT’S REAL.**

Reality verification infrastructure for detecting authentic, manipulated, synthetic, and uncertain digital content using multimodal forensics, provenance, and evidence fusion.

## Premium 2050 operating roadmap

REALITYX will expose advanced paid capabilities as **feature-gated services**, while keeping a useful free verification tier available for traffic growth and validation. Paid providers, GPU compute, external forensic APIs, signing infrastructure, premium storage, enterprise identity, and other recurring-cost services remain **inactive until technically necessary and explicitly activated**.

### Product rule
**Build the capability → keep it safely gated → run a free path where technically sound → measure demand → activate paid infrastructure only when the capability is needed and economically justified.**

No paid service should silently replace a working free path. No premium badge means a capability is already production-ready unless its implementation, tests, security controls and operational dependencies have been verified.

### Roadmap — execution order

- **P0 Foundation:** stable verification contract, verdict semantics, evidence schema, upload limits, parser validation, regression tests and CI.
- **P1 Forensics:** image/video/audio/document engines with isolated workers, deterministic versions and conservative scoring.
- **P2 Evidence Fusion:** independent signals, provenance, negative evidence, conflict handling and explicit abstention to UNCERTAIN.
- **P3 Trust Receipts:** artifact hash, protocol version, engine versions, evidence summary, timestamp, signed receipt format.
- **P4 Key Infrastructure:** key registration, rotation, revocation, verification endpoint and transparency records.
- **P5 AI-Agent API:** machine-readable verification/attestation endpoint, policy-friendly states, replay/idempotency protection and rate limits.
- **P6 Provenance:** C2PA interoperability boundary and provenance-aware evidence.
- **P7 Premium Controls:** authenticated premium access, usage quotas, feature flags, audit logs, billing-provider adapter and entitlement checks. Billing stays disabled until required.
- **P8 Scale Security:** isolated jobs, queueing, resource quotas, abuse prevention, observability, incident controls and privacy/minimal retention.
- **P9 Independent Assurance:** benchmark suite, reproducible evaluations, external security review readiness, conformance profiles and documented limitations.
- **P10 Certification readiness:** only pursue external audit/accreditation/certification where an authorized body and applicable standard require it.

### Free-first traffic mode

The free tier is intended to remain genuinely useful for acquiring users and traffic while the platform is being validated. Premium architecture is present as a controlled roadmap, but expensive services are not required for every request.

Free-first rules:
1. Prefer local/open-source deterministic analysis when it is safe and adequate.
2. Never expose a paid-provider key to the browser.
3. Use server-side feature flags for premium capabilities.
4. Fail safely when a paid provider is disabled or unavailable.
5. Never downgrade a failed premium check into a misleading positive verdict.
6. Record capability/dependency status without storing unnecessary originals.
7. Activate recurring-cost infrastructure only after demand, reliability and budget justify it.

## Capability watch — long-term AI resistance

REALITYX must not depend on the assumption that today's AI detectors remain sufficient. The runtime now has a deterministic capability-watch foundation that fingerprints the active engine registry and protocol. Future model or benchmark adapters can report capability changes, evaluation results and drift without changing the core verdict contract.

Operational rule: **new AI capability → measure → benchmark → compare against prior baseline → review limitations → gate deployment → update protocol/engine version**. A model is never treated as an authority merely because it is newer or more capable. This is a monitoring and re-validation system, not a claim of perfect prediction of future AI.

The operator-facing workflow profiles also define clear paths for government, legal/investigation, media, business/platform and public verification so users are not forced to understand the underlying engineering.

## Trust-layer vision

REALITYX is designed to become a **machine-verifiable reality verification layer** that AI agents, platforms, institutions, researchers, businesses, and people can query before trusting digital content.

The long-term architecture is built around four separations:

1. **Verification** — reproducible forensic analysis of the supplied artifact.
2. **Evidence** — machine-readable facts, signal provenance, model/engine versions, and limitations.
3. **Attestation** — cryptographically verifiable receipts proving which artifact was checked and what protocol produced the result.
4. **Certification** — a separate governance/accreditation layer issued only by an authorized certification body or regulator; a REALITYX verification result is **not automatically a government or legal certification**.

## AI-agent trust interface

Future integrations can verify a REALITYX receipt before accepting a claim:

**content → SHA-256 → REALITYX verification → evidence receipt → signature/attestation → AI agent / platform policy**

Agents should be able to distinguish:

- verified artifact identity
- evidence-backed verification result
- uncertain / abstained result
- stale or revoked receipt
- unsupported certification claim

No badge is intended to mean absolute truth. Verification is scoped to the exact artifact, protocol, evidence available, and time of analysis.

## Verification principle

REALITYX does not claim that any single signal can prove truth with certainty. It combines independent evidence and reports:

- 🟢 Verified — evidence met the active protocol threshold
- 🟠 Uncertain — evidence was insufficient or contradictory
- 🔴 Inauthentic — evidence met the active inauthenticity threshold

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
- Secrets only in managed server-side configuration
- Premium entitlements enforced server-side
- Safe failure and explicit uncertainty

## Engineering workflow

**Architecture → Security → Code → Tests → Integration → Performance → Final Verification**

Every roadmap feature must preserve working workflows and pass regression/security checks before being considered GREEN.

## Status

Premium 2050 foundation and gated roadmap established. Advanced paid infrastructure is intentionally **not activated by default**. Current priority remains a stable, secure free-first verification core that can accumulate legitimate traffic before costly services are enabled.
