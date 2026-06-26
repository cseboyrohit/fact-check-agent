"""
Verifies a claim by:
1. Searching the live web via Serper API
2. Asking Gemini to compare claim against search results
Returns verdict: VERIFIED | INACCURATE | FALSE
"""
import json
import re
import requests
import google.generativeai as genai


SERPER_URL = "https://google.serper.dev/search"

VERIFICATION_PROMPT = """You are an expert fact-checker. A document contains the following claim:

CLAIM: {claim}

I searched the web for this claim and found these results:

{search_results}

Based ONLY on the search results above, determine:
1. Is the claim VERIFIED (matches web data), INACCURATE (partially wrong or outdated), or FALSE (contradicted by evidence or no evidence found)?
2. Provide a brief 1-2 sentence explanation.
3. If INACCURATE or FALSE, state the correct fact.
4. Provide the most relevant source URL from the results.

Return ONLY a valid JSON object in this exact format (no markdown):
{{
  "verdict": "VERIFIED" | "INACCURATE" | "FALSE",
  "explanation": "...",
  "corrected_fact": "..." or null,
  "source_url": "https://..." or null
}}"""


def web_search(query: str, api_key: str, num: int = 5) -> list[dict]:
    """Search the web using Serper API."""
    headers = {
        "X-API-KEY": api_key,
        "Content-Type": "application/json",
    }
    payload = {"q": query, "num": num}
    try:
        resp = requests.post(SERPER_URL, headers=headers, json=payload, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        results = []
        for item in data.get("organic", [])[:num]:
            results.append({
                "title": item.get("title", ""),
                "snippet": item.get("snippet", ""),
                "link": item.get("link", ""),
            })
        return results
    except Exception:
        return []


def format_search_results(results: list[dict]) -> str:
    if not results:
        return "No search results found."
    lines = []
    for i, r in enumerate(results, 1):
        lines.append(f"[{i}] {r['title']}\n    {r['snippet']}\n    URL: {r['link']}")
    return "\n\n".join(lines)


def verify_claim(claim: str, serper_key: str, gemini_key: str) -> dict:
    """Verify a single claim and return structured result."""
    # Step 1: Web search
    search_results = web_search(claim, serper_key)
    formatted = format_search_results(search_results)

    # Step 2: Gemini analysis
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    prompt = VERIFICATION_PROMPT.format(
        claim=claim,
        search_results=formatted,
    )

    try:
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(
                temperature=0.1,
                max_output_tokens=512,
            ),
        )
        raw = response.text.strip()
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        parsed = json.loads(raw)
        verdict = parsed.get("verdict", "FALSE").upper()
        if verdict not in ("VERIFIED", "INACCURATE", "FALSE"):
            verdict = "FALSE"

        return {
            "claim": claim,
            "verdict": verdict,
            "explanation": parsed.get("explanation", ""),
            "corrected_fact": parsed.get("corrected_fact"),
            "source_url": parsed.get("source_url"),
        }

    except json.JSONDecodeError:
        # Try extracting JSON from response
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                parsed = json.loads(match.group())
                return {
                    "claim": claim,
                    "verdict": parsed.get("verdict", "FALSE").upper(),
                    "explanation": parsed.get("explanation", "Could not verify this claim."),
                    "corrected_fact": parsed.get("corrected_fact"),
                    "source_url": parsed.get("source_url"),
                }
            except Exception:
                pass

        return {
            "claim": claim,
            "verdict": "FALSE",
            "explanation": "Unable to verify — no supporting evidence found in web search.",
            "corrected_fact": None,
            "source_url": search_results[0]["link"] if search_results else None,
        }

    except Exception as e:
        return {
            "claim": claim,
            "verdict": "FALSE",
            "explanation": f"Verification error: {str(e)}",
            "corrected_fact": None,
            "source_url": None,
        }
