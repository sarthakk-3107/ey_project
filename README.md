# ey_project
# 🛡️ Sovereign AI Compliance Checker

A RAG-powered tool that analyzes AI deployment scenarios against multi-jurisdictional data sovereignty regulations across 6 regions (EU, India, Saudi Arabia, Singapore, Brazil, UAE).

Built with **Streamlit** and **Claude API** (Anthropic).

## What It Does

- Select a target country/region and an AI deployment scenario
- The tool retrieves relevant regulatory context from a curated knowledge base (data residency laws, model governance, compute locality, export controls)
- Claude analyzes the scenario against the regulatory context and generates a detailed compliance report:
  - **Compliance Feasibility Score** (0–100)
  - **Risk Flags** with severity levels (critical / high / medium / low)
  - **Data Residency Assessment**
  - **Model Governance Requirements**
  - **Compute Recommendations** with valid cloud regions
  - **Required Controls** checklist
  - **Recommended Architecture Pattern**

## Setup

```bash
# Clone the repo
git clone https://github.com/YOUR_USERNAME/sovereign-ai-checker.git
cd sovereign-ai-checker

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## API Key

You need an Anthropic API key. Either:
- Enter it in the sidebar when the app loads, OR
- Set the environment variable:
  ```bash
  export ANTHROPIC_API_KEY="sk-ant-..."
  ```

## Regions Covered

| Region | Key Regulations | Complexity |
|--------|----------------|------------|
| 🇪🇺 European Union | GDPR, EU AI Act | High |
| 🇮🇳 India | DPDPA 2023, IT Act | Medium |
| 🇸🇦 Saudi Arabia | PDPL, SDAIA | High |
| 🇸🇬 Singapore | PDPA, AI Verify | Low |
| 🇧🇷 Brazil | LGPD, AI Bill | Medium |
| 🇦🇪 UAE | Federal Data Protection Law | Medium |

## Tech Stack

- **Frontend:** Streamlit
- **LLM:** Claude (Anthropic API)
- **Pattern:** RAG — structured regulatory knowledge base used as retrieval context for LLM-powered analysis

## Disclaimer

This tool is for educational and demonstration purposes only. It does not constitute legal advice. Regulatory landscapes change frequently — always consult qualified legal counsel for actual deployments.
