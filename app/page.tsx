"use client";

import { useRef, useState } from "react";

const languages = [
  ["en","English"],["hi","हिन्दी"],["mr","मराठी"],["es","Español"],["fr","Français"],
  ["de","Deutsch"],["pt","Português"],["ar","العربية"],["bn","বাংলা"],["ja","日本語"],
  ["ko","한국어"],["zh","中文"],["ru","Русский"],["it","Italiano"],["tr","Türkçe"],
];

const copy: Record<string,{eyebrow:string;title:string;lead:string;verify:string;language:string}> = {
  en:{eyebrow:"REALITY VERIFICATION INFRASTRUCTURE",title:"Verify what’s real.",lead:"Evidence-first verification for people, platforms, institutions and AI agents.",verify:"Verify now",language:"Language"},
  hi:{eyebrow:"रियलिटी वेरिफिकेशन इन्फ्रास्ट्रक्चर",title:"जो वास्तविक है, उसे सत्यापित करें।",lead:"लोगों, प्लेटफ़ॉर्म, संस्थानों और AI agents के लिए evidence-first verification.",verify:"अभी सत्यापित करें",language:"भाषा"},
  mr:{eyebrow:"रिअॅलिटी व्हेरिफिकेशन इन्फ्रास्ट्रक्चर",title:"जे खरं आहे ते सत्यापित करा.",lead:"व्यक्ती, प्लॅटफॉर्म, संस्था आणि AI agents साठी evidence-first verification.",verify:"आता सत्यापित करा",language:"भाषा"},
  es:{eyebrow:"INFRAESTRUCTURA DE VERIFICACIÓN",title:"Verifica lo que es real.",lead:"Verificación basada en evidencia para personas, plataformas, instituciones y agentes de IA.",verify:"Verificar ahora",language:"Idioma"},
  fr:{eyebrow:"INFRASTRUCTURE DE VÉRIFICATION",title:"Vérifiez ce qui est réel.",lead:"Vérification fondée sur les preuves pour les personnes, plateformes, institutions et agents IA.",verify:"Vérifier maintenant",language:"Langue"},
  de:{eyebrow:"INFRASTRUKTUR ZUR REALITÄTSPRÜFUNG",title:"Prüfen Sie, was echt ist.",lead:"Beweisbasierte Prüfung für Menschen, Plattformen, Institutionen und KI-Agenten.",verify:"Jetzt prüfen",language:"Sprache"},
  pt:{eyebrow:"INFRAESTRUTURA DE VERIFICAÇÃO",title:"Verifique o que é real.",lead:"Verificação baseada em evidências para pessoas, plataformas, instituições e agentes de IA.",verify:"Verificar agora",language:"Idioma"},
  ar:{eyebrow:"بنية التحقق من الواقع",title:"تحقق مما هو حقيقي.",lead:"تحقق قائم على الأدلة للأفراد والمنصات والمؤسسات ووكلاء الذكاء الاصطناعي.",verify:"تحقق الآن",language:"اللغة"},
  bn:{eyebrow:"রিয়েলিটি ভেরিফিকেশন অবকাঠামো",title:"যা সত্য, তা যাচাই করুন।",lead:"মানুষ, প্ল্যাটফর্ম, প্রতিষ্ঠান এবং AI এজেন্টদের জন্য প্রমাণভিত্তিক যাচাই।",verify:"এখন যাচাই করুন",language:"ভাষা"},
  ja:{eyebrow:"リアリティ検証インフラ",title:"本物かどうかを確かめる。",lead:"人、プラットフォーム、組織、AIエージェントのための証拠ベース検証。",verify:"今すぐ検証",language:"言語"},
  ko:{eyebrow:"리얼리티 검증 인프라",title:"진짜인지 검증하세요.",lead:"사람, 플랫폼, 기관 및 AI 에이전트를 위한 증거 기반 검증.",verify:"지금 검증",language:"언어"},
  zh:{eyebrow:"数字现实验证基础设施",title:"验证真实。",lead:"面向个人、平台、机构和 AI 智能体的证据优先验证。",verify:"立即验证",language:"语言"},
  ru:{eyebrow:"ИНФРАСТРУКТУРА ПРОВЕРКИ РЕАЛЬНОСТИ",title:"Проверьте, что реально.",lead:"Проверка на основе доказательств для людей, платформ, организаций и ИИ-агентов.",verify:"Проверить сейчас",language:"Язык"},
  it:{eyebrow:"INFRASTRUTTURA DI VERIFICA",title:"Verifica ciò che è reale.",lead:"Verifica basata su prove per persone, piattaforme, istituzioni e agenti IA.",verify:"Verifica ora",language:"Lingua"},
  tr:{eyebrow:"GERÇEKLİK DOĞRULAMA ALTYAPISI",title:"Gerçek olanı doğrula.",lead:"İnsanlar, platformlar, kurumlar ve yapay zekâ ajanları için kanıt tabanlı doğrulama.",verify:"Şimdi doğrula",language:"Dil"},
};

