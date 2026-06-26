"""
Extracts verifiable factual claims from document text using Gemini API.
"""
import json
import re
import google.generativeai as genai


SYSTEM_PROMPT = """You are a professional fact-checker and claim extraction expert.

Given the text of a document, extract EVERY specific, verifiable factual claim.

Focus on:
- Statistics and percentages (e.g., "X% of users...", "revenue grew by Y%")
- Dates and timelines (e.g., "Founded in 2020", "By 2025...")
- Financial figures (e.g., "valued at $5 billion", "revenue of $2M")
- Company/product facts (e.g., "Company X has 500 employees")
- Technical specifications
- Market size claims
- Named entity facts

IGNORE:
- Opinions and subjective statements
- Vague claims without specific numbers or dates
- Future predictions framed as possibilities

Return a JSON array of claim strings. Each claim should be self-contained and specific.
Return ONLY valid JSON, no markdown, no explanation. Example:
["Claim 1 with specific detail", "Claim 2 with a statistic"]
"""


def extract_claims(text: str, api_key: str) -> list[str]:
    """Extract verifiable claims from document text."""
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Truncate to ~50K chars to stay within context
    truncated = text[:50000]

    prompt = f"{SYSTEM_PROMPT}\n\nDOCUMENT TEXT:\n{truncated}"

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=4096,
            ),
        )
        raw = response.text.strip()

        # Strip markdown code blocks if present
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        claims = json.loads(raw)
        if isinstance(claims, list):
            return [str(c) for c in claims if c][:30]  # Cap at 30 claims
        return []
    except json.JSONDecodeError:
        # Try to extract JSON array from response
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())[:30]
            except Exception:
                pass
        return []
    except Exception as e:
        raise RuntimeError(f"Claim extraction failed: {e}")
