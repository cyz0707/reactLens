import json
import anthropic
from dataclasses import dataclass


@dataclass
class AIRecommendation:
    summary: str
    top_issues: list[str]
    remediation_plan: list[str]
    overall_score: int
    score_label: str


def generate_recommendation(
    repo_name: str,
    total_files: int,
    high_debt_files: int,
    medium_debt_files: int,
    low_debt_files: int,
    top_components: list[dict],
    api_key: str,
) -> AIRecommendation:
    """Generate AI-powered debt summary and remediation plan."""

    top_summary = "\n".join([
        f"- {c['filename']} (score: {c['debt_score']}/100): {'; '.join(c['issues'][:2])}"
        for c in top_components[:5]
    ])

    prompt = f"""You are a senior React/TypeScript developer reviewing a codebase for technical debt.

Repository: {repo_name}
Total component files analysed: {total_files}
High debt files (score 60-100): {high_debt_files}
Medium debt files (score 30-59): {medium_debt_files}
Low debt files (score 0-29): {low_debt_files}

Top debt components:
{top_summary}

Respond ONLY with a JSON object in this exact format, no markdown, no preamble:
{{
  "summary": "2-3 sentence plain English summary of the overall debt situation",
  "top_issues": ["most critical issue", "second issue", "third issue"],
  "remediation_plan": [
    "Step 1: ...",
    "Step 2: ...",
    "Step 3: ..."
  ],
  "overall_score": <integer 0-100 where 100 means worst debt>,
  "score_label": "<one of: Healthy, Moderate, Significant, Critical>"
}}"""

    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    )

    text = message.content[0].text.strip()
    text = text.replace("```json", "").replace("```", "").strip()
    data = json.loads(text)

    return AIRecommendation(
        summary=data.get("summary", ""),
        top_issues=data.get("top_issues", []),
        remediation_plan=data.get("remediation_plan", []),
        overall_score=data.get("overall_score", 0),
        score_label=data.get("score_label", "Unknown"),
    )
