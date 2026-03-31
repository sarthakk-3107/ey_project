import streamlit as st
import json
import os
from openai import OpenAI

st.set_page_config(page_title="Sovereign AI Compliance Checker", page_icon="🛡️", layout="wide")

st.markdown("""
<style>
    .risk-critical { border-left: 4px solid #dc2626; padding: 12px 16px; background: rgba(220,38,38,0.08); border-radius: 8px; margin-bottom: 8px; }
    .risk-high { border-left: 4px solid #ea580c; padding: 12px 16px; background: rgba(234,88,12,0.08); border-radius: 8px; margin-bottom: 8px; }
    .risk-medium { border-left: 4px solid #ca8a04; padding: 12px 16px; background: rgba(202,138,4,0.08); border-radius: 8px; margin-bottom: 8px; }
    .risk-low { border-left: 4px solid #16a34a; padding: 12px 16px; background: rgba(22,163,74,0.08); border-radius: 8px; margin-bottom: 8px; }
    .score-box { text-align: center; padding: 24px; background: rgba(30,41,59,0.6); border-radius: 14px; border: 1px solid rgba(148,163,184,0.15); }
    .control-item { padding: 10px 14px; background: rgba(15,23,42,0.5); border-radius: 8px; margin-bottom: 6px; }
    .cloud-tag { display: inline-block; padding: 4px 12px; background: rgba(59,130,246,0.12); border: 1px solid rgba(59,130,246,0.25); border-radius: 6px; margin: 3px; font-size: 13px; color: #93c5fd; }
</style>
""", unsafe_allow_html=True)

