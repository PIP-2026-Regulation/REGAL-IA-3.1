"""EU AI Act Legal Advisor - Main business logic."""

import os
import re
import json
import logging
from typing import List, Dict, Tuple, Optional
from dotenv import load_dotenv

from .document_processor import DocumentChunk, DocumentProcessor, EmbeddingService
from .llm_client import OllamaClient

load_dotenv(override=True)
logger = logging.getLogger(__name__)

# Configuration
MAX_QUESTIONS = 15
MIN_QUESTIONS = 3
CONFIDENCE_THRESHOLD = 0.75
DUPLICATE_SIMILARITY_THRESHOLD = 0.75


class LegalAdvisor:
    """EU AI Act compliance advisor using RAG and LLM."""

    def __init__(self):
        self.ai_act_pdf = os.getenv("AI_ACT_PDF_PATH", "OJ_L_202401689_EN_TXT.pdf")
        self.questions_json = os.getenv("QUESTIONS_JSON_PATH", "Questions_Reference.json")

        self.llm = OllamaClient(
            base_url=os.getenv("OLLAMA_URL", "http://localhost:11434"),
            model=os.getenv("OLLAMA_MODEL", "llama3.1:8b")
        )
        self.embeddings = EmbeddingService()
        self.ai_act_chunks = self._load_document(self.ai_act_pdf, "ai_act_embeddings.pkl")
        self.audit_questions = self._load_audit_questions()

        # State
        self.model_description = ""
        self.pending_description = ""  # Stores description during prohibited confirmation
        self.interview_history: List[Dict] = []
        self.asked_questions_texts: List[str] = []
        self.relevant_articles: Dict = {}

    def _load_document(self, path: str, cache: str) -> List[DocumentChunk]:
        """Load and embed document chunks."""
        if not os.path.exists(path):
            logger.warning(f"Document not found: {path}")
            return []
        processor = DocumentProcessor(path)
        chunks = processor.load_and_chunk_document()
        return self.embeddings.generate_embeddings(chunks, cache) if chunks else []

    def _load_audit_questions(self) -> Dict:
        """Load audit questions from JSON."""
        if not os.path.exists(self.questions_json):
            logger.warning(f"Questions JSON not found: {self.questions_json}")
            return {}
        try:
            with open(self.questions_json, 'r', encoding='utf-8') as f:
                data = json.load(f)
            logger.info(f"✅ Loaded: {data.get('document_title', 'Questions')}")
            return data
        except Exception as e:
            logger.error(f"Failed to load questions: {e}")
            return {}

    def _get_relevant_questions_context(self, system_description: str) -> str:
        """Extract relevant questions based on system description."""
        if not self.audit_questions:
            return ""

        context_parts = []
        desc_lower = system_description.lower()

        type_mappings = {
            'type_1': ['llm', 'gpt', 'generative', 'chatbot', 'language model'],
            'type_2': ['decision', 'classification', 'recruitment', 'credit', 'scoring'],
            'type_3': ['biometric', 'face', 'facial', 'recognition'],
            'type_4': ['reinforcement', 'unsupervised', 'clustering', 'recommendation']
        }

        for type_key, keywords in type_mappings.items():
            if any(kw in desc_lower for kw in keywords):
                type_data = self.audit_questions.get(type_key, {})
                if type_data:
                    context_parts.append(f"\n**{type_data.get('name', type_key)}**")
                    for cat_key, cat_value in type_data.items():
                        if isinstance(cat_value, list) and cat_value:
                            for q in cat_value[:2]:
                                if isinstance(q, dict):
                                    context_parts.append(
                                        f"  - {q.get('question')} ({q.get('reference')})"
                                    )

        return "\n".join(context_parts)

    def _is_duplicate_question(self, new_question: str) -> bool:
        """Check if question is too similar to previously asked ones."""
        if not self.asked_questions_texts:
            return False
        for asked_q in self.asked_questions_texts[-3:]:
            similarity = self.embeddings.compute_similarity(new_question, asked_q)
            if similarity > DUPLICATE_SIMILARITY_THRESHOLD:
                logger.warning(f"🔄 Duplicate detected (similarity: {similarity:.2f})")
                return True
        return False

    def _get_system_prompt_for_questions(self) -> str:
        """System prompt for generating interview questions."""
        return """You are an EU AI Act compliance analyst conducting a structured interview.

RISK CLASSIFICATION FRAMEWORK:
1. PROHIBITED (Article 5): Social scoring, subliminal manipulation, real-time biometric surveillance
2. HIGH-RISK (Annex III): Biometrics, critical infrastructure, employment, education, law enforcement
3. LIMITED RISK (Article 52): Chatbots, deepfakes, emotion recognition - transparency required
4. MINIMAL RISK: General purpose AI with no special obligations

YOUR TASK:
- Ask ONE specific technical question to determine risk classification
- Focus on: purpose, data types, decision impact, human oversight, deployment context
- Avoid generic or repetitive questions
- After MIN_QUESTIONS, evaluate if you can confidently classify the system

RESPONSE FORMAT (JSON only):
{
  "assessment_status": "need_more_info" or "ready_to_conclude",
  "confidence": 0.0-1.0,
  "risk_hypothesis": "prohibited/high-risk/limited-risk/minimal-risk",
  "reasoning": "brief explanation of current assessment",
  "missing_info": ["specific gap 1", "specific gap 2"],
  "next_question": "your next question" or null
}"""

    def _get_system_prompt_for_final_report(self) -> str:
        """System prompt for generating final compliance report."""
        return """You are an EU AI Act compliance expert generating the FINAL ASSESSMENT REPORT.

CITATION RULES:
1. Article 5 (Prohibited) - ONLY cite if system explicitly matches prohibited practices
2. Annex III (High-Risk) - ONLY cite if system is used in specific high-risk contexts
3. Article 52 (Transparency) - Cite for systems interacting with humans

REPORT STRUCTURE:

# EU AI ACT COMPLIANCE ASSESSMENT

## 1. RISK CLASSIFICATION
**Risk Level:** [PROHIBITED / HIGH-RISK / LIMITED RISK / MINIMAL RISK]
**Confidence:** [Low/Medium/High]
**Rationale:** Why this classification was chosen

## 2. IDENTIFIED VIOLATIONS & CONCERNS
List violations with Article references and evidence

## 3. APPLICABLE ARTICLES
For each article: requirement, current status, gap analysis

## 4. PENALTIES (Article 99)
- Prohibited AI: €35M or 7% turnover
- High-risk violations: €15M or 3% turnover
- Other violations: €7.5M or 1.5% turnover

## 5. COMPLIANCE ROADMAP
Prioritized actions with timeline

## 6. TECHNICAL RECOMMENDATIONS
Specific measures to address gaps

QUALITY STANDARDS:
✓ Cite ONLY articles with clear evidence
✓ Include page numbers for citations
✓ Distinguish violations from concerns
✓ Base conclusions on interview data"""

    def _generate_question(self) -> Dict:
        """Generate next interview question."""
        all_content = self.model_description + " " + " ".join(
            [qa['answer'] for qa in self.interview_history]
        )
        reference_questions = self._get_relevant_questions_context(all_content)

        relevant_chunks = self.embeddings.find_relevant_chunks(
            all_content[-500:], self.ai_act_chunks, top_k=5
        )

        context = "\n\n".join([
            f"[Article {', '.join(c.extracted_articles)}] {c.text[:300]}..."
            for c in relevant_chunks if c.extracted_articles
        ])

        history_str = "\n".join([
            f"Q{i+1}: {qa['question'][:80]}... → A: {qa['answer'][:100]}..."
            for i, qa in enumerate(self.interview_history[-3:])
        ])

        prompt = f"""SYSTEM DESCRIPTION:
{self.model_description[:500]}

INTERVIEW HISTORY ({len(self.interview_history)} questions):
{history_str}

RELEVANT EU AI ACT CONTEXT:
{context[:1000]}

REFERENCE AUDIT QUESTIONS:
{reference_questions[:800]}

Generate your assessment and next question (or conclude if ready).
Questions asked: {len(self.interview_history)}/{MAX_QUESTIONS}"""

        messages = [
            {"role": "system", "content": self._get_system_prompt_for_questions()},
            {"role": "user", "content": prompt}
        ]

        response = self.llm.chat(messages, temperature=0.3, max_tokens=1000)

        try:
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                response = response.split("```")[1].split("```")[0]

            data = json.loads(response.strip())

            if data.get("next_question"):
                if self._is_duplicate_question(data["next_question"]):
                    return {
                        "assessment_status": "ready_to_conclude",
                        "confidence": 0.9,
                        "risk_hypothesis": data.get("risk_hypothesis", "assessment_needed"),
                        "reasoning": "Sufficient information gathered",
                        "next_question": None
                    }
                self.asked_questions_texts.append(data["next_question"])

            return data
        except json.JSONDecodeError:
            fallback_q = self._generate_fallback_question()
            if fallback_q:
                return {
                    "assessment_status": "need_more_info",
                    "confidence": 0.5,
                    "next_question": fallback_q
                }
            return {"assessment_status": "ready_to_conclude", "confidence": 0.7, "next_question": None}

    def _generate_fallback_question(self) -> Optional[str]:
        """Generate a fallback question if LLM fails."""
        fallbacks = [
            "What specific types of personal data does your AI system process?",
            "Describe the decision-making process: fully automated or human-reviewed?",
            "What are the consequences if your system makes an incorrect decision?",
            "In which EU member states will this system be deployed?",
            "What measures ensure accuracy and prevent bias?",
            "How are users notified they're interacting with an AI system?",
            "What documentation exists for training data and methodology?",
            "Describe your system's impact on fundamental rights."
        ]
        for question in fallbacks:
            if not self._is_duplicate_question(question):
                self.asked_questions_texts.append(question)
                return question
        return None

    def _should_conclude(self, assessment: Dict) -> bool:
        """Determine if assessment should conclude."""
        if len(self.interview_history) < MIN_QUESTIONS:
            return False
        if len(self.interview_history) >= MAX_QUESTIONS:
            return True
        if assessment.get("next_question") is None:
            return True
        if (assessment.get("assessment_status") == "ready_to_conclude" and
            assessment.get("confidence", 0) >= CONFIDENCE_THRESHOLD):
            return True
        return False

    def _extract_articles_with_context(self, chunks: List[DocumentChunk]) -> Dict:
        """Extract article information from chunks."""
        articles_info = {}
        for chunk in chunks:
            for article in chunk.extracted_articles:
                if article not in articles_info:
                    articles_info[article] = {
                        'page': chunk.page_number + 1,
                        'excerpts': [],
                        'full_text': chunk.text[:500]
                    }
        return articles_info

    def _generate_final_analysis(self) -> str:
        """Generate final compliance report."""
        all_content = self.model_description + " " + " ".join([
            f"{qa['question']} {qa['answer']}" for qa in self.interview_history
        ])

        relevant_chunks = self.embeddings.find_relevant_chunks(
            all_content, self.ai_act_chunks, top_k=15
        )
        articles_info = self._extract_articles_with_context(relevant_chunks)
        self.relevant_articles = articles_info

        context_parts = []
        for article, info in sorted(articles_info.items())[:20]:
            context_parts.append(
                f"\n**Article {article}** (Page {info['page']}):\n{info['full_text'][:400]}..."
            )
        article_context = "\n".join(context_parts)

        history_str = "\n".join([
            f"Q{i+1}: {qa['question']}\nA{i+1}: {qa['answer']}"
            for i, qa in enumerate(self.interview_history)
        ])

        prompt = f"""GENERATE COMPREHENSIVE EU AI ACT COMPLIANCE REPORT

SYSTEM ASSESSED:
{self.model_description}

INTERVIEW DATA ({len(self.interview_history)} questions):
{history_str}

RELEVANT EU AI ACT ARTICLES:
{article_context[:3000]}

Generate complete compliance report with risk level, violations, and recommendations."""

        messages = [
            {"role": "system", "content": self._get_system_prompt_for_final_report()},
            {"role": "user", "content": prompt}
        ]

        try:
            return self.llm.chat(messages, temperature=0.2, max_tokens=4000)
        except Exception as e:
            logger.error(f"Report generation failed: {e}")
            return self._generate_emergency_report(articles_info)

    def _generate_emergency_report(self, articles_info: Dict) -> str:
        """Generate basic report if LLM fails."""
        return f"""# EU AI ACT PRELIMINARY ASSESSMENT

⚠️ **AUTOMATED ASSESSMENT - LEGAL REVIEW REQUIRED**

## SYSTEM DESCRIPTION
{self.model_description[:500]}

## INTERVIEW SUMMARY
Total questions: {len(self.interview_history)}

## POTENTIALLY RELEVANT ARTICLES
{chr(10).join([f"- Article {art} (Page {info['page']})" for art, info in sorted(articles_info.items())[:15]])}

## RECOMMENDED ACTIONS
1. Consult EU AI Act legal specialist
2. Determine definitive risk classification
3. Begin conformity assessment if high-risk

**DISCLAIMER:** NOT a legal opinion. Professional counsel required."""

    def process_initial_description(self, description: str) -> Tuple[str, bool]:
      # Store description temporarily but don't set model_description until we know it's not prohibited
      # This ensures the CLI/app can properly handle the awaiting_confirmation state
      desc_lower = description.lower()
      temp_description = description

      prohibited_detections = []

      # ========================================================================
      # Article 5(1)(d) - Biométrie en temps réel dans espaces publics
      # ========================================================================

      realtime_surveillance_patterns = [
          'real-time identification', 'real time identification',
          'real-time recognition', 'real time recognition',
          'real-time biometric', 'real time biometric',
          'live identification', 'live recognition', 'live biometric',
          'continuous surveillance', 'continuous identification',
          'continuous tracking', 'continuous biometric',
          'ongoing surveillance', 'ongoing identification'
      ]

      simple_realtime = ['real-time', 'real time', 'live']

      biometric_indicators = ['facial recognition', 'face recognition', 'biometric identification',
                            'biometric', 'face id', 'facial id']
      public_indicators = ['public space', 'publicly accessible', 'public area', 'street',
                          'transport hub', 'shopping center', 'urban space', 'crowd',
                          'publicly accessible urban']

      has_realtime = any(pattern in desc_lower for pattern in realtime_surveillance_patterns)

      if not has_realtime:
          has_realtime = any(kw in desc_lower for kw in simple_realtime)

      if has_realtime and 'continuous' in desc_lower:
          monitoring_keywords = [
              'continuous monitoring', 'dashboard', 'audit', 'metric',
              'weekly', 'quarterly', 'logging', 'performance monitoring',
              'drift detection', 'accuracy monitoring'
          ]

          surveillance_context = ['surveillance', 'tracking', 'identification', 'general public']

          is_technical_monitoring = any(kw in desc_lower for kw in monitoring_keywords)
          has_surveillance_context = any(kw in desc_lower for kw in surveillance_context)

          if is_technical_monitoring and not has_surveillance_context:
              has_realtime = False

      has_biometric = any(kw in desc_lower for kw in biometric_indicators)
      has_public = any(kw in desc_lower for kw in public_indicators)

      if has_realtime and has_biometric and has_public:
          prohibited_detections.append({
              'type': 'Real-Time Remote Biometric Identification in Public Spaces',
              'article': 'Article 5(1)(d)',
              'severity': 'CRITICAL',
              'evidence': f"System uses real-time facial recognition in publicly accessible spaces",
              'criteria': 'Prohibited for ALL entities (limited exceptions only for law enforcement with judicial authorization)',
              'matches': {
                  'real-time': [kw for kw in realtime_surveillance_patterns + simple_realtime if kw in desc_lower],
                  'biometric': [kw for kw in biometric_indicators if kw in desc_lower],
                  'public': [kw for kw in public_indicators if kw in desc_lower]
              }
          })

      # ========================================================================
      # Article 5(1)(e) - Catégorisation biométrique (attributs sensibles)
      # ========================================================================
      sensitive_attrs = ['race', 'ethnicity', 'ethnic', 'political opinion', 'religious belief',
                        'sexual orientation', 'philosophical belief']
      biometric_inference = ['infer', 'deduce', 'predict', 'categorize', 'categorise', 'classify']

      has_sensitive = any(attr in desc_lower for attr in sensitive_attrs)
      has_inference = any(method in desc_lower for method in biometric_inference)

      exclusion_contexts = [
          'balanced across', 'balance across', 'balanced for',
          'no demographic classification', 'excluded scope',
          'does not infer', 'does not classify', 'does not categorize',
          'no inference', 'no classification', 'no categorization',
          'prevent bias', 'avoid bias', 'mitigate bias',
          'diversity in training', 'representative dataset'
      ]

      is_compliance_context = any(context in desc_lower for context in exclusion_contexts)

      if has_biometric and has_sensitive and (has_inference or 'attribute' in desc_lower) and not is_compliance_context:
          detected_attrs = [attr for attr in sensitive_attrs if attr in desc_lower]
          prohibited_detections.append({
              'type': 'Biometric Categorization Based on Sensitive Attributes',
              'article': 'Article 5(1)(e)',
              'severity': 'CRITICAL',
              'evidence': f"System infers sensitive attributes: {', '.join(detected_attrs)}",
              'criteria': 'Biometric categorization to infer race, political opinions, religion, sexual orientation is PROHIBITED',
              'matches': {
                  'sensitive_attributes': detected_attrs,
                  'inference_method': [m for m in biometric_inference if m in desc_lower]
              }
          })

      # ========================================================================
      # Article 5(1)(c) - Social Scoring
      # ========================================================================
      social_scoring = ['social scoring', 'social credit', 'trustworthiness score',
                      'citizen score', 'social ranking', 'reputation score']
      authority_indicators = ['government', 'public authority', 'state', 'municipality', 'agency']

      has_social_scoring = any(kw in desc_lower for kw in social_scoring)
      has_authority = any(kw in desc_lower for kw in authority_indicators)

      if has_social_scoring or (has_authority and 'trustworthiness' in desc_lower):
          prohibited_detections.append({
              'type': 'Social Scoring by Public Authorities',
              'article': 'Article 5(1)(c)',
              'severity': 'CRITICAL',
              'evidence': 'System evaluates trustworthiness/social behavior for governmental purposes',
              'criteria': 'Social scoring by public authorities leading to detrimental treatment is PROHIBITED'
          })

      # ========================================================================
      # Article 5(1)(a) - Manipulation subliminale
      # ========================================================================
      manipulation = ['subliminal', 'subconscious', 'manipulate behavior', 'manipulative technique',
                    'exploit psychological']

      if any(kw in desc_lower for kw in manipulation):
          prohibited_detections.append({
              'type': 'Subliminal Manipulation',
              'article': 'Article 5(1)(a)',
              'severity': 'CRITICAL',
              'evidence': 'System uses subliminal or manipulative techniques',
              'criteria': 'Techniques beyond consciousness causing harm are PROHIBITED'
          })

      # ========================================================================
      # Article 5(1)(b) - Exploitation de vulnérabilités
      # ========================================================================
      vulnerability_exploit = ['exploit vulnerability', 'exploit disabilities', 'exploit age',
                              'target vulnerable', 'exploit economic situation']

      if any(kw in desc_lower for kw in vulnerability_exploit):
          prohibited_detections.append({
              'type': 'Exploitation of Vulnerabilities',
              'article': 'Article 5(1)(b)',
              'severity': 'CRITICAL',
              'evidence': 'System exploits vulnerabilities of specific groups',
              'criteria': 'Exploiting vulnerabilities (age, disability, socio-economic) is PROHIBITED'
          })

      # ========================================================================
      # Article 5(1)(g) - Predictive Policing basé sur le profilage
      # ========================================================================
      predictive = ['predictive policing', 'crime prediction', 'risk assessment', 'recidivism prediction']
      profiling = ['profiling', 'personality trait', 'behavioral pattern', 'individual characteristic']

      has_predictive = any(kw in desc_lower for kw in predictive)
      has_profiling = any(kw in desc_lower for kw in profiling)

      if has_predictive and has_profiling:
          prohibited_detections.append({
              'type': 'Predictive Policing Based on Profiling',
              'article': 'Article 5(1)(g)',
              'severity': 'HIGH',
              'evidence': 'System predicts criminal behavior based on profiling',
              'criteria': 'Risk assessment based SOLELY on profiling or personality traits is PROHIBITED'
          })

      # ========================================================================
      # GÉNÉRATION DU RAPPORT SI DÉTECTIONS
      # ========================================================================
      if prohibited_detections:
          # Store in pending_description for final report, but don't set model_description
          # This keeps the CLI/app in "awaiting initial description" state
          self.pending_description = temp_description

          # Trier par sévérité
          critical = [d for d in prohibited_detections if d['severity'] == 'CRITICAL']
          high = [d for d in prohibited_detections if d['severity'] == 'HIGH']

          report = "⛔ **PROHIBITED AI SYSTEM DETECTED**\n\n"
          report += f"**{len(prohibited_detections)} Article 5 violation(s) identified:**\n\n"

          for detection in critical + high:
              report += f"### 🚨 {detection['type']}\n"
              report += f"**{detection['article']}** | Severity: {detection['severity']}\n\n"
              report += f"**Evidence from your description:**\n{detection['evidence']}\n\n"
              report += f"**Legal requirement:**\n{detection['criteria']}\n\n"

              # Afficher les correspondances détectées si disponibles
              if 'matches' in detection:
                  report += "**Detected indicators:**\n"
                  for category, keywords in detection['matches'].items():
                      if keywords:
                          report += f"- {category.replace('_', ' ').title()}: {', '.join(keywords)}\n"
                  report += "\n"

              report += "---\n\n"

          report += """## 💰 **PENALTIES - Article 99(3)**
  **Maximum fine:** €35,000,000 OR 7% of total worldwide annual turnover (whichever is higher)

  **Additional consequences:**
  - Immediate system shutdown order
  - Criminal liability (varies by Member State)
  - Civil liability for damages to affected individuals
  - Permanent market ban in the EU

  ---

  ## 🛑 **IMMEDIATE ACTIONS REQUIRED**

  1. **HALT all operations immediately** - Do NOT deploy or continue using this system
  2. **Engage qualified legal counsel** urgently (EU AI Act + GDPR specialist)
  3. **Document everything** - Preserve records of system capabilities and usage
  4. **Notify authorities if already deployed:**
    - Data Protection Authority (GDPR breach notification)
    - National AI Office / Market Surveillance Authority
  5. **Delete unlawfully collected data** - Especially biometric data obtained without consent

  ---

  ## ⚠️ **CRITICAL NOTES**

  - These violations are **NOT fixable** through documentation or procedural changes
  - The core functionality of your system is fundamentally prohibited
  - There is NO compliance path that maintains this functionality
  - Even if you disagree with this assessment, you MUST consult legal counsel before proceeding

  ---

  ## 📋 **LEGAL DISCLAIMER**

  This is an automated preliminary assessment based on pattern matching in your system description.
  It is NOT a legal opinion. However, the detected indicators are severe enough that you should
  treat this as a legal emergency requiring immediate professional legal consultation.

  ---

  **Your options:**
  - Type `quit` to exit and contact legal counsel (STRONGLY RECOMMENDED)
  - Type `continue` to proceed with detailed assessment (system remains prohibited regardless)
  - Type `dispute` if you believe the detection is incorrect (will ask clarifying questions)

  Your choice: """

          return report, True

      # Aucune pratique prohibée détectée clairement
      return "✅ No obvious Article 5 violations detected in initial description. Proceeding with detailed compliance assessment...", False

    def ask_next_question(self) -> Tuple[str, bool]:
        """Generate and return the next question."""
        assessment = self._generate_question()

        if self._should_conclude(assessment):
            logger.info("📊 Generating final assessment...")
            return self._generate_final_analysis(), True

        next_q = assessment.get("next_question")
        if not next_q:
            return self._generate_final_analysis(), True

        return next_q.strip(), False

    def process_answer(self, answer: str, question: str) -> Tuple[str, bool]:
        """Process user answer and generate next question or final report."""
        if len(answer.split()) < 3 and len(self.interview_history) >= MIN_QUESTIONS:
            return self._generate_final_analysis(), True

        self.interview_history.append({'question': question, 'answer': answer})
        return self.ask_next_question()

    def generate_prohibited_final_report(self) -> str:
        """Generate final report for prohibited systems without further interview."""
        # Use pending_description if available (for systems detected before confirmation)
        description = self.pending_description or self.model_description

        report = f"""# EU AI ACT COMPLIANCE ASSESSMENT - PROHIBITED SYSTEM

⛔ **FINAL DETERMINATION: PROHIBITED AI SYSTEM**

## SYSTEM ASSESSED
{description[:1000]}

## RISK CLASSIFICATION
**Risk Level:** PROHIBITED
**Confidence:** High
**Legal Basis:** Article 5 - Prohibited Artificial Intelligence Practices

## VIOLATION SUMMARY

Based on the system description, this AI system falls under **Article 5(1)(d)** of the EU AI Act, which explicitly prohibits:

> "The use of 'real-time' remote biometric identification systems in publicly accessible spaces for the purpose of law enforcement, unless certain limited exceptions apply"

### Evidence of Prohibited Practice

This system exhibits the following prohibited characteristics:

1. **Real-time operation**: The system operates continuously and performs identification in real-time
2. **Biometric identification**: Uses facial recognition technology to identify individuals
3. **Publicly accessible spaces**: Deployed in streets, transport hubs, shopping centers, and other public areas
4. **Automated decision-making**: Makes identification decisions without human validation

**This combination is explicitly prohibited under EU law.**

## LEGAL CONSEQUENCES

### Penalties (Article 99)
- **Maximum fine**: €35,000,000 OR 7% of total worldwide annual turnover (whichever is higher)
- **Additional sanctions**:
  - Immediate system shutdown order
  - Market ban in the EU
  - Criminal liability (Member State dependent)
  - Civil liability for damages to affected individuals

### Regulatory Actions
- Mandatory notification to national market surveillance authorities
- Data Protection Authority notification (GDPR breach)
- Potential investigation and enforcement proceedings

## IMMEDIATE ACTIONS REQUIRED

### 1. HALT ALL OPERATIONS ⚠️
- Immediately cease all deployment and use of this system
- Do NOT collect any further biometric data
- Preserve all system logs and documentation for regulatory review

### 2. LEGAL CONSULTATION 📋
- Engage qualified EU AI Act legal counsel immediately
- Consult GDPR/data protection specialists
- Prepare for potential regulatory inquiries

### 3. DATA HANDLING 🗑️
- Assess lawfulness of any data already collected
- Implement data deletion procedures for unlawfully obtained biometric data
- Document all data handling and deletion activities

### 4. NOTIFICATION OBLIGATIONS 📢
If the system has been deployed:
- Notify affected individuals (GDPR Article 34)
- Report to Data Protection Authority within 72 hours (GDPR Article 33)
- Inform national AI market surveillance authority

## COMPLIANCE PATH ASSESSMENT

### Can This System Be Made Compliant?

**NO.** The core functionality of this system is fundamentally prohibited by Article 5(1)(d).

Unlike high-risk AI systems that can achieve compliance through documentation, testing, and oversight measures, **prohibited AI systems cannot be made compliant** through procedural improvements.

The only potential exceptions are:
- Law enforcement use with **judicial authorization** for specific serious crimes (Article 5(1)(d) exceptions)
- These exceptions have **extremely narrow conditions** and require Member State legislation

**For private security or commercial use: NO COMPLIANCE PATH EXISTS.**

## APPLICABLE EU AI ACT ARTICLES

### Article 5 - Prohibited Artificial Intelligence Practices
**Pages**: Throughout Title II of the AI Act
**Status**: VIOLATED
**Gap**: System performs real-time remote biometric identification in public spaces

### Article 99 - Penalties
**Pages**: Near end of the AI Act
**Requirement**: Member States shall establish penalties for violations
**Your exposure**: Maximum tier penalty (€35M or 7% turnover)

### GDPR Implications
This system also likely violates:
- **Article 5(1)(a)**: Unlawful processing (no legal basis)
- **Article 9**: Processing of special category data (biometric data)
- **Article 6**: Lack of lawful basis for processing
- **Article 35**: Required but likely missing DPIA

## DISCLAIMER

⚠️ **This is an automated preliminary assessment, NOT a legal opinion.**

However, the indicators detected are sufficiently clear that you should:
1. Treat this as a legal emergency
2. Seek immediate professional legal counsel
3. Halt all operations pending legal review
4. Preserve all documentation

The determination that this system is prohibited is based on established legal interpretation of Article 5(1)(d) and is consistent with guidance from the European Commission and national regulators.

---

**Assessment completed**: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Session ID**: {id(self)}

---

## NEXT STEPS

Type 'reset' to start a new assessment with a different system.

**DO NOT proceed with deployment or operation of this system.**
"""
        return report

    def reset(self):
        """Reset advisor state for new consultation."""
        self.model_description = ""
        self.pending_description = ""
        self.interview_history = []
        self.asked_questions_texts = []
        self.relevant_articles = {}
        logger.info("✅ Consultation reset")

    def get_progress(self) -> Dict:
        """Get current assessment progress."""
        return {
            "questions_asked": len(self.interview_history),
            "max_questions": MAX_QUESTIONS,
            "min_questions": MIN_QUESTIONS,
            "has_description": bool(self.model_description)
        }
