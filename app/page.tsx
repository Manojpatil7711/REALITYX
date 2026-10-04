"use client";

import { useRef, useState } from "react";

const languages = [
  ["en","English"],["hi","हिन्दी"],["mr","मराठी"],["es","Español"],["fr","Français"],
  ["de","Deutsch"],["pt","Português"],["ar","العربية"],["bn","বাংলা"],["ja","日本語"],
  ["ko","한국어"],["zh","中文"],["ru","Русский"],["it","Italiano"],["tr","Türkçe"],
];

const ui: Record<string, {eyebrow:string; title:string; lead:string; verify:string; free:string; premium:string; business:string; language:string}> = {
  en:{eyebrow:"REALITY VERIFICATION INFRASTRUCTURE",title:"Verify what’s real.",lead:"A global evidence layer for digital reality — built for people, platforms, institutions and AI agents.",verify:"Verify now",free:"Free",premium:"Premium",business:"Business",language:"Language"},
  hi:{eyebrow:"रियलिटी वेरिफिकेशन इन्फ्रास्ट्रक्चर",title:"जो वास्तविक है, उसे सत्यापित करें।",lead:"डिजिटल दुनिया के लिए वैश्विक प्रमाण-आधारित सत्यापन परत।",verify:"अभी सत्यापित करें",free:"फ्री",premium:"प्रीमियम",business:"बिज़नेस",language:"भाषा"},
  mr:{eyebrow:"रिअॅलिटी व्हेरिफिकेशन इन्फ्रास्ट्रक्चर",title:"जे खरं आहे ते सत्यापित करा.",lead:"डिजिटल वास्तवासाठी जागतिक evidence layer — व्यक्ती, प्लॅटफॉर्म, संस्था आणि AI agents साठी.",verify:"आता सत्यापित करा",free:"मोफत",premium:"प्रीमियम",business:"बिझनेस",language:"भाषा"},
  es:{eyebrow:"INFRAESTRUCTURA DE VERIFICACIÓN",title:"Verifica lo que es real.",lead:"Una capa global de evidencia para la realidad digital.",verify:"Verificar ahora",free:"Gratis",premium:"Premium",business:"Empresa",language:"Idioma"},
  fr:{eyebrow:"INFRASTRUCTURE DE VÉRIFICATION",title:"Vérifiez ce qui est réel.",lead:"Une couche mondiale de preuves pour la réalité numérique.",verify:"Vérifier maintenant",free:"Gratuit",premium:"Premium",business:"Entreprise",language:"Langue"},
  de:{eyebrow:"INFRASTRUKTUR ZUR REALITÄTSPRÜFUNG",title:"Prüfen Sie, was echt ist.",lead:"Eine globale Beweisebene für die digitale Realität.",verify:"Jetzt prüfen",free:"Kostenlos",premium:"Premium",business:"Business",language:"Sprache"},
  pt:{eyebrow:"INFRAESTRUTURA DE VERIFICAÇÃO",title:"Verifique o que é real.",lead:"Uma camada global de evidências para a realidade digital.",verify:"Verificar agora",free:"Grátis",premium:"Premium",business:"Empresarial",language:"Idioma"},
  ar:{eyebrow:"بنية التحقق من الواقع",title:"تحقق مما هو حقيقي.",lead:"طبقة أدلة عالمية للواقع الرقمي.",verify:"تحقق الآن",free:"مجاني",premium:"مميز",business:"للأعمال",language:"اللغة"},
  bn:{eyebrow:"রিয়েলিটি ভেরিফিকেশন অবকাঠামো",title:"যা সত্য, তা যাচাই করুন।",lead:"ডিজিটাল বাস্তবতার জন্য একটি বৈশ্বিক প্রমাণ-ভিত্তিক স্তর।",verify:"এখন যাচাই করুন",free:"ফ্রি",premium:"প্রিমিয়াম",business:"ব্যবসা",language:"ভাষা"},
  ja:{eyebrow:"リアリティ検証インフラ",title:"本物かどうかを確かめる。",lead:"デジタル世界のためのグローバルな証拠検証レイヤー。",verify:"今すぐ検証",free:"無料",premium:"プレミアム",business:"ビジネス",language:"言語"},
  ko:{eyebrow:"리얼리티 검증 인프라",title:"진짜인지 검증하세요.",lead:"디지털 현실을 위한 글로벌 증거 검증 계층입니다.",verify:"지금 검증",free:"무료",premium:"프리미엄",business:"비즈니스",language:"언어"},
  zh:{eyebrow:"数字现实验证基础设施",title:"验证真实。",lead:"面向个人、平台、机构和 AI 智能体的全球证据层。",verify:"立即验证",free:"免费",premium:"高级",business:"企业",language:"语言"},
  ru:{eyebrow:"ИНФРАСТРУКТУРА ПРОВЕРКИ РЕАЛЬНОСТИ",title:"Проверьте, что реально.",lead:"Глобальный слой доказательств для цифровой реальности.",verify:"Проверить сейчас",free:"Бесплатно",premium:"Премиум",business:"Бизнес",language:"Язык"},
  it:{eyebrow:"INFRASTRUTTURA DI VERIFICA",title:"Verifica ciò che è reale.",lead:"Un livello globale di prove per la realtà digitale.",verify:"Verifica ora",free:"Gratuito",premium:"Premium",business:"Business",language:"Lingua"},
  tr:{eyebrow:"GERÇEKLİK DOĞRULAMA ALTYAPISI",title:"Gerçek olanı doğrula.",lead:"Dijital gerçeklik için küresel kanıt katmanı.",verify:"Şimdi doğrula",free:"Ücretsiz",premium:"Premium",business:"Kurumsal",language:"Dil"},
};