# ── Regulatory Knowledge Base ──
REGULATORY_DATA = {
    "European Union 🇪🇺": {
        "laws": ["GDPR", "EU AI Act", "Data Governance Act", "Digital Services Act"],
        "dataResidency": "Data of EU citizens must be processed within the EU/EEA or in countries with an adequacy decision. Cross-border transfers require Standard Contractual Clauses (SCCs) or Binding Corporate Rules.",
        "modelGovernance": "EU AI Act classifies AI systems by risk level (Unacceptable, High, Limited, Minimal). High-risk AI requires conformity assessments, human oversight, transparency documentation, and registration in the EU database.",
        "computeLocality": "No strict compute locality mandate, but GDPR's data minimization and purpose limitation principles effectively require EU-based processing for sensitive data.",
        "exportControls": "Dual-use regulation (EU 2021/821) covers certain AI technologies. Export of surveillance AI to sanctioned countries is restricted.",
        "riskLevel": "High",
        "keyConsiderations": ["AI Act enforcement begins in phases through 2027", "Right to explanation for automated decisions", "DPIAs mandatory for high-risk processing", "Fines up to 35M EUR or 7% global turnover"],
    },
    "India 🇮🇳": {
        "laws": ["Digital Personal Data Protection Act (DPDPA) 2023", "IT Act 2000", "Draft National Data Governance Framework"],
        "dataResidency": "DPDPA allows cross-border transfers except to countries on a government-notified restricted list. Critical personal data may require local storage. Data fiduciaries must appoint a DPO in India.",
        "modelGovernance": "No dedicated AI legislation yet, but DPDPA governs AI systems processing personal data. Sector-specific regulators (RBI, SEBI, IRDAI) have issued AI/ML guidelines.",
        "computeLocality": "IndiaAI Mission building sovereign compute (10,000+ GPUs). RBI requires financial data stored in India. Government projects may mandate domestic compute.",
        "exportControls": "Limited AI-specific export controls. General restrictions under Foreign Trade Act apply to dual-use technologies.",
        "riskLevel": "Medium",
        "keyConsiderations": ["DPDPA enforcement timeline evolving", "Banking/finance rules are strict", "Government pushing indigenous AI models", "Penalties up to 250 Cr INR"],
    },
    "Saudi Arabia 🇸🇦": {
        "laws": ["Personal Data Protection Law (PDPL)", "NDMO Data Governance Regulations", "SDAIA AI Ethics Principles"],
        "dataResidency": "PDPL requires personal data to remain within Saudi Arabia unless transfer meets adequacy conditions. Government data must be processed domestically.",
        "modelGovernance": "SDAIA governs national AI strategy. AI Ethics Principles mandate fairness, transparency, accountability. Sector-specific governance in healthcare (SFDA) and finance (SAMA).",
        "computeLocality": "Strong push for domestic compute under Vision 2030. Government cloud-first policy requires Saudi-based cloud regions.",
        "exportControls": "Restrictions on transferring government and critical infrastructure data outside KSA.",
        "riskLevel": "High",
        "keyConsiderations": ["PDPL enforcement began September 2024", "Government data has strictest residency requirements", "Vision 2030 driving massive AI investment", "Arabic language AI models are a priority"],
    },
    "Singapore 🇸🇬": {
        "laws": ["Personal Data Protection Act (PDPA)", "AI Verify Framework", "Model AI Governance Framework"],
        "dataResidency": "No blanket data localization requirement. Cross-border transfers permitted with comparable protection or contractual safeguards. MAS has specific financial data rules.",
        "modelGovernance": "AI Verify is voluntary self-assessment. Model AI Governance Framework provides implementation guidance. IMDA oversees with light-touch approach.",
        "computeLocality": "No strict mandates. Government encourages Singapore-based cloud for public sector. National compute via NSCC.",
        "exportControls": "Strategic Goods Act covers dual-use tech. Generally business-friendly with minimal AI-specific restrictions.",
        "riskLevel": "Low",
        "keyConsiderations": ["Most innovation-friendly regulatory environment in APAC", "AI Verify gaining international recognition", "Flexible on localization", "MAS has specific AI/ML requirements"],
    },
    "Brazil 🇧🇷": {
        "laws": ["LGPD", "AI Bill (PL 2338/2023 - pending)", "Marco Civil da Internet"],
        "dataResidency": "LGPD allows international transfers under adequacy decisions, SCCs, or consent. No strict localization mandate, but ANPD can restrict transfers.",
        "modelGovernance": "AI Bill proposes risk-based classification similar to EU AI Act. LGPD Art. 20 provides right to review automated decisions.",
        "computeLocality": "No mandatory compute localization. Government encouraging domestic cloud capacity. Public sector may prefer local infrastructure.",
        "exportControls": "Limited AI-specific export controls. General dual-use restrictions via SISCOMEX.",
        "riskLevel": "Medium",
        "keyConsiderations": ["AI Bill still in legislative process", "LGPD covers AI processing of personal data", "Right to human review exists", "ANPD developing AI guidance"],
    },
    "UAE 🇦🇪": {
        "laws": ["Federal Data Protection Law (2021)", "AI Office regulations", "Abu Dhabi Data Management Standards", "DIFC Data Protection Law"],
        "dataResidency": "Federal law requires data adequacy or contractual safeguards. Abu Dhabi government data must stay in-emirate. Free zones (DIFC, ADGM) have separate, more flexible regimes.",
        "modelGovernance": "UAE AI Office drives national strategy. National AI Strategy 2031 emphasizes responsible AI. Sector-specific guidelines emerging.",
        "computeLocality": "Government data requires UAE-based processing. Strong investment in domestic AI compute (G42, Falcon LLM).",
        "exportControls": "Restrictions on government and strategic data. General alignment with international dual-use controls.",
        "riskLevel": "Medium",
        "keyConsiderations": ["Free zone vs mainland regulatory differences", "Fastest-growing AI ecosystem in Middle East", "Falcon LLM shows sovereign model ambitions", "Government is major AI adopter"],
    },
}

SCENARIOS = [
    "Deploy a chatbot handling citizen health records",
    "Train an LLM on government procurement data",
    "Build a credit scoring model using consumer financial data",
    "Deploy facial recognition for public safety",
    "Process employee data for HR analytics platform",
    "Build a recommendation engine for e-commerce",
]


