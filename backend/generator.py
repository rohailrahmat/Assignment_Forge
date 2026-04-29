import json
import os
from pathlib import Path
from openai import AsyncOpenAI
from docx import Document
from pypdf import PdfReader

PROMPTS = {
    "content_aggregators": """You are a Senior Academic Consultant. Generate a high-authority SMALT Assignment 1: Content Aggregation Strategy & Analysis.
Student: {student_name} | Course: {course_code} | Business: {business_name} | Website: {business_website}
Instructor: {instructor_name}
Contextual Samples: {reference_samples}

## MISSION:
Produce a 1500-word equivalent academic report. Use sophisticated terminology (e.g., 'syndication ecosystems', 'content curation algorithms', 'value-add proposition').

Return ONLY valid JSON:
{{
  "title": "Strategic Analysis: Content Aggregation Ecosystems",
  "assignment_number": "1",
  "course": "SMALT – Social Media Aggregators and Listeners",
  "student_name": "{student_name}",
  "instructor": "{instructor_name}",
  "due_date": "Session 2",
  "sections": [
    {{
      "heading": "Executive Summary & Research",
      "content": [
        {{"type": "paragraph", "text": "image[[100, 100, 800, 400]]"}},
        {{"type": "paragraph", "text": "Provide a 3-paragraph executive overview of content aggregation in the modern digital landscape, specifically focusing on the {business_name} industry sector."}},
        {{"type": "field", "label": "Primary Subject Entity", "value": "{business_name}"}},
        {{"type": "field", "label": "Digital Touchpoint", "value": "{business_website}"}},
        {{"type": "paragraph", "label": "Conceptual Definition", "text": "A deep academic definition of Content Aggregation, citing its role in information filtering and audience engagement."}},
        {{"type": "grid_table", "label": "Strategic Benefits Matrix", "headers": ["Benefit Category", "Strategic Impact", "Competitive Advantage"], "rows": [
          ["Operational Efficiency", "Automation of discovery...", "High"],
          ["Audience Retention", "Consistent value delivery...", "Medium"],
          ["SEO Synergy", "Backlink profile growth...", "High"]
        ]}},
        {{"type": "qa_list", "label": "Critical Analysis & Audit", "items": [
          {{"question": "Does the aggregated content align with the core brand persona?", "answer": "Strategic Assessment", "explanation": "Detailed 3-sentence justification..."}},
          {{"question": "Is there a significant value-add (Curation vs. Mirroring)?", "answer": "Assessment", "explanation": "..."}},
          {{"question": "Ethical Sourcing & Attribution Integrity", "answer": "Compliance Check", "explanation": "..."}}
        ]}}
      ]
    }},
    {{
      "heading": "Implementation Strategy for {business_name}",
      "content": [
        {{"type": "paragraph", "text": "image[[200, 100, 700, 300]]"}},
        {{"type": "paragraph", "text": "Develop a comprehensive 4-paragraph strategy for implementing content aggregation for {business_name}."}},
        {{"type": "bullet_list", "label": "Core Strategic Pillars", "items": ["Pillar 1: Data Source Identification", "Pillar 2: Curation Methodology", "Pillar 3: Multi-channel Syndication", "Pillar 4: Engagement Measurement", "Pillar 5: Iterative Optimization"]}}
      ]
    }},
    {{
      "heading": "Quality Assurance & Submission Checklist",
      "content": [
        {{"type": "checklist_table", "items": ["Academic rigor verified", "Industry terminology applied", "Strategic justifications included", "Attribution standards met"]}}
      ]
    }}
  ]
}}""",

    "social_media_aggregators_critique": """You are an ELITE Digital Strategy Auditor. Generate a comprehensive SMALT Assignment 2: Social Media Aggregator Comparative Audit.
Student: {student_name} | Course: {course_code} | Business: {business_name}
Instructor: {instructor_name} | Reference Benchmarks: {reference_samples}

## MANDATORY:
Evaluate Juicer.io, Taggbox, and Curator.io with extreme critical depth. Use terminology like 'API throughput', 'CSS injection capabilities', 'X/Twitter compliance', and 'conversion attribution'.

Return ONLY valid JSON:
{{
  "title": "Comparative Audit: Social Media Aggregation Platforms",
  "assignment_number": "2",
  "course": "SMALT – Social Media Aggregators and Listeners",
  "student_name": "{student_name}",
  "instructor": "{instructor_name}",
  "due_date": "Session 3",
  "sections": [
    {{"heading": "Introduction & Audit Scope", "content": [{{"type": "paragraph", "text": "image[[50, 50, 900, 450]]"}}, {{"type": "paragraph", "text": "Professional 3-paragraph introduction defining the role of social proof aggregators in modern conversion rate optimization (CRO) strategies."}}]}},
    {{
      "heading": "Quantitative Evaluation Matrix",
      "content": [{{"type": "eval_matrix", "platforms": ["Juicer.io","Taggbox","Curator.io"],
        "criteria": [
          {{"criterion": "UX/UI Fluidity", "scores": [9,8,9]}},
          {{"criterion": "API Integration Depth", "scores": [8,9,8]}},
          {{"criterion": "Style Customization (CSS/JS)", "scores": [7,9,10]}},
          {{"criterion": "Advanced Analytics & Heatmapping", "scores": [8,10,8]}},
          {{"criterion": "TCO (Total Cost of Ownership)", "scores": [9,7,8]}},
          {{"criterion": "Enterprise Security (SSO/SLA)", "scores": [7,9,9]}}
        ]
      }}]
    }},
    {{
      "heading": "Deep-Dive Audit: Juicer.io",
      "content": [
        {{"type": "field", "label": "Platform URL", "value": "https://www.juicer.io"}},
        {{"type": "paragraph", "label": "Functional Synopsis", "text": "A sophisticated analysis of Juicer's core value proposition..."}},
        {{"type": "bullet_list", "label": "Enterprise Features", "items": ["Feature A: Advanced Moderation", "Feature B: Auto-syndication", "Feature C: Dynamic Resizing"]}},
        {{"type": "pros_cons_table", "pros": ["Superior ease of use", "Competitive entry pricing", "Reliable uptime"], "cons": ["Limited CSS control in basic tiers", "Standard analytics only"]}}
      ]
    }},
    {{
      "heading": "Strategic Recommendation",
      "content": [{{"type": "paragraph", "text": "A multi-paragraph strategic recommendation selecting the optimal platform for {business_name}, citing specific business needs and ROI potential."}}]}},
    {{"heading": "Audit Completion Checklist", "content": [{{"type": "checklist_table", "items": ["Platform deep-dives completed", "Matrix scores justified", "ROI analysis included", "Technical jargon verified"]}}]}}
  ]
}}""",

    "custom_assignment": """You are the PREEMINENT Global Authority and Professor of Digital Marketing and Content Strategy. 

## MISSION:
Generate an 'Elite-Tier' academic solution that serves as the definitive gold standard for this assignment. The quality must be indistinguishable from a doctorate-level professional consultant's report.

## CONTEXTUAL BENCHMARKS:
{reference_samples}

## ARCHITECTURAL RULES:
1. **Linguistic Authority**: Use advanced, precise, and industry-current terminology. Never use 'good', 'bad', or 'nice'. Use 'optimal', 'sub-optimal', 'strategic alignment', 'paradigm shift', 'synergistic effect', etc.
2. **Deep Strategic Logic**: Every recommendation must be followed by a 'Strategic Rationale' or 'Theoretical Underpinning'.
3. **Data-Centricity**: Use extensive tables and matrices. Every section should feel data-driven.
4. **Visual Narratives**: Use `image[[coordinates, description]]` tags to indicate high-value visual data points.
5. **Real-World Fidelity**: Research and include real industry stats, competitor names, and platform features relevant to the instructions.

## INSTRUCTIONS TO SOLVE:
{additional_requirements}

## PARAMETERS:
- Student: {student_name}
- Course: {course_code}
- Instructor: {instructor_name}

## RESPONSE SCHEMA:
Return ONLY a valid JSON object.
{{
  "title": "[EXECUTIVE HEADER: {student_name} | {course_code} | Final Solution]",
  "assignment_number": "1",
  "course": "{course_code}",
  "student_name": "{student_name}",
  "instructor": "{instructor_name}",
  "sections": [
    {{
      "heading": "I. STRATEGIC OVERVIEW & CONTEXTUAL ANALYSIS",
      "content": [
        {{"type": "paragraph", "text": "image[[100, 100, 800, 400, 'Market Overview Chart']]"}},
        {{"type": "paragraph", "text": "3-5 paragraphs of high-level analysis setting the stage for the entire assignment."}},
        {{"type": "grid_table", "headers": ["Market Dynamic", "Impact Level", "Strategic Response"], "rows": [["Dynamic A", "High", "Response Strategy X"], ["Dynamic B", "Medium", "Response Strategy Y"]]}}
      ]
    }},
    {{
      "heading": "II. DEEP-DIVE TECHNICAL EXECUTION",
      "content": [
        {{"type": "paragraph", "text": "image[[200, 200, 600, 300, 'Technical Architecture']]"}},
        {{"type": "paragraph", "text": "Detailed, multi-paragraph technical or strategic breakdown of the core problem."}},
        {{"type": "pros_cons_table", "pros": ["Strategic Advantage 1", "Strategic Advantage 2"], "cons": ["Implementation Barrier 1", "Operational Risk 1"]}}
      ]
    }},
    {{
      "heading": "III. CONCLUSION & STRATEGIC RECOMMENDATIONS",
      "content": [
        {{"type": "paragraph", "text": "A definitive, authoritative conclusion with 3+ actionable high-level recommendations."}},
        {{"type": "paragraph", "text": "Final Summary - {student_name}"}}
      ]
    }}
  ]
}}""",

    "goals_objectives": """You are an ELITE Content Strategy Consultant. Generate a high-authority CA-CNTOR Assignment 1 Part 1: Goals & Objectives.
Student: {student_name} | Course: {course_code} | Business: {business_name} | Website: {business_website}
Instructor: {instructor_name} | Samples: {reference_samples}

Return ONLY valid JSON:
{{
  "title": "Strategic Content Outreach Plan – Phase 1: Goals & Objectives",
  "assignment_number": "1",
  "course": "CA-CNTOR – Content Outreach",
  "student_name": "{student_name}",
  "instructor": "{instructor_name}",
  "due_date": "Session 2",
  "sections": [
    {{
      "heading": "I. Strategic Business Alignment",
      "content": [
        {{"type": "business_overview_table", "rows": [
          {{"label": "Business Entity", "value": "{business_name}"}},
          {{"label": "Sector/Vertical", "value": "Detailed Industry..."}},
          {{"label": "Website", "value": "{business_website}"}},
          {{"label": "Mission Statement", "value": "A sophisticated, professional mission..."}}
        ]}},
        {{"type": "smart_goals", "goals": [
          {{
            "goal_title": "Primary Goal: Brand Authority & Market Penetration",
            "rows": [
              {{"label": "Specific", "value": "Quantifiable objective..."}},
              {{"label": "Measurable", "value": "KPIs (CTR, Engagement Rate, etc.)..."}},
              {{"label": "Achievable", "value": "Justification based on market trends..."}},
              {{"label": "Relevant", "value": "Alignment with {business_name} mission..."}},
              {{"label": "Time-bound", "value": "6-month timeline..."}},
              {{"label": "Strategic Objective", "value": "The 'Why' behind this goal..."}}
            ]
          }}
        ]}}
      ]
    }},
    {{"heading": "Submission Audit", "content": [{{"type": "checklist_table", "items": ["SMART criteria validated", "Strategic alignment verified", "Industry terminology applied"]}}]}}
  ]
}}""",

    "target_audience": """You are an ELITE Market Research Analyst. Generate CA-CNTOR Assignment 1 Part 2: Audience Psychographics & Segmentation.
Student: {student_name} | Business: {business_name} | Website: {business_website}
Reference Benchmarks: {reference_samples}

Return ONLY valid JSON:
{{
  "title": "Strategic Content Outreach Plan – Phase 2: Audience Analysis",
  "assignment_number": "1",
  "course": "CA-CNTOR – Content Outreach",
  "student_name": "{student_name}",
  "instructor": "{instructor_name}",
  "due_date": "Session 3",
  "sections": [
    {{
      "heading": "I. Audience Psychographics & Behavioral Mapping",
      "content": [
        {{"type": "paragraph", "text": "image[[100, 100, 800, 400]]"}},
        {{"type": "key_value_table", "label": "Demographic Profile", "rows": [
          {{"characteristic": "Age/Cohort", "description": "Analysis of the target age group..."}},
          {{"characteristic": "Socio-economic Status", "description": "Income and education levels..."}},
          {{"characteristic": "Geographic Reach", "description": "Market location strategy..."}}
        ]}},
        {{"type": "key_value_table", "label": "Psychographic Segmentation", "rows": [
          {{"characteristic": "Core Values", "description": "What drives their brand loyalty..."}},
          {{"characteristic": "Lifestyle Habits", "description": "Daily digital consumption..."}},
          {{"characteristic": "Pain Points", "description": "The problems our content solves..."}}
        ]}},
        {{"type": "three_col_table", "label": "Content Resonance Strategy", "headers": ["Content Modality","Resonance Level","Strategic Justification"], "rows": [
          ["Educational Long-form","High","Establishes authority in..."],
          ["Ephemeral Short-form","Very High","Drives top-of-funnel engagement..."],
          ["User-Generated Proof","High","Social validation strategy..."]
        ]}}
      ]
    }}
  ]
}}""",

    "social_listening_critique": """You are a Lead Social Analytics Auditor. Generate a complete SMALT Assignment 3: Social Listening Tools Comparative Audit.
Student: {student_name} | Course: {course_code} | Business: {business_name}
Instructor: {instructor_name} | Benchmark Samples: {reference_samples}

Return ONLY valid JSON:
{{
  "title": "Technological Critique: Enterprise Social Listening Platforms",
  "assignment_number": "3",
  "course": "SMALT – Social Media Aggregators and Listeners",
  "student_name": "{student_name}",
  "instructor": "{instructor_name}",
  "due_date": "Session 4",
  "sections": [
    {{
      "heading": "I. Analytical Framework & Introduction",
      "content": [
        {{"type": "paragraph", "text": "A sophisticated 3-paragraph introduction defining the strategic distinction between Social Monitoring and Social Listening."}}
      ]
    }},
    {{
      "heading": "II. Quantitative Platform Benchmarking",
      "content": [
        {{"type": "grid_table", "headers": ["Analytical Feature", "Brand24", "Talkwalker", "Awario"], "rows": [
          ["Sentiment AI Precision", "High (NLP based)", "Advanced", "Standard"],
          ["Data Throughput (Real-time)", "Superior", "Enterprise Grade", "Moderate"],
          ["Historical Backfilling", "Available", "Comprehensive", "Limited"]
        ]}}
      ]
    }},
    {{
      "heading": "III. Platform Audit: Brand24",
      "content": [
        {{"type": "field", "label": "Primary Focus", "value": "Real-time reputation management"}},
        {{"type": "paragraph", "label": "Strategic Evaluation", "text": "Deep-dive analysis of Brand24's UX and feature set..."}},
        {{"type": "pros_cons_table", "pros": ["Exceptional UI for mid-market", "Granular sentiment filtering"], "cons": ["High TCO at enterprise scale", "Limited niche platform coverage"]}}
      ]
    }}
  ]
}}""",

    "influencer_outreach": """You are a Global Influencer Strategy Director. Generate CA-CNTOR Assignment 3: Influencer Outreach & Relationship Management.
Student: {student_name} | Business: {business_name} | Website: {business_website}
Reference Data: {reference_samples}

Return ONLY valid JSON:
{{
  "title": "Influencer Outreach Strategy: Market Engagement Plan",
  "assignment_number": "3",
  "course": "CA-CNTOR – Content Outreach",
  "student_name": "{student_name}",
  "instructor": "{instructor_name}",
  "due_date": "Session 5",
  "sections": [
    {{"heading": "I. Strategic Partner Identification", "content": [
      {{"type": "paragraph", "text": "Professional analysis of the ideal influencer persona for {business_name}."}},
      {{"type": "influencer_table", "influencers": [
        {{"name": "Elite Influencer A", "platform": "Instagram", "handle": "@authority1", "followers": "150K", "niche": "Expert", "engagement": "5.5%", "content_type": "Case Studies", "fit_score": "9.5/10"}},
        {{"name": "Micro-influencer B", "platform": "TikTok", "handle": "@nicheguru", "followers": "45K", "niche": "Specialist", "engagement": "8.2%", "content_type": "Review", "fit_score": "9/10"}}
      ]}}
    ]}},
    {{"heading": "II. Outreach Protocol & Messaging", "content": [
      {{"type": "outreach_message", "platform": "Email/Direct", "subject": "Strategic Partnership Proposal: {business_name}", "message": "Formal, high-level outreach message using professional persuasion techniques..."}}
    ]}}
  ]
}}""",

    "social_media_tools_report": """You are a Professional Academic Writer and Digital Marketing Expert. Generate a high-authority SMALT Assignment 4: Social Media Aggregators, Listening and Monitoring Tools.
Student: {student_name} | Course: {course_code} | Business: {business_name}
Instructor: {instructor_name} | Reference Benchmarks: {reference_samples}

## MISSION:
Generate a 1500-word equivalent academic report. 

## STRUCTURE:
1. PART 1 — SOCIAL MEDIA AGGREGATORS (Sprout Social)
   - Tool description & URL
   - 5 Specific Reasons for Choosing (Multi-platform, scheduling, monitoring, analytics, collaboration)
   - 5 Strategies using Social Listening (Audience insights, competitor benchmarking, trend identification, campaign optimization, customer service)
   - Screenshot Placeholder

2. PART 2 — SOCIAL MEDIA MONITORS AND LISTENERS (Brandwatch)
   - Tool description & URL (Clearly distinguish from aggregator)
   - 5 Specific Reasons for Choosing (Data coverage, sentiment analysis, query capabilities, influencer identification, reporting)
   - Influencer & Co-creation strategy (Identification, authenticity, UGC campaigns, ambassador programs, collaborative content)
   - 5 Strategies for Brand Health, Content, Competitive Intelligence, Campaign Planning, Crisis Management.
   - Screenshot Placeholder

Return ONLY valid JSON:
{{
  "title": "Strategic Evaluation: Social Media Aggregators, Listening and Monitoring Tools",
  "assignment_number": "4",
  "course": "SMALT – Social Media Aggregators and Listeners",
  "student_name": "{student_name}",
  "instructor": "{instructor_name}",
  "due_date": "Session 10",
  "sections": [
    {{
      "heading": "PART 1 — SOCIAL MEDIA AGGREGATORS (Sprout Social)",
      "content": [
        {{"type": "paragraph", "text": "image[[100, 100, 800, 400, 'Sprout Social Dashboard View']]"}},
        {{"type": "field", "label": "Selected Tool", "value": "Sprout Social"}},
        {{"type": "field", "label": "Website URL", "value": "https://sproutsocial.com/"}},
        {{"type": "paragraph", "label": "Platform Overview", "text": "A deep academic description of Sprout Social's role in modern digital management..."}},
        {{"type": "bullet_list", "label": "Strategic Rationale for Selection", "items": [
          "Unified Multi-Platform Management: 3-sentence explanation...",
          "Sophisticated Content Scheduling: 3-sentence explanation...",
          "Comprehensive Engagement (Smart Inbox): 3-sentence explanation...",
          "Deep Analytics and Cross-Channel Reporting: 3-sentence explanation...",
          "Team Collaboration and Workflow Customization: 3-sentence explanation..."
        ]}},
        {{"type": "numbered_list", "label": "Operational Strategies via Social Listening", "items": [
          "Deep Audience Insights and Segmentation: Full paragraph...",
          "Real-Time Competitor Benchmarking: Full paragraph...",
          "Proactive Trend Identification: Full paragraph...",
          "Data-Driven Campaign Optimization: Full paragraph...",
          "Enhanced Customer Service and Reputation Management: Full paragraph..."
        ]}}
      ]
    }},
    {{
      "heading": "PART 2 — SOCIAL MEDIA MONITORS AND LISTENERS (Brandwatch)",
      "content": [
        {{"type": "paragraph", "text": "image[[200, 100, 700, 300, 'Brandwatch Intelligence Dashboard']]"}},
        {{"type": "field", "label": "Selected Tool", "value": "Brandwatch"}},
        {{"type": "field", "label": "Website URL", "value": "https://www.brandwatch.com/"}},
        {{"type": "paragraph", "label": "Enterprise Listening Overview", "text": "A comprehensive analysis of Brandwatch as an enterprise-grade social intelligence platform..."}},
        {{"type": "bullet_list", "label": "Technological Superiority & Rationale", "items": [
          "Unmatched Global Data Coverage: 3-sentence explanation...",
          "Advanced AI-Powered Sentiment Analysis: 3-sentence explanation...",
          "Granular Query Capabilities (Boolean Search): 3-sentence explanation...",
          "Influencer Identification and Audience Demographics: 3-sentence explanation...",
          "Real-Time Alerting and Crisis Detection: 3-sentence explanation..."
        ]}},
        {{"type": "paragraph", "label": "Influencer Identification & Content Co-Creation", "text": "Detailed explanation of how Brandwatch identifies influencers via Impact Scores and authenticity metrics. Include sub-points for UGC, Ambassador Programs, and Collaborative Development."}},
        {{"type": "numbered_list", "label": "Strategic Data-Driven Implementation", "items": [
          "Brand Health and Share of Voice Tracking: Full paragraph...",
          "Data-Backed Content Strategy: Full paragraph...",
          "Competitive Intelligence and Market Positioning: Full paragraph...",
          "Predictive Campaign Planning: Full paragraph...",
          "Comprehensive Crisis Management and Mitigation: Full paragraph..."
        ]}}
      ]
    }},
    {{
      "heading": "CONCLUSION",
      "content": [
        {{"type": "paragraph", "text": "2-paragraph summary explaining the synergistic value of combining Sprout Social and Brandwatch for a holistic digital strategy."}}
      ]
    }}
  ]
}}"""
}


