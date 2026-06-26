# 🔍 FactCheck Agent — Truth Layer

> Automatically extracts and verifies every factual claim in any PDF against live web data.

Built for the **Cog Culture Product Management Trainee Assessment**.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## ✨ Features

| Feature | Description |
|---|---|
| 📄 PDF Upload | Drag-and-drop any PDF document |
| 🧠 AI Claim Extraction | Gemini identifies all verifiable facts, stats, dates, figures |
| 🌐 Live Web Verification | Each claim verified against live web via Serper API |
| 🏷️ Three-tier Verdict | **VERIFIED** · **INACCURATE** · **FALSE** with evidence |
| 📊 Credibility Score | Overall document credibility percentage |
| 📥 Report Export | Download full HTML verification report |

---

## 🏗️ Architecture

```
factcheck_app/
├── app.py                      # Main Streamlit UI
├── utils/
│   ├── pdf_extractor.py        # PyMuPDF / pdfplumber PDF reader
│   ├── claim_extractor.py      # Gemini claim extraction
│   ├── verifier.py             # Serper search + Gemini verification
│   └── report_generator.py    # HTML report builder
├── .streamlit/
│   ├── config.toml             # Theme & server config
│   └── secrets.toml            # API keys (NOT committed to git)
├── requirements.txt
└── README.md
```

### Flow
```
PDF Upload → Text Extraction → Gemini: Extract Claims
→ For Each Claim: Serper Web Search → Gemini: Verdict
→ Dashboard + HTML Report Download
```

---

## 🚀 Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/factcheck-agent.git
cd factcheck-agent
```

### 2. Create virtual environment
```bash
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure API keys
Create `.streamlit/secrets.toml`:
```toml
GEMINI_API_KEY = "your-gemini-key"
SERPER_API_KEY = "your-serper-key"
```

### 5. Run the app
```bash
streamlit run app.py
```

---

## ☁️ Deploy to Streamlit Cloud

1. **Push to GitHub** (make sure `.streamlit/secrets.toml` is in `.gitignore`)
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Click **New app** → Select your repo → Set `app.py` as main file
4. Go to **Settings → Secrets** and add:
   ```toml
   GEMINI_API_KEY = "your-gemini-key"
   SERPER_API_KEY = "your-serper-key"
   ```
5. Click **Deploy** — live in ~2 minutes ✅

---

## 🔑 API Keys

| Key | Where to Get | Cost |
|---|---|---|
| `GEMINI_API_KEY` | [aistudio.google.com](https://aistudio.google.com) | Free tier available |
| `SERPER_API_KEY` | [serper.dev](https://serper.dev) | 2,500 free queries/month |

---

## 🧪 Testing with Trap Documents

The app is designed to catch:
- **Outdated statistics** — e.g., "ChatGPT has 100M users" (outdated)
- **False financial figures** — e.g., fabricated revenue numbers
- **Wrong dates** — e.g., incorrect founding years
- **Hallucinated facts** — e.g., non-existent products or features

Upload a document containing known false claims to test the system.

---

## 📋 Evaluation Criteria Met

- ✅ PDF upload interface
- ✅ Factual claim extraction (stats, dates, financial figures, company facts)
- ✅ Live web verification (Serper API)
- ✅ Three-tier verdict system: VERIFIED / INACCURATE / FALSE
- ✅ Evidence sources shown for each claim
- ✅ Downloadable verification report
- ✅ Deployment-ready for Streamlit Cloud
- ✅ Clean, attractive UI with dark theme

---

## 🛠️ Tech Stack

- **Frontend**: Streamlit
- **AI Model**: Google Gemini 1.5 Flash
- **Web Search**: Serper API (Google Search)
- **PDF Parsing**: PyMuPDF + pdfplumber (fallback)
- **Deployment**: Streamlit Cloud

---

*Built with ❤️ for the Cog Culture Assessment — 2026*