def run_analysis(country: str, scenario: str, api_key: str, provider: str) -> dict:
    """Call Nemotron via OpenAI-compatible API with RAG context."""
    cd = REGULATORY_DATA[country]

    prompt = f"""You are a Sovereign AI compliance analyst. Analyze this deployment scenario against the regulatory context below.

REGULATORY CONTEXT FOR {country}:
- Laws: {', '.join(cd['laws'])}
- Data Residency: {cd['dataResidency']}
- Model Governance: {cd['modelGovernance']}
- Compute Locality: {cd['computeLocality']}
- Export Controls: {cd['exportControls']}
- Risk Level: {cd['riskLevel']}
- Key Considerations: {'; '.join(cd['keyConsiderations'])}

SCENARIO: "{scenario}"

Respond ONLY with a valid JSON object (no markdown, no backticks, no text before or after):
{{
  "complianceScore": <number 0-100>,
  "riskFlags": [{{"flag": "<title>", "severity": "critical|high|medium|low", "detail": "<explanation>"}}],
  "dataResidencyAssessment": "<2-3 sentences>",
  "modelGovernanceRequirements": "<2-3 sentences>",
  "computeRecommendations": "<2-3 sentences>",
  "validCloudRegions": ["<compliant cloud regions/providers>"],
  "requiredControls": ["<specific controls to implement>"],
  "architecturePattern": "<recommended architecture in 2-3 sentences>",
  "timeline": "<compliance deadlines or phasing>"
}}"""

    # Provider config
    providers = {
        "NVIDIA build.nvidia.com — Nemotron 3 Super": {
            "base_url": "https://integrate.api.nvidia.com/v1",
            "model": "nvidia/nemotron-3-super-120b-a12b",
        },
        "NVIDIA build.nvidia.com — Nemotron 3 Nano": {
            "base_url": "https://integrate.api.nvidia.com/v1",
            "model": "nvidia/nemotron-3-nano-30b-a3b",
        },
        "OpenRouter — Nemotron 3 Super (free)": {
            "base_url": "https://openrouter.ai/api/v1",
            "model": "nvidia/nemotron-3-super-120b-a12b:free",
        },
        "OpenRouter — Nemotron 3 Nano (free)": {
            "base_url": "https://openrouter.ai/api/v1",
            "model": "nvidia/nemotron-3-nano-30b-a3b:free",
        },
    }

    cfg = providers[provider]
    client = OpenAI(base_url=cfg["base_url"], api_key=api_key)

    response = client.chat.completions.create(
        model=cfg["model"],
        messages=[
            {"role": "system", "content": "You are a Sovereign AI compliance analyst. Respond with ONLY valid JSON. No markdown, no code fences, no thinking traces."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        max_tokens=2000,
    )

    raw = response.choices[0].message.content.strip()

    # Clean up — Nemotron models sometimes include thinking traces or markdown
    if "<think>" in raw:
        raw = raw.split("</think>")[-1].strip()
    raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()

    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    return json.loads(raw)


# ══════════════════════════════════════
# UI
# ══════════════════════════════════════

st.markdown("# 🛡️ Sovereign AI Compliance Checker")
st.markdown("Analyze AI deployment scenarios against multi-jurisdictional data sovereignty regulations · Powered by **NVIDIA Nemotron**")
st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    provider = st.selectbox("LLM Provider", [
        "NVIDIA build.nvidia.com — Nemotron 3 Super",
        "NVIDIA build.nvidia.com — Nemotron 3 Nano",
        "OpenRouter — Nemotron 3 Super (free)",
        "OpenRouter — Nemotron 3 Nano (free)",
    ])

    # API key loaded from environment variable — never shown in UI
    if "build.nvidia.com" in provider:
        api_key = os.environ.get("NVIDIA_API_KEY", "")
        key_status = "✅ NVIDIA_API_KEY loaded" if api_key else "❌ Set `NVIDIA_API_KEY` env variable"
        key_help = "🔗 [Get free key](https://build.nvidia.com/settings/api-keys)"
    else:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")
        key_status = "✅ OPENROUTER_API_KEY loaded" if api_key else "❌ Set `OPENROUTER_API_KEY` env variable"
        key_help = "🔗 [Get key](https://openrouter.ai/keys)"

    st.markdown(key_status)
    st.markdown(key_help)

    st.divider()
    st.markdown("### 📖 About")
    st.markdown("**RAG** over sovereign AI regulatory data + **NVIDIA Nemotron** for compliance analysis.")
    st.markdown("**Regions:** EU, India, Saudi Arabia, Singapore, Brazil, UAE")
    st.markdown("⚠️ *Educational/demo only. Not legal advice.*")

# Main inputs
col1, col2 = st.columns([1, 1.5])
with col1:
    country = st.selectbox("🌍 Target Region", [""] + list(REGULATORY_DATA.keys()))
with col2:
    scenario_option = st.selectbox("📋 Deployment Scenario", [""] + SCENARIOS + ["✏️ Custom scenario..."])

custom_scenario = ""
if scenario_option == "✏️ Custom scenario...":
    custom_scenario = st.text_input("Describe your AI deployment scenario:")

active_scenario = custom_scenario if scenario_option == "✏️ Custom scenario..." else scenario_option

# Country quick info
if country and country in REGULATORY_DATA:
    cdata = REGULATORY_DATA[country]
    risk_icon = {"High": "🔴", "Medium": "🟡", "Low": "🟢"}.get(cdata["riskLevel"], "")
    with st.expander(f"📋 {country} — Regulatory Overview"):
        st.markdown(f"**Risk:** {risk_icon} {cdata['riskLevel']}  ·  **Laws:** {' · '.join(cdata['laws'])}")
        st.markdown(f"**Data Residency:** {cdata['dataResidency']}")
        st.markdown(f"**Model Governance:** {cdata['modelGovernance']}")
        st.markdown(f"**Compute Locality:** {cdata['computeLocality']}")

# Run
can_run = bool(country and active_scenario and api_key)
if not api_key:
    env_var = "NVIDIA_API_KEY" if "build.nvidia.com" in provider else "OPENROUTER_API_KEY"
    st.warning(f"🔑 Set your `{env_var}` environment variable before running. Example:\n\n`export {env_var}=your-key-here`")

if st.button("🚀 Run Compliance Analysis", disabled=not can_run, use_container_width=True, type="primary"):
    with st.spinner("🔍 Analyzing with Nemotron..."):
        try:
            result = run_analysis(country, active_scenario, api_key, provider)
            st.session_state["result"] = result
            st.session_state["result_country"] = country
            st.session_state["result_scenario"] = active_scenario
        except json.JSONDecodeError as e:
            st.error(f"Failed to parse model response — try again. ({e})")
        except Exception as e:
            st.error(f"Error: {e}")

# ── Results ──
if "result" in st.session_state:
    result = st.session_state["result"]
    st.divider()

    score = result.get("complianceScore", 0)
    score_color = "#22c55e" if score >= 70 else "#eab308" if score >= 40 else "#ef4444"
    score_label = "High Feasibility" if score >= 70 else "Moderate Feasibility" if score >= 40 else "Low Feasibility"

    col_s, col_m = st.columns([1, 3])
    with col_s:
        st.markdown(f"""<div class="score-box">
            <div style="font-size:48px;font-weight:700;color:{score_color}">{score}</div>
            <div style="font-size:13px;color:#94a3b8">/ 100</div>
            <div style="font-size:14px;font-weight:600;color:{score_color};margin-top:4px">{score_label}</div>
        </div>""", unsafe_allow_html=True)
    with col_m:
        st.markdown(f"**Region:** {st.session_state['result_country']}")
        st.markdown(f"**Scenario:** {st.session_state['result_scenario']}")
        st.markdown(f"**Timeline:** {result.get('timeline', 'N/A')}")

    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Overview",
        f"⚠️ Risk Flags ({len(result.get('riskFlags', []))})",
        "🏗️ Architecture",
        "🔒 Controls",
    ])

    with tab1:
        st.markdown("#### Data Residency Assessment")
        st.markdown(result.get("dataResidencyAssessment", ""))
        st.markdown("#### Model Governance Requirements")
        st.markdown(result.get("modelGovernanceRequirements", ""))
        st.markdown("#### Compute Recommendations")
        st.markdown(result.get("computeRecommendations", ""))

    with tab2:
        for rf in result.get("riskFlags", []):
            sev = rf.get("severity", "medium")
            sev_color = {"critical": "#dc2626", "high": "#ea580c", "medium": "#ca8a04", "low": "#16a34a"}.get(sev, "#ca8a04")
            st.markdown(f"""<div class="risk-{sev}">
                <strong style="text-transform:uppercase;font-size:11px;color:{sev_color}">{sev}</strong>
                &nbsp;·&nbsp;<strong>{rf.get('flag', '')}</strong>
                <br><span style="font-size:13px;color:#94a3b8">{rf.get('detail', '')}</span>
            </div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("#### Recommended Architecture")
        st.markdown(result.get("architecturePattern", ""))
        st.markdown("#### Valid Cloud Regions")
        st.markdown("".join(f'<span class="cloud-tag">{r}</span>' for r in result.get("validCloudRegions", [])), unsafe_allow_html=True)

    with tab4:
        st.markdown("#### Required Controls")
        for c in result.get("requiredControls", []):
            st.markdown(f'<div class="control-item">✅ {c}</div>', unsafe_allow_html=True)

    st.divider()
    st.caption("⚠️ Educational/demo only. Not legal advice. Consult qualified counsel for actual deployments.")
