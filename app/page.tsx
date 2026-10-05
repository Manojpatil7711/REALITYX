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

const accepted = ["image/jpeg","image/png","image/webp","application/pdf","video/mp4","video/quicktime","video/webm","audio/mpeg","audio/wav","audio/x-wav","audio/mp4","audio/x-m4a","application/zip"];
type Result = {
  verification_id?:string; sha256?:string; result?:string; confidence?:number; signals?:Array<{evidence_id?:string;signal?:string;status?:string;summary?:string;confidence?:number;engine_version?:string}>; evidence?:Array<{evidence_id?:string;signal?:string;status?:string;summary?:string;confidence?:number;engine_version?:string}>;
  document_type?:string; authority_status?:string; risk_level?:string;
  evidence_graph_digest?:string; receipt_digest?:string; cryptographic_valid?:boolean;
  independent_source_count?:number; conflict?:boolean; copy_status?:string;
};

export default function Home(){
  const inputRef=useRef<HTMLInputElement>(null);
  const folderRef=useRef<HTMLInputElement>(null);
  const [lang,setLang]=useState("en");
  const [files,setFiles]=useState<File[]>([]);
  const [checking,setChecking]=useState(false);
  const [stage,setStage]=useState("");
  const [result,setResult]=useState<Result|null>(null);
  const [error,setError]=useState("");
  const resultRef=useRef<HTMLDivElement>(null);
  const t=copy[lang]||copy.en;

  function addFiles(list:FileList|null){
    if(!list?.length) return;
    const incoming=Array.from(list);
    const valid=incoming.filter(file=>accepted.includes(file.type)||/\.(pdf|png|jpe?g|webp|mp4|mov|webm|mp3|wav|m4a|zip)$/i.test(file.name));
    if(!valid.length){setError("No supported evidence files were selected.");return}
    setFiles(valid);setResult(null);setError("");
  }

  function selectFile(file?:File){
    if(!file) return;
    const transfer=new DataTransfer();
    transfer.items.add(file);
    addFiles(transfer.files);
  }

  function imageFile(){
    return files.find(file=>["image/jpeg","image/png","image/webp"].includes(file.type));
  }

  function downloadReceipt(){
    if(!result) return;
    const receipt={
      issuer:"REALITYX",
      protocol_version:"1.0",
      verification_id:result.verification_id,
      artifact_sha256:result.sha256,
      result:result.result,
      confidence:result.confidence,
      evidence_graph_digest:result.evidence_graph_digest,
      receipt_digest:result.receipt_digest,
      cryptographic_valid:result.cryptographic_valid,
      exported_at:new Date().toISOString(),
    };
    const blob=new Blob([JSON.stringify(receipt,null,2)],{type:"application/json"});
    const url=URL.createObjectURL(blob);
    const anchor=document.createElement("a");
    anchor.href=url;
    anchor.download=`realityx-${result.verification_id||"verification"}-receipt.json`;
    anchor.click();
    URL.revokeObjectURL(url);
  }

  function printResult(){
    if(!result) return;
    window.print();
  }

  async function verify(){
    const file=imageFile();
    if(!file){
      setError("This evidence type is not connected to the live verification engine yet.");
      return;
    }
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

  const imageCount=files.filter(f=>["image/jpeg","image/png","image/webp"].includes(f.type)).length;
  const pdfCount=files.filter(f=>f.type==="application/pdf"||/\.pdf$/i.test(f.name)).length;
  const videoCount=files.filter(f=>f.type.startsWith("video/")).length;
  const audioCount=files.filter(f=>f.type.startsWith("audio/")).length;
  const zipCount=files.filter(f=>f.type==="application/zip"||/\.zip$/i.test(f.name)).length;

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
        <div className="drop" role="button" tabIndex={0} onKeyDown={e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();inputRef.current?.click()}}} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();addFiles(e.dataTransfer.files)}} onClick={()=>inputRef.current?.click()}>
          <div className="uploadIcon">↑</div>
          <h2>{checking?(stage||"Verifying…"):"Choose evidence to verify"}</h2>
          <p>Images, PDF, video, audio and ZIP accepted for intake · drag & drop supported</p>
          <input ref={inputRef} hidden type="file" multiple accept=".jpg,.jpeg,.png,.webp,.pdf,.mp4,.mov,.webm,.mp3,.wav,.m4a,.zip" onChange={e=>addFiles(e.target.files)}/>
          <input ref={folderRef} hidden type="file" multiple {...({webkitdirectory:""} as React.InputHTMLAttributes<HTMLInputElement>)} onChange={e=>addFiles(e.target.files)}/>
          {files.length>0&&<div className="filename">{files.length} evidence file{files.length===1?"":"s"} selected</div>}
        </div>
        <div className="intakeActions">
          <button className="secondary" type="button" onClick={()=>inputRef.current?.click()}>Choose files</button>
          <button className="secondary" type="button" onClick={()=>folderRef.current?.click()}>Choose folder</button>
        </div>
        {files.length>0&&<div className="intakeSummary" aria-live="polite">
          {imageCount>0&&<span>IMAGE {imageCount}</span>}{pdfCount>0&&<span>PDF {pdfCount}</span>}{videoCount>0&&<span>VIDEO {videoCount}</span>}{audioCount>0&&<span>AUDIO {audioCount}</span>}{zipCount>0&&<span>ZIP {zipCount}</span>}
        </div>}
        <button className="primary" onClick={verify} disabled={checking}>{checking?"Analyzing…":t.verify}<span>→</span></button>
        {error&&<div className="verifyError" role="alert">{error}</div>}
        {result&&(()=>{
          const verdict=(result.result??"UNCERTAIN").toUpperCase();
          const tone=verdict==="VERIFIED"||verdict==="AUTHENTIC"?"verified":verdict==="INAUTHENTIC"||verdict==="MANIPULATED"||verdict==="AI_GENERATED"?"inauthentic":"uncertain";
          const label=tone==="verified"?"Verified":tone==="inauthentic"?"Inauthentic":"Uncertain";
          return <div ref={resultRef} className={`verifyResult trustResult ${tone}`} aria-live="polite">
            <div className="trustResultHeader">
              <div className="trustVerdict"><span className="statusDot"/><b>{label}</b></div>
              {typeof result.confidence==="number"&&<div className="confidence"><strong>{Math.round(result.confidence*100)}%</strong><span>confidence</span></div>}
            </div>
            <p className="trustSummary">{tone==="verified"?"Available evidence supports this result.":tone==="inauthentic"?"Available evidence indicates authenticity concerns.":"Evidence is not strong enough for a reliable yes/no decision."}</p>
            <div className="resultGrid">
              {result.document_type&&<div><small>Document type</small><b>{result.document_type}</b></div>}
              {result.copy_status&&<div><small>Copy / Xerox</small><b>{result.copy_status.replaceAll("_"," ")}</b></div>}
              {result.authority_status&&<div><small>Authority check</small><b>{result.authority_status.replaceAll("_"," ")}</b></div>}
              {result.risk_level&&<div><small>Risk level</small><b>{result.risk_level}</b></div>}
              {typeof result.independent_source_count==="number"&&<div><small>Independent sources</small><b>{result.independent_source_count}</b></div>}
              <div><small>Conflict</small><b>{result.conflict?"Detected":"None detected"}</b></div>
            </div>
            <div id="evidence-summary" className="evidenceNote"><span>✓</span><div><b>Evidence reviewed</b><small>Confidence is shown transparently. Uncertainty is never hidden.</small></div></div>
            {(()=>{
              const items=(result.evidence?.length?result.evidence:result.signals)||[];
              if(!items.length) return null;
              return <div className="evidenceList" aria-label="Evidence details">
                {items.slice(0,12).map((item,index)=><div className="evidenceItem" key={item.evidence_id||index}>
                  <div><b>{item.signal||"Evidence signal"}</b><small>{item.summary||"No summary supplied."}</small></div>
                  <span>{item.status||"available"}{typeof item.confidence==="number"?" · "+Math.round(item.confidence*100)+"%":""}</span>
                </div>)}
              </div>;
            })()}
            <div className="receipt">
              <div className="receiptTitle"><span>REALITYX TRUST RECEIPT</span>{result.cryptographic_valid&&<b>✓ Cryptographically valid</b>}</div>
              {result.verification_id&&<div><small>Verification ID</small><code>{result.verification_id}</code></div>}
              {result.sha256&&<div><small>Artifact SHA-256</small><code>{result.sha256}</code></div>}
              {result.evidence_graph_digest&&<div><small>Evidence digest</small><code>{result.evidence_graph_digest}</code></div>}
              {result.receipt_digest&&<div><small>Receipt digest</small><code>{result.receipt_digest}</code></div>}
            </div>
            <div className="resultActions"><button type="button" onClick={()=>resultRef.current?.querySelector("#evidence-summary")?.scrollIntoView({behavior:"smooth",block:"nearest"})}>View evidence</button><button type="button" onClick={downloadReceipt}>Download receipt</button><button type="button" onClick={printResult}>Print</button></div>
          </div>;
        })()}
        {!result&&!error&&<div className="privacy">Fast intake · evidence first · no silent certainty</div>}
      </div>
    </section>

    <section className="mediaStrip" id="verify-types" aria-label="Verification types">
      {media.map(([name,desc,status])=><button className="mediaCard" key={name} type="button" disabled={status!=="available"} aria-label={status==="available"?`Verify ${name}`:`${name} verification is not connected`} onClick={()=>{if(status==="available")inputRef.current?.click()}}>
        <span className="mediaIcon">{name==="IMAGE"?"◈":name==="VIDEO"?"▶":name==="AUDIO"?"◉":name==="DOCUMENT"?"▤":"⌁"}</span>
        <span className="mediaCopy"><b>{name}</b><small>{desc}</small></span><span className="mediaStatus">{status==="available"?"AVAILABLE":"NOT CONNECTED"}</span><span className="mediaArrow">→</span>
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