const types=[["Image","Photo authenticity, manipulation and provenance"],["Video","Deepfake and media integrity signals"],["Audio","Synthetic voice and audio manipulation signals"],["Document","Tampering, structure and provenance"],["URL","Source, domain and content trust signals"]];
const premiumCapabilities=[["MULTIMODAL FORENSICS","Independent image, video, audio and document evidence engines."],["EVIDENCE FUSION","Conservative cross-signal reasoning with abstention when evidence conflicts."],["CRYPTOGRAPHIC ATTESTATION","Signed receipts bound to the exact artifact, protocol and verification time."],["KEY TRUST & REVOCATION","Registered signing keys, lifecycle controls and future transparency infrastructure."],["AI-AGENT TRUST API","Machine-readable verification results designed for policy-driven agent decisions."],["C2PA / PROVENANCE","Interoperability boundary for provenance-aware media and future standards."],["SECURITY-FIRST INGESTION","Parser validation, resource limits, isolated analysis and minimal retention."],["AUDIT & REPRODUCIBILITY","Versioned protocols, evidence provenance and reproducible verification records."]];
const securityLayers=[["01","ZERO-TRUST","Treat every upload, parser, model and external signal as untrusted."],["02","DEFENCE IN DEPTH","Layered limits, authentication, isolation, rate controls and integrity checks."],["03","CRYPTOGRAPHIC TRUST","Artifact hashes, signed receipts, registered keys and revocation-aware verification."],["04","AI SAFETY","No single-model truth claims; contradictory evidence can produce UNCERTAIN."],["05","FUTURE CONFORMANCE","Protocol versioning and explicit boundaries for audits, accreditation and certification."]];

type VerificationResult={verification_id?:string;sha256?:string;result?:string;confidence?:number};

