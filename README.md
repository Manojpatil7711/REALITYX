# REALITYX

**VERIFY WHAT’S REAL.**

Reality verification infrastructure for detecting authentic, manipulated, synthetic, and uncertain digital content using multimodal forensics, provenance, and evidence fusion.

## Professional Verification Mode

REALITYX separates the **simple public verdict** from an evidence-grade professional workflow. Professional users should not be forced to interpret a percentage as “how real” or “how fake” an artifact is.

### Professional result contract

Every professional verification is designed to present, in this order:

1. **Verdict** — AUTHENTIC, INAUTHENTIC, or UNCERTAIN.
2. **Plain-language conclusion** — a short explanation a non-specialist can understand.
3. **Confidence / evidence strength** — supporting context, never presented as a literal percentage of truth.
4. **Evidence summary** — independent signals, strengths, weaknesses, and conflicts.
5. **Provenance status** — available, verified, missing, inconsistent, or unsupported.
6. **Artifact identity** — SHA-256 and verification ID.
7. **Protocol/engine versions** — enough information to reproduce or audit the decision.
8. **Limitations** — what the system could not establish.
9. **Detailed evidence report** — available to authorized professional users.

### Professional workflow

**Artifact → secure ingestion → forensic engines → provenance → evidence graph → conflict analysis → evidence fusion → calibrated verdict → professional report → optional signed trust receipt**

Professional mode is intended for journalism, investigation, legal review, research, business/platform trust teams, and AI-agent integrations.

### Evidence-grade capabilities

- Evidence graph showing how signals contributed to the verdict.
- Per-signal status such as STRONG, MEDIUM, WEAK, NEGATIVE, CONFLICTING, or NOT_AVAILABLE.
- Cross-modal consistency checks for audio/video/visual relationships.
- Suspicious-region/frame references where an engine can safely localize evidence.
- Artifact hash and deterministic verification ID.
- Engine/model/protocol version inventory.
- Provenance and Content Credentials/C2PA status boundary.
- Reproducible JSON report contract.
- Human-readable professional report contract.
- Cryptographic trust-receipt boundary for future signing.
- Batch/API-ready result structure.
- Explicit limitations and abstention; no false certainty.

### Verdict semantics

**AUTHENTIC** means the active protocol found sufficient supporting evidence and no disqualifying contradictory evidence within its tested scope. It does not mean universal proof of truth.

**INAUTHENTIC** means the active protocol found sufficient converging evidence of manipulation, synthetic generation, or another defined authenticity failure within its tested scope.

**UNCERTAIN** means evidence is insufficient, unavailable, or materially contradictory. Professional users must be able to see which evidence caused the uncertainty.

### Percentage rule

A confidence value must never be displayed alone as:

> “87% real” or “12% fake”.

Instead:

> **INAUTHENTIC — Strong evidence**  
> Confidence: 87%  
> **Meaning:** Multiple independent forensic signals indicate that this artifact is likely manipulated or synthetic.

The exact numerical calibration is protocol-dependent and must be validated against benchmark data before being exposed as a probability-like statement.

### Professional report minimum

A professional report should contain:

- Verification ID
- Artifact SHA-256
- Verdict
- Confidence/evidence strength
- Plain-language conclusion
- Evidence items and signal status
- Detector agreement/disagreement
- Provenance status
- Protocol version
- Engine/model versions
- Timestamp
- Limitations
- Reproducibility information
- Trust-receipt/signature status, when available

The report must never imply government, legal, regulatory, or accreditation certification unless an authorized body has actually issued it.

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

## Free-first traffic mode

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

## Public identity and ownership-proof boundary

REALITYX exposes a machine-readable public identity document at
/.well-known/realityx-identity. It publishes the product identity,
operator display name, preferred domain and an explicit ownership status.

Ownership is **fail-closed**: the default state is unverified. A production
deployment must independently establish domain/account ownership before
configuring domain_verified or owner_verified. The public identity digest
makes changes to the published identity detectable without exposing secrets.

The identity layer is deliberately separate from verification results,
cryptographic receipts and external certification. A REALITYX badge must
never imply government, legal or regulatory certification unless an authorized
body has actually issued that certification.

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

Professional Verification Mode contract established. Premium 2050 foundation and gated roadmap remain in place. Advanced paid infrastructure is intentionally **not activated by default**. Current priority remains a stable, secure free-first verification core that can accumulate legitimate traffic before costly services are enabled.

## SEO and Google readiness

REALITYX treats SEO as part of the roadmap, not a last-minute submission step.

- Public, indexable routes are the only candidates for the sitemap.
- API, admin, owner and private operational paths are excluded from crawling.
- The canonical URL, sitemap URLs and production host must resolve to the same preferred origin.
- Next.js generates /sitemap.xml and /robots.txt from code so route changes can be reviewed with the roadmap instead of relying on manual edits.
- Production URL resolution uses NEXT_PUBLIC_SITE_URL when configured, otherwise Vercel's production URL; the local fallback is never intended as the production canonical.
- Before Google Search Console submission: production build/CI must be GREEN, canonical/robots/sitemap must be checked, redirects and duplicate hosts must be reviewed, and the public sitemap must be reachable.
- New public pages must add metadata, internal links and sitemap coverage together; private/API endpoints are never added to the sitemap.

## Global intelligence layer

REALITYX is designed to study the public, documented verification ecosystem rather than blindly integrate every AI product. The research surface covers AI tool capabilities and versions; image, video, voice and document forensic signals; public profile and social-media provenance; and trust standards such as C2PA/Content Credentials.

Research inputs are restricted to user-provided material, consented data, public content, documented public APIs, official documentation/release notes, public benchmarks and open standards. The system must not harvest credentials, access private messages/accounts, covertly track people, build unauthorized social graphs, or infer identity without a lawful/consented basis.

The current catalog is a policy boundary and adapter map, not a claim that every global AI tool is already connected. New providers/models are added through measured adapters: capability inventory → benchmark → limitation record → security review → gated deployment → capability fingerprint update.

Current industry direction reinforces this architecture: provenance systems such as C2PA and watermarking such as SynthID are useful layers, but no single signal is sufficient for absolute authenticity. REALITYX therefore keeps provenance, forensic signals, evidence fusion and uncertainty as separate layers.
