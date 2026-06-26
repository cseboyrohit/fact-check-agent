"""
FactCheck Agent — Cog Culture Assessment
Automates claim extraction and live web verification from PDFs.
"""

import streamlit as st
import json
import time
import os
from datetime import datetime
from utils.pdf_extractor import extract_text_from_pdf
from utils.claim_extractor import extract_claims
from utils.verifier import verify_claim
from utils.report_generator import generate_report_html

# ─── Page Config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="FactCheck Agent | Truth Layer",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Global */
  [data-testid="stAppViewContainer"] { background: #0D1B2A; }
  [data-testid="stHeader"] { background: transparent; }
  .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }

  /* Typography */
  h1, h2, h3, p, label, .stMarkdown { color: #E2F0F0 !important; }

  /* Hero banner */
  .hero {
    background: linear-gradient(135deg, #0A9396 0%, #028090 60%, #005F73 100%);
    border-radius: 16px;
    padding: 2rem 2.5rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 8px 32px rgba(0,0,0,0.35);
  }
  .hero h1 { font-size: 2.4rem; font-weight: 800; margin: 0; color: #fff !important; }
  .hero p  { font-size: 1.05rem; color: #CAE9E9 !important; margin-top: 0.4rem; }
  .badge {
    display: inline-block;
    background: rgba(255,255,255,0.15);
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.75rem;
    color: #fff !important;
    margin-right: 6px;
  }

  /* Upload zone */
  [data-testid="stFileUploader"] {
    background: #132636;
    border: 2px dashed #0A9396;
    border-radius: 12px;
    padding: 1rem;
  }

  /* Claim cards */
  .claim-card {
    background: #132636;
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1rem;
    border-left: 5px solid #0A9396;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
  }
  .claim-card.verified  { border-left-color: #2ECC71; }
  .claim-card.inaccurate{ border-left-color: #F39C12; }
  .claim-card.false     { border-left-color: #E74C3C; }
  .claim-card.checking  { border-left-color: #95A5A6; }

  .verdict-badge {
    display: inline-block;
    border-radius: 20px;
    padding: 3px 14px;
    font-size: 0.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
  }
  .badge-verified   { background: #1A5C36; color: #2ECC71; }
  .badge-inaccurate { background: #5C3D1A; color: #F39C12; }
  .badge-false      { background: #5C1A1A; color: #E74C3C; }
  .badge-checking   { background: #2A2A2A; color: #95A5A6; }

  /* Stats bar */
  .stat-box {
    background: #132636;
    border-radius: 10px;
    padding: 1.2rem;
    text-align: center;
    box-shadow: 0 2px 12px rgba(0,0,0,0.2);
  }
  .stat-num { font-size: 2rem; font-weight: 800; }
  .stat-lbl { font-size: 0.8rem; color: #7AABB5 !important; }

  /* Buttons */
  .stButton > button {
    background: linear-gradient(135deg, #0A9396, #028090) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 0.6rem 2rem !important;
    font-weight: 700 !important;
    font-size: 1rem !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(10,147,150,0.4) !important;
    transition: all 0.2s !important;
  }
  .stButton > button:hover {
    box-shadow: 0 6px 20px rgba(10,147,150,0.6) !important;
    transform: translateY(-1px) !important;
  }

  /* Progress */
  .stProgress > div > div { background: #0A9396 !important; }

  /* Source link */
  .source-link {
    font-size: 0.78rem;
    color: #0A9396 !important;
    word-break: break-all;
  }

  /* Report download */
  .report-box {
    background: #132636;
    border: 1px solid #0A9396;
    border-radius: 12px;
    padding: 1.5rem;
    margin-top: 1.5rem;
    text-align: center;
  }

  /* Sidebar */
  [data-testid="stSidebar"] { background: #0D1B2A !important; }
</style>
""", unsafe_allow_html=True)


# ─── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>🔍 FactCheck Agent</h1>
  <p>Upload any PDF — we extract every factual claim and verify it against the live web in real-time.</p>
  <span class="badge">✨ AI-Powered</span>
  <span class="badge">🌐 Live Web Search</span>
  <span class="badge">📄 PDF Analysis</span>
  <span class="badge">📊 Full Report</span>
</div>
""", unsafe_allow_html=True)


# ─── API Key Check ────────────────────────────────────────────────────────────
gemini_key = os.getenv("GEMINI_API_KEY", "")
serper_key = os.getenv("SERPER_API_KEY", "")

if not gemini_key or not serper_key:
    st.error(
        "⚠️  API keys not configured. Set `GEMINI_API_KEY` and `SERPER_API_KEY` "
        "in your environment or Streamlit Cloud secrets."
    )
    with st.expander("How to configure API keys"):
        st.code("""# .streamlit/secrets.toml
GEMINI_API_KEY = "your-gemini-api-key"
SERPER_API_KEY = "your-serper-api-key"
""")
    st.stop()


# ─── File Upload ─────────────────────────────────────────────────────────────
col_upload, col_info = st.columns([2, 1])

with col_upload:
    st.markdown("### 📤 Upload Document")
    uploaded_file = st.file_uploader(
        "Drop a PDF here or click to browse",
        type=["pdf"],
        label_visibility="collapsed",
    )

with col_info:
    st.markdown("### ℹ️ How It Works")
    st.markdown("""
**Step 1** — Upload any PDF  
**Step 2** — AI extracts all factual claims  
**Step 3** — Each claim is verified against live web  
**Step 4** — Download full verification report
    """)

# ─── Main Logic ──────────────────────────────────────────────────────────────
if uploaded_file:
    pdf_bytes = uploaded_file.read()
    file_name = uploaded_file.name

    st.markdown(f"**📄 File:** `{file_name}` · `{len(pdf_bytes)/1024:.1f} KB`")
    st.divider()

    run_btn = st.button("🚀 Run Fact-Check Analysis", use_container_width=True)

    if run_btn or st.session_state.get("results_ready"):

        if run_btn:
            # ── Extract text ──────────────────────────────────────────────
            with st.spinner("📖 Reading PDF…"):
                pdf_text = extract_text_from_pdf(pdf_bytes)

            if not pdf_text.strip():
                st.error("Could not extract text from PDF. Try a text-based (non-scanned) PDF.")
                st.stop()

            st.success(f"✅ Extracted {len(pdf_text):,} characters from document")

            # ── Extract claims ─────────────────────────────────────────────
            with st.spinner("🧠 Identifying factual claims with Gemini…"):
                claims = extract_claims(pdf_text, gemini_key)

            if not claims:
                st.warning("No verifiable factual claims found in this document.")
                st.stop()

            st.info(f"🎯 Found **{len(claims)} verifiable claims** — starting web verification…")

            # ── Verify each claim ──────────────────────────────────────────
            progress_bar = st.progress(0, text="Verifying claims…")
            results = []

            for i, claim in enumerate(claims):
                progress_bar.progress((i + 1) / len(claims), text=f"Verifying claim {i+1}/{len(claims)}…")
                result = verify_claim(claim, serper_key, gemini_key)
                results.append(result)
                time.sleep(0.3)  # Rate limiting

            progress_bar.empty()
            st.session_state["results"] = results
            st.session_state["results_ready"] = True
            st.session_state["file_name"] = file_name

        results = st.session_state.get("results", [])
        if not results:
            st.stop()

        # ── Summary Stats ──────────────────────────────────────────────────
        verified   = sum(1 for r in results if r["verdict"] == "VERIFIED")
        inaccurate = sum(1 for r in results if r["verdict"] == "INACCURATE")
        false_     = sum(1 for r in results if r["verdict"] == "FALSE")

        st.markdown("## 📊 Verification Summary")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#E2F0F0">{len(results)}</div><div class="stat-lbl">Total Claims</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#2ECC71">{verified}</div><div class="stat-lbl">✅ Verified</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#F39C12">{inaccurate}</div><div class="stat-lbl">⚠️ Inaccurate</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-box"><div class="stat-num" style="color:#E74C3C">{false_}</div><div class="stat-lbl">❌ False</div></div>', unsafe_allow_html=True)

        # Accuracy score
        accuracy = round(verified / len(results) * 100) if results else 0
        st.markdown(f"### Document Credibility Score: **{accuracy}%**")
        st.progress(accuracy / 100)

        st.divider()
        st.markdown("## 🔎 Claim-by-Claim Results")

        # Filter tabs
        tab_all, tab_ver, tab_inac, tab_false = st.tabs([
            f"All ({len(results)})",
            f"✅ Verified ({verified})",
            f"⚠️ Inaccurate ({inaccurate})",
            f"❌ False ({false_})",
        ])

        def render_claims(claim_list):
            if not claim_list:
                st.info("No claims in this category.")
                return
            for r in claim_list:
                verdict = r["verdict"].lower()
                css_class = {"verified": "verified", "inaccurate": "inaccurate", "false": "false"}.get(verdict, "checking")
                badge_class = f"badge-{css_class}"
                emoji = {"verified": "✅", "inaccurate": "⚠️", "false": "❌"}.get(verdict, "🔄")

                st.markdown(f"""
<div class="claim-card {css_class}">
  <span class="verdict-badge {badge_class}">{emoji} {r['verdict']}</span>
  <p style="font-size:1rem; font-weight:600; color:#E2F0F0; margin:0.3rem 0;">{r['claim']}</p>
  <p style="font-size:0.9rem; color:#94B5B5; margin:0.4rem 0;">{r.get('explanation', '')}</p>
  {'<p style="font-size:0.85rem; color:#7AABB5;"><b>Real Fact:</b> ' + r['corrected_fact'] + '</p>' if r.get('corrected_fact') else ''}
  {'<p class="source-link">🔗 Source: <a href="' + r['source_url'] + '" target="_blank" style="color:#0A9396;">' + r['source_url'] + '</a></p>' if r.get('source_url') else ''}
</div>
""", unsafe_allow_html=True)

        with tab_all:
            render_claims(results)
        with tab_ver:
            render_claims([r for r in results if r["verdict"] == "VERIFIED"])
        with tab_inac:
            render_claims([r for r in results if r["verdict"] == "INACCURATE"])
        with tab_false:
            render_claims([r for r in results if r["verdict"] == "FALSE"])

        # ── Download Report ────────────────────────────────────────────────
        st.divider()
        st.markdown('<div class="report-box">', unsafe_allow_html=True)
        st.markdown("### 📥 Download Full Verification Report")

        report_html = generate_report_html(
            results,
            file_name=st.session_state.get("file_name", "document.pdf"),
            verified=verified,
            inaccurate=inaccurate,
            false_count=false_,
        )

        st.download_button(
            label="⬇️ Download HTML Report",
            data=report_html,
            file_name=f"factcheck_report_{datetime.now().strftime('%Y%m%d_%H%M')}.html",
            mime="text/html",
            use_container_width=True,
        )

        st.markdown(
            f"*Report generated on {datetime.now().strftime('%B %d, %Y at %H:%M')}*",
            help="This report can be opened in any browser"
        )
        st.markdown('</div>', unsafe_allow_html=True)


# ─── Footer ──────────────────────────────────────────────────────────────────
st.divider()
st.markdown(
    '<p style="text-align:center; color:#4A7A7A; font-size:0.8rem;">FactCheck Agent · Built for Cog Culture Assessment · Powered by Gemini + Serper</p>',
    unsafe_allow_html=True,
)