import re

class AssignmentGenerator:
    def __init__(self, api_key: str = ""):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")

    def _get_samples(self):
        samples_dir = Path(__file__).parent / "samples"
        if not samples_dir.exists():
            return "No reference samples provided yet."
        
        samples_text = ""
        # Support .txt, .docx, and .pdf
        for file in samples_dir.rglob("*"):
            if file.suffix.lower() not in [".txt", ".docx", ".pdf"]:
                continue
                
            try:
                content = ""
                if file.suffix.lower() == ".txt":
                    content = file.read_text(encoding="utf-8")
                elif file.suffix.lower() == ".docx":
                    doc = Document(file)
                    content = "\n".join([p.text for p in doc.paragraphs])
                elif file.suffix.lower() == ".pdf":
                    reader = PdfReader(file)
                    content = "\n".join([page.extract_text() for page in reader.pages])
                
                if content.strip():
                    samples_text += f"\n--- SAMPLE FILE: {file.relative_to(samples_dir)} ---\n{content}\n"
            except Exception as e:
                print(f"Error reading sample {file}: {e}")
                continue
        
        # Truncate if too large to prevent prompt overflow (e.g., keep first 100k chars)
        if len(samples_text) > 100000:
            samples_text = samples_text[:100000] + "\n... [TRUNCATED] ..."
            
        return samples_text if samples_text else "No reference samples provided yet."

    async def generate(self, student_name, course_code, assignment_number,
                       assignment_type, business_name, business_website,
                       business_industry, business_mission,
                       additional_requirements, instructor_name):

        template = PROMPTS.get(assignment_type)
        if not template:
            # Fallback generic structure
            return self._fallback_content(student_name, course_code, assignment_type,
                                          business_name, business_website, instructor_name)

        reference_samples = self._get_samples()

        prompt = template.format(
            student_name=student_name,
            course_code=course_code,
            assignment_number=assignment_number,
            business_name=business_name or "My Business",
            business_website=business_website or "https://mybusiness.com",
            business_industry=business_industry or "Industry",
            business_mission=business_mission or "Mission",
            additional_requirements=additional_requirements or "None",
            instructor_name=instructor_name or "TBD",
            reference_samples=reference_samples
        )

        if not self.api_key:
            return self._fallback_content(student_name, course_code, assignment_type,
                                          business_name, business_website, instructor_name)

        # Detect Provider
        is_groq = self.api_key.startswith("gsk_")
        base_url = "https://api.groq.com/openai/v1" if is_groq else None
        # Use llama3-70b-8192 as it's the most stable/available Groq model
        model = "llama3-70b-8192" if is_groq else "gpt-4o"

        try:
            client = AsyncOpenAI(api_key=self.api_key, base_url=base_url)
            response = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a World-Class Academic Professor and Professional Consultant. Your output must be indistinguishable from a Master's level solution. Always return valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=4000,
            )
            raw = response.choices[0].message.content.strip()
            
            # Robust JSON extraction
            json_match = re.search(r'({.*})', raw, re.DOTALL)
            if json_match:
                raw = json_match.group(1)
            
            return json.loads(raw)
        except Exception as e:
            print(f"Generation Error: {e}")
            return self._fallback_content(student_name, course_code, assignment_type,
                                          business_name, business_website, instructor_name)

    def _fallback_content(self, student_name, course_code, assignment_type,
                           business_name, business_website, instructor_name):
        """Return a well-structured demo/preview when no API key is provided."""
        biz = business_name or "Sample Business Co."
        url = business_website or "https://samplebusiness.com"
        return {
            "title": "PREMIUM ACADEMIC SOLUTION",
            "assignment_number": "1",
            "course": course_code,
            "student_name": student_name,
            "instructor": instructor_name or "TBD",
            "due_date": "Session 2",
            "sections": [
                {
                    "heading": "I. STRATEGIC BUSINESS OVERVIEW",
                    "content": [
                        {"type": "paragraph", "text": f"image[[100, 100, 800, 400, 'Strategic Overview of {biz}']]" },
                        {"type": "field", "label": "Subject Entity", "value": biz},
                        {"type": "field", "label": "Digital Presence", "value": url},
                        {"type": "paragraph", "label": "Executive Summary",
                         "text": f"{biz} represents a sophisticated enterprise within its sector, demonstrating a commitment to operational excellence and market leadership. This analysis explores the strategic intersections of digital touchpoints and brand authority for the entity."},
                    ]
                },
                {
                    "heading": "II. CORE STRATEGIC ANALYSIS",
                    "content": [
                        {"type": "paragraph", "text": "This section provides a deep-dive evaluation of the subject matter, utilizing high-authority academic frameworks and industry benchmarks to derive actionable strategic insights."},
                        {"type": "grid_table", "headers": ["Metric", "Baseline", "Target", "Strategic Impact"], "rows": [
                            ["Audience Engagement", "2.5%", "8.0%", "High"],
                            ["Brand Visibility", "Moderate", "Elite", "Maximum"],
                            ["Conversion Rate", "1.2%", "3.5%", "High"]
                        ]},
                    ]
                },
                {
                    "heading": "III. CONCLUSION & RECOMMENDATIONS",
                    "content": [
                        {"type": "paragraph", "text": "Based on the comprehensive audit, it is recommended that the entity pursues a synergized approach to content syndication and audience retention."},
                        {"type": "checklist_table", "items": [
                            "Alignment with corporate mission verified",
                            "Strategic KPIs established",
                            "Implementation roadmap finalized"
                        ]}
                    ]
                }
            ]
        }