const media = [
  ["IMAGE","Photos · edits · provenance","available"],
  ["VIDEO","Frames · deepfake signals","planned"],
  ["AUDIO","Voice · synthetic signals","planned"],
  ["DOCUMENT","Aadhaar · PAN · Passport · Visa","planned"],
  ["URL","Source · domain context","planned"],
];

const principles = [
  ["01","FAST SCAN","Integrity, hash and basic signals first."],
  ["02","DEEP ANALYSIS","Specialist engines when production-ready."],
  ["03","EVIDENCE FUSION","Independent signals combined conservatively."],
  ["04","DECISION","VERIFIED · INAUTHENTIC · UNCERTAIN"],
];

const trust = [
  ["Evidence first","Independent signals are preferred over a single model."],
  ["Uncertainty allowed","Conflicts and missing evidence can remain UNCERTAIN."],
  ["Cryptographic proof","Receipts bind results to the exact verified artifact."],
  ["Provider neutral","External engines can be added without changing the trust layer."],
];

type Result = { verification_id?:string; sha256?:string; result?:string; confidence?:number };

export default function Home(){
  const inputRef=useRef<HTMLInputElement>(null);
  const [lang,setLang]=useState("en");
  const [fileName,setFileName]=useState("");
  const [checking,setChecking]=useState(false);
  const [stage,setStage]=useState("");
  const [result,setResult]=useState<Result|null>(null);
  const [error,setError]=useState("");
  const t=copy[lang]||copy.en;

  function selectFile(file?:File){
    if(!file || !["image/jpeg","image/png","image/webp"].includes(file.type)) return;
    const dt=new DataTransfer(); dt.items.add(file);
    if(inputRef.current) inputRef.current.files=dt.files;
    setFileName(file.name); setResult(null); setError("");
  }

  async function verify(){
    const file=inputRef.current?.files?.[0];
    if(!file){inputRef.current?.click();return}
    setChecking(true);setStage("Preparing secure verification…");setError("");setResult(null);
    try{
      const apiBase=process.env.NEXT_PUBLIC_REALITYX_API_URL;
      if(!apiBase) throw new Error("Verification service is not connected yet.");
      const form=new FormData();form.append("file",file);
      setStage("Checking integrity and evidence…");
      const response=await fetch(`${apiBase.replace(/\/$/,"")}/v1/verify/image`,{method:"POST",headers:{"Idempotency-Key":crypto.randomUUID()},body:form});
      const body=await response.json().catch(()=>({}));
      if(!response.ok) throw new Error(body.detail||"Verification could not be completed.");
      setStage("Finalizing decision…");setResult(body);
    }catch(err){setError(err instanceof Error?err.message:"Verification could not be completed.")}
    finally{setChecking(false);setStage("")}
  }

  return <main>
    <nav className="nav">
      <a className="brand" href="#"><span className="mark">R×</span><span>REALITYX</span></a>
      <div className="navlinks"><a href="#verify">Verify</a><a href="#how">How it works</a><a href="#trust">Trust</a><a href="#plans">Plans</a></div>
      <div className="navActions">
        <label className="language"><span>◎</span><select aria-label={t.language} value={lang} onChange={e=>setLang(e.target.value)}>{languages.map(([id,name])=><option value={id} key={id}>{name}</option>)}</select></label>
        <button className="ghost">Sign in</button>
      </div>
    </nav>

    <section className="hero" id="verify">
      <div className="heroGlow"/>
      <div className="eyebrow">{t.eyebrow}</div>
      <h1>{t.title}</h1>
      <p className="lead">{t.lead}</p>
      <div className="heroTrust"><span>● Evidence-first</span><span>● Privacy-minded</span><span>● Provider-neutral</span><span>● No forced certainty</span></div>

      <div className="verifyCard">
        <div className="drop" role="button" tabIndex={0} onKeyDown={e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();inputRef.current?.click()}}} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();selectFile(e.dataTransfer.files?.[0])}} onClick={()=>inputRef.current?.click()}>
          <div className="uploadIcon">↑</div>
          <h2>{checking?(stage||"Verifying…"):"Choose evidence to verify"}</h2>
          <p>Images now supported · PDF, video, audio, ZIP and folder workflows are added as production modules</p>
          <input ref={inputRef} hidden type="file" accept="image/jpeg,image/png,image/webp" onChange={e=>selectFile(e.target.files?.[0])}/>
          {fileName&&<div className="filename">{fileName}</div>}
        </div>
        <button className="primary" onClick={verify} disabled={checking}>{checking?"Analyzing…":t.verify}<span>→</span></button>
        {error&&<div className="verifyError" role="alert">{error}</div>}
        {result&&<div className="verifyResult" aria-live="polite">
          <div className="resultTop"><span className="statusDot"/><b>{result.result??"UNCERTAIN"}</b>{typeof result.confidence==="number"&&<span>{Math.round(result.confidence*100)}% confidence</span>}</div>
          {result.sha256&&<code>{result.sha256}</code>}
          {result.verification_id&&<small>Verification ID: {result.verification_id}</small>}
          <div className="decision"><b>{result.result==="UNCERTAIN"?"Do not force a yes/no decision.":"Use the result with source and provenance context."}</b><span>Evidence reviewed · confidence shown · uncertainty preserved</span></div>
        </div>}
        {!result&&!error&&<div className="privacy">Fast path · evidence first · uncertainty reported</div>}
      </div>
    </section>

    <section className="mediaStrip" id="verify-types" aria-label="Verification types">
      {media.map(([name,desc,status])=><button className="mediaCard" key={name} type="button" disabled={status!=="available"} aria-label={status==="available"?`Verify ${name}`:`${name} verification planned`} onClick={()=>{if(status==="available"){document.getElementById("verify")?.scrollIntoView({behavior:"smooth"});inputRef.current?.click()}}}>
        <span className="mediaIcon">{name==="IMAGE"?"◈":name==="VIDEO"?"▶":name==="AUDIO"?"◉":name==="DOCUMENT"?"▤":"⌁"}</span>
        <span className="mediaCopy"><b>{name}</b><small>{desc}</small></span><span className="mediaStatus">{status==="available"?"AVAILABLE":"PLANNED"}</span><span className="mediaArrow">→</span>
      </button>)}
    </section>

    <section className="section" id="how">
      <div className="sectionHead"><div><div className="eyebrow">HOW IT WORKS</div><h2>Simple on the surface.<br/>Serious underneath.</h2></div><p>REALITYX keeps the user path short while the trust architecture stays evidence-driven. Production capabilities appear only after they are implemented and verified.</p></div>
      <div className="flow">{principles.map(([n,title,desc],i)=><div className="flowItem" key={n}><span>{n}</span><b>{title}</b><p>{desc}</p>{i<principles.length-1&&<i>→</i>}</div>)}</div>
    </section>

    <section className="section" id="trust">
      <div className="sectionHead"><div><div className="eyebrow">TRUST LAYER</div><h2>Evidence before certainty.</h2></div><p>Designed for high-stakes digital reality checks without pretending that a visual signal alone proves identity, origin or legal authenticity.</p></div>
      <div className="trustGrid">{trust.map(([title,desc])=><div className="trustCard" key={title}><span>◆</span><b>{title}</b><p>{desc}</p></div>)}</div>
    </section>

    <section className="section compact">
      <div className="sectionHead"><div><div className="eyebrow">2050 READY FOUNDATION</div><h2>Built to grow without rebuilding trust.</h2></div><p>Multimodal forensics, C2PA/provenance, signed receipts, key lifecycle, AI-agent trust and auditability can plug into the same evidence boundary.</p></div>
      <div className="capLine"><span>CRYPTOGRAPHIC RECEIPTS</span><span>KEY TRUST & REVOCATION</span><span>C2PA / PROVENANCE</span><span>AI-AGENT TRUST API</span><span>AUDIT & REPRODUCIBILITY</span></div>
    </section>

    <section className="plans" id="plans">
      <div className="planIntro"><div className="eyebrow">ACCESS</div><h2>Free first.<br/>Power when needed.</h2><p>Keep the first experience simple. Advanced engines, history and business controls can be introduced as they become production-ready.</p></div>
      <div className="plan"><b>FREE</b><h3>Essential verification</h3><p>Core evidence-first workflow.</p><button className="planButton">Start free →</button></div>
      <div className="plan premium"><b>PREMIUM</b><h3>Advanced verification</h3><p>Deeper analysis, reports and controlled history.</p><button className="planButton">Explore →</button></div>
      <div className="plan"><b>BUSINESS</b><h3>Verification infrastructure</h3><p>API, teams, audit and usage controls.</p><button className="planButton">Contact →</button></div>
    </section>

    <section className="languageBand">
      <div><div className="eyebrow">GLOBAL BY DESIGN</div><h2>One trust language.<br/>Many local languages.</h2><p>Interface localization stays separate from evidence logic so global expansion does not change the underlying verification protocol.</p></div>
      <div className="languageCloud">{languages.map(([id,name])=><button key={id} onClick={()=>setLang(id)} className={lang===id?"active":""}>{name}</button>)}</div>
    </section>

    <footer><div className="brand"><span className="mark">R×</span><span>REALITYX</span></div><span>VERIFY WHAT’S REAL.</span><span>© 2026 · Evidence, not blind certainty.</span></footer>
  </main>;
}
