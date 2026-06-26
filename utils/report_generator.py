"""Generates a self-contained HTML verification report."""
from datetime import datetime


def _verdict_color(verdict: str) -> str:
    return {"VERIFIED": "#2ECC71", "INACCURATE": "#F39C12", "FALSE": "#E74C3C"}.get(verdict, "#95A5A6")


def _verdict_emoji(verdict: str) -> str:
    return {"VERIFIED": "✅", "INACCURATE": "⚠️", "FALSE": "❌"}.get(verdict, "🔄")


def generate_report_html(
    results: list[dict],
    file_name: str = "document.pdf",
    verified: int = 0,
    inaccurate: int = 0,
    false_count: int = 0,
) -> str:
    total = len(results)
    accuracy = round(verified / total * 100) if total else 0
    timestamp = datetime.now().strftime("%B %d, %Y at %H:%M")

    claims_html = ""
    for r in results:
        color = _verdict_color(r["verdict"])
        emoji = _verdict_emoji(r["verdict"])
        corrected = f'<p class="corrected"><b>✏️ Real Fact:</b> {r["corrected_fact"]}</p>' if r.get("corrected_fact") else ""
        source = f'<p class="source">🔗 <a href="{r["source_url"]}" target="_blank">{r["source_url"]}</a></p>' if r.get("source_url") else ""

        claims_html += f"""
    <div class="claim-card" style="border-left-color: {color};">
      <span class="verdict" style="background:{color}20; color:{color};">{emoji} {r['verdict']}</span>
      <p class="claim-text">{r['claim']}</p>
      <p class="explanation">{r.get('explanation', '')}</p>
      {corrected}
      {source}
    </div>"""

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>FactCheck Report — {file_name}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; background: #0D1B2A; color: #E2F0F0; padding: 2rem; }}
  .header {{ background: linear-gradient(135deg, #0A9396, #005F73); border-radius: 16px; padding: 2rem; margin-bottom: 2rem; }}
  .header h1 {{ font-size: 2rem; margin-bottom: 0.3rem; }}
  .header p {{ color: #CAE9E9; }}
  .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 1rem; margin-bottom: 2rem; }}
  .stat {{ background: #132636; border-radius: 10px; padding: 1.2rem; text-align: center; }}
  .stat .num {{ font-size: 2rem; font-weight: 800; }}
  .stat .lbl {{ font-size: 0.8rem; color: #7AABB5; margin-top: 0.3rem; }}
  .progress-bar {{ background: #132636; border-radius: 10px; height: 12px; margin: 0.5rem 0 2rem; overflow: hidden; }}
  .progress-fill {{ height: 100%; background: linear-gradient(90deg, #0A9396, #2ECC71); border-radius: 10px; width: {accuracy}%; }}
  .claim-card {{ background: #132636; border-radius: 12px; padding: 1.2rem 1.4rem; margin-bottom: 1rem; border-left: 5px solid #0A9396; }}
  .verdict {{ display: inline-block; border-radius: 20px; padding: 3px 14px; font-size: 0.8rem; font-weight: 700; margin-bottom: 0.6rem; }}
  .claim-text {{ font-size: 1rem; font-weight: 600; color: #E2F0F0; margin-bottom: 0.4rem; }}
  .explanation {{ font-size: 0.9rem; color: #94B5B5; margin-bottom: 0.4rem; }}
  .corrected {{ font-size: 0.85rem; color: #F39C12; margin-bottom: 0.3rem; }}
  .source {{ font-size: 0.78rem; }}
  .source a {{ color: #0A9396; }}
  .footer {{ text-align: center; color: #4A7A7A; font-size: 0.8rem; margin-top: 2rem; }}
  h2 {{ margin-bottom: 1rem; }}
  .accuracy {{ font-size: 1.1rem; margin-bottom: 0.3rem; }}
</style>
</head>
<body>
  <div class="header">
    <h1>🔍 FactCheck Report</h1>
    <p>File: <b>{file_name}</b> · Generated: {timestamp}</p>
  </div>
  <div class="stats">
    <div class="stat"><div class="num" style="color:#E2F0F0">{total}</div><div class="lbl">Total Claims</div></div>
    <div class="stat"><div class="num" style="color:#2ECC71">{verified}</div><div class="lbl">✅ Verified</div></div>
    <div class="stat"><div class="num" style="color:#F39C12">{inaccurate}</div><div class="lbl">⚠️ Inaccurate</div></div>
    <div class="stat"><div class="num" style="color:#E74C3C">{false_count}</div><div class="lbl">❌ False</div></div>
  </div>
  <p class="accuracy">Document Credibility Score: <b>{accuracy}%</b></p>
  <div class="progress-bar"><div class="progress-fill"></div></div>
  <h2>Claim-by-Claim Results</h2>
  {claims_html}
  <div class="footer">FactCheck Agent · Built for Cog Culture Assessment · Powered by Gemini + Serper</div>
</body>
</html>"""
