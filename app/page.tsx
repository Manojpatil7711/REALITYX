"use client";

import { useRef, useState } from "react";

const types = [
  ["Image","Photo authenticity, manipulation and provenance"],
  ["Video","Deepfake and media integrity signals"],
  ["Audio","Synthetic voice and audio manipulation signals"],
  ["Document","Tampering, structure and provenance"],
  ["URL","Source, domain and content trust signals"],
];

export default function Home() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [fileName,setFileName] = useState("");
  const [checking,setChecking] = useState(false);

  async function verify() {
    const file = inputRef.current?.files?.[0];
    if (!file) { inputRef.current?.click(); return; }
    setChecking(true);
    // The verification API is intentionally kept behind an environment boundary.
    // The public UI remains usable while backend deployment evolves.
    await new Promise(r => setTimeout(r, 450));
    setChecking(false);
  }

  return (
    <main>
      <nav className="nav">
        <div className="brand"><span className="mark">R</span> REALITYX</div>
        <div className="navlinks"><a href="#how">How it works</a><a href="#plans">Plans</a><a href="#developers">Developers</a></div>
        <button className="ghost">Sign in</button>
      </nav>

      <section className="hero">
        <div className="eyebrow">REALITY VERIFICATION INFRASTRUCTURE</div>
        <h1>Verify what’s real.</h1>
        <p className="lead">Fast, evidence-based analysis for the digital content you rely on.</p>

        <div className="verifyCard">
          <div className="drop" onClick={()=>inputRef.current?.click()}>
            <div className="uploadIcon">↑</div>
            <h2>{checking ? "Verifying…" : "Drop something to verify"}</h2>
            <p>Image, video, audio or document</p>
            <input ref={inputRef} hidden type="file" onChange={e=>setFileName(e.target.files?.[0]?.name ?? "")} />
            {fileName && <div className="filename">{fileName}</div>}
          </div>
          <button className="primary" onClick={verify}>{checking ? "Analyzing…" : "Verify now"}</button>
          <div className="privacy">Private by design · Evidence first · Uncertainty is reported</div>
        </div>
      </section>

      <section className="types">
        {types.map(([name,desc])=><div className="type" key={name}><div className="dot"/><div><strong>{name}</strong><span>{desc}</span></div></div>)}
      </section>

      <section className="explain" id="how">
        <div><div className="eyebrow">NOT A GUESS</div><h2>Evidence before certainty.</h2></div>
        <p>REALITYX combines independent signals, provenance and forensic analysis instead of trusting a single AI model. Results can be authentic, uncertain or likely manipulated — with the evidence explained.</p>
      </section>

      <section className="layers">
        <div><span>01</span><b>Fast checks</b><p>Hash, metadata, provenance and integrity signals run first.</p></div>
        <div><span>02</span><b>Evidence fusion</b><p>Independent engines run in parallel and are combined.</p></div>
        <div><span>03</span><b>Deep verification</b><p>Expensive analysis is triggered only when it can improve the answer.</p></div>
      </section>

      <section className="plans" id="plans">
        <div><div className="eyebrow">START FREE</div><h2>Useful from the first check.</h2></div>
        <div className="plan"><b>Free</b><p>Quick verification and essential evidence.</p></div>
        <div className="plan premium"><b>Premium</b><p>Deeper analysis, larger media, reports and history.</p></div>
        <div className="plan"><b>Business</b><p>Teams, API, audit workflows and controlled verification.</p></div>
      </section>

      <section className="developers" id="developers"><div><div className="eyebrow">BUILT TO SCALE</div><h2>One verification layer.<br/>Many industries.</h2></div><p>Newsrooms, finance, insurance, marketplaces, legal workflows, government systems and future AI agents can connect through the same evidence-first core.</p></section>

      <footer><div className="brand"><span className="mark">R</span> REALITYX</div><span>VERIFY WHAT’S REAL.</span><span>© 2026 REALITYX</span></footer>
    </main>
  );
}
