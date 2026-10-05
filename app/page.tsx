"use client";

import { useEffect, useRef, useState } from "react";

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


const uiCopy: Record<string, Record<string,string>> = {"en":{"verify":"Verify","how":"How it works","trust":"Trust","plans":"Plans","signin":"Sign in","choose":"Choose evidence to verify","accepted":"Images, PDF, video, audio and ZIP accepted for intake · drag & drop supported","files":"Choose files","folder":"Choose folder","privacy":"Fast intake · evidence first · no silent certainty","evidenceReviewed":"Evidence reviewed","confidenceNote":"Confidence is shown transparently. Uncertainty is never hidden.","viewEvidence":"View evidence","download":"Download receipt","print":"Print","howEyebrow":"HOW IT WORKS","howTitle1":"Simple on the surface.","howTitle2":"Serious underneath.","howDesc":"REALITYX keeps the user path short while the trust architecture stays evidence-driven. Production capabilities appear only after they are implemented and verified.","trustEyebrow":"TRUST LAYER","trustTitle":"Evidence before certainty.","trustDesc":"Designed for high-stakes digital reality checks without pretending that a visual signal alone proves identity, origin or legal authenticity.","foundationEyebrow":"2050 READY FOUNDATION","foundationTitle":"Built to grow without rebuilding trust.","accessEyebrow":"ACCESS","accessTitle1":"Free first.","accessTitle2":"Power when needed.","accessDesc":"Keep the first experience simple. Advanced engines, history and business controls can be introduced as they become production-ready.","globalEyebrow":"GLOBAL BY DESIGN","globalTitle1":"One trust language.","globalTitle2":"Many local languages.","globalDesc":"Interface localization stays separate from evidence logic so global expansion does not change the underlying verification protocol.","free":"FREE","freeTitle":"Essential verification","freeDesc":"Core evidence-first workflow.","freeButton":"Start free","premium":"PREMIUM","premiumTitle":"Advanced verification","premiumDesc":"Deeper analysis, reports and controlled history.","premiumButton":"Explore","business":"BUSINESS","businessTitle":"Verification infrastructure","businessDesc":"API, teams, audit and usage controls.","businessButton":"Contact"},"hi":{"verify":"सत्यापित करें","how":"कैसे काम करता है","trust":"विश्वास","plans":"योजनाएँ","signin":"साइन इन","choose":"सत्यापित करने के लिए साक्ष्य चुनें","accepted":"इमेज, PDF, वीडियो, ऑडियो और ZIP स्वीकार हैं · ड्रैग और ड्रॉप समर्थित","files":"फ़ाइलें चुनें","folder":"फ़ोल्डर चुनें","privacy":"तेज़ इनटेक · साक्ष्य पहले · बिना छिपी निश्चितता","evidenceReviewed":"साक्ष्य की समीक्षा हुई","confidenceNote":"विश्वास स्तर पारदर्शी है। अनिश्चितता कभी छिपाई नहीं जाती।","viewEvidence":"साक्ष्य देखें","download":"रसीद डाउनलोड करें","print":"प्रिंट","howEyebrow":"यह कैसे काम करता है","howTitle1":"ऊपर से सरल।","howTitle2":"अंदर से गंभीर।","howDesc":"REALITYX उपयोगकर्ता का रास्ता छोटा रखता है और trust architecture को evidence-driven रखता है। Production capabilities केवल लागू और सत्यापित होने के बाद दिखाई देती हैं।","trustEyebrow":"ट्रस्ट लेयर","trustTitle":"निश्चितता से पहले साक्ष्य।","trustDesc":"उच्च-दांव वाली डिजिटल reality checks के लिए बनाया गया, बिना यह दावा किए कि केवल visual signal पहचान, स्रोत या कानूनी प्रामाणिकता सिद्ध करता है।","foundationEyebrow":"2050 तैयार आधार","foundationTitle":"विश्वास को फिर से बनाए बिना आगे बढ़ने के लिए।","accessEyebrow":"एक्सेस","accessTitle1":"पहले मुफ़्त।","accessTitle2":"ज़रूरत पर शक्ति।","accessDesc":"पहला अनुभव सरल रखें। Advanced engines, history और business controls production-ready होने पर जोड़े जा सकते हैं।","globalEyebrow":"वैश्विक रूप से डिज़ाइन","globalTitle1":"एक trust language.","globalTitle2":"कई स्थानीय भाषाएँ।","globalDesc":"Interface localization को evidence logic से अलग रखा गया है ताकि global expansion verification protocol को न बदले।","free":"मुफ़्त","freeTitle":"आवश्यक सत्यापन","freeDesc":"मुख्य evidence-first workflow।","freeButton":"मुफ़्त शुरू करें","premium":"प्रीमियम","premiumTitle":"उन्नत सत्यापन","premiumDesc":"गहरा विश्लेषण, रिपोर्ट और नियंत्रित इतिहास।","premiumButton":"देखें","business":"बिज़नेस","businessTitle":"वेरिफिकेशन इंफ्रास्ट्रक्चर","businessDesc":"API, teams, audit और usage controls।","businessButton":"संपर्क"},"mr":{"verify":"सत्यापित करा","how":"कसे काम करते","trust":"विश्वास","plans":"योजना","signin":"साइन इन","choose":"सत्यापित करण्यासाठी पुरावा निवडा","accepted":"इमेज, PDF, व्हिडिओ, ऑडिओ आणि ZIP स्वीकारले जातात · ड्रॅग आणि ड्रॉप समर्थित","files":"फाइल्स निवडा","folder":"फोल्डर निवडा","privacy":"जलद इनटेक · पुरावा प्रथम · लपवलेली खात्री नाही","evidenceReviewed":"पुराव्याचे परीक्षण झाले","confidenceNote":"विश्वास पातळी पारदर्शक आहे. अनिश्चितता कधीही लपवली जात नाही.","viewEvidence":"पुरावा पहा","download":"रसीद डाउनलोड करा","print":"प्रिंट","howEyebrow":"कसे काम करते","howTitle1":"वरून सोपे.","howTitle2":"आतून गंभीर.","howDesc":"REALITYX वापरकर्त्याचा मार्ग छोटा ठेवते आणि trust architecture evidence-driven ठेवते. Production capabilities लागू व सत्यापित झाल्यावरच दिसतात.","trustEyebrow":"ट्रस्ट लेयर","trustTitle":"खात्रीपूर्वी पुरावा.","trustDesc":"उच्च-जोखीम डिजिटल reality checks साठी तयार, केवळ visual signal मुळे ओळख, स्रोत किंवा कायदेशीर प्रामाणिकता सिद्ध होते असा दावा न करता.","foundationEyebrow":"2050 तयार पाया","foundationTitle":"विश्वास पुन्हा न बांधता वाढण्यासाठी.","accessEyebrow":"प्रवेश","accessTitle1":"आधी मोफत.","accessTitle2":"गरजेनुसार शक्ती.","accessDesc":"पहिला अनुभव सोपा ठेवा. Advanced engines, history आणि business controls production-ready झाल्यावर जोडता येतील.","globalEyebrow":"जागतिक डिझाइन","globalTitle1":"एक trust language.","globalTitle2":"अनेक स्थानिक भाषा.","globalDesc":"Interface localization ला evidence logic पासून वेगळे ठेवले आहे, त्यामुळे global expansion मुळे verification protocol बदलत नाही.","free":"मोफत","freeTitle":"मूलभूत सत्यापन","freeDesc":"मुख्य evidence-first workflow.","freeButton":"मोफत सुरू करा","premium":"प्रीमियम","premiumTitle":"प्रगत सत्यापन","premiumDesc":"सखोल विश्लेषण, रिपोर्ट्स आणि नियंत्रित इतिहास.","premiumButton":"पहा","business":"बिझनेस","businessTitle":"वेरिफिकेशन इन्फ्रास्ट्रक्चर","businessDesc":"API, teams, audit आणि usage controls.","businessButton":"संपर्क"},"es":{"verify":"Verificar","how":"Cómo funciona","trust":"Confianza","plans":"Planes","signin":"Iniciar sesión","choose":"Elige la evidencia que quieres verificar","accepted":"Se aceptan imágenes, PDF, vídeo, audio y ZIP · arrastrar y soltar compatible","files":"Elegir archivos","folder":"Elegir carpeta","privacy":"Carga rápida · evidencia primero · sin certeza silenciosa","evidenceReviewed":"Evidencia revisada","confidenceNote":"La confianza se muestra de forma transparente. La incertidumbre nunca se oculta.","viewEvidence":"Ver evidencia","download":"Descargar recibo","print":"Imprimir","howEyebrow":"CÓMO FUNCIONA","howTitle1":"Simple en la superficie.","howTitle2":"Serio por dentro.","howDesc":"REALITYX mantiene corto el recorrido del usuario mientras la arquitectura de confianza sigue basada en evidencia. Las capacidades de producción aparecen solo cuando están implementadas y verificadas.","trustEyebrow":"CAPA DE CONFIANZA","trustTitle":"Evidencia antes que certeza.","trustDesc":"Diseñado para comprobaciones digitales de alto riesgo sin afirmar que una señal visual por sí sola demuestra identidad, origen o autenticidad legal.","foundationEyebrow":"BASE LISTA PARA 2050","foundationTitle":"Crecer sin reconstruir la confianza.","accessEyebrow":"ACCESO","accessTitle1":"Primero gratis.","accessTitle2":"Potencia cuando se necesita.","accessDesc":"Mantén simple la primera experiencia. Los motores avanzados, historial y controles empresariales se introducirán cuando estén listos para producción.","globalEyebrow":"DISEÑADO GLOBALMENTE","globalTitle1":"Un lenguaje de confianza.","globalTitle2":"Muchas lenguas locales.","globalDesc":"La localización de interfaz permanece separada de la lógica de evidencia para que la expansión global no cambie el protocolo de verificación.","free":"GRATIS","freeTitle":"Verificación esencial","freeDesc":"Flujo central basado en evidencia.","freeButton":"Empezar gratis","premium":"PREMIUM","premiumTitle":"Verificación avanzada","premiumDesc":"Análisis profundo, informes e historial controlado.","premiumButton":"Explorar","business":"EMPRESA","businessTitle":"Infraestructura de verificación","businessDesc":"API, equipos, auditoría y controles de uso.","businessButton":"Contactar"},"fr":{"verify":"Vérifier","how":"Comment ça marche","trust":"Confiance","plans":"Offres","signin":"Se connecter","choose":"Choisissez les éléments à vérifier","accepted":"Images, PDF, vidéo, audio et ZIP acceptés · glisser-déposer pris en charge","files":"Choisir des fichiers","folder":"Choisir un dossier","privacy":"Import rapide · preuves d’abord · aucune certitude cachée","evidenceReviewed":"Preuves examinées","confidenceNote":"La confiance est affichée clairement. L’incertitude n’est jamais masquée.","viewEvidence":"Voir les preuves","download":"Télécharger le reçu","print":"Imprimer","howEyebrow":"COMMENT ÇA MARCHE","howTitle1":"Simple en surface.","howTitle2":"Sérieux à l’intérieur.","howDesc":"REALITYX garde le parcours utilisateur court tandis que l’architecture de confiance reste fondée sur les preuves. Les capacités de production apparaissent seulement après implémentation et vérification.","trustEyebrow":"COUCHE DE CONFIANCE","trustTitle":"Les preuves avant la certitude.","trustDesc":"Conçu pour les vérifications numériques à enjeux élevés sans prétendre qu’un simple signal visuel prouve l’identité, l’origine ou l’authenticité légale.","foundationEyebrow":"BASE PRÊTE POUR 2050","foundationTitle":"Grandir sans reconstruire la confiance.","accessEyebrow":"ACCÈS","accessTitle1":"Gratuit d’abord.","accessTitle2":"La puissance quand nécessaire.","accessDesc":"Gardez une première expérience simple. Les moteurs avancés, l’historique et les contrôles métier seront ajoutés lorsqu’ils seront prêts pour la production.","globalEyebrow":"CONÇU POUR LE MONDE","globalTitle1":"Un langage de confiance.","globalTitle2":"De nombreuses langues locales.","globalDesc":"La localisation de l’interface reste séparée de la logique des preuves afin que l’expansion mondiale ne change pas le protocole de vérification.","free":"GRATUIT","freeTitle":"Vérification essentielle","freeDesc":"Flux principal fondé sur les preuves.","freeButton":"Commencer gratuitement","premium":"PREMIUM","premiumTitle":"Vérification avancée","premiumDesc":"Analyse approfondie, rapports et historique contrôlé.","premiumButton":"Explorer","business":"ENTREPRISE","businessTitle":"Infrastructure de vérification","businessDesc":"API, équipes, audit et contrôles d’utilisation.","businessButton":"Contacter"},"de":{"verify":"Prüfen","how":"So funktioniert es","trust":"Vertrauen","plans":"Pläne","signin":"Anmelden","choose":"Wählen Sie die zu prüfenden Beweise","accepted":"Bilder, PDF, Video, Audio und ZIP werden akzeptiert · Drag-and-drop unterstützt","files":"Dateien wählen","folder":"Ordner wählen","privacy":"Schnelle Aufnahme · Beweise zuerst · keine stille Gewissheit","evidenceReviewed":"Beweise geprüft","confidenceNote":"Vertrauen wird transparent angezeigt. Unsicherheit wird nie verborgen.","viewEvidence":"Beweise ansehen","download":"Beleg herunterladen","print":"Drucken","howEyebrow":"SO FUNKTIONIERT ES","howTitle1":"An der Oberfläche einfach.","howTitle2":"Im Kern ernst.","howDesc":"REALITYX hält den Nutzerweg kurz, während die Vertrauensarchitektur evidenzbasiert bleibt. Produktionsfunktionen erscheinen erst nach Implementierung und Prüfung.","trustEyebrow":"VERTRAUENSEBENE","trustTitle":"Beweise vor Gewissheit.","trustDesc":"Für digitale Prüfungen mit hohen Anforderungen entwickelt, ohne zu behaupten, dass ein visuelles Signal allein Identität, Herkunft oder rechtliche Echtheit beweist.","foundationEyebrow":"BEREIT FÜR 2050","foundationTitle":"Wachsen, ohne Vertrauen neu aufzubauen.","accessEyebrow":"ZUGANG","accessTitle1":"Zuerst kostenlos.","accessTitle2":"Leistung nach Bedarf.","accessDesc":"Der erste Ablauf bleibt einfach. Erweiterte Engines, Verlauf und Geschäftskontrollen kommen hinzu, sobald sie produktionsreif sind.","globalEyebrow":"GLOBAL ENTWORFEN","globalTitle1":"Eine Vertrauenssprache.","globalTitle2":"Viele lokale Sprachen.","globalDesc":"Die Interface-Lokalisierung bleibt von der Evidenzlogik getrennt, damit globale Expansion das Prüfprotokoll nicht verändert.","free":"KOSTENLOS","freeTitle":"Basisprüfung","freeDesc":"Zentraler evidenzbasierter Ablauf.","freeButton":"Kostenlos starten","premium":"PREMIUM","premiumTitle":"Erweiterte Prüfung","premiumDesc":"Tiefenanalyse, Berichte und kontrollierter Verlauf.","premiumButton":"Entdecken","business":"BUSINESS","businessTitle":"Verifizierungsinfrastruktur","businessDesc":"API, Teams, Audit und Nutzungskontrollen.","businessButton":"Kontakt"},"pt":{"verify":"Verificar","how":"Como funciona","trust":"Confiança","plans":"Planos","signin":"Entrar","choose":"Escolha as evidências para verificar","accepted":"Imagens, PDF, vídeo, áudio e ZIP aceitos · arrastar e soltar compatível","files":"Escolher arquivos","folder":"Escolher pasta","privacy":"Entrada rápida · evidência primeiro · sem certeza silenciosa","evidenceReviewed":"Evidências analisadas","confidenceNote":"A confiança é mostrada com transparência. A incerteza nunca é ocultada.","viewEvidence":"Ver evidências","download":"Baixar recibo","print":"Imprimir","howEyebrow":"COMO FUNCIONA","howTitle1":"Simples por fora.","howTitle2":"Sério por dentro.","howDesc":"A REALITYX mantém o caminho do usuário curto enquanto a arquitetura de confiança permanece baseada em evidências. Recursos de produção aparecem somente após implementação e verificação.","trustEyebrow":"CAMADA DE CONFIANÇA","trustTitle":"Evidência antes da certeza.","trustDesc":"Projetado para verificações digitais de alto risco sem afirmar que um sinal visual sozinho prova identidade, origem ou autenticidade legal.","foundationEyebrow":"BASE PRONTA PARA 2050","foundationTitle":"Crescer sem reconstruir a confiança.","accessEyebrow":"ACESSO","accessTitle1":"Grátis primeiro.","accessTitle2":"Potência quando necessário.","accessDesc":"Mantenha a primeira experiência simples. Mecanismos avançados, histórico e controles empresariais entram quando estiverem prontos para produção.","globalEyebrow":"PROJETADO GLOBALMENTE","globalTitle1":"Uma linguagem de confiança.","globalTitle2":"Muitos idiomas locais.","globalDesc":"A localização da interface permanece separada da lógica de evidências para que a expansão global não altere o protocolo de verificação.","free":"GRÁTIS","freeTitle":"Verificação essencial","freeDesc":"Fluxo principal baseado em evidências.","freeButton":"Começar grátis","premium":"PREMIUM","premiumTitle":"Verificação avançada","premiumDesc":"Análise profunda, relatórios e histórico controlado.","premiumButton":"Explorar","business":"BUSINESS","businessTitle":"Infraestrutura de verificação","businessDesc":"API, equipes, auditoria e controles de uso.","businessButton":"Contato"},"ar":{"verify":"تحقق","how":"كيف يعمل","trust":"الثقة","plans":"الخطط","signin":"تسجيل الدخول","choose":"اختر الأدلة للتحقق منها","accepted":"تُقبل الصور وPDF والفيديو والصوت وZIP · السحب والإفلات مدعوم","files":"اختيار الملفات","folder":"اختيار مجلد","privacy":"إدخال سريع · الدليل أولاً · دون يقين خفي","evidenceReviewed":"تمت مراجعة الأدلة","confidenceNote":"تُعرض الثقة بشفافية. لا يتم إخفاء عدم اليقين أبداً.","viewEvidence":"عرض الأدلة","download":"تنزيل الإيصال","print":"طباعة","howEyebrow":"كيف يعمل","howTitle1":"بسيط من الخارج.","howTitle2":"جاد من الداخل.","howDesc":"تحافظ REALITYX على قصر مسار المستخدم بينما تبقى بنية الثقة قائمة على الأدلة. تظهر قدرات الإنتاج فقط بعد تنفيذها والتحقق منها.","trustEyebrow":"طبقة الثقة","trustTitle":"الأدلة قبل اليقين.","trustDesc":"مصمم لفحوصات الواقع الرقمي عالية المخاطر دون الادعاء بأن الإشارة المرئية وحدها تثبت الهوية أو المصدر أو الأصالة القانونية.","foundationEyebrow":"أساس جاهز لـ2050","foundationTitle":"النمو دون إعادة بناء الثقة.","accessEyebrow":"الوصول","accessTitle1":"مجاني أولاً.","accessTitle2":"القوة عند الحاجة.","accessDesc":"حافظ على بساطة التجربة الأولى. يمكن إضافة المحركات المتقدمة والسجل وضوابط الأعمال عند جاهزيتها للإنتاج.","globalEyebrow":"مصمم عالمياً","globalTitle1":"لغة ثقة واحدة.","globalTitle2":"لغات محلية متعددة.","globalDesc":"تبقى ترجمة الواجهة منفصلة عن منطق الأدلة حتى لا يغيّر التوسع العالمي بروتوكول التحقق.","free":"مجاني","freeTitle":"التحقق الأساسي","freeDesc":"مسار تحقق قائم على الأدلة.","freeButton":"ابدأ مجاناً","premium":"مميز","premiumTitle":"التحقق المتقدم","premiumDesc":"تحليل أعمق وتقارير وسجل مضبوط.","premiumButton":"استكشف","business":"أعمال","businessTitle":"بنية التحقق التحتية","businessDesc":"API والفرق والتدقيق وضوابط الاستخدام.","businessButton":"تواصل"},"ja":{"verify":"検証","how":"仕組み","trust":"信頼","plans":"プラン","signin":"サインイン","choose":"検証する証拠を選択","accepted":"画像、PDF、動画、音声、ZIPに対応 · ドラッグ＆ドロップ対応","files":"ファイルを選択","folder":"フォルダーを選択","privacy":"高速取り込み · 証拠を優先 · 隠れた断定なし","evidenceReviewed":"証拠を確認しました","confidenceNote":"信頼度を透明に表示します。不確実性を隠しません。","viewEvidence":"証拠を見る","download":"レシートをダウンロード","print":"印刷","howEyebrow":"仕組み","howTitle1":"表面はシンプル。","howTitle2":"内部は本格的。","howDesc":"REALITYXはユーザーの手順を短く保ちながら、信頼アーキテクチャを証拠中心に維持します。実装と検証が完了した機能だけを本番機能として表示します。","trustEyebrow":"トラストレイヤー","trustTitle":"確実性より証拠。","trustDesc":"視覚的な信号だけで本人性、出所、法的真正性を証明すると主張せず、高リスクなデジタル検証向けに設計されています。","foundationEyebrow":"2050対応基盤","foundationTitle":"信頼を作り直さず成長する。","accessEyebrow":"アクセス","accessTitle1":"まず無料。","accessTitle2":"必要なときに強力に。","accessDesc":"最初の体験をシンプルに保ちます。高度なエンジン、履歴、ビジネス管理は本番対応後に追加できます。","globalEyebrow":"グローバル設計","globalTitle1":"ひとつの信頼言語。","globalTitle2":"多くのローカル言語。","globalDesc":"UIのローカライズを証拠ロジックから分離し、グローバル展開で検証プロトコルを変えない設計です。","free":"無料","freeTitle":"基本検証","freeDesc":"証拠中心の基本ワークフロー。","freeButton":"無料で開始","premium":"プレミアム","premiumTitle":"高度な検証","premiumDesc":"詳細分析、レポート、管理された履歴。","premiumButton":"詳しく見る","business":"ビジネス","businessTitle":"検証インフラ","businessDesc":"API、チーム、監査、利用制御。","businessButton":"お問い合わせ"},"ko":{"verify":"검증","how":"작동 방식","trust":"신뢰","plans":"요금제","signin":"로그인","choose":"검증할 증거를 선택하세요","accepted":"이미지, PDF, 동영상, 오디오, ZIP 지원 · 드래그 앤 드롭 지원","files":"파일 선택","folder":"폴더 선택","privacy":"빠른 입력 · 증거 우선 · 숨겨진 확정 없음","evidenceReviewed":"증거 검토 완료","confidenceNote":"신뢰도를 투명하게 표시합니다. 불확실성을 숨기지 않습니다.","viewEvidence":"증거 보기","download":"영수증 다운로드","print":"인쇄","howEyebrow":"작동 방식","howTitle1":"겉은 단순하게.","howTitle2":"속은 진지하게.","howDesc":"REALITYX는 사용자 경로를 짧게 유지하면서 신뢰 아키텍처를 증거 중심으로 유지합니다. 구현 및 검증된 기능만 프로덕션 기능으로 표시합니다.","trustEyebrow":"신뢰 계층","trustTitle":"확실성보다 증거.","trustDesc":"시각 신호 하나만으로 신원, 출처 또는 법적 진위를 입증한다고 주장하지 않는 고위험 디지털 검증용 설계입니다.","foundationEyebrow":"2050 준비 기반","foundationTitle":"신뢰를 다시 만들지 않고 확장.","accessEyebrow":"액세스","accessTitle1":"먼저 무료.","accessTitle2":"필요할 때 강력하게.","accessDesc":"첫 경험은 단순하게 유지합니다. 고급 엔진, 기록 및 비즈니스 제어는 프로덕션 준비 후 추가할 수 있습니다.","globalEyebrow":"글로벌 설계","globalTitle1":"하나의 신뢰 언어.","globalTitle2":"다양한 현지 언어.","globalDesc":"인터페이스 현지화를 증거 로직과 분리하여 글로벌 확장이 검증 프로토콜을 바꾸지 않도록 합니다.","free":"무료","freeTitle":"기본 검증","freeDesc":"핵심 증거 중심 워크플로.","freeButton":"무료로 시작","premium":"프리미엄","premiumTitle":"고급 검증","premiumDesc":"심층 분석, 보고서 및 관리형 기록.","premiumButton":"살펴보기","business":"비즈니스","businessTitle":"검증 인프라","businessDesc":"API, 팀, 감사 및 사용량 제어.","businessButton":"문의"},"zh":{"verify":"验证","how":"工作原理","trust":"信任","plans":"方案","signin":"登录","choose":"选择要验证的证据","accepted":"支持图片、PDF、视频、音频和 ZIP · 支持拖放","files":"选择文件","folder":"选择文件夹","privacy":"快速导入 · 证据优先 · 不隐藏确定性","evidenceReviewed":"证据已审查","confidenceNote":"透明展示可信度，不隐藏不确定性。","viewEvidence":"查看证据","download":"下载凭证","print":"打印","howEyebrow":"工作原理","howTitle1":"表面简单。","howTitle2":"内在严谨。","howDesc":"REALITYX保持简短的用户路径，同时让信任架构以证据为核心。只有完成实现并验证的能力才会作为生产功能出现。","trustEyebrow":"信任层","trustTitle":"证据先于确定性。","trustDesc":"面向高风险数字真实性检查，不声称单一视觉信号即可证明身份、来源或法律真实性。","foundationEyebrow":"2050就绪基础","foundationTitle":"无需重建信任即可扩展。","accessEyebrow":"访问","accessTitle1":"先免费。","accessTitle2":"需要时获得更强能力。","accessDesc":"保持首次体验简单。高级引擎、历史记录和企业控制将在具备生产条件后加入。","globalEyebrow":"全球设计","globalTitle1":"一种信任语言。","globalTitle2":"多种本地语言。","globalDesc":"界面本地化与证据逻辑分离，确保全球扩展不会改变验证协议。","free":"免费","freeTitle":"基础验证","freeDesc":"核心证据优先工作流。","freeButton":"免费开始","premium":"高级","premiumTitle":"高级验证","premiumDesc":"深度分析、报告和受控历史。","premiumButton":"探索","business":"企业","businessTitle":"验证基础设施","businessDesc":"API、团队、审计和使用控制。","businessButton":"联系"},"ru":{"verify":"Проверить","how":"Как это работает","trust":"Доверие","plans":"Тарифы","signin":"Войти","choose":"Выберите доказательства для проверки","accepted":"Поддерживаются изображения, PDF, видео, аудио и ZIP · drag-and-drop поддерживается","files":"Выбрать файлы","folder":"Выбрать папку","privacy":"Быстрый ввод · сначала доказательства · без скрытой уверенности","evidenceReviewed":"Доказательства проверены","confidenceNote":"Уровень доверия отображается прозрачно. Неопределённость не скрывается.","viewEvidence":"Посмотреть доказательства","download":"Скачать квитанцию","print":"Печать","howEyebrow":"КАК ЭТО РАБОТАЕТ","howTitle1":"Снаружи просто.","howTitle2":"Внутри серьёзно.","howDesc":"REALITYX сохраняет короткий путь пользователя, а архитектура доверия остаётся основанной на доказательствах. Производственные возможности появляются только после реализации и проверки.","trustEyebrow":"СЛОЙ ДОВЕРИЯ","trustTitle":"Доказательства важнее уверенности.","trustDesc":"Для цифровых проверок высокого риска без утверждения, что одного визуального сигнала достаточно для подтверждения личности, происхождения или юридической подлинности.","foundationEyebrow":"ОСНОВА ГОТОВА К 2050","foundationTitle":"Рост без перестройки доверия.","accessEyebrow":"ДОСТУП","accessTitle1":"Сначала бесплатно.","accessTitle2":"Мощность по необходимости.","accessDesc":"Сохраняйте первый опыт простым. Расширенные движки, история и бизнес-контроли добавляются после готовности к производству.","globalEyebrow":"ГЛОБАЛЬНЫЙ ДИЗАЙН","globalTitle1":"Один язык доверия.","globalTitle2":"Много локальных языков.","globalDesc":"Локализация интерфейса отделена от логики доказательств, чтобы глобальное расширение не меняло протокол проверки.","free":"БЕСПЛАТНО","freeTitle":"Базовая проверка","freeDesc":"Основной процесс на основе доказательств.","freeButton":"Начать бесплатно","premium":"PREMIUM","premiumTitle":"Расширенная проверка","premiumDesc":"Глубокий анализ, отчёты и контролируемая история.","premiumButton":"Изучить","business":"БИЗНЕС","businessTitle":"Инфраструктура проверки","businessDesc":"API, команды, аудит и контроль использования.","businessButton":"Связаться"},"it":{"verify":"Verifica","how":"Come funziona","trust":"Fiducia","plans":"Piani","signin":"Accedi","choose":"Scegli le prove da verificare","accepted":"Immagini, PDF, video, audio e ZIP accettati · trascinamento supportato","files":"Scegli file","folder":"Scegli cartella","privacy":"Acquisizione rapida · prove prima · nessuna certezza nascosta","evidenceReviewed":"Prove esaminate","confidenceNote":"La fiducia è mostrata in modo trasparente. L’incertezza non viene mai nascosta.","viewEvidence":"Vedi prove","download":"Scarica ricevuta","print":"Stampa","howEyebrow":"COME FUNZIONA","howTitle1":"Semplice in superficie.","howTitle2":"Serio sotto.","howDesc":"REALITYX mantiene breve il percorso dell’utente mentre l’architettura della fiducia resta basata sulle prove. Le capacità di produzione compaiono solo dopo implementazione e verifica.","trustEyebrow":"LIVELLO DI FIDUCIA","trustTitle":"Le prove prima della certezza.","trustDesc":"Progettato per controlli digitali ad alto rischio senza affermare che un solo segnale visivo dimostri identità, origine o autenticità legale.","foundationEyebrow":"BASE PRONTA PER IL 2050","foundationTitle":"Crescere senza ricostruire la fiducia.","accessEyebrow":"ACCESSO","accessTitle1":"Prima gratis.","accessTitle2":"Potenza quando serve.","accessDesc":"Mantieni semplice la prima esperienza. Motori avanzati, cronologia e controlli aziendali saranno introdotti quando pronti per la produzione.","globalEyebrow":"PROGETTATO GLOBALMENTE","globalTitle1":"Un linguaggio della fiducia.","globalTitle2":"Molte lingue locali.","globalDesc":"La localizzazione dell’interfaccia resta separata dalla logica delle prove, così l’espansione globale non cambia il protocollo di verifica.","free":"GRATIS","freeTitle":"Verifica essenziale","freeDesc":"Flusso principale basato sulle prove.","freeButton":"Inizia gratis","premium":"PREMIUM","premiumTitle":"Verifica avanzata","premiumDesc":"Analisi approfondita, report e cronologia controllata.","premiumButton":"Esplora","business":"BUSINESS","businessTitle":"Infrastruttura di verifica","businessDesc":"API, team, audit e controlli d’uso.","businessButton":"Contatti"},"tr":{"verify":"Doğrula","how":"Nasıl çalışır","trust":"Güven","plans":"Planlar","signin":"Giriş yap","choose":"Doğrulanacak kanıtı seçin","accepted":"Görseller, PDF, video, ses ve ZIP desteklenir · sürükle-bırak desteklenir","files":"Dosya seç","folder":"Klasör seç","privacy":"Hızlı giriş · önce kanıt · gizli kesinlik yok","evidenceReviewed":"Kanıt incelendi","confidenceNote":"Güven düzeyi şeffaf gösterilir. Belirsizlik asla gizlenmez.","viewEvidence":"Kanıtları görüntüle","download":"Makbuzu indir","print":"Yazdır","howEyebrow":"NASIL ÇALIŞIR","howTitle1":"Yüzeyde basit.","howTitle2":"İçeride ciddi.","howDesc":"REALITYX kullanıcı yolunu kısa tutarken güven mimarisini kanıt odaklı korur. Üretim yetenekleri yalnızca uygulanıp doğrulandıktan sonra görünür.","trustEyebrow":"GÜVEN KATMANI","trustTitle":"Kesinlikten önce kanıt.","trustDesc":"Tek bir görsel sinyalin kimliği, kaynağı veya yasal gerçekliği kanıtladığını iddia etmeden yüksek riskli dijital kontroller için tasarlanmıştır.","foundationEyebrow":"2050 HAZIR TEMEL","foundationTitle":"Güveni yeniden kurmadan büyüyün.","accessEyebrow":"ERİŞİM","accessTitle1":"Önce ücretsiz.","accessTitle2":"Gerektiğinde güç.","accessDesc":"İlk deneyimi basit tutun. Gelişmiş motorlar, geçmiş ve işletme kontrolleri üretime hazır olduğunda eklenebilir.","globalEyebrow":"KÜRESEL TASARIM","globalTitle1":"Tek bir güven dili.","globalTitle2":"Birçok yerel dil.","globalDesc":"Arayüz yerelleştirmesi kanıt mantığından ayrı tutulur; böylece küresel genişleme doğrulama protokolünü değiştirmez.","free":"ÜCRETSİZ","freeTitle":"Temel doğrulama","freeDesc":"Temel kanıt odaklı iş akışı.","freeButton":"Ücretsiz başla","premium":"PREMIUM","premiumTitle":"Gelişmiş doğrulama","premiumDesc":"Derin analiz, raporlar ve kontrollü geçmiş.","premiumButton":"Keşfet","business":"İŞLETME","businessTitle":"Doğrulama altyapısı","businessDesc":"API, ekipler, denetim ve kullanım kontrolleri.","businessButton":"İletişim"}};
function ui(lang:string,key:string){return uiCopy[lang]?.[key]||uiCopy.en[key]||key;}