export default function Home(){
 const inputRef=useRef<HTMLInputElement>(null); const [lang,setLang]=useState("en"); const [fileName,setFileName]=useState(""); const [checking,setChecking]=useState(false); const [stage,setStage]=useState(""); const [result,setResult]=useState<VerificationResult|null>(null); const [error,setError]=useState("");
 const t=ui[lang]||ui.en;
 async function verify(){const file=inputRef.current?.files?.[0];if(!file){inputRef.current?.click();return}setChecking(true);setStage("Preparing secure verification…");setError("");setResult(null);try{setStage("Checking integrity and provenance…");const apiBase=process.env.NEXT_PUBLIC_REALITYX_API_URL;if(!apiBase)throw new Error("Verification service is not connected yet.");const form=new FormData();form.append("file",file);await new Promise(r=>setTimeout(r,220));setStage("Fusing independent evidence…");const response=await fetch(`${apiBase.replace(/\/$/,"")}/v1/verify/image`,{method:"POST",headers:{"Idempotency-Key":crypto.randomUUID()},body:form});const body=await response.json().catch(()=>({}));if(!response.ok)throw new Error(body.detail||"Verification could not be completed.");setResult(body)}catch(err){setError(err instanceof Error?err.message:"Verification could not be completed.")}finally{setChecking(false);setStage("")}}
 return <main>
  <nav className="nav"><div className="brand"><span className="mark">R×</span> REALITYX</div><div className="navlinks"><a href="#how">How it works</a><a href="#plans">Plans</a><a href="#intelligence">Intelligence</a><a href="#security">Security</a></div><div className="navActions"><label className="language"><span>◎</span><select aria-label={t.language} value={lang} onChange={e=>setLang(e.target.value)}>{languages.map(([id,name])=><option value={id} key={id}>{name}</option>)}</select></label><button className="ghost">Sign in</button></div></nav>

  <section className="hero">
   <div className="heroGlow"/>
   <div className="eyebrow">{t.eyebrow}</div>
   <h1>{t.title}</h1>
   <p className="lead">{t.lead}</p>
   <div className="heroTrust">
    <span>● Evidence-first</span><span>● Privacy-minded</span><span>● Provider-neutral</span><span>● Uncertainty is allowed</span>
   </div>
   <div className="verifyCard">
    <div
     className="drop"
     role="button"
     tabIndex={0}
     onKeyDown={e => {
      if (e.key === "Enter" || e.key === " ") {
       e.preventDefault();
       inputRef.current?.click();
      }
     }}
     onDragOver={e => e.preventDefault()}
     onDrop={e => {
      e.preventDefault();
      const f = e.dataTransfer.files?.[0];
      if (f && f.type.startsWith("image/")) {
       const dt = new DataTransfer();
       dt.items.add(f);
       if (inputRef.current) inputRef.current.files = dt.files;
       setFileName(f.name);
       setResult(null);
       setError("");
      }
     }}
     onClick={() => inputRef.current?.click()}
    >
     <div className="uploadIcon">↑</div>
     <h2>{checking ? (stage || "Verifying…") : "Drop something to verify"}</h2>
     <p>Image verification is available first. More media and authority connectors are added as production services are verified.</p>
     <input
      ref={inputRef}
      hidden
      type="file"
      accept="image/jpeg,image/png,image/webp"
      onChange={e => {
       setFileName(e.target.files?.[0]?.name ?? "");
       setResult(null);
       setError("");
      }}
     />
     {fileName && <div className="filename">{fileName}</div>}
    </div>
    <button className="primary" onClick={verify} disabled={checking}>
     {checking ? "Analyzing…" : t.verify}<span>→</span>
    </button>
    {error && <div className="verifyError" role="alert">{error}</div>}
    {result && (
     <div className="verifyResult" aria-live="polite">
      <div className="resultTop">
       <span className="statusDot"/>
       <b>{result.result ?? "UNCERTAIN"}</b>
       {typeof result.confidence === "number" && <span>{Math.round(result.confidence * 100)}% confidence</span>}
      </div>
      {result.sha256 && <code>{result.sha256}</code>}
      {result.verification_id && <small>Verification ID: {result.verification_id}</small>}
      {result && (
       <div className="decisionPanel">
        <div className="decisionEyebrow">DECISION SUPPORT</div>
        <h3>{result.result === "AUTHENTIC" ? "Evidence supports authenticity." : result.result === "INAUTHENTIC" ? "Evidence indicates manipulation or inauthenticity." : "Evidence is not strong enough for a safe binary decision."}</h3>
        <p>{result.result === "AUTHENTIC" ? "Use this result as a verification signal, then consider provenance and source context before high-impact decisions." : result.result === "INAUTHENTIC" ? "Treat the item as high-risk until independently reviewed. Do not rely on it alone for legal, financial or safety-critical decisions." : "Do not force a yes/no conclusion. Seek additional independent evidence or human review."}</p>
        <div className="decisionActions">
         <span>✓ Evidence reviewed</span>
         <span>✓ Confidence shown</span>
         <span>✓ Uncertainty preserved</span>
        </div>
        <div className="decisionNext"><b>Recommended next step</b><span>{result.result === "UNCERTAIN" ? "Add independent evidence → review again" : "Check provenance + source context → decide"}</span></div>
       </div>
      )}
     </div>
    )}
    {!result && !error && (

     <>
      <div className="quickTrust">
       <span>FAST PATH</span><span>NO BLIND AI DECISION</span><span>ABSTAIN WHEN UNCERTAIN</span>
      </div>
      <div className="privacy">Private by design · Evidence first · Uncertainty is reported</div>
     </>
    )}
   </div>
  </section>

  <section className="controlCenter" aria-label="Verification Control Center">
   <div className="controlHead"><div><div className="eyebrow">VERIFICATION CONTROL CENTER</div><h2>Instant visibility. No hidden guesses.</h2></div><p>Every stage reflects the real verification pipeline. Unavailable production engines stay clearly marked instead of producing invented evidence.</p></div>
   <div className="controlTrack">
    <div className="controlStep active"><span>01</span><b>Fast Scan</b><small>Integrity · hash · basic signals</small></div>
    <div className="controlLine"/>
    <div className="controlStep"><span>02</span><b>Deep Scan</b><small>Advanced engines when connected</small></div>
    <div className="controlLine"/>
    <div className="controlStep"><span>03</span><b>Evidence Fusion</b><small>Independent evidence + abstention</small></div>
    <div className="controlLine"/>
    <div className="controlStep"><span>04</span><b>Risk</b><small>Policy-controlled risk assessment</small></div>
    <div className="controlLine"/>
    <div className="controlStep final"><span>05</span><b>Final Decision</b><small>Verified · Manipulated · Uncertain</small></div>
   </div>
   <div className="controlNote"><span className="statusDot"/><b>Current release:</b> image verification is the first live path. Deep media engines, external authority connectors and paid entitlements remain disabled until independently verified.</div>
  </section>

  <section className="decisionGuide" aria-label="Decision guide">
   <div className="sectionHead"><div><div className="eyebrow">MAKE A BETTER DECISION</div><h2>Clear evidence. Clear limits. Your decision.</h2></div><p>REALITYX separates verification from judgment. You see what the system found, how confident it is, what remains unknown, and what to do next.</p></div>
   <div className="decisionGrid">
    <div><span>01</span><b>SEE THE RESULT</b><p>AUTHENTIC, INAUTHENTIC or UNCERTAIN — never a forced binary answer.</p></div>
    <div><span>02</span><b>UNDERSTAND WHY</b><p>Evidence signals and confidence are shown before you act.</p></div>
    <div><span>03</span><b>CHECK THE LIMITS</b><p>Missing provenance, conflicts and unavailable engines stay visible.</p></div>
    <div><span>04</span><b>CHOOSE THE NEXT STEP</b><p>Verify more, seek independent evidence, or proceed when the evidence supports it.</p></div>
   </div>
  </section>
  <section className="types">{types.map(([name,desc])=><div className="type" key={name}><div className="dot"/><div><strong>{name}</strong><span>{desc}</span></div></div>)}</section>

  <section className="plans" id="plans"><div className="planIntro"><div className="eyebrow">SIMPLE ACCESS</div><h2>Free to start.<br/>Power when you need it.</h2><p>No confusing tiers. The core experience stays clear; advanced services unlock as they become production-ready.</p></div>
   <div className="plan"><div className="planTop"><b>{t.free}</b><span>START</span></div><h3>Essential verification</h3><p>Core checks and evidence-first results for everyday verification.</p><ul><li>Essential verification workflow</li><li>Evidence and uncertainty signals</li><li>No subscription required to explore</li></ul><button className="planButton">Use free →</button></div>
   <div className="plan premium"><div className="planTop"><b>{t.premium}</b><span>DEEPER TRUST</span></div><h3>Advanced verification</h3><p>Designed for deeper analysis, advanced evidence, reports and controlled history.</p><ul><li>Advanced analysis layers</li><li>Portable verification proof</li><li>Expanded history and reports</li></ul><button className="planButton">Explore Premium →</button></div>
   <div className="plan business"><div className="planTop"><b>{t.business}</b><span>API / TEAMS</span></div><h3>Verification infrastructure</h3><p>For platforms and organizations that need controlled workflows and API integration.</p><ul><li>API and team workflows</li><li>Audit and usage metering</li><li>Provider-neutral integrations</li></ul><button className="planButton">Talk to REALITYX →</button></div>
  </section>

  <section className="purpose"><div className="purposeHead"><div><div className="eyebrow">ONE CORE · MANY USE CASES</div><h2>Built for the moments when truth matters.</h2></div><p>Choose a purpose. The evidence-first core stays the same while the workflow becomes easier to understand.</p></div><div className="purposeGrid">{[["Government","Verification → evidence → human decision"],["Legal / Investigation","Preserve → analyze → attest → review"],["News / Media","Screen → inspect signals → publish with context"],["Business / Platform","Automate → fuse evidence → escalate uncertainty"],["Personal","Upload → verify → understand the evidence"]].map(([a,b])=><div className="purposeCard" key={a}><b>{a}</b><span>{b}</span></div>)}</div></section>

  <section className="intelligence" id="intelligence"><div className="sectionHead"><div><div className="eyebrow">GLOBAL INTELLIGENCE LAYER</div><h2>One trust language for a multilingual world.</h2></div><p>REALITYX is designed for global users, provider-neutral evidence and machine-readable verification — without turning the platform into a surveillance system.</p></div><div className="intelGrid">{[["AI TOOLS","Capabilities · versions · limitations"],["IMAGE","Pixels · metadata · edits · provenance"],["VIDEO","Frames · codec · temporal consistency"],["VOICE","Spectral signals · provenance · consistency"],["DOCUMENT","Structure · metadata · signatures"],["PROFILES","Public claims · provenance · consistency"],["SOCIAL MEDIA","Public context · reposts · timestamps"],["TRUST STANDARDS","C2PA · Content Credentials · signatures"]].map(([a,b])=><div className="intelCard" key={a}><span>◆</span><b>{a}</b><p>{b}</p></div>)}</div></section>

  <section className="explain" id="how"><div><div className="eyebrow">NOT A GUESS</div><h2>Evidence before certainty.</h2></div><p>REALITYX combines independent signals, provenance and forensic analysis instead of trusting a single AI model. When evidence conflicts, the system can say <strong>UNCERTAIN</strong> instead of forcing an answer.</p></section>
  <section className="layers"><div><span>01</span><b>Fast checks</b><p>Hash, metadata, provenance and integrity signals run first.</p></div><div><span>02</span><b>Evidence fusion</b><p>Independent engines are combined conservatively.</p></div><div><span>03</span><b>Deep verification</b><p>Expensive analysis is triggered only when it can improve the answer.</p></div></section>

  <section className="premium2050"><div className="sectionHead"><div><div className="eyebrow">PREMIUM 2050 ARCHITECTURE</div><h2>Designed for the next generation of digital trust.</h2></div><p>Capabilities become visible as production services only after implementation, tests and controls are verified.</p></div><div className="capGrid">{premiumCapabilities.map(([a,b])=><div className="cap" key={a}><span className="capMark">◆</span><div><b>{a}</b><p>{b}</p></div></div>)}</div></section>
  <section className="securitySection" id="security"><div className="sectionHead"><div><div className="eyebrow">SECURITY BY DESIGN</div><h2>Trust is engineered, not claimed.</h2></div><p>Owner control stays separate from operational roles. Providers submit evidence; REALITYX policy makes the final decision.</p></div><div className="securityGrid">{securityLayers.map(([n,a,b])=><div className="securityCard" key={n}><span>{n}</span><b>{a}</b><p>{b}</p></div>)}</div></section>

  <section className="languageBand"><div><div className="eyebrow">GLOBAL FROM DAY ONE</div><h2>Speak to the world.</h2><p>Interface language is independent from verification evidence. Localized UI can expand without changing the underlying trust protocol.</p></div><div className="languageCloud">{languages.map(([id,name])=><button key={id} onClick={()=>setLang(id)} className={lang===id?"active":""}>{name}</button>)}</div></section>

  <footer><div className="brand"><span className="mark">R×</span> REALITYX</div><span>VERIFY WHAT’S REAL.</span><span>© 2026 REALITYX · Evidence, not blind certainty.</span></footer>
 </main>
}
