"use client";

import { useRef, useState } from "react";

const types = [
  ["Image","Photo authenticity, manipulation and provenance"],
  ["Video","Deepfake and media integrity signals"],
  ["Audio","Synthetic voice and audio manipulation signals"],
  ["Document","Tampering, structure and provenance"],
  ["URL","Source, domain and content trust signals"],
];

const premiumCapabilities = [
  ["MULTIMODAL FORENSICS","Independent image, video, audio and document evidence engines."],
  ["EVIDENCE FUSION","Conservative cross-signal reasoning with abstention when evidence conflicts."],
  ["CRYPTOGRAPHIC ATTESTATION","Signed receipts bound to the exact artifact, protocol and verification time."],
  ["KEY TRUST & REVOCATION","Registered signing keys, lifecycle controls and future transparency infrastructure."],
  ["AI-AGENT TRUST API","Machine-readable verification results designed for policy-driven agent decisions."],
  ["C2PA / PROVENANCE","Interoperability boundary for provenance-aware media and future standards."],
  ["SECURITY-FIRST INGESTION","Parser validation, resource limits, isolated analysis and minimal retention."],
  ["AUDIT & REPRODUCIBILITY","Versioned protocols, evidence provenance and reproducible verification records."],
];

const securityLayers = [
  ["01","ZERO-TRUST","Treat every upload, parser, model and external signal as untrusted."],
  ["02","DEFENCE IN DEPTH","Layered limits, authentication, isolation, rate controls and integrity checks."],
  ["03","CRYPTOGRAPHIC TRUST","Artifact hashes, signed receipts, registered keys and revocation-aware verification."],
  ["04","AI SAFETY","No single-model truth claims; contradictory evidence can produce UNCERTAIN."],
  ["05","FUTURE CONFORMANCE","Protocol versioning and explicit boundaries for audits, accreditation and certification."],
];

type VerificationResult = {
  verification_id?: string;
  sha256?: string;
  result?: string;
  confidence?: number;
  evidence?: string[];
  signals?: unknown;
};

