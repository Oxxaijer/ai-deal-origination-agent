import os
import json
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def analyze_article(title: str, description: str, content: str, source: str):
    article_text = f"""
Title: {title}
Description: {description}
Content: {content}
Source: {source}
"""

    prompt = f"""
You are assisting a private equity deal team focused on B2B software and IT services.

Analyze the article and return ONLY valid JSON in this exact structure:

{{
  "company_name": "",
  "other_companies_mentioned": [],
  "industry": "",
  "event_type": "",
  "funding_detected": false,
  "funding_amount": "",
  "country_or_region": "",
  "summary": "",
  "investment_signal": "",
  "growth_score": 0,
  "market_score": 0,
  "strategic_fit": 0,
  "risk_score": 0,
  "overall_score": 0,
  "reasoning": ""
}}

Rules:
- company_name should be the main company in the article.
- other_companies_mentioned should be a JSON array.
- funding_detected must be true if there is any mention of funding, raising capital, round, investment, or financing.
- funding_amount should be empty if unknown.
- event_type should be one of: funding, acquisition, expansion, hiring, product launch, partnership, other.
- investment_signal should be High, Medium, or Low.
- Scores must be integers from 1 to 10.
- overall_score must be a number from 1 to 10.
- Return JSON only. No markdown. No explanation.

Article:
{article_text}
"""

    response = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    raw_output = response.output_text.strip()

    try:
        data = json.loads(raw_output)
        if not isinstance(data.get("other_companies_mentioned", []), list):
            data["other_companies_mentioned"] = []
        return data
    except json.JSONDecodeError:
        return {
            "company_name": "Unknown",
            "other_companies_mentioned": [],
            "industry": "Unknown",
            "event_type": "other",
            "funding_detected": False,
            "funding_amount": "",
            "country_or_region": "",
            "summary": raw_output,
            "investment_signal": "Low",
            "growth_score": 3,
            "market_score": 3,
            "strategic_fit": 3,
            "risk_score": 7,
            "overall_score": 3,
            "reasoning": "Model did not return clean JSON."
        }