const resultCopy: Record<string,Record<string,string>>={en:{confidence:"confidence",evidenceStrength:"Evidence strength:",provenance:"Provenance:",documentType:"Document type",copy:"Copy / Xerox",authority:"Authority check",risk:"Risk level",sources:"Independent sources",conflict:"Conflict",detected:"Detected",none:"None detected",scope:"Scope & limitations",evidenceDetails:"Evidence details",valid:"Cryptographically valid",verify:"Verify"},hi:{confidence:"विश्वास स्तर",evidenceStrength:"साक्ष्य स्तर:",provenance:"प्रोवेनेंस:",documentType:"दस्तावेज़ प्रकार",copy:"कॉपी / ज़ेरॉक्स",authority:"प्राधिकरण जाँच",risk:"जोखिम स्तर",sources:"स्वतंत्र स्रोत",conflict:"टकराव",detected:"पता चला",none:"कोई नहीं",scope:"दायरा और सीमाएँ",evidenceDetails:"साक्ष्य विवरण",valid:"क्रिप्टोग्राफिक रूप से मान्य",verify:"सत्यापित करें"},mr:{confidence:"विश्वास पातळी",evidenceStrength:"पुराव्याची ताकद:",provenance:"प्रोव्हेनन्स:",documentType:"दस्तऐवज प्रकार",copy:"कॉपी / झेरॉक्स",authority:"अधिकृतता तपासणी",risk:"जोखीम पातळी",sources:"स्वतंत्र स्रोत",conflict:"विसंगती",detected:"आढळली",none:"आढळली नाही",scope:"व्याप्ती आणि मर्यादा",evidenceDetails:"पुराव्याचे तपशील",valid:"क्रिप्टोग्राफिकदृष्ट्या वैध",verify:"सत्यापित करा"}};
function rc(lang:string,key:string){return resultCopy[lang]?.[key]||resultCopy.en[key]||key;}

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
  conclusion?:string; limitations?:string[]; evidence_strength?:string; provenance_status?:string;
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
    // One-action UX: a single supported image starts verification immediately.
    if(valid.length===1&&["image/jpeg","image/png","image/webp"].includes(valid[0].type)) void verifyFile(valid[0]);
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

  async function verifyFile(file:File){
    
    setChecking(true);setStage("Preparing secure verification…");setError("");setResult(null);
    try{
      const configuredApiBase=process.env.NEXT_PUBLIC_REALITYX_API_URL;
      // Prefer an explicitly configured backend, but keep the public Vercel app functional
      // when that variable is absent by using the same-origin backend rewrite.
      const apiBase=configuredApiBase?.replace(/\/$/,"")||`${window.location.origin}/api`;

      const form=new FormData();form.append("file",file);
      setStage("Checking integrity and evidence…");
      const response=await fetch(`${apiBase.replace(/\/$/,"")}/v1/verify/image`,{method:"POST",headers:{"Idempotency-Key":crypto.randomUUID()},body:form});
      const body=await response.json().catch(()=>({}));
      if(!response.ok) throw new Error(body.detail||"Verification could not be completed.");
      setStage("Finalizing decision…");
      let enriched:Result=body;
      if(body.verification_id){
        try{
          const reportResponse=await fetch(apiBase.replace(/\/$/,"")+"/v1/professional/reports/"+encodeURIComponent(body.verification_id),{cache:"no-store"});
          if(reportResponse.ok){
            const reportBody=await reportResponse.json().catch(()=>({}));
            const report=reportBody?.report;
            if(report){
              enriched={...body,conclusion:report.conclusion,limitations:report.limitations,evidence_strength:report.evidence_strength,provenance_status:report.provenance_status};
            }
          }
        }catch{
          // Core verification remains authoritative if the optional report is unavailable.
        }
      }
      setResult(enriched);
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
      <div className="navlinks"><a href="#verify">{ui(lang,"verify")}</a><a href="#how">{ui(lang,"how")}</a><a href="#trust">{ui(lang,"trust")}</a><a href="#plans">{ui(lang,"plans")}</a></div>
      <div className="navActions">
        <label className="language"><span>◎</span><select aria-label={t.language} value={lang} onChange={e=>setLang(e.target.value)}>{languages.map(([id,name])=><option value={id} key={id}>{name}</option>)}</select></label>
        <button className="ghost">{ui(lang,"signin")}</button>
      </div>
    </nav>

    <section className="hero" id="verify">
      <div className="heroGlow"/>
      <div className="eyebrow">{t.eyebrow}</div>
      <h1>{t.title}</h1>
      <p className="lead">{t.lead}</p>
      <div className="heroTrust"><span>● {lang==="hi"?"साक्ष्य पहले":lang==="mr"?"पुरावा प्रथम":lang==="ar"?"الدليل أولاً":lang==="ja"?"証拠を優先":lang==="ko"?"증거 우선":lang==="zh"?"证据优先":"Evidence-first"}</span><span>● {lang==="hi"?"गोपनीयता":lang==="mr"?"गोपनीयता":lang==="ar"?"الخصوصية":lang==="ja"?"プライバシー重視":lang==="ko"?"개인정보 보호":lang==="zh"?"隐私优先":"Privacy-minded"}</span><span>● {lang==="hi"?"प्रदाता-निरपेक्ष":lang==="mr"?"प्रदाता-निरपेक्ष":lang==="ar"?"محايد تجاه المزوّد":lang==="ja"?"プロバイダー中立":lang==="ko"?"제공자 중립":"Provider-neutral"}</span><span>● {lang==="hi"?"बिना जबरन निश्चितता":lang==="mr"?"जबरदस्तीची खात्री नाही":lang==="ar"?"دون يقين قسري":lang==="ja"?"断定を強制しない":lang==="ko"?"강제 확정 없음":"No forced certainty"}</span></div>

      <div className="verifyCard">
        <div className="drop" role="button" tabIndex={0} onKeyDown={e=>{if(e.key==="Enter"||e.key===" "){e.preventDefault();inputRef.current?.click()}}} onDragOver={e=>e.preventDefault()} onDrop={e=>{e.preventDefault();addFiles(e.dataTransfer.files)}} onClick={()=>inputRef.current?.click()}>
          <div className="uploadIcon">↑</div>
          <h2>{checking?(stage||"Verifying…"):ui(lang,"choose")}</h2>
          <p>{ui(lang,"accepted")}</p>
          <input ref={inputRef} hidden type="file" multiple accept=".jpg,.jpeg,.png,.webp,.pdf,.mp4,.mov,.webm,.mp3,.wav,.m4a,.zip" onChange={e=>addFiles(e.target.files)}/>
          <input ref={folderRef} hidden type="file" multiple {...({webkitdirectory:""} as React.InputHTMLAttributes<HTMLInputElement>)} onChange={e=>addFiles(e.target.files)}/>
          {files.length>0&&<div className="filename">{files.length} evidence file{files.length===1?"":"s"} selected</div>}
        </div>
        <div className="intakeActions">
          <button className="secondary" type="button" onClick={()=>inputRef.current?.click()}>{ui(lang,"files")}</button>
          <button className="secondary" type="button" onClick={()=>folderRef.current?.click()}>{ui(lang,"folder")}</button>
        </div>
        {files.length>0&&<div className="intakeSummary" aria-live="polite">
          {imageCount>0&&<span>IMAGE {imageCount}</span>}{pdfCount>0&&<span>PDF {pdfCount}</span>}{videoCount>0&&<span>VIDEO {videoCount}</span>}{audioCount>0&&<span>AUDIO {audioCount}</span>}{zipCount>0&&<span>ZIP {zipCount}</span>}
        </div>}
        <button className="primary" onClick={()=>{const file=imageFile();if(file) void verifyFile(file);else setError("This evidence type is not connected to the live verification engine yet.");}} disabled={checking}>{checking?"Analyzing…":t.verify}<span>→</span></button>
        {error&&<div className="verifyError" role="alert">{error}</div>}
        {result&&(()=>{
          const verdict=(result.result??"UNCERTAIN").toUpperCase();
          const tone=verdict==="VERIFIED"||verdict==="AUTHENTIC"?"verified":verdict==="INAUTHENTIC"||verdict==="MANIPULATED"||verdict==="AI_GENERATED"?"inauthentic":"uncertain";
          const label=tone==="verified"?"Verified":tone==="inauthentic"?"Inauthentic":"Uncertain";
          return <div ref={resultRef} className={`verifyResult trustResult ${tone}`} aria-live="polite">
            <div className="trustResultHeader">
              <div className="trustVerdict"><span className="statusDot"/><b>{label}</b></div>
              {typeof result.confidence==="number"&&<div className="confidence"><strong>{Math.round(result.confidence*100)}%</strong><span>{rc(lang,"confidence")}</span></div>}
            </div>
            <p className="trustSummary">{result.conclusion||(
              tone==="verified"?"Available evidence supports this result.":tone==="inauthentic"?"Available evidence indicates authenticity concerns.":"Evidence is not strong enough for a reliable yes/no decision."
            )}</p>
            {(result.evidence_strength||result.provenance_status)&&<div className="resultMeta">
              {result.evidence_strength&&<span>{rc(lang,"evidenceStrength")} <b>{result.evidence_strength.replaceAll("_"," ")}</b></span>}
              {result.provenance_status&&<span>{rc(lang,"provenance")} <b>{result.provenance_status.replaceAll("_"," ")}</b></span>}
            </div>}
            <div className="resultGrid">
              {result.document_type&&<div><small>{rc(lang,"documentType")}</small><b>{result.document_type}</b></div>}
              {result.copy_status&&<div><small>{rc(lang,"copy")}</small><b>{result.copy_status.replaceAll("_"," ")}</b></div>}
              {result.authority_status&&<div><small>{rc(lang,"authority")}</small><b>{result.authority_status.replaceAll("_"," ")}</b></div>}
              {result.risk_level&&<div><small>{rc(lang,"risk")}</small><b>{result.risk_level}</b></div>}
              {typeof result.independent_source_count==="number"&&<div><small>{rc(lang,"sources")}</small><b>{result.independent_source_count}</b></div>}
              <div><small>{rc(lang,"conflict")}</small><b>{result.conflict?rc(lang,"detected"):rc(lang,"none")}</b></div>
            </div>
            <div id="evidence-summary" className="evidenceNote"><span>✓</span><div><b>{ui(lang,"evidenceReviewed")}</b><small>{ui(lang,"confidenceNote")}</small></div></div>
            {(()=>{
              const items=(result.evidence?.length?result.evidence:result.signals)||[];
              if(!items.length) return null;
              return <div className="evidenceList" aria-label={rc(lang,"evidenceDetails")}>
                {items.slice(0,12).map((item,index)=><div className="evidenceItem" key={item.evidence_id||index}>
                  <div><b>{item.signal||"Evidence signal"}</b><small>{item.summary||"No summary supplied."}</small></div>
                  <span>{item.status||"available"}{typeof item.confidence==="number"?" · "+Math.round(item.confidence*100)+"%":""}</span>
                </div>)}
              </div>;
            })()}
            {result.limitations?.length&&<div className="limitations">
              <b>{rc(lang,"scope")}</b>
              <ul>{result.limitations.slice(0,4).map((item,index)=><li key={index}>{item}</li>)}</ul>
            </div>}
            <div className="receipt">
              <div className="receiptTitle"><span>REALITYX TRUST RECEIPT</span>{result.cryptographic_valid&&<b>✓ {rc(lang,"valid")}</b>}</div>
              {result.verification_id&&<div><small>Verification ID</small><code>{result.verification_id}</code></div>}
              {result.sha256&&<div><small>Artifact SHA-256</small><code>{result.sha256}</code></div>}
              {result.evidence_graph_digest&&<div><small>Evidence digest</small><code>{result.evidence_graph_digest}</code></div>}
              {result.receipt_digest&&<div><small>Receipt digest</small><code>{result.receipt_digest}</code></div>}
            </div>
            <div className="resultActions"><button type="button" onClick={()=>resultRef.current?.querySelector("#evidence-summary")?.scrollIntoView({behavior:"smooth",block:"nearest"})}>{ui(lang,"viewEvidence")}</button><button type="button" onClick={downloadReceipt}>{ui(lang,"download")}</button><button type="button" onClick={printResult}>{ui(lang,"print")}</button></div>
          </div>;
        })()}
        {!result&&!error&&<div className="privacy">{ui(lang,"privacy")}</div>}
      </div>
    </section>

    <section className="mediaStrip" id="verify-types" aria-label="Verification types">
      {media.map(([name,desc,status])=><button className="mediaCard" key={name} type="button" disabled={status!=="available"} aria-label={status==="available"?`Verify ${name}`:`${name} verification is not connected`} onClick={()=>{if(status==="available")inputRef.current?.click()}}>
        <span className="mediaIcon">{name==="IMAGE"?"◈":name==="VIDEO"?"▶":name==="AUDIO"?"◉":name==="DOCUMENT"?"▤":"⌁"}</span>
        <span className="mediaCopy"><b>{name}</b><small>{desc}</small></span><span className="mediaStatus">{status==="available"?"AVAILABLE":"NOT CONNECTED"}</span><span className="mediaArrow">→</span>
      </button>)}
    </section>

    <section className="section" id="how">
      <div className="sectionHead"><div><div className="eyebrow">{ui(lang,"howEyebrow")}</div><h2>{ui(lang,"howTitle1")}<br/>{ui(lang,"howTitle2")}</h2></div><p>{ui(lang,"howDesc")}</p></div>
      <div className="flow">{principles.map(([n,title,desc],i)=><div className="flowItem" key={n}><span>{n}</span><b>{title}</b><p>{desc}</p>{i<principles.length-1&&<i>→</i>}</div>)}</div>
    </section>

    <section className="section" id="trust">
      <div className="sectionHead"><div><div className="eyebrow">{ui(lang,"trustEyebrow")}</div><h2>{ui(lang,"trustTitle")}</h2></div><p>{ui(lang,"trustDesc")}</p></div>
      <div className="trustGrid">{trust.map(([title,desc])=><div className="trustCard" key={title}><span>◆</span><b>{title}</b><p>{desc}</p></div>)}</div>
    </section>

    <section className="section compact">
      <div className="sectionHead"><div><div className="eyebrow">{ui(lang,"foundationEyebrow")}</div><h2>{ui(lang,"foundationTitle")}</h2></div><p>{lang==="hi"?"मल्टीमोडल फोरेंसिक्स, C2PA/प्रोवेनेंस, साइन किए गए रिसीट, की लाइफसायकल, AI-agent trust और auditability इसी evidence boundary से जुड़ सकते हैं।":lang==="mr"?"मल्टीमोडल फॉरेन्सिक्स, C2PA/प्रोव्हेनन्स, साइन केलेल्या रसीदी, की लाइफसायकल, AI-agent trust आणि auditability याच evidence boundary शी जोडता येतात.":"Multimodal forensics, C2PA/provenance, signed receipts, key lifecycle, AI-agent trust and auditability can plug into the same evidence boundary."}</p></div>
      <div className="capLine"><span>CRYPTOGRAPHIC RECEIPTS</span><span>KEY TRUST & REVOCATION</span><span>C2PA / PROVENANCE</span><span>AI-AGENT TRUST API</span><span>AUDIT & REPRODUCIBILITY</span></div>
    </section>

    <section className="plans" id="plans">
      <div className="planIntro"><div className="eyebrow">{ui(lang,"accessEyebrow")}</div><h2>{ui(lang,"accessTitle1")}<br/>{ui(lang,"accessTitle2")}</h2><p>{ui(lang,"accessDesc")}</p></div>
      <div className="plan"><b>{ui(lang,"free")}</b><h3>{ui(lang,"freeTitle")}</h3><p>{ui(lang,"freeDesc")}</p><button className="planButton">{ui(lang,"freeButton")} →</button></div>
      <div className="plan premium"><b>{ui(lang,"premium")}</b><h3>{ui(lang,"premiumTitle")}</h3><p>{ui(lang,"premiumDesc")}</p><button className="planButton">{ui(lang,"premiumButton")} →</button></div>
      <div className="plan"><b>{ui(lang,"business")}</b><h3>{ui(lang,"businessTitle")}</h3><p>{ui(lang,"businessDesc")}</p><button className="planButton">{ui(lang,"businessButton")} →</button></div>
    </section>

    <section className="languageBand">
      <div><div className="eyebrow">{ui(lang,"globalEyebrow")}</div><h2>{ui(lang,"globalTitle1")}<br/>{ui(lang,"globalTitle2")}</h2><p>{ui(lang,"globalDesc")}</p></div>
      <div className="languageCloud">{languages.map(([id,name])=><button key={id} onClick={()=>setLang(id)} className={lang===id?"active":""}>{name}</button>)}</div>
    </section>

    <footer><div className="brand"><span className="mark">R×</span><span>REALITYX</span></div><span>VERIFY WHAT’S REAL.</span><span>© 2026 · Evidence, not blind certainty.</span></footer>
  </main>;
}