export default function Home() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName,setFileName] = useState("");
  const [checking,setChecking] = useState(false);
  const [result,setResult] = useState<VerificationResult | null>(null);
  const [error,setError] = useState("");

  async function verify() {
    const file = inputRef.current?.files?.[0];
    if (!file) { inputRef.current?.click(); return; }
    setChecking(true);
    setError("");
    setResult(null);

    try {
      const apiBase = process.env.NEXT_PUBLIC_REALITYX_API_URL;
      if (!apiBase) throw new Error("Verification service is not connected yet.");
      const form = new FormData();
      form.append("file", file);
      const response = await fetch(`${apiBase.replace(/\/$/, "")}/v1/verify/image`, {
        method: "POST",
        headers: { "Idempotency-Key": crypto.randomUUID() },
        body: form,
      });
      const body = await response.json().catch(() => ({}));
      if (!response.ok) throw new Error(body.detail || "Verification could not be completed.");
      setResult(body);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Verification could not be completed.");
    } finally {
      setChecking(false);
    }
  }

  return (
    <main>
      <nav className="nav">
        <div className="brand"><span className="mark">R</span> REALITYX</div>
        <div className="navlinks">
          <a href="#how">How it works</a>
          <a href="#intelligence">Intelligence</a>
          <a href="#premium">Premium 2050</a>
          <a href="#security">Security</a>
        </div>
        <button className="ghost">Sign in</button>
      </nav>

      <section className="hero">
        <div className="eyebrow">REALITY VERIFICATION INFRASTRUCTURE</div>
        <h1>Verify what’s real.</h1>
        <p className="lead">A future-ready evidence layer for digital reality — built for people, platforms, institutions and AI agents.</p>

        <div className="verifyCard">
          <div className="drop" onClick={()=>inputRef.current?.click()}>
            <div className="uploadIcon">↑</div>
            <h2>{checking ? "Verifying…" : "Drop something to verify"}</h2>
            <p>Start with an image. Video, audio, documents and URL verification are designed as the next adapters.</p>
            <input ref={inputRef} hidden type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>{setFileName(e.target.files?.[0]?.name ?? "");setResult(null);setError("");}} />
            {fileName && <div className="filename">{fileName}</div>}
          </div>
          <button className="primary" onClick={verify} disabled={checking}>{checking ? "Analyzing…" : "Verify now"}</button>
          {error && <div className="verifyError" role="alert">{error}</div>}
          {result && (
            <div className="verifyResult" aria-live="polite">
              <div className="resultTop"><span className="statusDot"/><b>{result.result ?? "UNCERTAIN"}</b>{typeof result.confidence === "number" && <span>{Math.round(result.confidence * 100)}% confidence</span>}</div>
              <p>Evidence is shown as a verification signal, not as an absolute truth claim.</p>
              {result.sha256 && <code>{result.sha256}</code>}
              {result.verification_id && <small>Verification ID: {result.verification_id}</small>}
            </div>
          )}
          {!result && !error && <div className="privacy">Private by design · Evidence first · Uncertainty is reported</div>}
        </div>
      </section>

      <section className="types">
        {types.map(([name,desc])=><div className="type" key={name}><div className="dot"/><div><strong>{name}</strong><span>{desc}</span></div></div>)}
      </section>

      <section className="purpose" aria-label="Choose your verification purpose">
        <div className="purposeHead">
          <div><div className="eyebrow">START WITHOUT CONFUSION</div><h2>Why are you here?</h2></div>
          <p>Choose the closest purpose. REALITYX keeps the same evidence-first engine underneath; only the workflow guidance changes.</p>
        </div>
        <div className="purposeGrid">
          <div className="purposeCard"><b>Government</b><span>Submitted material → verification → evidence → human decision</span></div>
          <div className="purposeCard"><b>Legal / Investigation</b><span>Preserve → analyze → attest → review</span></div>
          <div className="purposeCard"><b>News / Media</b><span>Screen → inspect signals → publish with context</span></div>
          <div className="purposeCard"><b>Business / Platform</b><span>Automate → fuse evidence → escalate uncertainty</span></div>
          <div className="purposeCard"><b>Personal</b><span>Upload → verify → understand the evidence</span></div>
        </div>
      </section>

      <section className="intelligence" id="intelligence">
        <div className="sectionHead">
          <div><div className="eyebrow">GLOBAL INTELLIGENCE LAYER</div><h2>Study the signal ecosystem — without becoming a surveillance system.</h2></div>
          <p>REALITYX can continuously compare documented AI capabilities, public provenance standards, media signals and user-supplied evidence. Private accounts, stolen credentials and unauthorized personal profiling stay outside the system.</p>
        </div>
        <div className="intelGrid">
          {[
            ["AI TOOLS","Capabilities · versions · limitations · benchmarks"],
            ["IMAGE","Pixels · metadata · edits · provenance · watermark"],
            ["VIDEO","Frames · codec · temporal consistency · provenance"],
            ["VOICE","Spectral signals · watermark · provenance · consistency"],
            ["DOCUMENT","Structure · metadata · signatures · tamper signals"],
            ["PROFILES","Public claims · provenance · content consistency"],
            ["SOCIAL MEDIA","Public context · reposts · timestamps · media integrity"],
            ["TRUST STANDARDS","C2PA · Content Credentials · signatures · key status"],
          ].map(([title,desc])=><div className="intelCard" key={title}><span>◆</span><b>{title}</b><p>{desc}</p></div>)}
        </div>
        <div className="intelRule"><b>Research rule</b><span>Public/documented sources + consented/user-provided material only. No credential harvesting, private-message access, covert tracking or identity inference.</span></div>
      </section>

      <section className="explain" id="how">
        <div><div className="eyebrow">NOT A GUESS</div><h2>Evidence before certainty.</h2></div>
        <p>REALITYX combines independent signals, provenance and forensic analysis instead of trusting a single AI model. Results can be verified, uncertain or likely inauthentic — with the evidence and limitations exposed.</p>
      </section>

      <section className="layers">
        <div><span>01</span><b>Fast checks</b><p>Hash, metadata, provenance and integrity signals run first.</p></div>
        <div><span>02</span><b>Evidence fusion</b><p>Independent engines run in parallel and are combined conservatively.</p></div>
        <div><span>03</span><b>Deep verification</b><p>Expensive analysis is triggered only when it can improve the answer.</p></div>
      </section>

      <section className="premium2050" id="premium">
        <div className="sectionHead">
          <div><div className="eyebrow">PREMIUM 2050 ARCHITECTURE</div><h2>Built for the next generation of digital trust.</h2></div>
          <p>Premium capabilities are designed as secure, independently gated layers. A capability is not advertised as active until its implementation, tests and production controls are verified.</p>
        </div>
        <div className="capGrid">
          {premiumCapabilities.map(([title,desc])=><div className="cap" key={title}><span className="capMark">◆</span><div><b>{title}</b><p>{desc}</p></div></div>)}
        </div>
        <div className="futureBanner"><div><span className="statusDot"/> <b>2050-ready principle</b></div><p>Protocol versioning, cryptographic receipts, revocation, reproducibility and explicit governance boundaries are foundational — not decorative promises.</p></div>
      </section>

      <section className="securitySection" id="security">
        <div className="sectionHead">
          <div><div className="eyebrow">TOP SECURITY BASELINE</div><h2>Security is part of the verification engine.</h2></div>
          <p>REALITYX follows a defence-in-depth model. High-risk components remain isolated, least-privileged and evidence-driven.</p>
        </div>
        <div className="securityGrid">
          {securityLayers.map(([num,title,desc])=><div className="securityCard" key={num}><span>{num}</span><b>{title}</b><p>{desc}</p></div>)}
        </div>
      </section>

      <section className="plans" id="plans">
        <div><div className="eyebrow">ACCESS MODEL</div><h2>Start free. Scale with trust.</h2></div>
        <div className="plan"><b>Free</b><p>Quick verification and essential evidence.</p></div>
        <div className="plan premium"><b>Premium</b><p>Deeper analysis, advanced evidence, reports and controlled history as the corresponding services become production-ready.</p></div>
        <div className="plan"><b>Business</b><p>Teams, API, audit workflows and controlled verification.</p></div>
      </section>

      <section className="developers" id="developers">
        <div><div className="eyebrow">BUILT TO SCALE</div><h2>One verification layer.<br/>Many industries.</h2></div>
        <p>Newsrooms, finance, insurance, marketplaces, legal workflows, government systems and future AI agents can connect through the same evidence-first core. Verification is separate from attestation, and attestation is separate from certification.</p>
      </section>

      <footer><div className="brand"><span className="mark">R</span> REALITYX</div><span>VERIFY WHAT’S REAL.</span><span>© 2026 REALITYX</span></footer>
    </main>
  );
}
